import os
from sortedcontainers import SortedDict

from .base import AbstractDBFile, FileFormatError, compare, DBError
from .paging import PagingFile, INVALID_OFF
from .table import TableFile
from .index import IndexFile
from .valuetype import ValueType as vt, parse_from_str, parse_from_int, \
        vpack1, Float32, NULLVAL

__all__ = ['RelationalDBFile', 'create_dbfile', 'drop_dbfile', 'get_dbfile',
        'get_meta_columns', 'get_meta_tables']

path_base = './table/'

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

def init_idx_with(idx, tbl, colind):
    for tup in tbl:
        rowid = tup[0]
        idx.add(rowid, tup[colind])

class MemoryIndex(object):
    ''' An ad-hoc memory index file for when an on-file index file does not
    exist. '''

    def __init__(self, tbl, colind):
        self.__idx = SortedDict(Key)
        init_idx_with(self, tbl, colind)

    def add(self, rowid, key):
        if key not in self.__idx:
            val = set()
            self.__idx[key] = val
        else:
            val = self.__idx[key]
        val.add(rowid)

    def clear(self):
        self.__idx.clear()

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

    def modify(self, old_rowid, new_rowid, key):
        if key not in self.__idx:
            return False
        s = self.__idx[key]
        if rowid not in s:
            return False
        s.remove(old_rowid)
        s.add(new_rowid)
        return True

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


# TODO: primary don't need that
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

    def close(self):
        self.__tbl.close()

    def flush(self):
        self.__tbl.flush()

    @property
    def meta(self):
        return self._meta

    @property
    def name(self):
        return self.__name

    def _index_file(self, colind):
        return path_base + self.__name + '.' + self.__cols[colind].name + '.ndx'

    def _table_file(self):
        return path_base + self.__name + '.tbl'

    def _create_index(self, colind):
        index_fname = self._index_file(colind)
        if os.access(index_fname, os.F_OK):
            raise DBError(f'Index for column {self.__cols[colind].name} ' + \
                    'already exists!')
        idx = IndexFile(open(index_fname, 'w+b'), [self.__cols[colind].dtype])
        self.__idx[colind] = idx
        init_idx_with(idx, self.__tbl, colind)

    def _get_index(self, colind, create_mem=True):
        idx = self.__idx[colind] 

        # Return a full-fledged file index if we have one
        if idx != None and type(idx) is not MemoryIndex:
            return idx

        # Otherwise load one if it exists
        index_fname = self._index_file(colind)
        if os.access(index_fname, os.F_OK) :
            idx = IndexFile(open(index_fname, 'r+b'), [self.__cols[colind].dtype])
            self.__idx[colind] = idx
            return idx

        # Otherwise load a memory index if not already loaded.
        if idx == None and create_mem:
            idx = MemoryIndex(self.__tbl, colind)
            self.__idx[colind] = idx
        return idx

    def _update_dirty(self):
        if in_bootstrap:
            return
        try:
            dbfile_tables.select_one('table_name', self.__name)
        except:
            print('WARNING: table name not set when update dirty!')
        for prop, val in self.__tbl.dirty_props().items():
            dbfile_tables.modify(prop, val, 'table_name', self.__name)

    def _deleteall(self):
        deleted = len(list(self.__tbl))
        for cind, idx in self._itr_loaded_index():
            idx.clear()

        self.__tbl.clear()
        self._update_dirty()
        return deleted

    def _delete(self, colind, value, cond):
        if cond not in ('=', '!=', '<', '<=', '>', '>='):
            return 0
        value = self._typecast(self.__cols[colind].dtype, value)
        rowids = list(self._get_index(colind).search(value, cond))
        deleted = 0
        for rid in rowids:
            tup = self.__tbl.select(rid)
            if tup == None: continue
            if tup[colind] == NULLVAL: # explicitly disallow nulls
                continue

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
        tblid, = dbfile_tables.select_one('table_name', name, '=', ['rowid'])
        dbfile_columns.delete('table_rowid', tblid)
#        dbfile_tables.delete('table_name', name)

    def _itr_loaded_index(self):
        for cind in range(len(self.__cols)):
            idx = self._get_index(cind, False)
            if idx != None:
                yield (cind, idx)
        
    def _find(self, colind, value, cond):
        if cond not in ('=', '!=', '<', '<=', '>', '>='):
            return
        value = self._typecast(self.__cols[colind].dtype, value)
        for rowid in self._get_index(colind).search(value, cond):
            tup = self.__tbl.select(rowid)
            if tup == None: continue
            if tup[colind] == NULLVAL: # explicitly disallow nulls
                continue
            yield tup

    def _findall(self):
        yield from self.__tbl

    def _typecast(self, dtype, value):
        if value != NULLVAL:
            # Cast it if possible
            if dtype == vt.TEXT:
                if type(value) is str:
                    value = bytes(value, 'utf8')
            elif dtype is vt.FLOAT and type(value) == float:
                value = Float32(value)
            elif type(value) in (str, bytes):
                value = parse_from_str(dtype, value)
            elif type(value) is int:
                value = parse_from_int(dtype, value)

            # Check for exact types at this point
            vpack1(dtype, value)
        return value


    def _check_constraint(self, ind, value):
        col = self.__cols[ind]
        value = self._typecast(col.dtype, value)

        # Check non-null constraints
        if not col.is_nullable and value == NULLVAL:
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

        return rowid

    def _modify(self, mod_colind, new_value, cond_colind, cond_value, cond='='):
        cond_value = self._typecast(self.__cols[cond_colind].dtype, cond_value)
        new_value = self._check_constraint(mod_colind, new_value)
        for rowid in self._get_index(cond_colind).search(cond_value, cond):
            tup = self.__tbl.select(rowid)
            if tup == None: continue
            if tup[cond_colind] == NULLVAL: # explicitly disallow nulls
                continue

            new_tup = list(tup)
            new_tup[mod_colind] = new_value
            new_rowid = self.__tbl.modify(rowid, new_tup[1:])

            if new_rowid == rowid:
                continue

            # Update stuff
            for cind, idx in self._itr_loaded_index():
                if cind == mod_colind:
                    # Delete from index, and re-insert
                    idx = self._get_index(mod_colind, False)
                    if idx != None:
                        idx.delete(rowid, tup[mod_colind])
                        idx.add(new_rowid, new_value)
                else:
                    idx.modify(rowid, new_rowid, tup[cind])
        
        return 0

dbfile_tables = None

def _meta_create_dbfile(table_name, columns):
    ''' Create a meta database if does not exists, otherwise get database, with
    hard coded column specs '''
    fname = path_base + table_name + '.tbl'

    root = INVALID_OFF
    last_rowid = 0
    if os.access(fname, os.F_OK):
        # Only place needed to bypass Table and DBfile api since we need to
        # bootstrap the root_page of this file
        tuple_types = [types[col[1]] for col in columns]
        if dbfile_tables == None:
            pager = PagingFile(fname, tuple_types[1:])
            root = pager.calc_root()
            pager.close()
        else:
            try:
                _, _, root, last_rowid = dbfile_tables.select_one('table_name',
                        bytes(table_name, 'utf8'))
            except:
                pass

    ret = RelationalDBFile((table_name, root, last_rowid), columns)
    ret._meta = True
    return ret

_init = False
_meta = None
_tbls = {}
dbfile_tables = None
dbfile_columns = None
in_bootstrap = True
def _doinit():
    global _init, dbfile_tables, dbfile_columns, _meta, in_bootstrap
    if _init:
        return

    from query import metadata
    _init = True
    _meta = metadata

    old = dbfile_tables = _meta.meta_initialize1()
    in_bootstrap = False
    dbfile_tables._update_dirty()
    old.flush()
    
    in_bootstrap = True

    dbfile_tables, dbfile_columns = _meta.meta_initialize2()
    old.close()

    in_bootstrap = False
    _tbls[dbfile_tables.name] = dbfile_tables
    _tbls[dbfile_columns.name] = dbfile_columns
    dbfile_tables._update_dirty()
    dbfile_columns._update_dirty()

def create_dbfile(table_name, columns):
    ''' Creates a table from table name, and a list of tuples of column specs, 
    the positions/oridinals given here are ignored and will be automatically
    assigned based on position of columns '''

    _doinit()
    _check_tbl_name(table_name)

    if os.access(path_base + table_name + '.tbl', os.F_OK):
        raise DBError(f'Table {table_name} already exists!')
    tbl = RelationalDBFile((table_name, INVALID_OFF, 0), columns)
    _meta.init_metadata_for(table_name, columns)
    _tbls[table_name] = tbl
    return tbl

def get_meta_tables():
    _doinit()
    return dbfile_tables

def get_meta_columns():
    _doinit()
    return dbfile_columns

def get_dbfile(table_name):
    _doinit()
    # Check cache
    if table_name in _tbls:
        return _tbls[table_name]

    # Then go through to actually fetch on disk
    _check_tbl_name(table_name)
    if not os.access(path_base + table_name + '.tbl', os.F_OK):
        raise DBError(f'Table {table_name} does not exist!')

    rowid, _, root, last_rowid = dbfile_tables.select_one('table_name',
            table_name, '=')

    col_specs = _meta.get_column_specs(rowid)
    tbl = RelationalDBFile((table_name, root, last_rowid), col_specs)
    _tbls[tbl.name] = tbl
    return tbl

def drop_dbfile(table_name):
    _check_tbl_name(table_name)
    get_dbfile(table_name).drop()
    _meta.deinit_metadata_for(table_name)
    del _tbls[table_name]

