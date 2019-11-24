from file.valuetype import *
from binascii import hexlify
import datetime

dt = DateTime(0)
ddt = Date(100000000000000)
tm = Time(23, 1, 2, 103)
tm2 = Time(4359084)
yr = Year(2016)
print(dt, ddt, tm, tm2)

data = vpack([0, 1, 2, 3, 6, 10, 11, 9, 9, 8, 0xc], 
        None, 23, 267, 234524, 4.5654, dt, ddt, tm, tm2, yr, b'hello world!!!!')
print('** DATA **************')
for i in range(0, len(data), 8):
    print('%04x: %s' % (i, str(hexlify(data[i:i+8]), 'utf8')))
print('**********************')
print(vunpack(data))
