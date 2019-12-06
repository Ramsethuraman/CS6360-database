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
        'check_type_compat', 'parse_from_int', 'parse_from_str', 'vpack',
        'vpack1', 'vunpack', 'vunpack1', 'vunpack_from', 'vunpack1_from', 
        'NULLVAL']

import enum
import datetime
import struct

from .base import FileFormatError

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

    def __init__(self):
        if type(self) == DBData:
            raise ValueError('Instantiation of abstract type')

    @classmethod
    def parse(cls, strval):
        ''' Abstract parse from string function for all DBData objects. Defaults
        to throwing an error '''
        raise FileFormatError(f'Cannot convert a string to a(n) {cls.__name__} value')

    @classmethod
    def parse_int(cls, intval):
        raise FileFormatError(f'Cannot convert an integer to a(n) {cls.__name__} value')

    @classmethod
    def decode(cls, numb):
        return cls(numb)

    def encode(self):
        raise NotImplementedError('Abstract method')

    def __eq__(self, other):
        if not isinstance(other, DBData):
            return False
        return self.encode() == other.encode()

    def __gt__(self, other):
        return self.encode() > other.encode()

    def __ge__(self, other):
        return self.encode() >= other.encode()

    def __hash__(self):
        return hash(self.encode())

NULLVAL = None
class NullType(DBData):
    @classmethod
    def decode(cls, numb): return NULLVAL

    def __init__(self):
        if NULLVAL != None:
            raise ValueError('Singleton instantiation')

    def __str__(self): return 'NULL'
    def __repr__(self): return 'NULL'
    def __hash__(self): return 0

    def __bool__(self): return False

    def __gt__(self, other): return False
    def __ge__(self, other): return False
    def __lt__(self, other): return False
    def __le__(self, other): return False

    def encode(self): return b''
NULLVAL = NullType()

class Float32(float, DBData):
    ''' Wraps around a float value so that a string representation of this will
    be (hopefully) as if it were "32-bit" or single precision. More specifically
    it forces up to 6 decimal places of precision, which should almost entirely
    hide the "imprecisions" when casted from a double float to single float and
    back to a double again.'''

    @classmethod
    def parse(cls, strval):
        return cls(strval)

    @classmethod
    def parse_int(cls, intval):
        return cls(intval)

    @classmethod
    def decode(cls, numb):
        return cls(numb)

    def __init__(self, val):
        float.__init__(self)

    def __str__(self):
        s = f'{self:g}'
        return s if '.' in s else s + '.0'

    def __repr__(self):
        return str(self)

    def encode(self):
        return self

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
            raise FileFormatError('Not in range of supported years!')
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
                raise FileFormatError('Bad millis offset')
            self.__time = hour
        else:
            if not (0 <= hour < 24):
                raise FileFormatError('Bad hour')
            if not (0 <= minute < 60):
                raise FileFormatError('Bad minute')
            if not (0 <= second < 60):
                raise FileFormatError('Bad second')
            if not (0 <= millis < 1000):
                raise FileFormatError('Bad millis')
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
        return cls(_strptime(cls._dfmt, strval))

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
                raise FileFormatError('Invalid type')
        else:
            if millis != None:
                millis *= 1000
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
                raise FileFormatError('Invalid type')

        super().__init__(year, month, day)

class ValueType(enum.IntEnum):
    ''' This holds all the possible data types that can be representable in a
    database and its lowest typeid corresponding to that type'''

    NULL, TINYINT, SMALLINT, INT, BIGINT, FLOAT, DOUBLE, _, YEAR, TIME, \
            DATETIME, DATE, TEXT = range(13)

# TODO: check integer ranges
__type_map = {
        ValueType.NULL:     (ValueType.NULL,     0, '0s',  NullType),
        ValueType.TINYINT:  (ValueType.TINYINT,  1, 'b', int),
        ValueType.SMALLINT: (ValueType.SMALLINT, 2, 'h', int),
        ValueType.INT:      (ValueType.INT,      4, 'i', int),
        ValueType.BIGINT:   (ValueType.BIGINT,   8, 'q', int),
        ValueType.FLOAT:    (ValueType.FLOAT,    4, 'f', Float32),
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

def check_type_compat(expected, actual):
    if actual in __type_map: actual = __type_map[actual][0]
    if expected == actual or actual == 0:
        return
    n_actual = hex(actual)
    n_expected = hex(expected)
    if actual in __type_map: n_actual = __type_map[actual][0].name
    if expected in __type_map: n_expected = __type_map[expected][0].name
    raise FileFormatError(f'type {n_actual} not compatible with type {n_expected}')

def vpack(typeids, *data):
    ''' Packs some data, given its typeids, into a marshalled, packed tuple,
    that includes number of items in tuple and typeid's. This returns a stream
    of bytes that represents the tuple of the data.'''

    data2 = []
    typeids2 = []

    if len(typeids) != len(data):
        raise FileFormatError(f'Expected {len(typeids)} data points, only got {len(data)} data points')

    full_fmt = '>B' + 'B' * len(typeids)
    for typeid, data in zip(typeids, data):
        if typeid not in __type_map:
            raise FileFormatError(f'Invalid type-id: 0x{typeid:x}')

        typeid, _, fmt, dtype = __type_map[typeid]

        # Check data-type of data
        if type(data) != dtype:
            raise FileFormatError('Data is not proper type to ' + \
                f'marshall, got {type(data)}, expected {dtype}')

        # Marshall value if needed
        if isinstance(data, DBData):
            data = data.encode()

        # Retype TEXT if needed 
        if typeid == ValueType.TEXT:
            typeid = ValueType.TEXT + len(data)
            if typeid > MAX_TYPE:
                raise FileFormatError('Text is too long.')
            _, _, fmt, dtype = __type_map[typeid]

        typeids2.append(typeid)
        if fmt:
            data2.append(data)
            full_fmt += fmt

    return struct.pack(full_fmt, len(typeids), *(typeids2 + data2)) 

def vpack1(typeid, data):
    ''' Packs a single data point, given its typeids, into a marshalled, packed
    tuple, that includes number of items in tuple and typeid (that does not
    include the number of columns)'''

    return vpack([typeid], data)[1:]

def vunpack(data):
    ''' Unpacks an marshalled tuple data with unknown types. This will return
    a list of data points that has been unpacked and unmarshalled. The data
    given MUST have exactly the same size of the tuple.'''
    return vunpack_from(data, 0, True)[0]

def vunpack_from(data, offset=0, exact=False):
    ''' Unpacks an marshalled tuple data with unknown types from some buffer.
    This will return a list of data points that has been unpacked and
    unmarshalled. Data must be AT LEAST the size of the tuple. On return, it
    will return a tuple of the element tuple and total size in bytes. '''

    if type(data) is not bytes:
        raise FileFormatError('Expected data to be of type bytes')

    if len(data) == 0:
        raise FileFormatError('Short read in unpack')

    cols = data[0]
    col_types = struct.unpack_from('>x' + 'B' * cols, data, offset)

    if offset + cols + 1 > len(data):
        raise FileFormatError('Short read in unpack')

    full_fmt = '>' + 'x' * (cols + 1)
    dtypes = []
    for typeid in col_types:
        _, size, fmt, dtype = __type_map[typeid] # Should't cause error
        full_fmt += fmt
        dtypes.append(dtype)

    fmt = struct.Struct(full_fmt)
    if offset + fmt.size > len(data):
        raise FileFormatError('Short read in unpack')
    elif exact and offset + fmt.size != len(data):
        raise FileFormatError('Not exact unpack')

    datas = list(struct.unpack_from(full_fmt, data, offset))
    for ind, data in enumerate(datas):
        dtype = dtypes[ind]
        if dtype != type(data):
            data = dtype.decode(data)
        datas[ind] = data

    return (tuple(datas), fmt.size)

def vunpack1_from(data, offset=0):
    ''' Unpacks one data point from an offset (without a header for number of
    columns).  Otherwise this does exactly the same as vunpack, but returns the
    actual value, not a 1-tuple. Size of data must be at least the size of the
    data type and the typeid byte'''

    data2 = data[offset:]
    tup, size = vunpack_from(b'\x01' + data2)
    return tup[0], size - 1

def vunpack1(data):
    ''' Unpacks one data point (without a header for number of columns).
    Otherwise this does exactly the same as vunpack, but returns the actual
    value, not a 1-tuple'''

    if type(data) is not bytes:
        raise FileFormatError('Expected data to be of type bytes')
    return vunpack(b'\x01' + data)[0]


def parse_from_str(typeid, strval):
    ''' Takes a string literal (minus quotations) and attempts to parse it into
    the respective marshalled object associated with the specified type.
    
    MAKE SURE TO CATCH THIS METHOD IF IT FAILS!!! Usually, the error messages
    that is raised at this point should be meaningful to the user, so use that.
    '''

    if typeid not in __type_map:
        raise FileFormatError(f'Invalid type-byte: 0x{typeid:x}')

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
        raise FileFormatError(f'Invalid type-byte: 0x{typeid:x}')

    _, _, _, dtype = __type_map[typeid]

    if issubclass(dtype, DBData):
        return dtype.parse_int(intval)
    else:
        return dtype(intval)
    
