from .base import FileFormatError, require_params
from .paging import create_cell, Page, PageTypes as pt, PagingFile, \
        INVALID_OFF, TableInteriorCell
from functools import lru_cache

class TableInteriorRightCell(object):
    __slots__ = ['__page']

    def __init__(self, page):
        self.__page = page

    def _set_left_child(self, val):
        self.__page.pnum_right = val
    def _get_left_child(self):
        return self.__page.pnum_right
    left_child = property(_get_left_child, _set_left_child)

    @property
    def rowid(self): return INVALID_OFF

class TableNode(object):
    def __init__(self, tbl, page):
        if page.type not in (pt.TableInterior, pt.TableLeaf):
            raise ValueError('Not a table page')
        self.__tbl = tbl
        self.__page = page
        self.__total = page.page_size - Page.get_page_header_size()
        self.__minfill = self.__total // 2
        self.__right = TableInteriorRightCell(page)

    @property
    def page(self): return self.__page
    @property
    def pagenum(self): return self.__page.cur_pnum

    def add(self, tupleVal):
        ''' Adds a tuple value into this node. 
        
        This will try to fit the value into the current node, but if it fails,
        it will return the page number of the overflow node that should be
        added. This function will always return a tuple: the rowid of the new
        element added and the page number of the overflow page (or None, if no
        overflow occurred) 
        '''
        p = self.__page
        tbl = self.__tbl
        cells = p.cells
        if cells[-1].rowid >= tbl.last_rowid + 1:
            raise FileFormatError('Corrupted last_rowid')

        if p.type == pt.TableInterior:
            n = tbl._fetch_node(p.pnum_right)
            rowid, ovf = n.add(tupleVal)
            if ovf == None:
                return rowid, None

            n_ovf = tbl._fetch_node(ovf)
            cell = create_cell(pt.TableInterior, p.tuple_types,
                    rowid = n_ovf.get_min_rowid(), left_child = p.pnum_right)
            p.pnum_right = ovf
        else: # p.type == pt.TableLeaf
            rowid = tbl._next_rowid()
            cell = create_cell(pt.TableLeaf, p.tuple_types, rowid = rowid,
                    tuples = tupleVal)
            if self.__total < p.get_cell_size(cell):
                raise FileFormatError('Data tuple too big for page size')

        # Check for overflow
        if p.get_free_size() >= p.get_cell_size(cell):
            # Simply add the value
            cells.append(cell)
            self.writeback()
            return rowid, None

        # Add a new page with the overflow node as a sibiling of the parent (to
        # the right):
        #  - For interior nodes, we add a node with degree 1, no cells
        #  - For leaf nodes, add node with degree 1, with the cell of the tuple
        cells = [cell] if p.type == pt.TableLeaf else []
        n_ovf2 = tbl._create_node(p.type, p.pnum_right, p.pnum_parent, cells)

        # TODO: make it degree 2 instead of 1 for interior
        if p.type == pt.TableInterior:
            # Update the parent of the overflow node's child
            n_ovf._reparent(n_ovf2.pagenum)
        else:
            # Update this right pointer to point to new sibling
            p.pnum_right = n_ovf2.pagenum
            self.writeback()

        return rowid, n_ovf2.pagenum

    def delete(self, rowid):
        p = self.__page
        path = self.get_branch(rowid)
        if path == -1:
            return False
#            return False, False

        if p.type == pt.TableLeaf:
            del p.cells[path] 
            self.writeback()
            return True
#            return True, p.get_used_size() < self.__minfill

        return self._delete_interior(path, rowid)

    def _delete_interior(self, path, rowid):
        cell = self.get_cell(path)
        n_chld = self.__tbl._fetch_node(cell.left_child)
        p_chld = n_chld.__page
#        is_rm, is_udf = n.delete(rowid)

        is_rm = n_chld.delete(rowid)

        # Update pivot
        if is_rm and path > 0:
            self.get_cell(path - 1).rowid = n_chld.get_min_rowid()
            self.writeback()

        return is_rm
        

#    def _delete_interior(self, path, rowid)
#        cell = self.get_cell(path)
#        n_chld = self.__tbl._fetch_node(cell.left_child)
#        p_chld = n_chld.__page
#        is_rm, is_udf = n.delete(rowid)
#
#        # Update pivot
#        if is_rm and path > 0:
#            self.get_cell(path - 1).rowid = cell.get_min_rowid()
#            dirty = True
#
#        if not is_udf:
#            if dirty: self.writeback()
#            return is_rm, False
#            
##        # If children are leaf nodes, delete
##        if p_chld.type == pt.TableLeaf:
#
#        # Try borrowing a node if (a) it fits, (b) 
#        if 
#
#        if is_udf and path < len(p.cells):
#            sib = get_cell(path)
#            n_sib = self.__tbl.fetch_node(sib.left_child)
#
#            p_sib = n_sib.__page
#            p_chld = n.__page
#
#            if p_sib.get_used_size() <= p_chld.get_free_size():
#                # Merge these two cells
#                p_chld.cells += p_sib.cells
#                if path + 1 == len(p.cells):
#
#                del p.cells[path]
#                
#
#            take = p_sib.cells[0]
#            if p_sib.get_cell_size(take) <= p_chld
#
#    def _steal(self, n_chld, n_sib):
#        p_chld = n_chld.__page
#        p_sib = n_sib.__page
#
#        # The case to merge all children
#        if p_sib.get_used_size() <= p_chld.get_free_size():
#
#

    def _select_branch(self, rowid):
        ''' Determines which branch to take to get the rowid '''
        path = self.get_branch(rowid)
        cell = self.get_cell(path)
        if cell == None:
            return None, None
        if self.__page.type == pt.TableLeaf:
            return self, path
        else:
            return self.__tbl._fetch_node(cell.left_child)._select_branch(rowid)

    def select(self, rowid):
        n, path = self._select_branch(rowid)
        if n == None:
            return None
        cell = n.get_cell(path)
        return [rowid] + list(cell.tuples)

    def get_cell(self, ind):
        ''' Obtains the cell at the index. If the index is len(cells), it will
        return a special cell that can be used to get/set the right pointer.
        '''

        p = self.__page
        if ind == len(p.cells) and p.type == pt.TableInterior:
            return self.__right
        elif ind < 0:
            return None
        else:
            return p.cells[ind]

    def get_branch(self, rowid):
        ''' Obtains the index of the pointer/leaf cell that this rowid
        value should fall under. 
        
        For leaf pages, it will return -1 if it doesn't find an exact rowid
        match
        '''

        p = self.__page
        if p.type == pt.TableLeaf:
            for i in range(len(p.cells)):
                if rowid == p.cells[i].rowid:
                    return i
            else:
                return -1
        else:
            for i in range(len(p.cells)):
                if rowid < p.cells[i].rowid:
                    return i
            else:
                return len(p.cells)

    def get_min_rowid(self):
        p = self.__page
        tbl = self.__tbl

        if p.type == pt.TableInterior:
            if len(p.cells) == 0:
                return tbl._fetch_node(p.pnum_right).get_min_rowid()
            else:
                return tbl._fetch_node(p.cells[0].left_child).get_min_rowid()
        else:
            if len(p.cells) == 0:
                raise FileFormatError('Leaf node has 0 cells')
            return p.cells[0].rowid

    def modify(self, rowid, tupleVal):
        ''' Edits a row to be the tuple value specified. Note that the tuple
        does not contain the rowid value. This function will return the rowid of
        the tuple value after being modified, or None if it is not found. The
        rowid may change if the tuple value is too large, and it would have to
        be reinserted. '''

        tbl = self.__tbl
        n, path = self._select_branch(rowid)
        if n == None:
            return None

        cell = n.get_cell(path)
        if self.__page.type == pt.TableInterior:
            return n.modify(rowid, tupleVal)
        else:
            old = cell.tuples
            old_size = self.__page.get_cell_size(cell)
            cell.tuples = tupleVal
            if self.__page.get_free_size() >= 0:
                # TODO: maybe cell coalition if underflow?
                self.writeback()
                return True
            else:
                # Revert, as this would cause an overflow
                cell.tuples = old
                return False

    def writeback(self):
        self.__tbl.write_page(self.__page)

    def _reparent(self, pnum_parent):
        self.__page.pnum_parent = pnum_parent
        self.writeback()

def to_signed(val):
    if val >= 2**31:
        val -= 2**32
    return val

class TableFile(PagingFile):
    # TODO: transactions if we have time
    def __init__(self, *args, **kargs):
        require_params(kargs, 'last_rowid', 'root_page')

        self.__dirty = set()
        self.__lastrowid = kargs.pop('last_rowid') & 0xffffffff
        root_page = kargs.pop('root_page') & 0xffffffff

        super().__init__(*args, **kargs)

        if root_page == INVALID_OFF:
            self.__root = None
        else:
            self.__root = root = self._fetch_node(root_page)
            if root.page.pnum_parent != INVALID_OFF:
                raise FileFormatError('Corrupted root page number')

    @property
    def root_page(self): 
        if self.__root == None:
            return to_signed(INVALID_OFF)
        return to_signed(self.__root.pagenum)
    @property
    def last_rowid(self): return to_signed(self.__lastrowid)

    def __iter__(self):
        ''' This will return an iterator that iterates through all the tuple
        values in this table in increasing monotonic order. Each element is
        represented as a 2-tuple of rowid and tuple value'''

        if self.__root == None:
            return

        n = self.__root
        while n.page.type != pt.TableLeaf:
            n = self._fetch_node(n.get_cell(0).left_child)
        while True: 
            for c in n.page.cells:
                yield [c.rowid] + list(c.tuples)
            if n.page.pnum_right == INVALID_OFF:
                break
            n = self._fetch_node(n.page.pnum_right)

    def dirty_props(self):
        ''' Queries and clears any table properties that might be dirty after
        modifying some internal state of the table. This function will return a
        dict of all dirty prop names to new prop values. '''
        dirty = self.__dirty
        ret = {}
        self.__dirty = set()
        
        for d in dirty:
            ret[d] = getattr(self, d)
        return ret

    @lru_cache(128)
    def _fetch_node(self, pagenum):
        return TableNode(self, self.read_page(pagenum))

    def _create_node(self, ptype, pnum_right, pnum_parent, cells):
        page = Page(self, -1, ptype, self.tuple_types, pnum_right, pnum_parent,
                cells)
        self.write_page(page)
        return TableNode(self, page)

    def _next_rowid(self):
        self.__lastrowid += 1
        self.__dirty.add('last_rowid')
        return self.__lastrowid

    def add(self, tupleVal):
        ''' Adds an tuple into this table. This function returns the rowid of
        the newly added item. The table's last rowid and root page might be
        modified, so it is *strongly* advised to update the dirty metadata
        properties as prescribed by dirty_props. '''

        if self.__root == None:
            rowid = self._next_rowid()
            cell = create_cell(pt.TableLeaf, self.tuple_types, 
                    rowid = rowid, tuples = tupleVal)
            self.__root = self._create_node(pt.TableLeaf, INVALID_OFF,
                    INVALID_OFF, [cell])
            self.__dirty.add('root_page')
            return rowid

        rowid, ovf = self.__root.add(tupleVal)
        if ovf != None:
            n_ovf = self._fetch_node(ovf)
            cell = create_cell(pt.TableInterior, self.tuple_types, 
                    left_child = self.__root.pagenum, 
                    rowid = n_ovf.get_min_rowid())
            newroot = self._create_node(pt.TableInterior, ovf, 
                    INVALID_OFF, [cell])
            n_ovf._reparent(newroot.pagenum)
            self.__root._reparent(newroot.pagenum)
            self.__root = newroot
            self.__dirty.add('root_page')

        return rowid

    def clear(self):
        TableFile._fetch_node.cache_clear()
        self.file.truncate(0)
        self.__root = None
        self.__dirty.add('root_page')

    def delete(self, rowid):
        if self.__root == None:
            return False
        return self.__root.delete(rowid)

    def select(self, rowid):
        if self.__root == None:
            return None
        return self.__root.select(rowid)

    def modify(self, rowid, tupleVal):
        ''' Modifies the rowid to have the new tupleVal. If the tupleVal would
        cause an overflow in the page that it is in, this will remove the rowid
        and insert a new row with that tupleVal. This will return the (possibly
        new) rowid of the modified tuple, or None on failure'''

        if self.__root == None:
            return None
        
        ret = self.__root.modify(rowid, tupleVal)
        if ret == None:
            return None
        elif ret == False:
            if not self.delete(rowid):
                return None
            return self.add(tupleVal)
        else:
            return rowid



