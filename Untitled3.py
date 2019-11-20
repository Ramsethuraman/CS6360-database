#!/usr/bin/env python
# coding: utf-8




#Table Set
from prettytable import PrettyTable
import re
Tables={"Name":["Tables","Columns"],
        "MaxCurrentIndex":[2,4],
        "NumColumns":[3,2]}

Columns={"Name":["Tables.Name","Columns.Name","Columns.Type","Tables.MaxCurrentIndex","Tables.NumColumns"],
        "Type":[0,0,1,1,1]}
#for type, currently just has 0 for string, 1 for int





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





