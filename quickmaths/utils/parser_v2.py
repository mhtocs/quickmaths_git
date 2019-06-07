import cv2
import numpy as np
from quickmaths.utils.misc import DotDict, list_splice, listsub
from quickmaths.utils.constants import c, subt, supt, t, r, s
from copy import deepcopy


class Draculae:
    def __init__(self):
        pass

    def parse(self, symlist):
        pass


class BSTNode:
    def __init__(self, data="", is_region=False):
        if is_region:
            self.symbols = []
            self.label = data  # pass Expression for first one
            self.node = None
            print(f"Creating : {self.label}")
        else:
            self.regions = {}
            self.parent = None
            self.label = data.label
            self.node = data
            self.min_x = data.min_x
            self.min_y = data.min_y  # - (data.height)
            self.max_x = data.max_x
            self.max_y = data.max_y  # + (data.height)
            self.width = data.width
            self.height = data.height  # self.max_y - self.min_y
            self.centroid_x = (self.min_x + self.max_x) / 2
            print(f"Creating : {self.label}")

            if self.label in ['_']:
                self.symbol_class = s.FRACTION_BAR
                self.centroid_y = self.max_y - self.height / 2
                self.BELOW = self.centroid_y
                self.ABOVE = self.centroid_y
                self.SUBSC = None
                self.SUPER = None

            elif self.label in list(map(str, '123456789')):
                self.symbol_class = s.DIGIT

                self.centroid_y = self.max_y - self.height * c
                self.BELOW = self.max_y - self.height * t
                self.ABOVE = self.max_y - (self.height - self.height * t)
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

            elif self.label in list(map(str, '+-')):
                self.symbol_class = s.NON_SCRIPTED
                self.centroid_y = self.max_y - self.height / 2
                self.BELOW = self.centroid_y
                self.ABOVE = self.centroid_y
                self.SUBSC = None
                self.SUPER = None

            elif self.label in list(map(str, '{[(')):
                self.symbol_class = s.OPEN_BRACKET
                self.centroid_y = self.max_y - self.height * c
                self.BELOW = self.min_y
                self.ABOVE = self.max_y
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

            elif self.label in list(map(str, '}])')):
                self.symbol_class = s.CLOSE_BRACKET
                self.centroid_y = self.max_y - self.height / 2
                self.BELOW = self.max_y - self.height * t
                self.ABOVE = self.max_y - (self.height - self.height * t)
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

            elif self.label in list(map(str, '√')):
                self.symbol_class = s.ROOT
                self.centroid_y = self.max_y - self.height * c
                self.ABOVE = self.min_y
                self.BELOW = self.max_y
                self.SUBSC = self.max_y - self.height * t
                self.SUPER = self.max_y - (self.height - self.height * t)

            elif self.label in list(map(str, 'Σ∫Π')):
                self.symbol_class = s.VARIABLE_RANGE
                self.centroid_y = self.max_y - self.height / 2

                self.BELOW = self.max_y - self.height * t
                self.ABOVE = self.max_y - (self.height - self.height * t)
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

            else:
                self.symbol_class = s.CENTERED
                self.centroid_y = self.max_y - self.height / 2

                self.BELOW = self.max_y - self.height * t
                self.ABOVE = self.max_y - (self.height - self.height * t)
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

    def is_adj(self, b):
        # print(f'is_adj():  self.type = {type(self)}, b.type = {type(b)}')
        # if None in [self.SUBSC, self.SUPER, b.SUPER, b.SUBSC]:
        #     return False

        if (b.symbol_class != s.NON_SCRIPTED and self != b and b.SUBSC >= self.centroid_y > b.SUPER):
            return True
        return False

    def contains(self, b):
        a = self
        return (a != b and
                a.symbol_class == s.ROOT and
                a.min_x <= b.centroid_x <= a.max_x and
                a.min_y <= b.centroid_y <= b.max_y)

    def overlaps(self, b):
        a = self
        return (a != b and
                a.symbol_class == s.NON_SCRIPTED and
                a.min_x <= b.centroid_x < a.max_x and
                not b.contains(a) and
                not (b.symbol_class in [
                    s.OPEN_BRACKET, s.CLOSE_BRACKET] and
                    b.min_y <= a.centroid_y < b.max_y and
                    b.min_x <= a.min_x) and
                not (b.symbol_class in [s.NON_SCRIPTED, s.VARIABLE_RANGE] and
                     b.max_x - b.min_x > a.max_x - a.min_x)
                )

    @property
    def is_region(self):
        if self.node is None:
            return True
        return False

    @property
    def is_symbol(self):
        if self.node is not None:
            return True
        return False

    def __eq__(self, other):
        if isinstance(other, BSTNode) and not self.is_region:
            return self.min_x == other.min_x and self.max_x == other.max_x and self.max_y == other.max_x and self.min_y == other.min_y and self.label == other.label
        return False
    # @property
    # def symbols(self):
    #     assert self.is_region, f"symbols(): label {self.label} is not a region!"
    #     return self.symbols.copy()  # return a copy

    def insert_symbol(self, snode):
        assert self.is_region, f"insert_symbol: label {self.label} is not a region!"
        assert snode.is_symbol, f"insert_symbol: label {self.label} is not a symbol!"
        self.symbols.append(snode)

    def insert_region(self, region_name, children_list=[]):
        assert self.is_symbol, f"insert_region(): label {self.label} is not a symbol!"
        self.regions[region_name] = BSTNode(data=region_name, is_region=True)
        self.regions[region_name].symbols = children_list

    def insert_symbol_to_region(self, snode, region_name=None):
        assert snode.is_symbol, f"insert_symbol(): label {self.label} is not a symbol!"
        assert self.is_symbol, f"insert_symbol(): label {self.label} is not a symbol!"
        assert region_name is not None, f"insert_symbol(): region name cannot be None!"
        if not self.regions.get(region_name, False):
            self.regions[region_name] = BSTNode(data=region_name, is_region=True)
        self.regions[region_name].insert_symbol(snode)

    def copy(self):
        return deepcopy(self)

    def __repr__(self):
        return self.label

    def __str__(self):
        string = ""
        if self.is_region:
            if len(self.symbols) > 0:
                string += self.label
                string += "("
                for i in range(len(self.symbols)):
                    if i > 0:
                        string += ", "
                    string += str(self.symbols[i])
                string += ") "
        else:
            string += '[' + self.label + ']'
            children_text = ''
            for i in self.regions.values():
                children_text += str(i)
            if children_text:
                string += '{' + children_text + '} '
        return string


def Start(snode_list):
    """Find the symbol node which begins
    the dominant baseline in snode list.

    snode_list      list of symbol nodes

    Returns the starting symbol node
    """
    # print(f'Start:() {snode_list},len: {len(snode_list)}')
    if len(snode_list) == 1:
        return snode_list
    sn = snode_list[-1]
    sn_1 = snode_list[-2]
    if sn.overlaps(sn_1) or sn.contains(sn_1) or (sn.symbol_class == s.VARIABLE_RANGE and not sn_1.is_adj(sn)):
        snode_list.remove(sn_1)
    else:
        snode_list.remove(sn)
    if len(snode_list) > 1:
        Start(snode_list)
    return snode_list


# TLEFT
# BLEFT
# ABOVE
# BELOW
# CONTAINS

def Partition(snodelist, snode):
    """
    The symbol nodes in snode list are tested for
    belonging in regions of snode. Symbol nodes that fail the
    test are returned in list snodelist1. Symbol nodes that pass
    the test are placed below the appropriate child region
    nodes of snode; the updated subtree is returned as snode.
    """
    snodelist1 = snodelist.copy()

    # print(snodelist1)
    snodelist1.remove(snode)
    for node in snodelist:

        if node.centroid_x < snode.min_x:
            # SUPERSCRIPT
            if node.centroid_y < snode.SUPER:
                snode.insert_symbol_to_region(node, r.TLEFT)
                snodelist1.remove(node)

            # SUBSCRIPT
            elif node.centroid_y > snode.SUBSC:
                snode.insert_symbol_to_region(node, r.BLEFT)
                snodelist1.remove(node)

        # FRACTION
        elif snode.overlaps(node):
            if node.centroid_y < snode.ABOVE:
                snode.insert_symbol_to_region(node, r.ABOVE)
                snodelist1.remove(node)

            elif node.centroid_y > snode.BELOW:
                snode.insert_symbol_to_region(node, r.BELOW)
                snodelist1.remove(node)

        # ROOT
        elif snode.contains(node):
            snode.insert_symbol_to_region(node, r.CONTAINS)
            snodelist1.remove(node)

    return snodelist1, snode


def ConcatLists(snodelist1, snodelist2):
    return snodelist1 + snodelist2


def isRegularHor(snode1, snode2):
    return (snode2.is_adj(snode1) or
            (snode1.max_y <= snode2.max_y and
             snode1.min_y >= snode2.min_y) or
            snode2.symbol_class in [s.OPEN_BRACKET, s.CLOSE_BRACKET] and
            snode2.min_y <= snode1.centroid_y <= snode2.max_y
            )


def PartitionFinal(snodelist, snode):
    for node in snodelist:

        if node.min_x >= snode.centroid_x and snode != node:
            # SUPERSCRIPT
            if node.centroid_y <= snode.SUPER:
                snode.insert_symbol_to_region(node, r.SUPER)

            # SUBSCRIPT
            elif node.centroid_y >= snode.SUBSC:
                snode.insert_symbol_to_region(node, r.SUBSC)
    return snode


def CheckOverlap(snode, snodelist):
    wide_node = None
    for node in snodelist:
        if node.overlaps(snode):
            if wide_node is None:
                wide_node = node
            elif node.width > wide_node:
                wide_node = node

    if wide_node is None:
        wide_node = snode

    return wide_node


def Symbols(rnode):
    if rnode is None:
        return []
    assert rnode.is_region, "Symbols(), label: {rnode.label} is not a region"
    return rnode.symbols


root = None


def Hor(snodelist1, snodelist2):
    """Find the symbols of the baseline that
    begins with the symbols in snodelist1 and continues
    with a subset of the symbols in snodelist2.The symbols
    of the baseline are returned as snodelist3. Nonbaseline
    symbols in snodelist are partitioned into TLEFT ,
    BLEFT , ABOVE, BELOW , and CONTAINS regions.
    Symbols in TLEFT and BLEFT regions are later
    reassigned by the CollectRegions function.
    """
    # print(f'list1: {snodelist1}')
    # print(f'list2: {snodelist2}')
    print(root)
    if len(snodelist2) == 0:
        return snodelist1
    current_symbol = snodelist1[-1]
    print(f'current_symbol: {current_symbol},list2 is: {snodelist2}')
    remaining_symbols, current_symbol = Partition(snodelist2, current_symbol)
    print(f'current_symbol: {current_symbol},remaining_symbols is: {remaining_symbols}')

    snodelist1[-1] = current_symbol
    print(f'new snodelist {snodelist1}')

    if len(remaining_symbols) == 0:
        return snodelist1

    if current_symbol.symbol_class == s.NON_SCRIPTED:
        return Hor(ConcatLists(snodelist1, Start(remaining_symbols)), remaining_symbols)

    SL = remaining_symbols.copy()
    while len(SL) != 0:
        l1 = SL[0]
        if isRegularHor(current_symbol, l1):
            return Hor(ConcatLists(snodelist1, [CheckOverlap(l1, remaining_symbols)]), remaining_symbols)
        print(f'removing {l1.label}')
        SL.remove(l1)

    print(f'current_symbol: {current_symbol},remaining_symbols1 is: {remaining_symbols}')
    current_symbol = PartitionFinal(remaining_symbols, current_symbol)
    print(f'current_symbol: {current_symbol}')
    try:
        snodelist1.remove(current_symbol)
    except:
        pass
    print(f'concatelist {ConcatLists(snodelist1, [current_symbol])}')
    return ConcatLists(snodelist1, [current_symbol])


def HasNonEmptyRegion(snode, region_label):
    """Return true if snode has a child region
    node rnode with region label region_label, and
    |Symbols(rnode)| > 0

    snode                       BSTNode on which search to be performed
    region_label                name of region
    """
    return (region_label in snode.regions and
            len(Symbols(snode.regions.get(region_label, None))) > 0
            )


def PartitionSharedRegion(rlabel, snode1, snode2):
    if rlabel == r.TLEFT:
        rnode = snode2.regions.get(r.TLEFT, None)
        SL = Symbols(rnode)
        if snode1.symbol_class == s.NON_SCRIPTED:
            snodelist1 = []
        elif (snode2.symbol_class != s.VARIABLE_RANGE or
              snode2.symbol_class == s.VARIABLE_RANGE and
              not HasNonEmptyRegion(snode2, r.ABOVE)):
            snodelist1 = SL
        elif (snode2 == s.VARIABLE_RANGE and
              HasNonEmptyRegion(snode2, r.ABOVE)):
            snodelist1 = []
            for si in SL:
                if si.is_adj(snode2):
                    snodelist1.append(si)
                else:
                    break
        return snodelist1, listsub(SL, snodelist1)


def AddSuper(snodelist, snode):
    for node in snodelist:
        snode.insert_symbol_to_region(node, r.SUPER)
    return snode


def AddTleft(snodelist, snode):
    for node in snodelist:
        snode[r.SUPER].insert_symbol_to_region(node, r.SUPER)
    return snode


def RemoveRegions(region_label_list, snode):
    """
    Remove all child region nodes from snode
    that match any of the labels in region label list.

    region_label_list           list containing region labels
    snode                       node from which nodes to be removed


    Returns snode (modified)
    """
    for region in region_label_list:
        snode.regions.pop(region, None)
    return snode


def MergeRegions(region_label_list, region_label, snode):
    """For every region label in region label list,
    find all children of snode that have this label.
    All of these region nodes are then merged into a
    single region node labeled region_label.
    """
    all_childrens = []
    for region in region_label_list:
        region = snode.regions.pop(region, None)
        all_childrens.extend(Symbols(region))
    snode.insert_region(region_label, all_childrens)


def CollectRegions(snodelist):
    print(f'Called CollectRegions with {snodelist}')
    if len(snodelist) == 0:
        return snodelist
    s1 = snodelist[0]
    s11 = s1.copy()
    snodelist.remove(s1)
    snodelist1 = snodelist  # listsub(snodelist, [s1])

    if len(snodelist) > 1:
        s2 = snodelist[1]
        s21 = s2.copy()
        print(f'line: 442 snodelist1: {snodelist}')
        superList, tleftList = PartitionSharedRegion(r.TLEFT, s1, s2)
        print(f'superlist: {superList}')
        s11 = AddSuper(superList, s1)
        print(f'after super : {s11.label}')
        s21 = AddTleft(tleftList, RemoveRegions([r.TLEFT], s2))
        print(f'after tleft : {s21}')

        print(f'line: 446 snodelist1: {snodelist1}')
        snodelist1[1] = s21
        print(f'after asigning : {snodelist1}')

    if s11.symbol_class == s.VARIABLE_RANGE:
        upperlist = [r.TLEFT, r.ABOVE, r.SUPER]
        s11 = MergeRegions(upperlist, r.UPPER, s1)
    return ConcatLists([s11], CollectRegions(snodelist1))


def ExtractBaseline(rnode):
    """Find the dominant baseline in the region represented by
    rnode and update the part of BST that is rooted at rnode.
    Make recursive calls to add nested baselines

    rnode           region node


    Returns updated node
    """
    snode_list = Symbols(rnode)
    if len(snode_list) <= 1:
        return rnode
    s_start = Start(snode_list.copy())  # pass a copy
    # snode_list = listsub(snode_list, s_start)
    print(f'START: {s_start},nodelist: {snode_list}')
    baseline_symbols = Hor(s_start, snode_list)
    updated_baseline = baseline_symbols
    updated_baseline = CollectRegions(baseline_symbols)

    rnode.symbols = updated_baseline
    print(f'updated_baseline is: {updated_baseline}')
    for symbol in updated_baseline:
        print(symbol.regions)
        for region in symbol.regions.values():
            print(f'region_label: {region.label}')
            ExtractBaseline(region)
    return rnode


def SortSymbolsByMinX(snodelist):
    return sorted(snodelist, key=lambda symbol: symbol.min_x)


def BuildBST(snodelist):
    """Construct a Baseline Structure Tree from snode_list

    snode_list          sorted list (min_x -> max_x) of symbol nodes

    Returns the root node of BST
    """
    global root
    root = BSTNode(data=r.EXPRESSION, is_region=True)
    snodelist = SortSymbolsByMinX(snodelist)

    # return if empty
    if not snodelist:
        return root

    # make each symbol node in snode_list be a child of root
    for snode in snodelist:
        snode = BSTNode(snode)
        root.symbols.append(snode)

    print(root)

    return ExtractBaseline(root)
