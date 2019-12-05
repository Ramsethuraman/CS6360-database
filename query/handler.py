from file import *
from .tokenizer import Tokenizer, TokenType as tt
import re

types = vt.__members__

def _parse_where(where_clause):
    tkn = Tokenizer(where_clause)
    tkn.expect(tt.IDENT)
    name = tkn.lval
    tkn.expect(tt.OPER)
    oper = tkn.lval
    tkn.expect(tt.INT, tt.FLOAT, tt.TEXT)
    val = tkn.lval
    tkn.assert_end()
    return name, val, oper

def create_index_handler(table_name, column_name):
    # TODO
    pass

def drop_tables_query_handler(table_name):
    drop_dbfile(table_name)
    print(f'Dropped {table_name}')

def show_tables_query_handler():
    tbls = get_meta_tables()
    tbls.print_table(tbls.findall(project=['table_name']), ['table_name'])

def create_table_query_handler(table_name, column_list):
    SYN_ERROR = 'Syntax error: CREATE TABLE <TABLE_NAME> (<COLUMN_NAME> <DATA_TYPE> <NOT_NULL> <UNIQUE>,...)'

    col_spec = [('rowid', 'INT', 1, False, True)]
    used_names = set(['rowid'])
    for col in column_list:
        name = col[0]
        if name in used_names:
            raise DBError('Two columns defined with same name')
        used_names.add(name)

        state = 0
        is_null = True
        is_uniq = False
        dtype = None
        for val in col[1:]:
            val = val.upper()
            if state == 0:
                if val == 'NOT':
                    state = 1
                elif val == 'UNIQUE':
                    is_uniq = True
                elif val in types:
                    if dtype != None:
                        raise DBError('Multiple data types defined')
                    dtype = val
                else:
                    raise DBError(SYN_ERROR)
            elif state == 1:
                if val == 'NULL':
                    is_null = False
                    state = 0
                else:
                    raise DBError(SYN_ERROR)

        col_spec.append((name, dtype, len(col_spec) + 1, is_null, is_uniq))

    create_dbfile(table_name, col_spec)

def select_query_handler(column_list, table_name, where_clause):
    if column_list == ['*']:
        column_list = None

    tbl = get_dbfile(table_name)
    if where_clause:
        args = tuple(_parse_where(where_clause)) + (column_list,)
        rs = tbl.find(*args)
    else:
        rs = tbl.findall(column_list)

    tbl.print_table(rs, column_list)

def insert_query_handler(table_name, column_list, value_list):
    tbl = get_dbfile(table_name)
    mapping = {}
    for col, val in zip(column_list, value_list):
        mapping[col] = val
    tbl.insert(mapping)
    print(f'Affected rows: 1')

def delete_query_handler(table_name, where_clause):
    changed = get_dbfile(table_name).delete(*_parse_where())
    print(f'Affected rows: {changed}')

def update_query_handler(table_name, column_name, column_value, where_clause):
    changed = get_dbfile(table_name).delete(column_name, column_value, 
            *_parse_where())
    print(f'Affected rows: {changed}')
