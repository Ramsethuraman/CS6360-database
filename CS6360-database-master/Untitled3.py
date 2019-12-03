#!/usr/bin/env python
# coding: utf-8




#Table Set
from prettytable import PrettyTable
from file import *
from file.valuetype import Float32
from file.paging import *
import os
import re
#Tables={"Name":["Tables","Columns"],
 #       "MaxCurrentIndex":[2,4],
  #      "NumColumns":[3,2]}

#Columns={"Name":["Tables.Name","Columns.Name","Columns.Type","Tables.MaxCurrentIndex","Tables.NumColumns"],
 #       "Type":[0,0,1,1,1]}
#for type, currently just has 0 for string, 1 for int
Tables={"Name":[],"MaxCurrentIndex":[],"NumColumns":[]}
Columns={"Name":[],"Type":[]}
def convert(dataC, dataT):
    for i in range(0,len(dataC)):
    #for i in dataC:
        Columns["Name"]= Columns["Name"]+[dataC[i][0].decode("utf-8")]
        Columns["Type"]=Columns["Type"]+[dataC[i][1]]
    #for i in range(0,len(dataT)):
    for i in dataT:
        Tables["Name"]= Tables["Name"]+[dataT[i][0].decode("utf-8")]
        Tables["MaxCurrentIndex"]=Tables["MaxCurrentIndex"]+[dataT[i][1]]
        Tables["NumColumns"]=Tables["NumColumns"]+[dataT[i][2]]
    print("Tables",Tables)
    print()
    print("COlumns",Columns)

def instantiate():
    if os.path.exists("..\\Tables.tbl"):
        print("no instantiation")
    else:
        pt = PageTypes
        types=[vt.TEXT,vt.SMALLINT,vt.SMALLINT]
        data=((b'Tables',2,3),
             (b'Columns',4,2))
        open('..\\Tables.tbl', 'wb').close()
        dbfile = PagingFile('..\\Tables.tbl', types)

        cells = [create_cell(pt.TableLeaf, types, rowid=1, tuples = data[0]),
                create_cell(pt.TableLeaf, types, rowid=2, tuples = data[1])]
        page = Page(dbfile, 0, pt.TableLeaf, types, 1, 2, cells)
        dbfile.write_page(page)

        cells = [create_cell(pt.TableLeaf, types, rowid=2, tuples = data[1])]
        page = Page(dbfile, -1, pt.TableLeaf, types, INVALID_OFF, 2, cells)
        dbfile.write_page(page)

        cells = [create_cell(pt.TableInterior, types, rowid=2, left_child = 0)]
        page = Page(dbfile, 2, pt.TableInterior, types, 1, INVALID_OFF, cells)
        dbfile.write_page(page)
    
def instantiate2():
    if os.path.exists("..\\Columns.tbl"):
        print("no instantiation")
    else:
        pt = PageTypes
        types=[vt.TEXT,vt.SMALLINT]
        data=()
       # for i in range(0,5):
        #    data= data+('b'+Columns["Name"][i],Columns["Type"][i])
        data=((b'Tables.Name',0),
              (b'Tables.MaxCurrentIndex',1),
              (b'Tables.NumColumns',1),
              (b'Columns.Name',0),
              (b'Columns.Type',1))
        open('..\\Columns.tbl', 'wb').close()
        dbfile = PagingFile('..\\Columns.tbl', types)

        cells = [create_cell(pt.TableLeaf, types, rowid=1, tuples = data[0]),
                create_cell(pt.TableLeaf, types, rowid=2, tuples = data[1]),
                create_cell(pt.TableLeaf, types, rowid=3, tuples = data[2]),
                create_cell(pt.TableLeaf, types, rowid=4, tuples = data[3]),
                create_cell(pt.TableLeaf, types, rowid=5, tuples = data[4])]
        page = Page(dbfile, 0, pt.TableLeaf, types, 1, 2, cells)
        dbfile.write_page(page)

        cells = [create_cell(pt.TableLeaf, types, rowid=5, tuples = data[4])]
        page = Page(dbfile, -1, pt.TableLeaf, types, INVALID_OFF, 2, cells)
        dbfile.write_page(page)

        cells = [create_cell(pt.TableInterior, types, rowid=2, left_child = 0)]
        page = Page(dbfile, 2, pt.TableInterior, types, 1, INVALID_OFF, cells)
        dbfile.write_page(page)

    


#adds a table, its rows, and its row types to the metadata
def create_table(name, columns, types):
    #formats the columns to include table prefix
    for i in range(0,len(columns)):
        columns[i]=name+"."+columns[i]
        
    #adds the columns and their types to the columns table
    Columns["Name"]= Columns["Name"]+columns
    Columns["Type"]= Columns["Type"]+types
    
    #adds table name to table table
    Tables["Name"]= Tables["Name"]+[name]
    
    #maxcurrentindex starts at 0
    Tables["MaxCurrentIndex"]= Tables["MaxCurrentIndex"]+[0]
    
    #adds 1 to max current index of table table
    #adds column number to maxcurrentindex of column table
    Tables["MaxCurrentIndex"][0]= Tables["MaxCurrentIndex"][0]+1
    Tables["MaxCurrentIndex"][1]= Tables["MaxCurrentIndex"][1]+len(columns)
    
    #adds new int on numcolumns for the new table
    Tables["NumColumns"]=Tables["NumColumns"]+[len(columns)]




#prints the table
def print_table(name, Table):
    cols=list(Table.keys())
    x=PrettyTable()
    x.field_names=cols
    for i in range(0,len(Table[cols[0]])):
        hold=[]
        for j in range(0,len(Table)):
            hold= hold + [Table[cols[j]][i]]
        x.add_row(hold)
    print(name)
    print(x)
        





#adds column to existing table
def add_column(column,typer,table):
    #formats the name into columns name
    Columns["Name"]=Columns["Name"]+[table+"."+column]
    
    #adds another column type indicator
    Columns["Type"]=Columns["Type"]+[typer]
    
    #adds 1 to number of columns in the target table
    Tables["NumColumns"][Tables["Name"].index(table)]+=1





#drops the table targeted
def drop_table(name):
    #gets list of table table keys
    cols=list(Tables.keys())
    
    #goes from the end of the name key value in columns, and deletes entries from the table specified by name in method call
    for i in reversed(range(len(Columns["Name"]))):
        if(re.search(r"%s.*" % name, Columns["Name"][i], re.IGNORECASE)):
            Columns["Name"].pop(i)
            #also removes corresponding type
            Columns["Type"].pop(i)
            
    #removes table and corresponding values from table table
    for i in range(len(Tables["Name"])):
        if(re.search(r"%s" % name, Tables["Name"][i], re.IGNORECASE)):
            Tables["Name"].pop(i)
            Tables["MaxCurrentIndex"].pop(i)
            Tables["NumColumns"].pop(i)
            break
    


instantiate()
instantiate2()
dataC=((b'Tables.Name',0),
    (b'Tables.MaxCurrentIndex',1),
    (b'Tables.NumColumns',1),
    (b'Columns.Name',0),
    (b'Columns.Type',1))
dataT=((b'Tables',2,3),
    (b'Columns',4,2))
column_specs=(('Name',"TEXT",1,True,False),('MaxCurrentIndex',"INT",2,True,False),('NumColumns',"INT",3,True,False))

open('..\\Tables.tbl', 'w+').close()
rdbfile = RelationalDBFile(('..\\Tables', INVALID_OFF, 0), column_specs)
hold=()
for i in rdbfile.findall():
    print("in loop")
    print(i)
convert(dataC,hold)

print_table("Tables",Tables)
print()
print_table("Columns",Columns)

newCol=["Salary", "Name", "Sex"]
newType=[1,0,0]
create_table("Employees",newCol,newType)

print()
print("after table addition")
print_table("Tables",Tables)
print_table("Columns",Columns)

add_column("birthday",1,"Employees")
print()
print("after column addition to employees")
print_table("Tables",Tables)
print_table("Columns",Columns)


drop_table("Employees")

print()
print("after dropping the employees table")
print_table("Tables",Tables)
print_table("Columns",Columns)


testtable= {"Name":Columns["Name"]}
print_table("justnames",testtable)






