#!/bin/python
from file import *
from file.index import IndexFile
from file.paging import INVALID_OFF
from file.valuetype import Float32
from file.valuetype import Date
import datetime

types = [vt.INT]

#Tag ID     Name     Weight(kg)    Age (years)
data = ((933,   b'Rover',   Float32(20.6), 4),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (8326,  b'Spot',    Float32(10.8), 7),
        (5359,  b'Lucky',   Float32(31.2), 5),
        (10355, b'Dinky',   Float32(4.8),  11),
        (7757,  b'Bruiser', Float32(42.0), 6), 
        (3597,  b'Patch',   Float32(29.6), 9), 
        (202,   b'Prince',  Float32(16.6), 7), 
        (5359,  b'Lucky',   Float32(31.2), 5),
        (5359,  b'Lucky',   Float32(31.2), 5),
        (5359,  b'Lucky',   Float32(31.2), 5),
        (10355, b'Dinky',   Float32(4.8),  11),
        (7757,  b'Bruiser', Float32(42.0), 6), 
        (3597,  b'Patch',   Float32(29.6), 9), 
        (202,   b'Prince',  Float32(16.6), 7), 
        (10355, b'Dinky',   Float32(4.8),  11),
        (7757,  b'Bruiser', Float32(42.0), 6), 
        (3597,  b'Patch',   Float32(29.6), 9), 
        (202,   b'Prince',  Float32(16.6), 7), 
        (10355, b'Dinky',   Float32(4.8),  11),
        (7757,  b'Bruiser', Float32(42.0), 6), 
        (3597,  b'Patch',   Float32(29.6), 9), 
        (202,   b'Prince',  Float32(16.6), 7), 
        (1630,  b'Bubbles', Float32(7.1),  11),
        (1223,  b'Peanut',  Float32(14.3), 2))
'''
data = ((933,   b'Rover',   Float32(20.6), 4),
        (8326,  b'Spot',    Float32(10.8), 7), 
        (5359,  b'Lucky',   Float32(31.2), 5), 
        (10355, b'Dinky',   Float32(4.8),  11),
        (7757,  b'Bruiser', Float32(42.0), 6), 
        (3597,  b'Patch',   Float32(29.6), 9), 
        (202,   b'Prince',  Float32(16.6), 7), 
        (1630,  b'Bubbles', Float32(7.1),  11),
        (1223,  b'Peanut',  Float32(14.3), 2))
'''
dbfile = IndexFile(open('dogs.ind', 'w+b'), types, 128, root_page = INVALID_OFF)
#REMOVED LOOP FOR NOW 
i = 1;
while True:
    dbfile.add(i,i)
    i+=1
    for j in range(dbfile.next_page()):
        print(repr(dbfile.read_page(j)))
    input('************* Next... *****************')


