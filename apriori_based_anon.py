"""
main module of Apriori based Anon
"""

#!/usr/bin/env python
#coding=utf-8

import pdb
import time
from models.gentree import GenTree
from models.counttree import CountTree
from random import randrange
from itertools import combinations


__DEBUG = False
# QI number
# att_tree store root node for each att
ATT_TREE = {}
# count tree root
COUNT_TREE = []
COUNT_DICT = {}
ELEMENT_NUM = 0
LEAF_NUM = 0
NOT_OVERLAP = {}


def tran_cmp(node1, node2):
    """Compare node1 (str) and node2 (str)
    Compare two nodes according to their support
    """
    leaf_num1 = len(ATT_TREE[node1])
    leaf_num2 = len(ATT_TREE[node2])
    if leaf_num1 != leaf_num2:
        return cmp(leaf_num1, leaf_num2)
    else:
        return cmp(node1, node2)


def cut_cmp(cut1, cut2):
    """Compare cut1 (list) and cut2 (list)
    Compare two cut according to their sum of node support
    """
    leaf_num1 = 0
    leaf_num2 = 0
    for item in cut1:
        leaf_num1 += len(ATT_TREE[item])
    for item in cut2:
        leaf_num2 += len(ATT_TREE[item])
    if leaf_num1 != leaf_num2:
        return cmp(leaf_num1, leaf_num2)
    else:
        return cmp(cut1, cut2)


def expand_tran(tran, cut={}):
    """expand transaction according to generalization cut
    """
    ex_tran = tran[:]
    # extend item with all parents
    for temp in tran:
        # remove '*', which is tail of parent
        for item in ATT_TREE[temp].parent[:-1]:
            ex_tran.append(item.value)
    # remove duplicate values
    ex_tran = list(set(ex_tran))
    # sort ex_tran
    ex_tran.sort(cmp=tran_cmp, reverse=True)
    if __DEBUG:
        print "tran", tran
        print "ex_tran", ex_tran
    if len(cut) > 0:
        check_result = []
        for temp in ex_tran:
            try:
                cut[temp]
            except KeyError:
                check_result.append(temp)
        ex_tran = check_result
    return ex_tran


def init_gl_count_tree():
    """Init count tree order according to generalizaiton hierarchy
    """
    global COUNT_TREE
    # creat count tree
    COUNT_TREE = []
    for item_k in ATT_TREE.keys():
        if item_k is not '*':
            COUNT_TREE.append(item_k)
    # delete *, and sort reverse
    # COUNT_TREE.remove('*')
    COUNT_TREE.sort(cmp=tran_cmp, reverse=True)


def init_count_tree():
    """initialize a new cout tree
    """
    # initialize count tree
    global COUNT_DICT
    COUNT_DICT = {}
    ctree = CountTree('*')
    COUNT_DICT['*'] = ctree
    # just make root ctree has a none zero support
    ctree.support = ELEMENT_NUM
    for item in COUNT_TREE:
        node = CountTree(item, ctree)
        COUNT_DICT[str(node)] = node
    return ctree


def create_count_tree(trans, m):
    """Creat a count_tree for DA
    """
    ctree = init_count_tree()
    # extend item and insert to count tree
    for tran in trans:
        ex_t = expand_tran(tran)
        for i in range(1, m + 1):
            insert_to_ctree(ex_t, i)
    return ctree


def insert_to_ctree(ex_t, m):
    """
    insert extanded tran to ctree
    """
    temp = combinations(ex_t, m)
    # convet tuple to list
    temp = [list(t) for t in temp]
    for item in temp:
        if not check_overlap(item) and len(item) > 0:
            item.sort(cmp=tran_cmp, reverse=True)
            add_to_tree(item)


def add_to_tree(tran):
    """
    add to count accoding to COUNT_DICT
    """
    vtemp = ';'.join(tran)
    try:
        COUNT_DICT[vtemp]
        COUNT_DICT[vtemp].support += 1
    except KeyError:
        parent_temp = COUNT_DICT[';'.join(tran[:-1])]
        temp = CountTree(tran[-1], parent_temp)
        COUNT_DICT[vtemp] = temp
        temp.support += 1


def check_overlap(tran):
    """Check if items can joined with each other
    return True if overlapped, False if not
    """
    if len(tran) == 1:
        return False
    vtemp = ';'.join(tran)
    try:
        if NOT_OVERLAP[vtemp] > 0:
            return False
        else:
            return True
    except KeyError:
        pass
    cover_list = []
    for item in tran:
        cover_list.extend(ATT_TREE[item].cover.keys())
        if len(cover_list) != len(set(cover_list)):
            NOT_OVERLAP[vtemp] = 0
            return True
    NOT_OVERLAP[vtemp] = 1
    return False


def merge_cut(cut, new_cut):
    """Merge new_cut to cut to form a stronger cut
    return cut cover both of them
    """
    if new_cut is None or len(new_cut) == 0:
        return
    # merge coverd and overlaped
    for item in new_cut.keys():
        try:
            if len(ATT_TREE[cut[item]]) < len(ATT_TREE[new_cut[item]]):
                cut[item] = new_cut[item]
        except KeyError:
            cut[item] = new_cut[item]


def get_cut_dict(cut):
    """
    creat cut (dict) according to cut (list)
    """
    cut_dict = dict()
    for item in cut:
        cover_list = ATT_TREE[item].cover.keys()
        for cover_value in cover_list:
            if cover_value == item:
                continue
            try:
                cut_dict[cover_value]
                # watch dog to check if check_overlap works
                print "ERROR: Overlap cut!"
                pdb.set_trace()
            except KeyError:
                cut_dict[cover_value] = item
    return cut_dict


def get_cut(ctree, k):
    """Given a tran, return cut making it k-anonymity with mini information
    return cut is a list e.g. ['A', 'B']
    """
    # pdb.set_trace()
    tran = ctree.path[:]
    # get all ancestors
    ancestor = []
    for item in tran:
        parents = ATT_TREE[item].parent[:-1]
        # parents.insert(0, ATT_TREE[item])
        for parent in parents:
            ancestor.append(parent.value)
    ancestor = list(set(ancestor))
    # ancestor.remove('*')
    # generate all possible cuts for tran
    len_ance = len(ancestor)
    cuts = []
    for i in range(1, len_ance + 1):
        cuts = []
        temp = combinations(ancestor, i)
        # convet tuple to list
        temp = [list(combination) for combination in temp]
        # remove combination with overlap
        for item in temp:
            if not check_overlap(item) and len(item):
                cuts.append(item)
        # # sort by support, the same effect as sorting by NCP
        cuts.sort(cmp=cut_cmp)
        # pdb.set_trace()
        for cut in cuts:
            gen_tran = []
            cut_dict = get_cut_dict(cut)
            for item in tran:
                try:
                    gen_tran.append(cut_dict[item])
                except:
                    gen_tran.append(item)
            gen_tran = list(set(gen_tran))
            gen_tran.sort(cmp=tran_cmp, reverse=True)
            vtemp = ';'.join(gen_tran)
            if COUNT_DICT[vtemp].support >= k:
                if __DEBUG:
                    print "tran", tran
                    print "cut", cut
                return cut_dict
    # Well, Terrovitis don't metion this sitituation. I suggest suppress them.
    # print "Error: Can not find cut for %s" % tran
    return get_cut_dict(['*'])


def R_DA(ctree, cut, k=25, m=2):
    """
    Re-useable DA, compute cut on ctree.
    """
    ctree_traversal = []
    ctree.dfs_traversal(ctree_traversal)
    # delete_list = dict()
    for index, ctree_key in enumerate(ctree_traversal):
        current_ctree = COUNT_DICT[ctree_key]
        # if len(delete_list) > 0:
        #     pdb.set_trace()
        # try:
        #     delete_list[ctree_key]
        #     continue
        # except KeyError:
        #     pass
        if current_ctree.support == 0 or len(current_ctree.child) > 0:
            continue
        try:
            cut[current_ctree.value]
            continue
        except KeyError:
            pass
        if current_ctree.support < k:
            new_cut = get_cut(current_ctree, k)
            merge_cut(cut, new_cut)
            # backtrack to longest prefix of path J, where in no item
            # has been generalized in Cut
            # J = current_ctree.prefix[:]
            # need_gen = [current_ctree.value]
            # longest_prefix = []
            # for item in J:
            #     try:
            #         cut[item]
            #         continue
            #     except KeyError:
            #         longest_prefix.append(item)
            # if len(longest_prefix) > 0:
            #     # pdb.set_trace()
            #     for pos in range(index + 1, len(ctree_traversal)):
            #         temp = ctree_traversal_dict[ctree_traversal[pos]]
            #         if longest_prefix == temp.prefix:
            #             break
            #     for i in range(index + 1, pos):
            #         delete_list[ctree_traversal[i]] = 1
    # return cut


def DA(trans, k=10, m=170):
    """
    Direct anonymization for transaction anonymization.
    Developed by Manolis Terrovitis
    """
    cut = dict()
    ctree = create_count_tree(trans, m)
    R_DA(ctree, cut, k, m)
    # pdb.set_trace()
    return cut


def AA(trans, k=10, m=4):
    """
    Apriori-based anonymization for transaction anonymization.
    Developed by Manolis Terrovitis
    """
    cut = dict()
    # Codes below are slightly different from Manolis's pseudocode
    # I confirmed with Manolis that it's actual implement for AA.
    # The pseudocode in paper is not abstracted carefully.
    ctree = init_count_tree()
    for i in range(1, m + 1):
        for tran in trans:
            ex_t = expand_tran(tran, cut)
            insert_to_ctree(ex_t, i)
        # run DA
        R_DA(ctree, cut, k, i)
        # pdb.set_trace()
    return cut


def init(att_tree, data):
    global ATT_TREE, ELEMENT_NUM, LEAF_NUM, COUNT_DICT, NOT_OVERLAP
    NOT_OVERLAP = {}
    ELEMENT_NUM = 0
    COUNT_DICT = {}
    ATT_TREE = att_tree
    LEAF_NUM = len(ATT_TREE['*'])
    for tran in data:
        ELEMENT_NUM += len(tran)
    init_gl_count_tree()


def apriori_based_anon(att_tree, trans, type_alg='AA', k=10, m=4):
    """
    main function of apriori_based_anon
    att_tree: generalizaiton hierarchies in [dict, dict, ...] format
    type_alg: DA: Direct Anon, AA: Apriori based Anon

    """
    # AA is not correct
    init(att_tree, trans)
    start_time = time.time()
    if type_alg == 'DA' or type_alg == 'da':
        cut = DA(trans, k, m)
    else:
        cut = AA(trans, k, m)
    rtime = float(time.time() - start_time)
    result = []
    ncp = 0.0
    for tran in trans:
        gen_tran = []
        rncp = 0.0
        for item in tran:
            try:
                gen_tran.append(cut[item])
                rncp += 1.0 * len(ATT_TREE[cut[item]]) / LEAF_NUM
            except KeyError:
                gen_tran.append(item)
        gen_tran = list(set(gen_tran))
        result.append(gen_tran)
        ncp += rncp
    ncp /= ELEMENT_NUM
    ncp *= 100
    if __DEBUG:
        list_cut = list(set(cut.values()))
        list_cut.sort(cmp=tran_cmp, reverse=True)
        print "Final Cut", list_cut
    return (result, (ncp, rtime, cut))
