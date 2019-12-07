from file.relate import _meta_create_dbfile, get_meta_tables, get_meta_columns
from prettytable import PrettyTable

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

def _yesno(boolval):
    return ['NO', 'YES'][bool(boolval)]

def _yn_bool(boolstr):
    if boolstr == b'NO':
        return False
    elif boolstr == b'YES':
        return True
    else:
        x = str(boolstr, 'utf8')
        raise FileFormatError(f'Must be "YES" or "NO" string, but got "{x}"')

def get_column_specs(table_id):
    col_specs = []
    tbl_columns = get_meta_columns()
    for _, _, col_name, data_type, pos, is_null, is_uniq in \
            tbl_columns.select('table_rowid', table_id):
        is_null = _yn_bool(is_null)
        is_uniq = _yn_bool(is_uniq)
        col_specs.append((str(col_name, 'utf8'), str(data_type, 'utf8'), pos, 
            is_null, is_uniq))
    return col_specs

startup = [['davisbase_tables', tables_cols], 
        ['davisbase_columns', columns_cols]]
need_init = False

# TODO: refactor these string constants
def meta_initialize1():
    global need_init
    tbl_tables = _meta_create_dbfile('davisbase_tables', tables_cols)

    # Add tables first if needed
    if not next(tbl_tables.find('table_name', 'davisbase_tables'), None):
        for tbl_spec in startup:
            tbl_spec.append(tbl_tables.insert((None, tbl_spec[0], -1, 0)))

        # Mark next initialization stage to load the columns
        need_init = True

    return tbl_tables

def meta_initialize2():
    global need_init
    tbl_tables = _meta_create_dbfile('davisbase_tables', tables_cols)
    tbl_columns = _meta_create_dbfile('davisbase_columns', columns_cols)

    if need_init:
        need_init = False

        # Then add the columns
        for _, cols, tbl_rowid in startup:
            for col in cols:
                col = [None, tbl_rowid] + list(col)
                col[5] = _yesno(col[5])
                col[6] = _yesno(col[6])
                tbl_columns.insert(col)

    return tbl_tables, tbl_columns

def init_metadata_for(table_name, column_specs):
    tbl_tables = get_meta_tables()
    tbl_columns = get_meta_columns()

    tbl_rowid = tbl_tables.insert((None, table_name, -1, 0))
    for col in column_specs:
        col = [None, tbl_rowid] + list(col)
        col[5] = _yesno(col[5])
        col[6] = _yesno(col[6])
        tbl_columns.insert(col)

def deinit_metadata_for(table_name): 
    tbl_tables = get_meta_tables()
    tbl_columns = get_meta_columns()

    tblid, = tbl_tables.select_one('table_name', table_name, '=', ['rowid'])
    tbl_columns.delete('table_rowid', tblid)
    tbl_tables.delete('table_name', table_name)
