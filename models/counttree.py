"""
class for count tree
"""

#!/usr/bin/env python
#coding=utf-8

# count tree


class CountTree(object):

    """
    Class for Count Tree Used in AA and DA.
    Store tree node in instances.
    self.value: node value
    self.level: tree level (root is 0)
    self.parent: ancestor node list
    self.child: successor node list
    self.support: support
    self.prefix: i-itemset
    """

    def __init__(self, value=None, parent=None):
        self.value = ''
        self.level = 0
        self.support = 0
        self.parent = []
        self.child = []
        self.prefix = []
        self.path = []
        if value is not None:
            self.value = value
            self.path.append(value)
        if parent is not None:
            self.parent = parent.parent[:]
            self.parent.insert(0, parent)
            self.prefix = parent.prefix[:]
            if parent.value != '*':
                self.prefix.append(parent.value)
            self.path = self.prefix[:]
            self.path.append(self.value)
            parent.child.append(self)
            self.level = parent.level + 1

    def increase_support(self):
        """
        increase support of current node by 1
        """
        self.support += 1

    def dfs_traversal(self, traversal):
        """
        return deep first traversal of count tree
        """
        if self.value != '*':
            v_temp = ';'.join(self.path)
            traversal.append(v_temp)
        for child in self.child:
            child.dfs_traversal(traversal)

    def print_tree(self):
        """
        print node and its direct children in count tree
        """
        print "prefix %s" % self.prefix
        for t in self.child:
            print t.value,

    def __len__(self):
        """
        return support of current node
        """
        return self.support

    def __str__(self):
        """
        return print
        """
        return ';'.join(self.path)
