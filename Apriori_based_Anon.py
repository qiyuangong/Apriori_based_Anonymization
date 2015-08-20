"""
main module of Apriori based Anon
"""

#!/usr/bin/env python
#coding=utf-8

# Poulis set k=25, m=2 as default!

import pdb
import time
from models.gentree import GenTree
from models.counttree import CountTree
from random import randrange
from itertools import combinations


__DEBUG = False
# QI number
# att_tree store root node for each att
ATT_TREE = []
# count tree root
COUNT_TREE = []
ELEMENT_NUM = 0
TREE_SUPPORT = 0


def tran_cmp(node1, node2):
    """Compare node1 (str) and node2 (str)
    Compare two nodes according to their support
    """
    support1 = ATT_TREE[node1].support
    support2 = ATT_TREE[node2].support
    if support1 != support2:
        return cmp(support1, support2)
    else:
        return cmp(node1, node2)


def cut_cmp(cut1, cut2):
    """Compare cut1 (list) and cut2 (list)
    Compare two cut according to their sum of node support
    """
    support1 = 0
    support2 = 0
    for t in cut1:
        support1 += ATT_TREE[t].support
    for t in cut2:
        support2 += ATT_TREE[t].support
    if support1 != support2:
        return cmp(support1, support2)
    else:
        return (cut1 > cut2)


def expand_tran(tran, cut=None):
    """expand transaction according to generalization cut
    """
    ex_tran = tran[:]
    # extend t with all parents
    for temp in tran:
        for t in ATT_TREE[temp].parent:
            if t.value not in set(ex_tran) and t.value != '*':
                ex_tran.append(t.value)
    # ex_tran.remove('*')
    # sort ex_tran
    ex_tran.sort(cmp=tran_cmp, reverse=True)
    if __DEBUG:
        print "tran %s " % tran
        print "ex_tran %s" % ex_tran
    if cut:
        delete_list = []
        for temp in set(ex_tran):
            ancestor = set([parent.value for parent in ATT_TREE[temp].parent])
            for t in cut:
                if t in ancestor:
                    delete_list.append(temp)
                    break
        for t in set(delete_list):
            ex_tran.remove(t)
    return ex_tran


def init_gl_count_tree():
    """Init count tree order according to generalizaiton hierarchy
    """
    global COUNT_TREE
    # creat count tree
    COUNT_TREE = []
    for k, v in ATT_TREE.iteritems():
        COUNT_TREE.append(k)
    # delete *, and sort reverse
    COUNT_TREE.remove('*')
    COUNT_TREE.sort(cmp=tran_cmp, reverse=True)


def init_count_tree():
    """initialize a new cout tree
    """
    # initialize count tree
    ctree = CountTree('*')
    for t in COUNT_TREE:
        CountTree(t, ctree)
    return ctree


def check_overlap(tran):
    """Check if items can joined with each other
    return True if overlapped, False if not
    """
    len_tran = len(tran)
    for i in range(len_tran):
        for j in range(len_tran):
            if i == j:
                continue
            ancestor = [parent.value for parent in ATT_TREE[tran[j]].parent]
            ancestor.append(tran[j])
            if tran[i] in set(ancestor):
                return True
    return False


def check_cover(tran, cut):
    """Check if tran if covered by cut
    return True if covered, False if not
    """
    if len(cut) == 0:
        return False
    for temp in tran:
        ancestor = [parent.value for parent in ATT_TREE[temp].parent]
        ancestor.append(temp)
        for t in cut:
            if t in set(ancestor):
                break
        else:
            return False
    return True


def create_count_tree(trans, m):
    """Creat a count_tree for DA
    """
    ctree = init_count_tree()
    # extend t and insert to count tree
    for tran in trans:
        ex_t = expand_tran(tran)
        for i in range(1, m + 1):
            temp = combinations(ex_t, i)
            # convet tuple to list
            temp = [list(combination) for combination in temp]
            for t in temp:
                if not check_overlap(t) and len(t):
                    t.sort(cmp=tran_cmp, reverse=True)
                    ctree.add_to_tree(t)
    return ctree


def get_cut(ctree, k):
    """Given a tran, return cut making it k-anonymity with mini information
    return cut is a list e.g. ['A', 'B']
    """
    ancestor = []
    cut = []
    c_root = ctree.parent[-1]
    tran = ctree.prefix[:]
    # get all ancestors
    for t in tran:
        parents = ATT_TREE[t].parent[:]
        parents.append(ATT_TREE[t])
        for p in parents:
            if p.value not in set(ancestor):
                ancestor.append(p.value)
    ancestor.remove('*')
    # generate all possible cut for tran
    len_ance = len(ancestor)
    for i in range(1, len_ance + 1):
        temp = combinations(ancestor, i)
        # convet tuple to list
        temp = [list(combination) for combination in temp]
        # remove combination with overlap
        for t in temp:
            if not check_overlap(t) and len(t):
                cut.append(t)
    # remove cut cannot cover tran
    temp = cut[:]
    cut = []
    for t in temp:
        if check_cover(tran, t):
            cut.append(t)
    # sort by support, the same effect as sorting by NCP
    cut.sort(cmp=cut_cmp)
    for t in cut:
        t.sort(cmp=tran_cmp, reverse=True)
    # return
    for t in cut:
        if c_root.node(t).support >= k:
            if __DEBUG:
                print "tran %s" % tran
                print "cut %s" % t
            return t
    # Well, Terrovitis don't metion this sitituation. I suggest suppress them.
    print "Error: Can not find cut for %s" % tran
    # pdb.set_trace()


def merge_cut(cut, new_cut):
    """Merge new_cut to cut to form a stronger cut
    return cut cover both of them
    """
    if new_cut is None:
        return cut
    for t in new_cut:
        if t not in set(cut):
            cut.append(t)
    # merge coverd and overlaped
    cut.sort(cmp=tran_cmp, reverse=True)
    delete_list = []
    len_cut = len(cut)
    for i in range(len_cut):
        temp = cut[i]
        for j in range(i, len_cut):
            t = cut[j]
            ancestor = [parent.value for parent in ATT_TREE[t].parent]
            if temp in set(ancestor):
                delete_list.append(t)
    delete_list = list(set(delete_list))
    for t in delete_list:
        cut.remove(t)
    return cut


def R_DA(ctree, cut, k=25, m=2):
    """
    Recursively get cut. Each branch can be paralleled
    """
    if ctree.level > 0 and check_cover([ctree.value], cut):
        return []
    # leaf node means that this node value is not generalized
    if len(ATT_TREE[ctree.value].child) == 0:
        return []
    if len(ctree.child):
        for temp in ctree.child:
            new_cut = R_DA(temp, cut, k, m)
            merge_cut(cut, new_cut)
    elif ctree.support < k and ctree.support > 0:
        new_cut = get_cut(ctree, k)
        merge_cut(cut, new_cut)
    else:
        return []
    return cut


def DA(att_tree, trans, k=25, m=2):
    """
    Direct anonymization for transaction anonymization.
    Developed by Manolis Terrovitis
    """
    cut = []
    ctree = create_count_tree(trans, m)
    if __DEBUG:
        print "Cut Tree"
    R_DA(ctree, cut, k, m)
    return cut[:]


def AA(att_tree, trans, k=25, m=2):
    """
    Apriori-based anonymization for transaction anonymization.
    Developed by Manolis Terrovitis
    """
    cut = []
    # Codes below are slightly different from Manolis's pseudocode
    # I confirmed with Manolis that it's actual implement for AA.
    # The pseudocode in paper is not abstracted carefully.
    ctree = init_count_tree()
    for i in range(1, m + 1):
        for t in trans:
            ex_t = expand_tran(t, cut)
            temp = combinations(ex_t, i)
            # convet tuple to list
            temp = [list(t) for t in temp]
            for t in temp:
                if not check_overlap(t) and len(t):
                    t.sort(cmp=tran_cmp, reverse=True)
                    ctree.add_to_tree(t)
        # run DA
        R_DA(ctree, cut, k, i)
    return cut


def trans_gen(trans, cut):
    """Generalize transaction according to ger cut
    """
    gen_trans = []
    ncp = 0.0
    for tran in trans:
        gen_tran = []
        for t in tran:
            ancestor = set([parent.value for parent in ATT_TREE[t].parent])
            for c in cut:
                if c in ancestor:
                    gen_tran.append(c)
                else:
                    gen_tran.append(t)
        rncp = 0.0
        for t in set(gen_tran):
            rncp += 1.0 * ATT_TREE[t].support / TREE_SUPPORT
        gen_trans.append(list(set(gen_tran)))
        ncp += rncp
    ncp /= ELEMENT_NUM
    ncp *= 100
    return gen_trans, ncp


def init(att_tree, data):
    global ATT_TREE, ELEMENT_NUM, TREE_SUPPORT
    ELEMENT_NUM = 0
    ATT_TREE = att_tree
    TREE_SUPPORT = ATT_TREE['*'].support
    for tran in data:
        ELEMENT_NUM += len(tran)
    init_gl_count_tree()


def apriori_based_anon(att_tree, trans, type_alg='AA', k=25, m=2):
    """
    """
    init(att_tree, trans)
    start_time = time.time()
    if type_alg == 'DA':
        print "Begin DA"
        cut = DA(att_tree, trans)
    else:
        print "Begin AA"
        cut = AA(att_tree, trans)
    rtime = float(time.time() - start_time)
    # if __DEBUG:
    print "Final Cut"
    print cut
    result, ncp = trans_gen(trans, cut)
    return (result, (ncp, rtime))
