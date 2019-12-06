from prettytable import PrettyTable

__all__ = ['FileFormatError', 'AbstractDBFile', 'DBError']

def require_params(params, *names):
    for n in names:
        if params.get(n, None) == None:
            raise ValueError(f'Require parameter "{n}"')

def compare(a, b, inequ):
    ''' Compares a and b using the inequality string given. Note that if the two
    values are not comparable, this will throw an error back to the user. '''
    from .valuetype import NULLVAL


    aa = a != NULLVAL
    bb = b != NULLVAL
    opers = {
        '<': lambda a, b: a < b,
        '<=': lambda a, b: a <= b,
        '=': lambda a, b: a == b,
        '!=': lambda a, b: a != b,
        '>=': lambda a, b: a >= b,
        '>': lambda a, b: a > b
    }

    if inequ not in opers:
        return False

    if aa != bb or a == NULLVAL:
        return opers[inequ](aa, bb)
    else:
        try:
            return opers[inequ](a, b)
        except:
            raise DBError(f'Cannot compare {type(a)} with {type(b)}')

def catch_err(action, *args, **kwargs):
    try:
        return action(*args, **kwargs)
    except DBError:
        raise
    except Exception as exc:
        raise DBError(type(exc).__name__ + ': ' + ' '.join(map(str, exc.args)))

def catch_err_itr(action, *args, **kwargs):
    try:
        yield from action(*args, **kwargs)
    except DBError:
        raise
    except Exception as exc:
        raise DBError(type(exc).__name__ + ': ' + ' '.join(map(str, exc.args)))


class DBError(Exception):
    ''' Special error that can be thrown by any database operation if some error
    occurs. This should be caught and printed out to the end user'''
    pass

class FileFormatError(Exception):
    ''' Error that is thrown when a file format specification gets violated'''
    pass

class AbstractDBFile(object):
    ''' This is the abstract API used to read and write records from a database
    file. All the SDL implementations of this are hoisted onto a subclass '''

    def __init__(self, columns, data = None):
        ''' Creates a DBFile instance with some data from a tuple of data and
        some columns. Note that subclasses that override the SDL part should
        pass data as None '''

        if data == None and type(self) == AbstractDBFile:
            raise ValueError('Must give data for AbstractDBFile')

        if data:
            self.__data = [list(tup) for tup in data]

        self.__columns = tuple(columns)

        colind_bynames = dict()
        for ind, col in enumerate(columns):
            if col not in colind_bynames:
                colind_bynames[col] = ind
        self.__colind_byname = colind_bynames

    @property
    def columns(self):
        return self.__columns

    def _parse_column(self, column):
        if type(column) is str:
            return self.find_colind_byname(column)
        elif type(column) is bytes:
            return self.find_colind_byname(str(column, 'utf8'))
        elif type(column) is int:
            return column
        else:
            raise DBError(f'Invalid column value "{column}"')
        

    def create_index(self, col_name):
        ''' Create an index on the column name. '''
        catch_err(self._create_index, self._parse_column(col_name))

    def _create_index(self, colind):
        # Does nothing by default
        pass

    def find_colind_byname(self, column_name):
        ''' Finds the column index (which is the order that this data is put
        within each record tuple) corresponding to the given column name. Note
        that if there are duplicate columns with the same name, it will return
        the first index that match the name '''
        if column_name not in self.__colind_byname:
            raise DBError(f'Cannot find column "{column_name}" in table')
        return self.__colind_byname[column_name]

    def findall(self, project=None):
        ''' Returns the entire table as a result set'''
        if project != None:
            project = [self._parse_column(col) for col in project]
        rs = catch_err(self._findall)
        return catch_err_itr(self._project, rs, project)
        
    def _findall(self):
        return map(list, self.__data)

    def select(self, column, value, cond='=', project=None):
        ''' Alias to find '''
        return self.find(column, value, cond, project)

    def select_one(self, column, value, cond='=', project=None):
        ''' Select one item '''
        rs = catch_err(self.find, column, value, cond, project)
        try:
            return next(rs)
        except:
            pass

        raise DBError(f'Could not find row where {column} {cond} {value}')
    
    def find(self, column, value, cond='=', project=None):
        ''' Searches the DBFile by column name or column index. Returns a list
        of tuples that match the find. There is also an optional project
        parameter that allows the user to only select certain columns '''
        if project != None:
            project = [self._parse_column(col) for col in project]
        rs = catch_err(self._find, self._parse_column(column), value, cond)
        return catch_err_itr(self._project, rs, project)

    def _find(self, colind, value, cond):
        ''' Implementation-specific version of find. '''
        for tup in self.__data:
            if compare(tup[colind], value, cond):
                yield(list(tup))

    def _project(self, rs, colinds):
        if colinds == None:
            yield from rs
            return
        for tup in rs:
            yield list(tup[c] for c in colinds)
                
    def delete(self, column, value, cond='='):
        ''' Deletes all rows with a specific condition on column. Returns the
        number of rows that are deleted '''
        return catch_err(self._delete, self._parse_column(column), value, cond)


    def _delete(self, colind, value, cond):
        ''' Implementation-specific version of update. '''
        changed = 0
        for tup in list(self.__data):
            if compare(tup[colind], value, cond):
                changed += 1
                self.__data.remove(tup)
        return changed

    def deleteall(self):
        return catch_err(self._deleteall)

    def _deleteall(self):
        self.__data.clear()

    def modify(self, mod_column, new_value, cond_column, cond_value, cond='='):
        ''' Modifies a column value with all rows that match a condition '''
        return catch_err(self._modify, self._parse_column(mod_column), 
                new_value, self._parse_column(cond_column), cond_value, cond)

    def _modify(self, mod_colind, new_value, cond_colind, cond_value, cond='='):
        changed = 0
        for tup in self.__data:
            if compare(tup[cond_colind], cond_value, cond):
                changed += 1
                tup[mod_colind] = new_value
        return changed

    def insert(self, val = None):
        ''' Inserts a row into the table. The caller may either supply an entire
        tuple, or a dict mapping '''
        from .valuetype import NULLVAL

        if val == None:
            raise ValueError('Invalid argument to insert')
        elif type(val) is dict:
            tup = [NULLVAL] * len(self.__columns)
            for key, val in val.items():
                tup[self._parse_column(key)] = val
        elif type(val) in (list, tuple):
            if len(val) != len(self.__columns):
                raise DBError('Expected a tuple of length '+
                        f'{len(self.__columns)}, got length {len(tup)}')
            tup = val

        return catch_err(self._insert, tup)

    def _insert(self, tup):
        if len(tup) != len(self.__columns):
            raise DBError('Expected a tuple of length '+
                    f'{len(self.__columns)}, got length {len(tup)}')
        self.__data.append(list(tup))

    def drop(self):
        ''' Drops the table. Since this is just a RAM layout by default, this
        function does nothing. Should call though because subclasses may need to
        delete the respective file on disk. '''
        catch_err(self._drop)

    def _drop(self):
        pass

    def print_table(self, tups, columns = None):
        if columns == None:
            columns = self.__columns
        tab = PrettyTable()
        tab.field_names = columns
        ct = 0
        for tup in tups:
            ct += 1
            x = list(tup)
            for i in range(len(x)):
                if type(x[i]) == bytes:
                    x[i] = str(x[i], 'utf8')
            tab.add_row(x)

        #if hasattr(self, 'name'):
        #    print('+-' + '-' * len(self.name))
        #    print('| ' + self.name)
        print(tab)
        print(f'{ct} record(s).')
        print('')





