import struct
import .base

_s_page_header = struct.Struct('>BxHHIIxx')
_s_page_offs = struct.Struct('>H')

INVALID_OFF = 0xffffffff

def readn(file, size):
    read = data = file.read(size)
    while len(data) != size:
        if not read:
            raise EOFError('Short read')
        read = file.read(size - len(data))
        data += read

    return data


class PagingFile(object):
    ''' Represents a paginated B-tree like structure that lays out key and
    value pairs within a searchable paging system'''

    def __init__(self, filename, page_size = 512):
        ''' Create paging DB file from a specific file. '''
        self.__file = open(filename, 'rb+')
        self.__filename = filename
        self.__pagesize = pagesize

    def read_page(self, pagenum):
        ''' Reads a page from disk into memory, representing this page as a Page
        object.'''

        # Seek to the respective page.
        f = self.__file
        f.seek(pagenum * self.__pagesize)
        
        # Parse page header
        page = readn(f, self.__pagesize)
        ptype, ncells, poff_start, pnum_right, pnum_parent = \
                _s_page_header.unpack_from(page)

    def write_page()


class Page(object):
    __slots__ = ['parent', 'type']
    def __init__(self, dbfile):
        self.parent = dbfile
