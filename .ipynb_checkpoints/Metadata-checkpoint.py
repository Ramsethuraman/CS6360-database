#!/usr/bin/env python
# coding: utf-8

from prettytable import PrettyTable
from file import *


import re

Tables_specs=(('rowid',"INT",1, False, True),('Name',"TEXT",2,True,False),('MaxCurrentIndex',"INT",3,True,False),('NumColumns',"INT",4,True,False))
Columns_specs=(('rowid',"INT",1, False, True),('Name',"TEXT",2,True,False),('Type',"TEXT",3,True,False))

def instantiate():
    data=((1,"Tables",-1,0),
        (2,"Columns",-1,0))
    #open('Tables.tbl', 'wb').close()
    
    types= [vt.SMALLINT,vt.TEXT,vt.SMALLINT,vt.SMALLINT]
    dbfile = get_meta_tables()
    for i in range(len(data)):
        dbfile.insert(data[i])
    types=[vt.TEXT,vt.SMALLINT]
    data=()
# for i in range(0,5):
#    data= data+('b'+Columns["Name"][i],Columns["Type"][i])
    data=((1,1,"Tables.rowid","INT",1,"False","True"),
        (2,2,"Tables.name","TEXT",2,"False","True"),
        (3,3,"Tables.root_page","INT",3,"False","True"),
        (4,4,"Tables.last_rowid","INT",4,"False","False"),
        (5,1,"Columns.rowid","INT",1,"False","True"),
        (6,2,"Columns.table_rowid","INT",2,"False","False"),
        (7,3,"Columns.name","TEXT",3,"False","True"),
        (8,4,"Columns.data_type","INT",4,"False","False"),
        (9,5,"Columns.ordinal_position","TINYINT",5,"False","False"),
        (10,6,"Columns.is_nullable","TEXT",6,"False","False"),
        (11,7,"Columns.is_unique","TEXT",7,"False","False"))
    #open('Columns.tbl', 'wb').close()
    types=[vt.SMALLINT,vt.TEXT,vt.TEXT]
    
    dbfile = get_meta_columns()
    for i in range(len(data)):
        dbfile.insert(data[i])

Tablecols=('rowid','name','root_page','last_rowid')
Columncols=('rowid','table_rowid','name','data_type','ordinal_position','is_nullable','is_unique')

#This should work for any table, so long as you give it the columns and tuples
#also supports aliasing of the table and columns, so that's nice
#passes str name, relationaldbfile(get_table) Tups, and str list columns
def print_table(name, Tups,columns):
    x=PrettyTable()
    x.field_names=columns
    for i in Tups.findall():
        x.add_row(i)
    print(name)
    print(x)
        
        
'''
Method Call functions:

create_table(table_name, column_list)
    column_list in form: ((name, type, nullable, unique))

add_column(table_name, column_list)
    column_list should be in the same form as the one in create_table

drop_table(table_name)

drop_column(table_name, column_name)

'''
#Below Will not work if meta files already instantiated

#instantiate()
#holdT= relate.get_meta_tables()
#holdC= relate.get_meta_columns()
#print_table('Table',holdT,Tablecols)
#print_table('Column',holdC,Columncols)