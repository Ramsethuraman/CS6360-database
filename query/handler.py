from file import *
from .tokenizer import Tokenizer, TokenType as tt
import re

types = vt.__members__

def _parse_where(where_clause):
    invert_map = {
        '>=': '<',
        '>': '<=',
        '=': '!=',
        '!=': '=',
        '<': '>=',
        '<=': '>'
    }
    invert = False
    tkn = Tokenizer(where_clause)
    tkn.expect(tt.IDENT)
    if tkn.lval.lower() == 'not':
        invert = True
        tkn.expect(tt.IDENT)
    name = tkn.lval
    tkn.expect(tt.OPER)
    oper = tkn.lval
    if invert:
        oper = invert_map[oper]

    tkn.expect_value()
    val = tkn.lval
    tkn.assert_end()
    return name, val, oper

def create_index_handler(table_name, column_name):
    get_dbfile(table_name).create_index(column_name)

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
    prim = None
    for col in column_list:
        name = col[0]
        if name in used_names:
            raise DBError(f'Two columns defined with same name: `{name}`')
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
                elif val == 'LONG':
                    if dtype != None:
                        raise DBError(f'Multiple data types defined: {dtype} ' +\
                                f'and {val}')
                    dtype = 'BIGINT'
                elif val in types:
                    if dtype != None:
                        raise DBError(f'Multiple data types defined: {dtype} ' +\
                                f'and {val}')
                    dtype = val
                elif val == 'PRIMARY':
                    state = 2
                else:
                    raise DBError(f'Expected: NOT|UNIQUE|types, got {val}')
            elif state == 1:
                if val == 'NULL':
                    is_null = False
                    state = 0
                else:
                    raise DBError('Expected: NULL, got {val}')
            elif state == 2:
                if val == 'KEY':
                    if prim != None:
                        raise DBError('Only one primary key allowed')
                    prim = name
                    state = 0
                else:
                    raise DBError('Expected: KEY, got {val}')

        col_spec.append((name, dtype, len(col_spec) + 1, is_null, is_uniq))

    dbfile = create_dbfile(table_name, col_spec)
    if prim != None:
        dbfile.create_index(prim)

def select_query_handler(column_list, table_name, where_clause):
    tbl = get_dbfile(table_name)
    if column_list == ['*']:
        column_list = tbl.columns[1:]

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
    if where_clause == '':
        #TODO: better performance
        changed = get_dbfile(table_name).deleteall()
    else:
        changed = get_dbfile(table_name).delete(*_parse_where(where_clause))
    print(f'Affected rows: {changed}')

def update_query_handler(table_name, column_name, column_value, where_clause):
    changed = get_dbfile(table_name).modify(column_name, column_value, 
            *_parse_where(where_clause))
    print(f'Affected rows: {changed}')
