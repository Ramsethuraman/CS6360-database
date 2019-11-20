
class AbstractDBFile(object):
    ''' This is the abstract API used to read and write records from a database
    file. All the SDL implementations of this are hoisted onto a subclass '''

    def __init__(self, columns, data = None):
        ''' Creates a DBFile instance with some data from a tuple of data and
        some columns. Note that subclasses that override the SDL part should
        pass data as None '''

        if data == None and type(self) == AbstractDBFile:
            raise ValueError('Must give data for AbstractDBFile')

        self.__data = data
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
        elif type(column) is int:
            return column
        else:
            raise ValueError('Not a valid column value: ' + str(column) + '')
        

    def find_colind_byname(self, column_name):
        ''' Finds the column index (which is the order that this data is put
        within each record tuple) corresponding to the given column name. Note
        that if there are duplicate columns with the same name, it will return
        the first index that match the name '''
        return self.__colind_byname[column_name]
        
    def findall(self):
        ''' Returns the entire table as a result set'''
        return list([list(a) for a in self.__data])

    def find(self, column, value):
        ''' Searches the DBFile by column name or column index. Returns a list
        of tuples that match the find. '''
        return self._find(self._parse_column(colind), value)

    def _find(self, colind, value):
        ''' Implementation-specific version of find. '''
        rs = []
        for tup in self.__data:
            if tup[colind] == value:
                rs.append(list(tup))
        return rs
                
    def delete(self, column, value):
        ''' Deletes all rows with a specific condition on column. Returns the
        number of rows that are deleted '''
        return self._delete(self._parse_column(colind), value)

    def _delete(self, colind, value):
        ''' Implementation-specific version of update. '''
        changed = 0
        for tup in self.__data:
            if tup[colind] == value:
                changed += 1
                self.__data.remove(tup)
        return changed

    def modify(self, mod_column, new_value, cond_column, cond_value):
        ''' Modifies a column value with all rows that match a condition '''
        return self._modify(self._parse_column(mod_column), new_value, 
                self._parse_column(cond_column), cond_value)

    def _modify(self, mod_colind, new_value, cond_colind, cond_value):
        changed = 0
        for tup in self.__data:
            if tup[cond_colind] == cond_value:
                changed += 1
                tup[mod_colind] = new_value

    def insert(self, tup):
        ''' Inserts a tuple into the table'''
        if len(tup) != len(self.__columns):
            raise ValueError('Expected a tuple of length ' +
                    str(len(self.__columns)))
        self.__data.append(list(tup))
            

    def drop(self):
        ''' Drops the table. Since this is just a RAM layout by default, this
        function does nothing. Should call though because subclasses may need to
        delete the respective file on disk. '''
        pass


