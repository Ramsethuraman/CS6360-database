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

    def add(self,rowid, key):
        ''' Adds a rowid and key value into this node. 

        This will try to fit the value into the current node, if it cannot fit, it will return the rowids, the key, and the page numbers of the left and right child to be merged into the node above. 
        '''
        p = self.__page
        ind = self.__ind
        cells = p.cells
        ovfrow = None
        ovfkey = None
        ovfl = None
        ovfr = None
        found = False
        intAdd = 0
        
        #First, we check what type of node we are working with
        if p.type == pt.IndexInterior:

            #print(str(self.pagenum) + " Interior Insert") <<< This and all other prints are debug code that will print a trace of what's going on.
            
            #We are an interior node, so we will need to handle recursion
            for icell in cells:
                if key == icell.key:
                    #We found the key, so we can just insert into it.

                    #print("\tKey Found")
                    
                    found = True
                    size = p.get_cell_size(icell)
                    icell.rowids.add(rowid)
                    break
                elif key < icell.key:
                    #We did not find the key, but we found a left_child to insert it into.
                    
                    #print("\tKey Not Found, But Valid Spot Found")
                    
                    found = True
                    n = ind._fetch_node(icell.left_child)
                    ovfrow, ovfkey ,ovfl, ovfr = n.add(rowid,key)
                    break
                intAdd = intAdd + 1
            if not found:
                    #We did not find any place, so we just insert it into the right child.
                    
                    #print("\tKey Not Found")
                    
                    n = ind._fetch_node(p.pnum_right)
                    ovfrow, ovfkey ,ovfl, ovfr = n.add(rowid,key)

        else: # p.type == pt.IndexLeaf
            
            #print(str(self.pagenum) + " Leaf Insert")
            
            #This node is a leaf node, so we must find a place to add
            exists = False
            for icell in cells:
                #The key exists already, so we can just add to that

                if key == icell.key:
                    
                    #print("\tKey Exists")
                    
                    exists = True
                    icell.rowids.add(rowid)
                    break
            if not exists:
                #print("\tKey Doesn't Exist")
                
                #The key does not exist, so we can just add it in a new cell.
                
                cell = create_cell(pt.IndexLeaf,p.tuple_types,rowids = {rowid}, key = key)
                
                for i in range(len(cells)):
                    if key < cells[i].key:
                        cells.insert(i,cell)
                        break
                    elif i == len(cells)-1:
                        cells.append(cell)

        #Check to see if any of the above recursion returned overflow, if so merge.
        if ovfrow != None:
            #print(str(self.pagenum) + " OVF Returned")
            
            #Check if we found a place or not. If we found a place to insert, we will insert in a left child, otherwise, we will do it in the right child.
            if found: 
                #print("\tMerge from cells")
                
                #Iterate through to find where ovf key goes. 
                cells[intAdd].left_child = ovfr.pagenum
                ovfr._reparent(self.pagenum)
                ovfc = create_cell(pt.IndexInterior, p.tuple_types, rowids = ovfrow,key = ovfkey, left_child = ovfl.pagenum)
                cells.insert(intAdd, ovfc)
            else:
                #print("\tMerge from right")

                ovfc = create_cell(pt.IndexInterior, p.tuple_types, rowids = ovfrow,key = ovfkey, left_child = ovfl.pagenum)     
                p.pnum_right = ovfr.pagenum
                ovfr._reparent(self.pagenum)
                cells.append(ovfc)

        #If our file is way too big, we need to return overflow values for the recursion. This will just split the node in half and work with it.
        if p.get_free_size() < 0:
            #print("\tReturning OVF")
            
            if len(cells) > 2:
                ovfr = None
                if p.pnum_right == None:
                    
                    #print("\tLeaf")
                    
                    ovfr = ind._create_node(p.type, INVALID_OFF, INVALID_OFF,cells[len(cells)//2+1:])
                else:
                    
                    #print("\tInterior")
                    
                    ovfr = ind._create_node(p.type, p.pnum_right, INVALID_OFF,cells[len(cells)//2+1:])
                ovfrow = cells[len(cells)//2].rowids
                ovfkey = cells[len(cells)//2].key
                for i in reversed(range(len(cells)//2,len(cells))):
                    del cells[i]
                self.writeback()
                return ovfrow,ovfkey, self, ovfr
            else:
                #We cannot actually split anything with two nodes, but we did not write any code to recurse backwards. If you reach this point, the database is as good as ruined.
                raise FileFormatError('Page cannot be split. Database may be in an inconsistent state.')

        else:
            #We are good. Just writeback and return.
            self.writeback()
            return None,None,None,None
    
    def search(self,key,inequality):
        ''' A recursive search function for a node. Returns a list of rowids.
        Inequalities are a string representing: == , != , <= , < , > , >= '''
        p = self.__page
        ind = self.__ind
        cells = p.cells

        #If our inequality is equal, just traverse until we hit something greater than us. 
        #If we found something equal, return. Else return a search on the left child. 
        #If nothing is greater, return a search on the right chid.
        if inequality == '=':
            for icell in cells:
                if icell.key == key:
                    return icell.rowids
                elif key < icell.key:
                    if p.type == pt.IndexLeaf:
                        return []
                    n = ind._fetch_node(icell.left_child)
                    return n.search(key,inequality)

            if p.type != pt.IndexLeaf:
                n = ind._fetch_node(p.pnum_right)
                return n.search(key,inequality)

            return []
        #This one is the most complicated, so commented in detail.
        elif inequality == '<' or inequality == '<=':
            rowids = []
            for icell in cells:
                #If the cell is less than us, we can definitely add it and traverse down its child.
                if icell.key < key:
                    #Add the rowids of the cell
                    rowids += icell.rowids
                    #Add the rowids of the left child
                    if p.type != pt.IndexLeaf:
                        n = ind._fetch_node(icell.left_child)
                        rowids += n.search(key,inequality)
                #If it's equal, we need to check if we are on a <=, if so, add and traverse the left child. Return because we know there is nothing past.
                elif key == icell.key:
                    if inequality == '<=':
                        rowids += icell.rowids
                    if p.type != pt.IndexLeaf:
                        n = ind._fetch_node(icell.left_child)
                        rowids += n.search(key,inequality)
                    return rowids

                #finally, if it is greater, we want to search the left child and return because we know nothing is past this point.
                else: #icell.key > key
                    if p.type != pt.IndexLeaf:
                        n = ind._fetch_node(icell.left_child)
                        rowids += n.search(key,inequality)
                    return rowids
            #If we're here, it means we never hit the last two cases, meaning we need to search the right child
            if p.type != pt.IndexLeaf:
                n = ind._fetch_node(p.pnum_right)
                return n.search(key,inequality)

            return rowids

        elif inequality == '>' or inequality == '>=':
            rowids = []
            for icell in cells:
                #If the cell is greater than us, add it and traverse its child.
                if icell.key > key:
                    rowids += icell.rowids
                    if p.type != pt.IndexLeaf:
                        n = ind._fetch_node(icell.left_child)
                        rowids += n.search(key,inequality)
                #If it is equal, only add on !=. Don't traverse because we know it will all be less than.
                elif key == icell.key:
                    if inequality == '>=':
                        rowids += icell.rowids
            #Traverse the right child and return.
            if p.type != pt.IndexLeaf:
                n = ind._fetch_node(p.pnum_right)
                rowids += n.search(key,inequality)
            return rowids   
        
        else: #inequality == '!='
            rowids = []
            #For every cell, check if it is not equal. If so add it. In all cases, traverse the left child.
            for icell in cells:
                if icell.key != key:
                    rowids += icell.rowids
                if p.type != pt.IndexLeaf:
                    n = ind._fetch_node(icell.left_child)
                    rowids += n.search(key,inequality)
            #If we are an interior node, traverse the right child.
            if p.type != pt.IndexLeaf:
                n = ind._fetch_node(p.pnum_right)
                rowids += n.search(key,inequality)
            return rowids


                

    def modify(self,old_rowid,new_rowid,key):
        '''modifes a rowid, key pair, replacing it with the new_rowid'''
        p = self.__page
        ind = self.__ind
        cells = p.cells

        for icell in cells:
            #If the key is equal, modify it.
            if icell.key == key:
                for i, row in enumerate(icell.rowids):
                    if row == old_rowid:
                        icell.rowids[i] = row
                        return True
                return False
            #Check the left path on everything greater than us.
            elif key < icell.key:
                if p.type != pt.IndexLeaf:
                    n = ind._fetch_node(icell.left_child)
                    return n.modify(old_rowid,new_rowid,key)
        if p.type != pt.IndexLeaf:
            n = ind._fetch_node(p.pnum_right)
            return n.modify(old_rowid,new_rowid,key)
        return False
    
    def delete(self,rowid,key):
        '''deletes a rowid, key pair. Code implemented similar to the modify code'''
        p = self.__page
        ind = self.__ind
        cells = p.cells
        for icell in cells:
            #If the key is equal, delete if it has more than one rowid.
            if icell.key == key:
                if rowid in icell.rowids:
                    icell.rowids.remove(rowid)
                    return True
                else:
                    raise ValueError()
                    return False
#                if len(icell.rowids) > 1:
#                    icell.rowids.remove(rowid)
#                else:
#                    raise FileFormatError('Cannot delete without removing cell. Database left unchanged.')
            #Check the left path on everything greater than us.
            elif key < icell.key:
                if p.type != pt.IndexLeaf:
                    n = ind._fetch_node(icell.left_child)
                    return n.delete(rowid,key)
                else:
                    return False
        #if we made it here, we hit nothing. try the delete on the right child.
        if p.type != pt.IndexLeaf:
            n = ind._fetch_node(p.pnum_right)
            return n.delete(rowid,key)
        
        return False
        
    
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
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

        root_page = self.calc_root()
        if root_page == INVALID_OFF:
            self.__root = None
        else:
            self.__root = root = self._fetch_node(root_page)
            if root.pnum_parent != INVALID_OFF:
                raise FileFormatError('Corrupted root page number')

    @property
    def root_page(self):
        if self.__root == None:
            return INVALID_OFF
        return self.__root.cur_pnum
    
    @lru_cache(128)
    def _fetch_node(self, pagenum):
        return IndexNode(self, self.read_page(pagenum))

    def _create_node(self, ptype, pnum_right, pnum_parent, cells):
        page = Page(self, -1, ptype, self.tuple_types, pnum_right, pnum_parent,
                cells)
        self.write_page(page)
        return IndexNode(self, page)

    def add(self, rowid, keyv):
        '''Adds an element. If there is not a root node, it is created. Overflows are handled recursively.'''

        #if no root, make a new root and insert
        if self.__root == None:
            cell = create_cell(pt.IndexLeaf, self.tuple_types, rowids = {rowid}, key = keyv)
            self.__root = self._create_node(pt.IndexLeaf, INVALID_OFF,
                    INVALID_OFF, [cell])
         
            # I hid the dirty stuff, but figured you'd be better at cleaning it up
            #self.__dirty.add('root_page')
            
            return None

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

        return None
    
    def clear(self):
        IndexFile._fetch_node.cache_clear()
        self.file.truncate(0)
        self.__root = None

    def search(self,key,inequality):
        '''Searches for a key and returns all associated rowids based on inequality, which is a string representing the following:
            < , <= , > , >= , == , != .'''
        if self.__root != None:
            return self.__root.search(key, inequality)
        else:
            return []
    
    def delete(self,rowid,key):
        '''Deletes the rowid, key combination'''
        if self.__root != None:
            return self.__root.delete(rowid,key)
        else:
            return False
    
    def modify(self,old_rowid,new_rowid,key):
        '''Modifys the rowid at key to a new rowid'''
        if self.__root != None:
            return self.__root.delete(old_rowid,new_rowid,key)
        else:
            return False





