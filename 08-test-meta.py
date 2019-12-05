from file import *

db_tables = get_meta_tables()
db_columns = get_meta_columns()
print(list(db_tables.findall()))
print(list(db_columns.findall()))
