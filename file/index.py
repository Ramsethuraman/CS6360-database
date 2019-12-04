from .base import FileFormatError, require_params
from .paging import create_cell, Page, PageTypes as pt, PagingFile, INVALID_OFF
from functools import lru_cache

class IndexNode(object):
    def __init__(self, ind, page):
        if page.type not in (pt.IndexInterior, pt.IndexLeaf):
            raise ValueError('Not a table page')
        self.__ind = ind
        self.__page = page
        self.__total = page.page_size - Page.get_page_header_size()
        self.__minfill = self.__total // 2
        self.__minemp = self.__total - self.__minfill

    @property
    def pagenum(self):
        return self.__page.cur_pnum

    #THIS IS FUNCTION IS GOING TO BE CALLED. NO MATTER. I JUST WANT THE FIRST INSERT
    def add(self,rowid, key):
        ''' Adds a tuple value into this node. 
        
        This will try to fit the value into the current node, but if it fails,
        it will return the page number of the overflow node that should be
        added. This function will always return a tuple: the rowid of the new
        element added and the page number of the overflow page (or None, if no
        overflow occurred) 
        '''
        p = self.__page
        ind = self.__ind
        cells = p.cells
        #if cells[-1].rowid >= tbl.last_rowid + 1:
        #    raise FileFormatError('Corrupted last_rowid')
        ovfrow = None
        ovfkey = None
        ovfl = None
        ovfr = None
        intAdd = 0
        if p.type == pt.IndexInterior:
            print("Interior Insert")
            #iterate over children to see where to add
            found = False

            for icell in cells:
                intAdd = intAdd + 1
                if key == icell.key:
                    found = True
                    size = p.get_cell_size(icell)
                    icell.rowids.append(rowid)
                    if p.get_free_size()-size >= p.get_cell_size(test):
                        print()
                    #icell.
                    #add to cell and handle checks
                    break
                elif key < icell.key:
                    found = True
                    n = ind._fetch_node(icell.left_child)
                    ovfrow, ovfkey ,ovfl, ovfr = n.add(rowid,key)
                    #add on left child and handle checks + recursion up
                    break
            if not found:
                    n = ind._fetch_node(p.pnum_right)
                    ovfrow, ovfkey ,ovfl, ovfr = n.add(rowid,key)

        else: # p.type == pt.IndexLeaf
            print("Leaf Insert")
            #check if the key exists and if so add
            exists = False
            for icell in cells:
                if key == icell.key:
                    exists = True
                    #add to cell and handle checks
                    icell.rowids.append(rowid)
                    print("TEST " + str(p.get_free_size()))
                    break
            if not exists:
                cell = create_cell(pt.IndexLeaf,p.tuple_types,rowids = [rowid], key = key)
                #Insert cell into node
                for i in range(len(cells)):
                    if key < cells[i].key:
                        cells.insert(i,cell)
                        break
                    elif i == len(cells)-1:
                        cells.append(cell)

        #Handle ovf
        #Check size requirements
        if ovfrow != None:
            #Iterate through to find where ovf key goes. 
            cells[intAdd].left_child = ovfr.pagenum
            ovfr._reparent(cells[intAdd].pagenum)
            ovfc = create_cell(pt.IndexInterior, self.tuple_types, rowids = ovfrow,key = ovfkey, left_child = ovfl.pagenum)
            cells.insert(intAdd, ovfc)
        
        if p.get_free_size() < 0:
            ovfr = ind._create_node(p.type, INVALID_OFF, INVALID_OFF,cells[len(cells)//2+1:])
            ovfrow = cells[len(cells)//2].rowids
            ovfkey = cells[len(cells)//2].key
            print(len(cells)//2)
            for i in reversed(range(len(cells)//2,len(cells))):
                print(i)
                del cells[i]
            self.writeback()
            return ovfrow,ovfkey, self, ovfr
            #split, writeback, and return overflow
        
        self.writeback()
        return None,None,None,None
    
    #def get_branch(self, rowid):
    #    p = self.__page
    #    for i in range(len(p.cells)):
    #        if rowid <= p.cells[i].rowid:
    #            return i
    #    else:
    #        return len(p.cells)

    #def get_min_rowid(self):
    #    p = self.__page
    #    tbl = self.__tbl

    #    if p.type == pt.TableInterior:
    #        if len(p.cells) == 0:
    #            return tbl._fetch_node(p.pnum_right).get_min_rowid()
    #        else:
    #            return tbl._fetch_node(p.cells[0].left_child).get_min_rowid()
    #    else:
    #        if len(p.cells) == 0:
    #            raise FileFormatError('Leaf node has 0 cells')
    #        return p.cells[0].rowid

    def writeback(self):
        self.__ind.write_page(self.__page)

    def _reparent(self, pnum_parent):
        self.__page.pnum_parent = pnum_parent
        self.writeback()

class IndexFile(PagingFile):
    # TODO: transactions if we have time
    def __init__(self, *args, **kargs):
        require_params(kargs, 'root_page')

        #self.__dirty = set()
        #self.__lastrowid = kargs.pop('last_rowid')
        root_page = kargs.pop('root_page')

        super().__init__(*args, **kargs)

        if root_page == INVALID_OFF:
            self.__root = None
        else:
            self.__root = root = self._fetch_node(root_page)
            if root.pnum_parent != INVALID_OFF:
                raise FileFormatError('Corrupted root page number')


    @property
    def root_page(self):
        return self.__root.cur_pnum

    @property
    def last_rowid(self):
        return self.__lastrowid

    def dirty_props(self):
        ''' Queries and clears any table properties that might be dirty after
        modifying some internal state of the table. This function will return a
        dict of all dirty prop names to new prop values. '''
        dirty = self.__dirty
        ret = {}
        self.__dirty = set()
        
        for d in dirty:
            ret[d] = getattr(self, d)

    @lru_cache(128)
    def _fetch_node(self, pagenum):
        return IndexNode(self, self.read_page(pagenum))

    def _create_node(self, ptype, pnum_right, pnum_parent, cells):
        page = Page(self, -1, ptype, self.tuple_types, pnum_right, pnum_parent,
                cells)
        self.write_page(page)
        return IndexNode(self, page)

    def add(self, rowid, keyv):
        ''' Adds an tuple into this table. This function returns the rowid of
        the newly added item. The table's last rowid and root page might be
        modified, so it is *strongly* advised to update the dirty metadata
        properties as prescribed by dirty_props. '''
        
        #THIS IS WHERE THE TEST BEGINS

        print(rowid)
        print(keyv)
        #if no root, make a new root and insert
        if self.__root == None:
            cell = create_cell(pt.IndexLeaf, self.tuple_types, rowids = [rowid], key = keyv)
            self.__root = self._create_node(pt.IndexLeaf, INVALID_OFF,
                    INVALID_OFF, [cell])
         
            # I hid the dirty stuff, but figured you'd be better at cleaning it up
            #self.__dirty.add('root_page')
            
            return None

        #EVERYTHING PAST THIS POINT IS UNTESTED
        ovfrow, ovfkey ,ovfl, ovfr = self.__root.add(rowid,keyv)
        if ovfrow != None:
            ovfc = create_cell(pt.IndexInterior, self.tuple_types, rowids = ovfrow,key = ovfkey, left_child = ovfl.pagenum)
            ovfc.left_child = ovfl.pagenum
            
            newroot = self._create_node(pt.IndexInterior, ovfr.pagenum, 
        INVALID_OFF, [ovfc])
            ovfr._reparent(newroot.pagenum)
            ovfl._reparent(newroot.pagenum)
            self.__root = newroot
            #self.__dirty.add('root_page')



        return rowid





