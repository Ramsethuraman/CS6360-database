'''
This module contains all the possible value types associated with a DB field. 

The different value types can be classifed into roughly two categories:
primitives and extended primitives. The primitives are your ints and strings
(NOTE THAT THOUGH THE TEXT TYPE IS A bytes NOT A str TYPE!!!) Extended
primitives are value type entities that can be defined for a single DB field,
but is not an actual primitive in python. These are defined as subclasses of
DBData, and each extended primtive type overrides certain methods in DBData in
order to marshall/unmarshall/parse data of this type.

In order to pack/unpack binary data consisting of these values, the methods
vpack and vunpack_from can be used respectively.

In order to convert some string or integer (i.e. a SQL string literal or numeric
literal) into the corresponding value types, the parse_from_int and
parse_from_str methods can be used to convert primitives to whatever value type
as needed (primitive or extended primitive)

'''

__all__ = ['Date', 'DateTime', 'Time', 'DBData', 'ValueType', 'Year', 
        'parse_from_int', 'parse_from_str', 'vpack', 'vunpack', 'vunpack1']

import enum
import datetime
import struct

def _strptime(fmts, timestr):
    if type(fmts) is str:
        fmts = [fmts]

    for fmt in fmts:
        try:
            return datetime.datetime.strptime(timestr, fmt)
        except:
            pass

    raise ValueError(f"time data '{timestr}' does not match formats '{fmts}'")

class DBData(object):
    ''' This is the abstract base class for any type of DB data that may require
    unmarshalling/marshalling when converting to/from binary data. This is the
    case when we need to define some artificial type that doesn't automatically
    get packed/unpacked by struct.'''

    @classmethod
    def parse(cls, strval):
        ''' Abstract parse from string function for all DBData objects. Defaults
        to throwing an error '''
        raise ValueError(f'Cannot convert a string to a(n) {cls.__name__} value')

    @staticmethod
    def parse_int(intval):
        raise ValueError(f'Cannot convert an integer to a(n) {cls.__name__} value')

    @classmethod
    def decode(cls, numb):
        return cls(numb)

    def encode(self):
        raise NotImplementedError('Please implement this in the subclass')

    def __eq__(self, other):
        return self.encode() == other.encode()

    def __gt__(self, other):
        return self.encode() > other.encode()

    def __ge__(self, other):
        return self.encode() >= other.encode()


class Year(DBData):
    ''' This type wraps around some year. This is a special numeric type that is
    a 1-byte size, supporting years between 1872 to 2127 (it takes a 2's
    complement signed byte and adds 2000 to it).'''

    @classmethod
    def parse(cls, strval):
        return cls(int(strval))

    @classmethod
    def parse_int(cls, intval):
        return cls(intval)

    @classmethod
    def decode(cls, numb):
        return cls(numb + 2000)

    def __init__(self, year):
        x = year - 2000
        if not (-128 <= x <= 127):
            raise ValueError('Not in range of supported years!')
        self.__year = year

    def __str__(self):
        return str(self.__year)
    
    def __repr__(self):
        return f'Year({self.__year})'

    @property
    def year(self):
        return self.__year

    def encode(self):
        return self.year - 2000

class Time(DBData):
    ''' This represents a time (hour, minute, second, opt. milliseconds) in
    terms of milliseconds from midnight. This is 4 bytes size.'''

    __tfmt = ['%H:%M:%S', '%H:%M:%S.%f']

    @classmethod
    def parse(cls, strval):
        tme = _strptime(cls.__tfmt, strval).time()
        return cls(tme.hour, tme.minute, tme.second, tme.microsecond // 1000)

    @classmethod
    def parse_int(cls, intval):
        return cls.decode(intval)

    def __init__(self, hour, minute=None, second=None, millis=None):
        if minute == None:
            if not (0 <= hour < 86400000):
                raise ValueError('Bad millis offset')
            self.__time = hour
        else:
            if not (0 <= hour < 24):
                raise ValueError('Bad hour')
            if not (0 <= minute < 60):
                raise ValueError('Bad minute')
            if not (0 <= second < 60):
                raise ValueError('Bad second')
            if not (0 <= millis < 1000):
                raise ValueError('Bad millis')
            self.__time = (((hour * 60) + minute) * 60 + second) * 1000 + millis

    def __str__(self):
        return f'{self.hour}:{self.minute:02}:{self.second:02}.{self.millis:03}'

    def __repr__(self):
        return f'Time({str(self)})'

    @property
    def hour(self): return self.__time // (60 * 60 * 1000)
    @property
    def minute(self): return self.__time // (60 * 1000) % 60
    @property
    def second(self): return self.__time // 1000 % 60
    @property
    def millis(self): return self.__time % 1000

    def encode(self):
        return self.__time

class DateTime(DBData):
    ''' This represents a date and time component, together holding 8 bytes, in
    terms of milliseconds from the epoch era (January 1, 1970, 00:00:00). '''

    _dfmt = ['%Y-%m-%d_%H:%M:%S', '%Y-%m-%d_%H:%M:%S.%f']

    @classmethod
    def parse(cls, strval):
        return DateTime(_strptime(strval, cls._dfmt))

    def __init__(self, year, month=None, day=None, hour=0, minute=0,
            second=0, millis=0):
        if month == None:
            d = year
            if type(d) is int:
                self.__time = datetime.datetime.fromtimestamp(year / 1000,
                        datetime.timezone.utc)
            elif type(d) is datetime.date:
                self.__time = datetime.datetiem(d.year, d.month, d.day)
            elif type(d) is datetime.datetime:
                self.__time = d
            else:
                raise ValueError('Invalid type')
        else:
            if millis != None:
                millis *= 1000
            print(year, month, day, hour, minute, second, millis)
            self.__time = datetime.datetime(year, month, day, hour, minute,
                    second, millis)

    @property
    def year(self): return self.__time.year
    @property
    def month(self): return self.__time.month
    @property
    def day(self): return self.__time.day
    @property
    def hour(self): return self.__time.hour
    @property
    def minute(self): return self.__time.minute
    @property
    def second(self): return self.__time.second
    @property
    def millis(self): return self.__time.microsecond // 1000

    def __str__(self):
        return self.__time.strftime(type(self)._dfmt[0])

    def __repr__(self):
        return f'{type(self).__name__}({str(self)})'

    def encode(self):
        return int(self.__time.timestamp() * 1000)

class Date(DateTime):
    ''' This represents a sole date component, holding 8 bytes. There is still a
    "time" component, but all these values are forced to 0, i.e. 00:00:00.
    Likewise, it is internally represented as the number of milliseconds from 
    the epoch era (January 1, 1970, 00:00:00). '''

    _dfmt = ['%Y-%m-%d']

    def __init__(self, year, month=None, day=None):
        if month == None:
            d = year
            if type(d) == int:
                date_time = 24 * 60 * 60 * 1000
                year = year // date_time * date_time
            elif isinstance(d, datetime.date):
                year = d.year
                month = d.month
                day = d.day
            else:
                raise ValueError('Invalid type')

        super().__init__(year, month, day)

class ValueType(enum.IntEnum):
    ''' This holds all the possible data types that can be representable in a
    database and its lowest typeid corresponding to that type'''

    NULL, TINYINT, SMALLINT, INT, BIGINT, FLOAT, DOUBLE, _, YEAR, TIME, \
            DATETIME, DATE, TEXT = range(13)

__type_map = {
        ValueType.NULL:     (ValueType.NULL,     0, '',  None),
        ValueType.TINYINT:  (ValueType.TINYINT,  1, 'B', int),
        ValueType.SMALLINT: (ValueType.SMALLINT, 2, 'H', int),
        ValueType.INT:      (ValueType.INT,      4, 'I', int),
        ValueType.BIGINT:   (ValueType.BIGINT,   8, 'Q', int),
        ValueType.FLOAT:    (ValueType.FLOAT,    4, 'f', float),
        ValueType.DOUBLE:   (ValueType.DOUBLE,   8, 'd', float),
        ValueType.YEAR:     (ValueType.YEAR,     1, 'b', Year),
        ValueType.TIME:     (ValueType.TIME,     4, 'I', Time),
        ValueType.DATETIME: (ValueType.DATETIME, 8, 'Q', DateTime),
        ValueType.DATE:     (ValueType.DATE,     8, 'Q', Date),
    }

MAX_TYPE = 255
for i in range(ValueType.TEXT, MAX_TYPE + 1):
    leng = i - ValueType.TEXT
    __type_map[i] = (ValueType.TEXT, leng, str(leng) + 's', bytes)

def vpack(typeids, *data):
    ''' Packs some data, given its typeids, into a marshalled, packed tuple,
    that includes number of items in tuple and typeid's. This returns a stream
    of bytes that represents the tuple of the data.'''

    data2 = []
    typeids2 = []

    if len(typeids) != len(data):
        raise ValueError(f'Expected {len(typeids)} data points, only got {len(data)} data points')

    full_fmt = '>B' + 'B' * len(typeids)
    for typeid, data in zip(typeids, data):
        if typeid not in __type_map:
            raise ValueError(f'Invalid type-id: 0x{typeid:x}')

        typeid, _, fmt, dtype = __type_map[typeid]

        # Check data-type of data
        if typeid == ValueType.NULL:
            if data != None:
                raise ValueError('Data should be None for NULL type')
        else:
            if type(data) != dtype:
                raise ValueError('Data is not proper type to marshall')

        # Marshall value if needed
        if isinstance(data, DBData):
            data = data.encode()

        # Retype TEXT if needed 
        if typeid == ValueType.TEXT:
            typeid = ValueType.TEXT + len(data)
            if typeid > MAX_TYPE:
                raise ValueError('Text is too long.')
            _, _, fmt, dtype = __type_map[typeid]

        typeids2.append(typeid)
        if fmt:
            data2.append(data)
            full_fmt += fmt

    return struct.pack(full_fmt, len(typeids), *(typeids2 + data2)) 

def vunpack1(data):
    ''' Unpacks one data point (without a header for number of columns).
    Otherwise this does exactly the same as vunpack, but returns the actual
    value, not a 1-tuple'''

    if type(data) is not bytes:
        raise ValueError('Expected data to be of type bytes')
    return vunpack(b'\x01' + data)[0]

def vunpack(data):
    ''' Unpacks an marshalled tuple data with unknown types. This will return a
    a list of data points that has been unpacked and unmarshalled. The data
    given MUST have exactly the same size of the tuple.'''

    if type(data) is not bytes:
        raise ValueError('Expected data to be of type bytes')

    cols = data[0]
    col_types = struct.unpack_from('>x' + 'B' * cols, data)

    full_fmt = '>' + 'x' * (cols + 1)
    dtypes = []
    for typeid in col_types:
        _, size, fmt, dtype = __type_map[typeid] # Should't cause error
        if not fmt: 
            dtype = None
            fmt = '0s' # Make sure that we make a space
        full_fmt += fmt
        dtypes.append(dtype)

    datas = list(struct.unpack(full_fmt, data))
    for ind, data in enumerate(datas):
        # Special case for NULL
        dtype = dtypes[ind]
        if not dtype: data = None
        elif dtype != type(data):
            data = dtype.decode(data)
        datas[ind] = data

    return tuple(datas)

def parse_from_str(typeid, strval):
    ''' Takes a string literal (minus quotations) and attempts to parse it into
    the respective marshalled object associated with the specified type.
    
    MAKE SURE TO CATCH THIS METHOD IF IT FAILS!!! Usually, the error messages
    that is raised at this point should be meaningful to the user, so use that.
    '''

    if typeid not in __type_map:
        raise ValueError(f'Invalid type-byte: 0x{typeid:x}')

    _, _, _, dtype = __type_map[typeid]

    if issubclass(dtype, DBData):
        return dtype.parse(strval)
    else:
        return dtype(strval)
    
def parse_from_int(typeid, intval):
    ''' Takes an integer literal and attempts to parse it into the respective
    marshalled object associated with the specified type. 
    
    AS WITH parse_from_str, MAKE SURE TO CATCH THIS METHOD IF IT FAILS!!! The
    error messages that is raised at this point should be meaningful to the
    user, so use that.
    '''

    if typeid not in __type_map:
        raise ValueError(f'Invalid type-byte: 0x{typeid:x}')

    _, _, _, dtype = __type_map[typeid]

    if issubclass(dtype, DBData):
        return dtype.parse_int(strval)
    else:
        return dtype(strval)
    
