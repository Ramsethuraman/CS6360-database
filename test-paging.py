from file import *

pt = PageTypes
vt = ValueType



types = [vt.SMALLINT, vt.TEXT, vt.FLOAT, vt.TINYINT]

#Tag ID     Name     Weight(kg)    Age (years)
data = ((933,   b'Rover',   20.6, 4),
        (8326,  b'Spot',    10.8, 7), 
        (5359,  b'Lucky',   31.2, 5), 
        (10355, b'Dinky',   4.8,  11),
        (7757,  b'Bruiser', 42.0, 6), 
        (3597,  b'Patch',   29.6, 9), 
        (202,   b'Prince',  16.6, 7), 
        (1630,  b'Bubbles', 7.1,  11),
        (1223,  b'Peanut',  14.3, 2))

dbfile = PagingFile('dogs.tbl', types)

cells = [create_cell(pt.TableLeaf, types, rowid=1, tuples = data[0]),
        create_cell(pt.TableLeaf, types, rowid=2, tuples = data[1]),
        create_cell(pt.TableLeaf, types, rowid=3, tuples = data[2]),
        create_cell(pt.TableLeaf, types, rowid=4, tuples = data[3])]
page = Page(0, pt.TableLeaf, types, 1, 2, cells)
dbfile.write_page(page)

cells = [create_cell(pt.TableLeaf, types, rowid=4, tuples = data[4])]
page = Page(1, pt.TableLeaf, types, INVALID_OFF, 2, cells)
dbfile.write_page(page)

cells = [create_cell(pt.TableInterior, types, rowid=5, left_child = 0)]
page = Page(2, pt.TableInterior, types, 1, INVALID_OFF, cells)
dbfile.write_page(page)



