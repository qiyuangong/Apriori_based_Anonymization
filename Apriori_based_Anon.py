#!/usr/bin/env python
#coding=utf-8

# Poulis set k=25, m=2 as default!

import pdb
from generalization import GenTree, CountTree
from random import randrange
from itertools import combinations


_DEBUG = False

class Apriori_based_Anon(object):

    """Class for Apriori based Anonymization.
    self.att_tree: store generalization hierarchy (dict)
    self.gl_count_tree: store sorted nodes
    """

    def __init__(self, att_tree):
        # att_tree store root node for each att
        self.att_tree = att_tree
        # count tree root
        self.gl_count_tree = []
        for k, v in self.att_tree.iteritems():
            self.gl_count_tree.append(k)
        # delete *, and sort reverse
        self.gl_count_tree.remove('*')
        self.gl_count_tree.sort(cmp=self.tran_cmp, reverse=True)

    def tran_cmp(self, node1, node2):
        """Compare node1 (str) and node2 (str)
        Compare two nodes according to their support
        """
        support1 = self.att_tree[node1].support
        support2 = self.att_tree[node2].support
        if support1 != support2:
            return support1 - support2
        else:
            return cmp(node1, node2)

    def cut_cmp(self, cut1, cut2):
        """Compare cut1 (list) and cut2 (list)
        Compare two cut according to their sum of node support
        """
        support1 = 0
        support2 = 0
        for t in cut1:
            support1 += self.att_tree[t].support
        for t in cut2:
            support2 += self.att_tree[t].support
        if support1 != support2:
            return support1 - support2
        else:
            return (cut1 > cut2)    

    def expand_tran(self, tran, cut=None):
        """expand transaction according to generalization cut
        """
        ex_tran = tran[:]
        # extend t with all parents
        for temp in tran:
            for t in self.att_tree[temp].parent:
                if not t.value in ex_tran: 
                    ex_tran.append(t.value)
        ex_tran.remove('*')
        # sort ex_tran
        ex_tran.sort(cmp=self.tran_cmp, reverse=True)
        if _DEBUG:
            print "tran %s " % tran
            print "ex_tran %s" % ex_tran
        if cut:
            delete_list = []
            for temp in ex_tran:
                ancestor = [parent.value for parent in self.att_tree[temp].parent]
                for t in cut:
                    if t in ancestor:
                        delete_list.append(temp)
                        break
            for t in delete_list:
                ex_tran.remove(t)
        return ex_tran

    def init_count_tree(self):
        """initialize a new cout tree
        """
        # initialize count tree sort
        ctree = CountTree('*')
        for t in self.gl_count_tree:
            CountTree(t, ctree)
        return ctree

    def check_overlap(self, tran):
        """Check if items can joined with each other
        return True if overlapped, False if not
        """
        len_tran = len(tran)
        for i in range(len_tran):
            for j in range(len_tran):
                if i == j:
                    continue
                ancestor = [parent.value for parent in self.att_tree[tran[j]].parent]
                ancestor.append(tran[j])
                if tran[i] in ancestor:
                    return True
        return False

    def check_cover(self, tran, cut):
        """Check if tran if covered by cut
        return True if covered, False if not
        """
        if len(cut) == 0:
            return False
        for temp in tran:
            ancestor = [parent.value for parent in self.att_tree[temp].parent]
            ancestor.append(temp)
            for t in cut:
                if t in ancestor:
                    break
            else:
                return False
        return True

    def create_count_tree(self, trans, m):
        """Creat a count_tree for DA
        """
        ctree = self.init_count_tree()
        # extend t and insert to count tree
        for tran in trans:
            ex_t = self.expand_tran(tran)
            for i in range(1, m+1):
                temp = combinations(ex_t, i)
                # convet tuple to list
                temp = [list(combination) for combination in temp]
                for t in temp:
                    if not self.check_overlap(t) and len(t):
                        t.sort(cmp=self.tran_cmp, reverse=True)
                        ctree.add_to_tree(t)
        return ctree

    def get_cut(self, ctree, k):
        """Given a tran, return cut making it k-anonymity with mini information
        return cut is a list e.g. ['A', 'B']
        """
        ancestor = []
        cut = []
        c_root = ctree.parent[-1]
        tran = ctree.prefix[:]
        # get all ancestors
        for t in tran:
            parents = self.att_tree[t].parent[:]
            parents.append(self.att_tree[t])
            for p in parents:
                if not p.value in ancestor:
                    ancestor.append(p.value)
        ancestor.remove('*')
        # generate all possible cut for tran
        len_ance = len(ancestor)
        for i in range(1, len_ance+1):
            temp = combinations(ancestor, i)
            # convet tuple to list
            temp = [list(combination) for combination in temp]
            # remove combination with overlap
            for t in temp:
                if not self.check_overlap(t) and len(t):
                    cut.append(t)
        # remove cut cannot cover tran
        temp = cut[:]
        cut = []
        for t in temp:
            if self.check_cover(tran, t):
                cut.append(t) 
        # sort by support, the same effect as sorting by NCP
        cut.sort(cmp=self.cut_cmp)
        for t in cut:
            t.sort(cmp=self.tran_cmp, reverse=True)
        # return 
        for t in cut:
            if c_root.node(t).support >= k:
                if _DEBUG:
                    print "tran %s" % tran
                    print "cut %s" % t
                return t
        # Well, Terrovitis don't metion this sitituation. I suggest suppress them.
        print "Error: Can not find cut for %s" % tran
        # pdb.set_trace()

    def merge_cut(self, cut, new_cut):
        """Merge new_cut to cut to form a stronger cut
        return cut cover both of them
        """
        if new_cut == None:
            return cut
        for t in new_cut:
            if not t in cut:
                cut.append(t)
        # merge coverd and overlaped
        cut.sort(cmp=self.tran_cmp, reverse=True)
        delete_list = []
        len_cut = len(cut)
        for i in range(len_cut):
            temp = cut[i]
            for j in range(i, len_cut):
                t = cut[j]
                ancestor = [parent.value for parent in self.att_tree[t].parent]
                if temp in ancestor:
                    delete_list.append(t)
        delete_list = list(set(delete_list))
        for t in delete_list:
            cut.remove(t)
        return cut

    def R_DA(self, ctree, cut, k=25, m=2):
        """Recursively get cut. Each branch can be paralleled
        """
        # pdb.set_trace()
        if ctree.level > 0 and self.check_cover([ctree.value], cut):
            return []
        if len(self.att_tree[ctree.value].child) == 0:
            return []
        if len(ctree.child):
            for temp in ctree.child:
                new_cut = self.R_DA(temp, cut, k, m)
                self.merge_cut(cut, new_cut)
        elif ctree.support < k and ctree.support > 0:
            new_cut = self.get_cut(ctree, k)
            self.merge_cut(cut, new_cut)
        else:
            return []
        return cut

    def DA(self, trans, k=25, m=2):
        """Direct anonymization for transaction anonymization.
        Developed by Manolis Terrovitis
        """
        cut = []
        ctree = self.create_count_tree(trans, m)
        if _DEBUG:
            print "Cut Tree"
        self.R_DA(ctree, cut, k, m)
        return cut[:]

    def AA(self, trans, k=25, m=2):
        """Apriori-based anonymization for transaction anonymization. 
        Developed by Manolis Terrovitis
        """
        cut = []
        # Codes below slightly different from Manolis's pseudocode.
        # I confirmed with Manolis that it's actual implement for AA.
        # The pseudocode in paper is not abstracted carefully.
        ctree = self.init_count_tree()
        for i in range(1, m+1):
            for t in trans:
                ex_t = self.expand_tran(t, cut)
                temp = combinations(ex_t, i)
                # convet tuple to list
                temp = [list(t) for t in temp]
                for t in temp:
                    if not self.check_overlap(t) and len(t):
                        t.sort(cmp=self.tran_cmp, reverse=True)
                        ctree.add_to_tree(t)
            # run DA
            self.R_DA(ctree, cut, k, i)
        return cut

    def trans_gen(self, trans, cut):
        """Generalize transaction according to ger cut
        """
        gen_trans = []
        for tran in trans:
            gen_tran = []
            for t in tran:
                ancestor = [parent.value for parent in self.att_tree[t].parent]
                for c in cut:
                    if c in ancestor:
                        gen_tran.append(c)
                    else:
                        gen_tran.append(t)
            gen_trans.append(list(set(gen_tran)))
        return gen_trans



