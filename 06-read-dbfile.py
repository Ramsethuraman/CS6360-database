from file import *

#Tag ID     Name     Weight(kg)    Age (years)
columns = ['Tag_ID', 'Name', 'Weight', 'Age']
column_specs = (('rowid',  "INT",      1, False, True),
                ('Tag_ID', "SMALLINT", 2, False, True),
                ('Name',   "TEXT",     3, False, False), 
                ('Weight', "FLOAT",    4, False, False),
                ('Age',    "TINYINT",  5, False, False))

data = ((933,   b'Rover',   Float32(20.6), 4),
        (8326,  b'Spot',    Float32(10.8), 7),
        (5359,  b'Lucky',   Float32(31.2), 5),
        (10355, b'Dinky',   Float32(4.8),  11),
        (7757,  b'Bruiser', Float32(42.0), 6), 
        (3597,  b'Patch',   Float32(29.6), 9), 
        (202,   b'Prince',  Float32(16.6), 7), 
        (1630,  b'Bubbles', Float32(7.1),  11),
        (1223,  b'Peanut',  Float32(14.3), 2))

def test_dbfile(dbfile, hasrowid=False):
    print('Columns: ' + ', '.join(dbfile.columns))

    print('Current table:')
    for tup in dbfile.findall():
        print(tup)
    print('--------------\n')

    tagids = []
    for tid, in dbfile.findall(['Tag_ID']):
        tagids.append(str(tid))
    print('All tag_ids: ' + ', '.join(tagids))

    if hasrowid:
        ele = (None, 7758,  b'Bruiser', Float32(42.0), 6)
    else:
        ele = (7758,  b'Bruiser', Float32(42.0), 6)
    print('Inserting element: ' + str(ele))
    dbfile.insert(ele)
    print('Result for SELECT * FROM Dogs WHERE Tag_ID = 8326;')
    for tup in dbfile.find('Tag_ID', 8326):
        print(tup)
    print('--------------\n')

    print('Result for SELECT * FROM Dogs Where Name < "H";')
    for tup in dbfile.find('Name', b'H', '<'):
        print(tup)
    print('--------------\n')

    print('Deleting all dogs under 20.6 kg:')
    print('Affected rows: ' + str(dbfile.delete('Weight', 20.6, '<=')))
    for tup in dbfile.findall():
        print(tup)
    print('--------------\n')

    print('Modifying weight of dog 7757 to 30.0')
    print('Affected rows: ' + str(dbfile.modify('Weight', Float32(30.0), 
        'Tag_ID', 7757)))
    for tup in dbfile.findall():
        print(tup)
    print('--------------\n')

print('***************************')
print('* AbstractDBFile          *')
print('***************************')
adbfile = AbstractDBFile(columns, data)
test_dbfile(adbfile)
print('***************************\n')

print('***************************')
print('* RelationalDBFile        *')
print('***************************')
open('dogs.tbl', 'w+').close()
rdbfile = RelationalDBFile(('dogs', INVALID_OFF, 0), column_specs)
for tup in data:
    # Must insert a blank column for rowid
    rdbfile.insert((None,) + tup)
test_dbfile(rdbfile, True)
print('***************************\n')
