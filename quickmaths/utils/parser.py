import cv2
import numpy as np
from quickmaths.utils.misc import DotDict
from quickmaths.utils.constants import c, subt, supt, t


class Draculae:
    def __init__(self):
        pass

    def parse(self, symlist):
        pass


class BSTNode:
    def __init__(self, data=None, is_region=False):

        if not data:
            data = BSTNode.region.EXPRESSION

        if is_region:
            self.children = []
            self.parent = None
            self.label = data
            self.symbol_class = None
            self.node = None
            self.min_x = 0
            self.min_y = 0
            self.max_x = 0
            self.max_y = 0
            self.width = 0
            self.height = 0
            self.centroid_x = 0
            self.centroid_y = 0

        else:
            self.children = []
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

            # fix this errors
            if self.label in ['—']:
                self.symbol_class = BSTNode.symbol.FRACTION_BAR
                self.centroid_y = self.max_y - self.height / 2
                self.BELOW = self.centroid_y
                self.ABOVE = self.centroid_y
                self.SUBSC = None
                self.SUPER = None

            elif self.label in list(map(str, '123456789')):
                self.symbol_class = BSTNode.symbol.DIGIT
                self.centroid_y = self.max_y - self.height * c

                self.BELOW = self.max_y - self.height * t
                self.ABOVE = self.max_y - (self.height - self.height * t)
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

            elif self.label in list(map(str, '+-')):
                self.symbol_class = BSTNode.symbol.NON_SCRIPTED
                self.centroid_y = self.max_y - self.height / 2
                self.BELOW = self.centroid_y
                self.ABOVE = self.centroid_y
                self.SUBSC = None
                self.SUPER = None

            elif self.label in list(map(str, '{[(')):
                self.symbol_class = BSTNode.symbol.OPEN_BRACKET
                self.centroid_y = self.max_y - self.height * c
                self.BELOW = self.min_y
                self.ABOVE = self.max_y
                self.SUBSC = None
                self.SUPER = None

            elif self.label in list(map(str, '}])')):
                self.symbol_class = BSTNode.symbol.CLOSE_BRACKET
                self.centroid_y = self.max_y - self.min_y / 2
                self.BELOW = self.max_y - self.height * t
                self.ABOVE = self.max_y - (self.height - self.height * t)
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

            elif self.label in list(map(str, '√')):
                self.symbol_class = BSTNode.symbol.ROOT
                self.centroid_y = self.max_y - self.height * c
                self.ABOVE = self.min_y
                self.BELOW = self.max_y
                self.SUBSC = self.max_y - self.height * t
                self.SUPER = self.max_y - (self.height - self.height * t)

            elif self.label in list(map(str, 'Σ∫Π')):
                self.symbol_class = BSTNode.symbol.VARIABLE_RANGE
                self.centroid_y = (self.min_y + self.max_y) / 2

                self.BELOW = self.max_y - self.height * t
                self.ABOVE = self.max_y - (self.height - self.height * t)
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

            else:
                self.symbol_class = BSTNode.symbol.CENTERED
                self.centroid_y = (self.min_y + self.max_y) / 2

                self.BELOW = self.max_y - self.height * t
                self.ABOVE = self.max_y - (self.height - self.height * t)
                self.SUBSC = self.BELOW
                self.SUPER = self.ABOVE

            # add regions
            for i in range(len(BSTNode.region)):
                self.children.append(BSTNode(i, is_region=True))

    def contains(self, b):
        a = self
        return (a.symbol_class == BSTNode.symbol.ROOT and
                a.min_x <= b.centroid_x <= a.max_x and
                a.min_y <= b.centroid_y <= b.max_y)

    def overlaps(self, b):
        a = self
        return (a.symbol_class == BSTNode.symbol.NON_SCRIPTED and
                a.min_x <= b.centroid_x < a.max_x and
                not b.contains(a) and
                not (b.symbol_class in [
                    BSTNode.symbol.OPEN_BRACKET, BSTNode.symbol.CLOSE_BRACKET] and
                    b.min_y <= a.centroid_y < b.max_y and
                    b.min_x <= a.min_x) and
                not (b.symbol in [BSTNode.symbol.NON_SCRIPTED, BSTNode.symbol.VARIABLE_RANGE] and
                     b.max_x - b.min_x > a.max_x - a.min_x)
                )

    def determine_position(self, node):
        root = self
        # dy = node.centroid_y - root.centroid_y

        if root.symbol_class == BSTNode.symbol.OPEN_BRACKET:
            if root.min_y < node.centroid_y < root.max_y:
                if node.symbol_class == BSTNode.symbol.CLOSE_BRACKET:
                    root.symbol_class = BSTNode.symbol.BRACKETED
                return BSTNode.region.CONTAINS

        elif root.overlaps(node):
            if node.centroid_y < root.ABOVE:
                return BSTNode.region.ABOVE
            elif node.centroid_y > root.BELOW:
                return BSTNode.region.BELOW

        elif root.contains(node):
            return BSTNode.region.CONTAINS

        elif node.centroid_x < root.min_x and root.SUBSC is not None and root.SUPER is not None:
            if node.centroid_y > root.SUBSC:  # subt * root.height:
                return BSTNode.region.BLEFT
            elif node.centroid_y < root.SUPER:
                return BSTNode.region.TLEFT

        elif node.centroid_x > root.min_x and root.SUBSC is not None and root.SUPER is not None:
            if node.centroid_y > root.SUBSC:
                return BSTNode.region.SUBSC
            elif node.centroid_y < root.SUPER:
                return BSTNode.region.SUPER

        return BSTNode.region.NULL

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

    def insert(self, node):
        if not node:
            print('unknown node in insert()')
            return False

        if self.is_region:
            i = len(self.children) - 1
            while i >= 0 and not self.children[i].insert(node):
                i -= 1
            if i < 0:
                # was not inserted in any child
                self.add(None, node)
            else:
                self.extend(self.children[i])

            return True
        else:
            position = self.determine_position(node)
    # constants
    region = DotDict({
        "NULL": 0,
        "ABOVE": 1,
        "BELOW": 2,
        "SUPER": 3,
        "SUBSC": 4,
        "UPPER": 5,
        "LOWER": 6,
        "TLEFT": 7,
        "BLEFT": 8,
        "CONTAINS": 9,
        "EXPRESSION": 10
    })

    symbol = DotDict({
        "FRACTION_BAR": 1,
        "DIGIT": 2,
        "NON_SCRIPTED": 3,
        "OPEN_BRACKET": 4,
        "ROOT": 5,
        "VARIABLE_RANGE": 6,
        "CENTERED": 7,
        "INTEGER": 8,
        "REAL": 9,
        "FUNCTION": 10,
        "CLOSE_BRACKET": 11,
        "BRACKETED": 12
    })
