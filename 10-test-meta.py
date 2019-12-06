from file import *
from prettytable import PrettyTable

db_tables = get_meta_tables()
db_columns = get_meta_columns()

db_tables.print_table(db_tables.findall())
db_columns.print_table(db_columns.findall())

specs = (('rowid', 'INT',  1, False, True), 
         ('name',  'TEXT', 2, False, False))
db_bobby = create_dbfile('bobby', specs)

db_tables.print_table(db_tables.findall())
db_columns.print_table(db_columns.findall())

