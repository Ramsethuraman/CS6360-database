import os
from sortedcontainers import SortedDict

from .base import AbstractDBFile, FileFormatError, compare, DBError
from .table import TableFile
from .valuetype import ValueType

path_base = './'

types = ValueType.__members__

class DBColumn(object):
    def __init__(self, col_name, data_type, is_nullable, is_unique):
        if data_type not in types:
            raise FileFormatError(f'Invalid data type ({data_type}) ' + \
                    f'for column "{col_name}"')
        self.name = col_name
        self.dtype = types[data_type]
        self.is_nullable = bool(is_nullable)
        self.is_unique = bool(is_unique)

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
            col_name, data_type, pos, is_nullable, is_unique = descr
            if pos <= 0 or pos > len(cols) or cols[pos-1] != None:
                raise FileFormatError('Invalid ordinal position for ' + \
                        f'column "{col_name}"')
            cols[pos-1] = DBColumn(col_name, data_type, is_nullable, is_unique)

        for col in cols:
            columns.append(col.name)
            tuple_types.append(col.dtype)

        super().__init__(columns)

        self.__name = tbl_name

        self.__cols = cols
        self.__tuple_types = tuple_types[1:]
        
        self.__tbl = TableFile(self._table_file(), self.__tuple_types,
                last_rowid = last_rowid, root_page = root_page)
        self.__idx = [None] * len(cols)

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
            # TODO: should we lazy load, or load all indexes on startup?
            idx = None # TODO: load the file idx
            self.__idx[colind] = idx
            return idx

        # Otherwise load a memory index if not already loaded.
        if idx == None and create_mem:
            idx = MemoryIndex(self.__tbl, colind)
            self.__idx[colind] = idx
        return idx

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

        #TODO: update meta tables

        return deleted

    def _drop(self):
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

        # TODO: update meta tables

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

    def _insert(self, tup):
        tup = list(tup)
        for ind, col in enumerate(self.__cols):
            if ind == 0: # Skip rowid
                continue

            # Check non-null constraints
            if not col.is_nullable and tup[ind] == None:
                raise DBError(f'Column "{col.name}" must be non-NULL')

            # Check unique constraints
            if col.is_unique:
                found = False
                try:
                    next(self._find(ind, tup[ind], '='))
                    found = True
                except StopIteration:
                    found = False

                if found:
                    raise DBError(f'Column "{col.name}" must be unique')

        # Add to table, ignoring rowid
        rowid = self.__tbl.add(tup[1:])
        tup[0] = rowid

        # Add to loaded indicies
        for cind, idx in self._itr_loaded_index():
            idx.add(tup[0], tup[cind])

    def _modify(self, mod_colind, new_value, cond_colind, cond_value, cond='='):
        # TODO:
        return 0


