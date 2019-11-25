from file.valuetype import ValueType as vt
from file.paging import *
from file.paging import PageTypes as pt

types = [vt.SMALLINT, vt.TEXT, vt.FLOAT, vt.TINYINT]

#Tag ID     Name     Weight(kg)    Age (years)
dbfile = PagingFile('dogs.tbl', types)

print(repr(dbfile.read_page(0)))
print(repr(dbfile.read_page(1)))
print(repr(dbfile.read_page(2)))



