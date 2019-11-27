from .base import FileFormatError, require_params
from .paging import create_cell, Page, PageTypes as pt, PagingFile, INVALID_OFF
from functools import lru_cache

class TableNode(object):
    def __init__(self, tbl, page):
        if page.type not in (pt.TableInterior, pt.TableLeaf):
            raise ValueError('Not a table page')
        self.__tbl = tbl
        self.__page = page
        self.__total = page.page_size - Page.get_page_header_size()
        self.__minfill = self.__total // 2
        self.__minemp = self.__total - self.__minfill

    @property
    def pagenum(self):
        return self.__page.cur_pnum

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

        if p.type == pt.TableInterior:
            # Update the parent of the overflow node's child
            n_ovf._reparent(n_ovf2.pagenum)
        else:
            # Update this right pointer to point to new sibling
            p.pnum_right = n_ovf2.pagenum
            self.writeback()

        return rowid, n_ovf2.pagenum

    def get_branch(self, rowid):
        p = self.__page
        for i in range(len(p.cells)):
            if rowid <= p.cells[i].rowid:
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

    def writeback(self):
        self.__tbl.write_page(self.__page)

    def _reparent(self, pnum_parent):
        self.__page.pnum_parent = pnum_parent
        self.writeback()

class TableFile(PagingFile):
    # TODO: transactions if we have time
    def __init__(self, *args, **kargs):
        require_params(kargs, 'last_rowid', 'root_page')

        self.__dirty = set()
        self.__lastrowid = kargs.pop('last_rowid')
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





