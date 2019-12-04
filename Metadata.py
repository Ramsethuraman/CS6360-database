#!/usr/bin/env python
# coding: utf-8

from prettytable import PrettyTable
from file import *


import re

Tables_specs=(('rowid',"INT",1, False, True),('Name',"TEXT",2,True,False),('MaxCurrentIndex',"INT",3,True,False),('NumColumns',"INT",4,True,False))
Columns_specs=(('rowid',"INT",1, False, True),('Name',"TEXT",2,True,False),('Type',"TEXT",3,True,False))

def instantiate():
    data=((1,"Tables",2,3),
        (2,"Columns",4,2))
    #open('Tables.tbl', 'wb').close()
    
    types= [vt.SMALLINT,vt.TEXT,vt.SMALLINT,vt.SMALLINT]
    dbfile = get_meta_tables()
    for i in range(len(data)):
        dbfile.add(data[i])
    types=[vt.TEXT,vt.SMALLINT]
    data=()
# for i in range(0,5):
#    data= data+('b'+Columns["Name"][i],Columns["Type"][i])
    data=((1,"Tables.Name","TEXT"),
        (2,"Tables.MaxCurrentIndex","INT"),
        (3,"Tables.NumColumns","INT"),
        (4,"Columns.Name","TEXT"),
        (5,"Columns.Type","INT"))
    #open('Columns.tbl', 'wb').close()
    types=[vt.SMALLINT,vt.TEXT,vt.TEXT]
    
    dbfile = get_meta_columns()
    for i in range(len(data)):
        dbfile.add(data[i])







instantiate()
holdT= relate.get_meta_tables()
holdC= relate.get_meta_columns()
for i in holdT:
    print(i)

