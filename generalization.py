#!/usr/bin/env python
#coding=utf-8

# logic tree
class GenTree(object):

    """Class for Generalization hierarchies (Taxonomy Tree). 
    Store tree node in instances.
    self.value: node value
    self.level: tree level (top is 0)
    self.support: support
    self.parent: ancestor node list
    self.child: successor node list
    self.cover: leaf values cover by node
    """

    def __init__(self, value = None, parent = None):
        self.value = ''
        self.level = 0
        self.support = 0
        self.parent = []
        self.child = []
        # range is for ARE, all possible values are in range
        self.cover = []
        if value != None:
            self.value = value
        if parent != None:
            self.parent = parent.parent[:]
            self.parent.insert(0, parent)
            parent.child.append(self)
            self.level = parent.level + 1

    def node(self, value):
        """Search tree with value, return GenTree node.
        If value == node value, return node. 
        If value != node value, recurse search.
        """
        if self.value == value:
            return self
        else:
            for tn in child:
                return child.node(value)

    def compute_support(self):
        """compute the tree's support, and store in their var support
        """
        if len(self.child) != 0:
            for t in self.child:
                self.support = self.support + t.compute_support()
                self.cover.extend(t.cover)
        else:
            self.support = 1
            self.cover.append(self.value)
        return self.support


class CountTree(object):

    """Class for Count Tree Used in AA and DA. 
    Store tree node in instances.
    self.value: node value
    self.level: tree level (root is 0)
    self.parent: ancestor node list
    self.child: successor node list
    self.support: support 
    self.prefix: i-itemset
    """

    def __init__(self, value = None, parent = None):
        self.value = ''
        self.level = 0
        self.support = 0
        self.parent = []
        self.child = []
        self.prefix = []
        self.cover = []
        if value != None:
            self.value = value
        if parent != None:
            self.parent = parent.parent[:]
            self.parent.insert(0, parent)
            parent.child.append(self)
            self.level = parent.level + 1

    def node(self, value):
        """Search tree with value, return GenTree node.
        If value == node value, return node. 
        If value != node value, recurse search.
        """
        if self.value == value:
            return self
        else:
            for tn in child:
                return child.node(value)

    def add_to_tree(self, tran, prefix=[]):
        """Add combiation to count tree, add prefix to node
        """
        if len(prefix) >= 1 and len(self.prefix) == 0:
            self.prefix = prefix[:]
        index = 0
        len_tran = len(tran)
        for index, t in enumerate(self.child):
            if t.value == tran[0]:
                break
        else:
            self.child.append(CountTree(tran[0]))
            index = 0
        next_prefix = prefix[:]
        next_prefix.append(tran[0])
        if self.level > 0:
            self.value = tran[0]
        if len_tran > 1:
            self.child[index].add_to_tree(tran[1:], next_prefix)
        else:
            self.child[index].support += 1
            self.child[index].prefix = next_prefix


    def print_tree(self, print_matrix=[]):
        """print count tree
        """
        if self.level >= len(print_matrix):
            print_matrix.append([])
        if len(self.child) == 0:
            print_matrix[self.level].append(self.value)
        else:
            for t in self.child:
                t.print_tree(print_matrix)

        if self.level == 0:
            for i in range(len(print_matrix)):
                for j in range(len(print_matrix[i])):
                    print print_matrix[i][j],


if __name__ == '__main__':
    print 'OK'
