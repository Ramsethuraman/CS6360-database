import os
from sortedcontainers import SortedDict

from .base import AbstractDBFile, FileFormatError, compare, DBError
from .paging import PagingFile, INVALID_OFF
from .table import TableFile
from .valuetype import ValueType as vt, parse_from_str, parse_from_int, \
        vpack1, Float32

__all__ = ['RelationalDBFile', 'create_dbfile', 'drop_dbfile', 'get_dbfile',
        'get_meta_columns', 'get_meta_tables']

path_base = './table'

types = vt.__members__

class DBColumn(object):
    def __init__(self, col_name, data_type, pos, is_nullable, is_unique):
        if data_type not in types:
            raise FileFormatError(f'Invalid data type ({data_type}) ' + \
                    f'for column "{col_name}"')
        self.name = col_name
        self.dtype = types[data_type]
        self.pos = pos
        self.is_nullable = bool(is_nullable)
        self.is_unique = bool(is_unique)

    def to_specs(self):
        return (self.name, self.dtype.name, self.pos, self.is_nullable, 
                self.is_unique)

class Key(object):
    def __init__(self, val): self.val = val
    def __lt__(self, other): return compare(self.val, other.val, '<')
    def __le__(self, other): return compare(self.val, other.val, '<=')
    def __eq__(self, other): return compare(self.val, other.val, '=')

class MemoryIndex(object):
    ''' An ad-hoc memory index file for when an on-file index file does not
    exist. '''

    def __init__(self, tbl, colind):
        self.__idx = SortedDict(Key)
        for tup in tbl:
            rowid = tup[0]
            self.add(rowid, tup[colind])


    def add(self, rowid, key):
        if key not in self.__idx:
            val = set()
            self.__idx[key] = val
        else:
            val = self.__idx[key]
        val.add(rowid)

    def search(self, key, inequality):
        if inequality == '!=':
            for k in self.__idx:
                if compare(k, key, '!='):
                    yield from self.__idx[k]
        elif inequality in ('=', '=='):
            if key in self.__idx:
                yield from self.__idx[key]
        else:
            opers = {
                '<=': {'minimum': None, 'maximum': key},
                '<':  {'minimum': None, 'maximum': key, 
                    'inclusive': (False, False)},
                '>=': {'minimum': key,  'maximum': None},
                '>':  {'minimum': key,  'maximum': None, 
                    'inclusive': (False, False)}
            }
            for k in self.__idx.irange(**opers[inequality]):
                yield from self.__idx[k]

    def delete(self, rowid, key):
        if key not in self.__idx:
            return False
        s = self.__idx[key]
        if rowid not in s:
            return False
        s.remove(rowid)
        return True

def _check_tbl_name(table_name):
    for c in '/\\*.\n\r':
        if c in table_name:
            raise DBError(f'Please do not use {repr(c)} in the table name!')

def create_dbfile(table_name, columns):
    ''' Creates a table from table name, and a list of tuples of column specs, 
    the positions/oridinals given here are ignored and will be automatically
    assigned based on position of columns '''

    _check_tbl_name(table_name)

    if os.access(path_base + table_name + '.tbl', os.F_OK):
        raise DBError(f'Table {table_name} already exists!')
    return RelationalDBFile((table_name, INVALID_OFF, 0), columns)

# TODO: primary
class RelationalDBFile(AbstractDBFile):
    def __init__(self, table_specs, column_specs):
        ''' Creates a relational DB file from the specified table specs and
        column specs.

        table_specs is expected to be a tuple: (table_name, root_page, last_rowid)

        column_specs is expected to be a list of tuples: 
        (column_name, data_type, ordinal_position, is_nullable, is_unique)
        '''

        tbl_name, root_page, last_rowid = table_specs

        cols = [None] * len(column_specs)
        columns = []
        tuple_types = []
        for descr in column_specs: 
            pos = descr[2]
            if pos <= 0 or pos > len(cols) or cols[pos-1] != None:
                raise FileFormatError('Invalid ordinal position for ' + \
                        f'column "{col_name}"')
            cols[pos-1] = DBColumn(*descr)

        if cols[0].to_specs() != ('rowid', "INT", 1, False, True): 
            print(cols[0].to_specs())
            raise DBError('First column of all tables MUST BE rowid')

        for col in cols:
            columns.append(col.name)
            tuple_types.append(col.dtype)

        super().__init__(columns)

        self._meta = False

        self.__name = tbl_name

        self.__cols = cols
        self.__tuple_types = tuple_types[1:]
        
        self.__tbl = TableFile(self._table_file(), self.__tuple_types,
                last_rowid = last_rowid, root_page = root_page)
        self.__idx = [None] * len(cols)

    @property
    def meta(self):
        return self._meta

    def _index_file(self, colind):
        return path_base + self.__name + '_' + self.__cols[colind].name + '.ndx'

    def _table_file(self):
        return path_base + self.__name + '.tbl'

    def _get_index(self, colind, create_mem=True):
        idx = self.__idx[colind] 

        # Return a full-fledged file index if we have one
        if idx != None and type(idx) is not MemoryIndex:
            return idx

        # Otherwise load one if it exists
        index_fname = self._index_file(colind)
        if os.access(index_fname, os.F_OK) :
            idx = None # TODO: load the file idx
            self.__idx[colind] = idx
            return idx

        # Otherwise load a memory index if not already loaded.
        if idx == None and create_mem:
            idx = MemoryIndex(self.__tbl, colind)
            self.__idx[colind] = idx
        return idx

    def _update_dirty(self):
        for prop, val in self.__tbl.dirty_props().items():
            dbfile_tables.modify(prop, val, 'table_name', 
                    bytes(self.__name, 'utf8'))

    def _delete(self, colind, value, cond):
        if cond not in ('=', '!=', '<', '<=', '>', '>='):
            return 0
        rowids = list(self._get_index(colind).search(value, cond))
        deleted = 0
        for rid in rowids:
            tup = self.__tbl.select(rid)

            # Delete table row
            self.__tbl.delete(rid)
            
            # Delete from respective indexes
            for cind, idx in self._itr_loaded_index():
                idx.delete(rid, tup[cind])

            deleted += 1

        self._update_dirty()
        return deleted

    def _drop(self):
        if self.meta:
            raise DBError('Cannot drop meta tables')

        # Delete table
        try:
            os.remove(self._table_file())
        except:
            pass

        # Drop all indexes
        for cind in range(len(self.__cols)):
            try:
                os.remove(self._index_file(cind))
            except:
                pass

        # Update metadata
        name = bytes(self.__name, 'utf8')
        tblid, = dbfile_tables.select_one('table_name', name, ['rowid'])
        dbfile_columns.delete('table_rowid', tblid)
        dbfile_tables.delete('table', name)

    def _itr_loaded_index(self):
        for cind in range(len(self.__cols)):
            idx = self._get_index(cind, False)
            if idx != None:
                yield (cind, idx)
        
    def _find(self, colind, value, cond):
        if cond not in ('=', '!=', '<', '<=', '>', '>='):
            return
        for rowid in self._get_index(colind).search(value, cond):
            yield self.__tbl.select(rowid)

    def _findall(self):
        yield from self.__tbl

    def _check_constraint(ind, value):
        col = self.__cols[ind]

        # Cast it if possible
        col = DBColumn()
        if col.dtype == vt.TEXT:
            if type(value) is str:
                value = bytes(value, 'utf8')
        elif col.dtype is vt.FLOAT and type(value) == float:
            value = Float32(value)
        elif type(value) in (str, bytes):
            value = parse_from_str(value)
        elif type(value) is int:
            value = parse_from_int(value)

        # Check for exact types at this point
        vpack1(col.dtype, value)

        # Check non-null constraints
        if not col.is_nullable and value == None:
            raise DBError(f'Column "{col.name}" must be non-NULL')

        # Check unique constraints
        if col.is_unique:
            found = False
            try:
                next(self._find(ind, value, '='))
                found = True
            except StopIteration:
                found = False

            if found:
                raise DBError(f'Column "{col.name}" must be unique')

        return value

    def _insert(self, tup):
        tup = list(tup)

        # Check all columns (execept rowid)
        for ind in range(1, len(self.__cols)):
            tup[ind] = self._check_constraint(ind, tup[ind])

        # Add to table, ignoring rowid
        rowid = self.__tbl.add(tup[1:])
        tup[0] = rowid

        # Add to loaded indicies
        for cind, idx in self._itr_loaded_index():
            idx.add(tup[0], tup[cind])

        # Update metadata
        self._update_dirty()

    def _modify(self, mod_colind, new_value, cond_colind, cond_value, cond='='):
        new_value = self._check_constraint(mod_colind, new_value)
        for rowid in self._get_index(cond_colind).search(cond_value, cond):
            tup = list(self.__tbl.select(rowid))
            new_tup = list(tup)
            new_tup[mod_colind] = new_value
            new_rowid = self.__tbl.modify(rowid, new_tup)

            if new_rowid != rowid:
                # Delete from index, and re-insert
                idx = self._get_index(mod_colind, False)
                if idx != None:
                    idx.delete(rowid, tup[mod_colind])
                    idx.add(new_rowid, new_value)

                # Delete from respective indexes
                for cind, idx in self._itr_loaded_index():
                    idx.delete(rid, tup[cind])
        
        return 0

tables_cols = (('rowid',      'INT',  1, False, True), 
               ('table_name', 'TEXT', 2, False, True),
               ('root_page',  'INT',  3, False, False),
               ('last_rowid', 'INT',  4, False, False))
columns_cols = (('rowid',       'INT',  1, False, True), 
                ('table_rowid', 'INT',  2, False, False),
                ('column_name', 'TEXT', 3, False, False),
                ('data_type',   'TEXT', 4, False, False),
                ('ordinal_position', 'TINYINT', 5, False, False),
                ('is_nullable', 'TEXT', 6, False, False), 
                ('is_unique',   'TEXT', 7, False, False))

dbfile_tables = None

def _calc_root(fname, tuple_types):
    root = 0
    raw = PagingFile(fname, tuple_types)
    if raw.next_page() == 0:
        return INVALID_OFF

    while True:
        p = raw.read_page(root)
        if p.pnum_parent == INVALID_OFF:
            break
        root = p.pnum_parent

def _meta_create_dbfile(table_name, columns):
    ''' Create a meta database if does not exists, otherwise get database, with
    hard coded column specs '''
    fname = path_base + table_name + '.tbl'
    if os.access(fname, os.F_OK):
        # Only place needed to bypass Table and DBfile api since we need to
        # bootstrap the root_page of this file
        tuple_types = [types[col[1]] for col in columns]
        if dbfile_tables == None:
            root = _calc_root(fname, tuple_types)
            last_rowid = 0
        else:
            try:
                _, _, root, last_rowid = dbfile_tables.select_one('table_name',
                        bytes(table_name, 'utf8'))
            except:
                root = INVALID_OFF
                last_rowid = 0
        ret = RelationalDBFile((table_name, root, last_rowid), columns)
    else:
        ret = RelationalDBFile((table_name, INVALID_OFF, 0), columns)
    ret._meta = True


dbfile_tables = _meta_create_dbfile('davisbase_tables', tables_cols)
dbfile_tables = _meta_create_dbfile('davisbase_tables', tables_cols)
dbfile_columns = _meta_create_dbfile('davisbase_columns', columns_cols)

def get_meta_tables():
    return dbfile_tables

def get_meta_columns():
    return dbfile_columns

def get_dbfile(table_name):
    if table_name == 'davisbase_tables':
        return get_meta_tables()
    elif table_name == 'davisbase_columns':
        return get_meta_columns()

    _check_tbl_name(table_name)
    if not os.access(path_base + table_name + '.tbl', os.F_OK):
        raise DBError(f'Table {table_name} does not exist!')

    _, _, root, last_rowid = dbfile_tables.select_one('table_name',
            bytes(table_name, 'utf8'))

    col_specs = []
    for _, _, col_name, data_type, pos, is_null, is_uniq in \
            dbfile_columns.select('table_name', bytes(table_name, 'utf8')):
        col_specs.append((str(col_name, 'utf8'), str(data_type, 'utf8'), 
                ordinal_position, is_null != b'NO', is_unique != b'NO'))

    return RelationalDBFile((table_name, root, last_rowid), col_specs)


def drop_dbfile(table_name):
    _check_tbl_name(table_name)
    get_dbfile(table_name).drop()


