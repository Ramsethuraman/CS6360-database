from file.valuetype import ValueType as vt
from file.paging import *
from file.paging import PageTypes as pt

types = [vt.SMALLINT, vt.TEXT, vt.FLOAT, vt.TINYINT]

#Tag ID     Name     Weight(kg)    Age (years)
dbfile = PagingFile('dogs.tbl', types)


for i in range(dbfile.next_page()):
    p = dbfile.read_page(i)
    print(repr(p))
    print(f'There is {p.get_free_size()} bytes left in this page')
    print(f'This page is: {p.page_size} bytes long in total, with a ' + \
            f'header of {Page.get_page_header_size()} bytes')
    print('')



