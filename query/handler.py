from file import *
import re

types = vt.__members__

def _nicetry(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except:
        return None

def _parse_string(s):
    quote = s[0]
    if quote not in "'\"":
        return None
    if s[-1] != quote:
        return None
    
    ret = ''
    prev_quote = False
    for i in range(1, len(s) - 1):
        if s[i] == quote:
            if prev_quote:
                ret += quote
            prev_quote = not prev_quote
        elif prev_quote:
            return None
        else:
            ret += s[i]

    if prev_quote:
        return None

    return ret

def _parse_where(where_clause):
    SYN_ERROR = 'SYNTAX ERROR: <where clause> should be <NAME> <COND> <VALUE>\n' + \
                '  where cond can be < <= = >= > != \n' + \
                '  and <VALUE> is either int, float, or string'
    parts = re.split(' +', where_clause, 2)
    if len(parts) != 3:
        raise DBError(SYN_ERROR)

    if parts[1] not in ['<', '<=', '=', '!=', '>=', '>']:
        raise DBError(SYN_ERROR)

    val = _nicetry(int, parts[2])
    if val == None:
        val = _nicetry(float, parts[2])
    if val == None:
        val = _nicetry(_parse_string, parts[2])
        print(val)
    if val == None:
        raise DBError(SYN_ERROR)
    return parts[0], parts[1], val

def drop_tables_query_handler(table_name):
    drop_dbfile(table_name)

def show_tables_query_handler():
    get_meta_tables().print_table()

def create_table_query_handler(table_name, column_list):
    SYN_ERROR = 'Syntax error: CREATE TABLE <TABLE_NAME> (<COLUMN_NAME> <DATA_TYPE> <NOT_NULL> <UNIQUE>,...)'

    col_spec = [('rowid', 'INT', 1, False, True)]
    used_names = set(['rowid'])
    for col in column_list:
        parts = re.split(' +', col)
        name = parts[0]
        if name in used_names:
            raise DBError('Two columns defined with same name')
        used_names.add(name)

        state = 0
        is_null = True
        is_uniq = False
        dtype = None
        for val in parts[1:]:
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
        col, cond, val = _parse_where(where_clause)
        rs = tbl.find(col, val, cond, column_list)
    else:
        rs = tbl.findall(column_list)

    tbl.print_table(rs, column_list)

def insert_query_handler(table_name, column_list, value_list):
    #TODO - Not implemented
    pass

def delete_query_handler(table_name, where_clause):
    #TODO - Not implemented
    pass

def update_query_handler(table_name, column_name, column_value, where_clause):
    #TODO - Not implemented
    pass
