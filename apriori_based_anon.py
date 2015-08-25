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
ATT_TREE = {}
# count tree root
COUNT_TREE = []
ELEMENT_NUM = 0
LEAF_NUM = 0


def tran_cmp(node1, node2):
    """Compare node1 (str) and node2 (str)
    Compare two nodes according to their support
    """
    support1 = ATT_TREE[node1].leaf_num
    support2 = ATT_TREE[node2].leaf_num
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
    for item in cut1:
        support1 += ATT_TREE[item].leaf_num
    for item in cut2:
        support2 += ATT_TREE[item].leaf_num
    if support1 != support2:
        return cmp(support1, support2)
    else:
        return cmp(cut1, cut2)


def expand_tran(tran, cut=None):
    """expand transaction according to generalization cut
    """
    ex_tran = tran[:]
    # extend item with all parents
    for temp in tran:
        # remove '*', which is tail of parent
        for item in ATT_TREE[temp].parent[:-1]:
            ex_tran.append(item.value)
    ex_tran = list(set(ex_tran))
    # ex_tran.remove('*')
    # sort ex_tran
    ex_tran.sort(cmp=tran_cmp, reverse=True)
    if __DEBUG:
        print "tran %s " % tran
        print "ex_tran %s" % ex_tran
    if cut:
        check_result = []
        for temp in ex_tran:
            try:
                cut[temp]
            except:
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
    ctree = CountTree('*')
    # just make root ctree has a none zero support
    ctree.support = ELEMENT_NUM
    for item in COUNT_TREE:
        CountTree(item, ctree)
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
    if isinstance(cut, dict):
        for temp in tran:
            try:
                cut[temp]
            except:
                return False
        return True
    else:
        for temp in tran:
            ancestor = [parent.value for parent in ATT_TREE[temp].parent]
            ancestor.append(temp)
            for item in cut:
                if item in set(ancestor):
                    break
            else:
                return False
        return True


def merge_cut(cut, new_cut):
    """Merge new_cut to cut to form a stronger cut
    return cut cover both of them
    """
    if new_cut is None or len(new_cut) == 0:
        return
    # merge coverd and overlaped
    for item in new_cut.keys():
        try:
            if ATT_TREE[cut[item]].leaf_num < ATT_TREE[new_cut[item]].leaf_num:
                cut[item] = new_cut[item]
        except KeyError:
            cut[item] = new_cut[item]
    return


def create_count_tree(trans, m):
    """Creat a count_tree for DA
    """
    ctree = init_count_tree()
    # extend item and insert to count tree
    for tran in trans:
        ex_t = expand_tran(tran)
        for i in range(1, m + 1):
            temp = combinations(ex_t, i)
            # convet tuple to list
            temp = [list(combination) for combination in temp]
            for item in temp:
                if not check_overlap(item) and len(item):
                    item.sort(cmp=tran_cmp, reverse=True)
                    ctree.add_to_tree(item)
    return ctree


def get_cut(ctree, k):
    """Given a tran, return cut making it k-anonymity with mini information
    return cut is a list e.g. ['A', 'B']
    """
    ancestor = []
    cuts = []
    c_root = ctree.parent[-1]
    tran = ctree.prefix[:]
    tran.append(ctree.value)
    # get all ancestors
    for item in tran:
        parents = ATT_TREE[item].parent[:-1]
        parents.insert(0, ATT_TREE[item])
        for parent in parents:
            ancestor.append(parent.value)
    ancestor = list(set(ancestor))
    # ancestor.remove('*')
    # generate all possible cuts for tran
    len_ance = len(ancestor)
    for i in range(1, len_ance + 1):
        temp = combinations(ancestor, i)
        # convet tuple to list
        temp = [list(combination) for combination in temp]
        # remove combination with overlap
        for item in temp:
            if not check_overlap(item) and len(item):
                cuts.append(item)
    # remove cuts cannot cover tran
    cuts = [cut for cut in cuts if check_cover(tran, cut)]
    # sort by support, the same effect as sorting by NCP
    for cut in cuts:
        cut.sort(cmp=tran_cmp, reverse=True)
    cuts.sort(cmp=cut_cmp)
    # return
    for cut in cuts:
        if c_root.node(cut).support >= k:
            if __DEBUG:
                print "tran", tran
                print "cut", cut
            dict_cut = dict()
            for item in cut:
                cover_list = ATT_TREE[item].cover.keys()
                for cover_value in cover_list:
                    try:
                        dict_cut[cover_value]
                        pdb.set_trace()
                    except:
                        dict_cut[cover_value] = item
            return dict_cut
    # Well, Terrovitis don't metion this sitituation. I suggest suppress them.
    # print "Error: Can not find cut for %s" % tran
    dict_cut = {}
    cover_list = ATT_TREE['*'].cover.keys()
    for cover_value in cover_list:
        try:
            dict_cut[cover_value]
            pdb.set_trace()
        except:
            dict_cut[cover_value] = item
    return dict_cut


def R_DA(ctree, cut, k=25, m=2):
    """
    Recursively get cut. Each branch can be paralleled
    """
    ctree_traversal, ctree_traversal_dict = ctree.dfs_traversal()
    # delete_list = dict()
    for index, ctree_key in enumerate(ctree_traversal):
        current_ctree = ctree_traversal_dict[ctree_key]
        # if len(delete_list) > 0:
        #     pdb.set_trace()
        # try:
        #     delete_list[ctree_key]
        #     continue
        # except KeyError:
        #     pass
        if current_ctree.support == 0:
            continue
        if check_cover([current_ctree.value], cut):
            continue
        if current_ctree.support < k:
            new_cut = get_cut(current_ctree, k)
            merge_cut(cut, new_cut)
            # backtrack to longest prefix of path J, where in no item
            # has been generalized in Cut
            # J = ctree_traversal_dict[ctree_key].prefix[:]
            # J.append(ctree_traversal_dict[ctree_key].value)
            # longest_prefix = []
            # for i in range(len(J)):
            #     if check_cover(J[:-1 - i], cut):
            #         continue
            #     else:
            #         longest_prefix = J[:-1 - i]
            #         break
            # if len(longest_prefix) > 0:
            #     pdb.set_trace()
            #     for pos in range(index + 1, len(ctree_traversal)):
            #         temp = ctree_traversal_dict[ctree_traversal[pos]]
            #         if longest_prefix == temp.prefix:
            #             break
            #     for i in range(index + 1, pos):
            #         delete_list[ctree_traversal[i]] = 1
    return cut


def DA(trans, k=25, m=2):
    """
    Direct anonymization for transaction anonymization.
    Developed by Manolis Terrovitis
    """
    cut = dict()
    ctree = create_count_tree(trans, m)
    if __DEBUG:
        print "Cut Tree"
    R_DA(ctree, cut, k, m)
    # pdb.set_trace()
    return cut


def OLD_R_DA(trans, k=25, m=2):
    """
    Recursively get cut. Each branch can be paralleled
    """
    cut = dict()
    if ctree.level > 0 and check_cover([ctree.value], cut):
        return {}
    if len(ctree.child):
        # not leaf node of count tree
        for temp in ctree.child:
            new_cut = R_DA(temp, cut, k, m)
            merge_cut(cut, new_cut)
    elif ctree.support < k and ctree.support > 0:
        # leaf node of count tree, and the support is less than k
        new_cut = get_cut(ctree, k)
        merge_cut(cut, new_cut)
    else:
        return {}
    return cut


def AA(trans, k=25, m=2):
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
        for t in trans:
            ex_t = expand_tran(t, cut)
            temp = combinations(ex_t, i)
            # convet tuple to list
            temp = [list(t) for t in temp]
            for t in temp:
                if not check_overlap(t) and len(t):
                    t.sort(cmp=tran_cmp, reverse=True)
                    ctree.add_to_tree(t)
        # pdb.set_trace()
        # run DA
        R_DA(ctree, cut, k, i)
    return cut


def init(att_tree, data):
    global ATT_TREE, ELEMENT_NUM, LEAF_NUM
    ELEMENT_NUM = 0
    ATT_TREE = att_tree
    LEAF_NUM = ATT_TREE['*'].leaf_num
    for tran in data:
        ELEMENT_NUM += len(tran)
    init_gl_count_tree()


def apriori_based_anon(att_tree, trans, type_alg='AA', k=25, m=2):
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
    elif type_alg == 'AA' or type_alg == 'aa':
        cut = AA(trans, k, m)
    else:
        cut = OLD_DA(trans, k, m)
    rtime = float(time.time() - start_time)
    result = []
    ncp = 0.0
    for tran in trans:
        gen_tran = []
        rncp = 0.0
        for item in tran:
            try:
                gen_tran.append(cut[item])
                rncp += 1.0 * ATT_TREE[cut[item]].leaf_num / LEAF_NUM
            except:
                gen_tran.append(item)
        result.append(gen_tran)
        ncp += rncp
    ncp /= ELEMENT_NUM
    ncp *= 100
    # if __DEBUG:
    list_cut = list(set(cut.values()))
    list_cut.sort(cmp=tran_cmp, reverse=True)
    print "Final Cut", list_cut
    # pdb.set_trace()
    return (result, (ncp, rtime))
