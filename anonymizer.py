#!/usr/bin/env python
#coding=utf-8

from generalization import GenTree, CountTree
from datetime import datetime
from random import randrange
import pdb
import sys
from ftp_upload import ftpupload
import socket
from itertools import permutations, combinations
# from pylab import *



# Poulis set k=25, m=2 as default!
__DEBUG = False
gl_threshold = 100000
gl_useratt = ['DUID','PID','DUPERSID','DOBMM','DOBYY','SEX','RACEX','RACEAX','RACEBX','RACEWX','RACETHNX','HISPANX','HISPCAT','EDUCYEAR','Year','marry','income','poverty']
gl_conditionatt = ['DUID','DUPERSID','ICD9CODX','year']
gl_att_name = []
gl_att_QI = 7
gl_attlist = [3,4,5,6,13,15,16]
# att_tree store root node for each att
gl_att_tree = []
# databack store all reacord for dataset
gl_databack = []
# store data for python plot
gl_plotdata = [[],[],[]]
gl_treecover = []
# store coverage of each att according to  dataset
gl_att_cover = [[],[],[],[],[],[],[],[]]
# count tree root
gl_count_tree = []


def tran_cmp(node1, node2):
    """Compare node1 (str) and node2 (str)"""
    support1 = gl_att_tree[-1][node1].support
    support2 = gl_att_tree[-1][node2].support
    if support1 != support2:
        return support1 - support2
    else:
        return (node1 > node2)


def cut_cmp(cut1, cut2):
    """Compare cut1 (list) and cut2 (list)
    """
    support1 = 0
    support2 = 0
    for t in cut1:
        support1 += gl_att_tree[-1][t].support
    for t in cut2:
        support2 += gl_att_tree[-1][t].support
    if support1 != support2:
        return support1 - support2
    else:
        return (node1 > node2)    


def expand_tran(tran, cut=None):
    """expand transaction according to generalization cut
    """
    ex_tran = tran[:]
    # extend t with all parents
    for temp in tran:
        for t in gl_att_tree[-1][temp].parent:
            if not t.value in ex_tran: 
                ex_tran.append(t.value)
    ex_tran.remove('*')
    # sort ex_tran
    ex_tran.sort(cmp=tran_cmp, reverse=True)
    """if __DEBUG:
        print ex_tran
    """
    if cut:
        for temp in ex_tran:
            ancestor = [parent.value for parent in gl_att_tree[-1][temp].parent]
            for t in cut:
                if t in ancestor:
                    ex_tran.remove(temp)
    return ex_tran


def init_count_tree():
    """initialize a new cout tree
    """
    # initialize count tree
    ctree = CountTree('*')
    for t in gl_count_tree:
        CountTree(t, ctree)
    return ctree


def check_overlap(tran):
    """Check if items can joined with each other
    """
    len_tran = len(tran)
    for i in range(len_tran):
        for j in range(len_tran):
            if i == j:
                continue
            ancestor = [parent.value for parent in gl_att_tree[-1][tran[j]].parent]
            if tran[i] in ancestor:
                return False
    return True


def check_cover(tran, cut):
    """Check if tran if covered by cut
    return True if covered, False if not
    """
    if len(cut) == 0:
        return False

    for temp in tran:
        ancestor = [parent.value for parent in gl_att_tree[-1][temp].parent]
        for t in cut:
            if t in ancestor:
                break
        else:
            return True
    return False


def create_count_tree(trans, m):
    """Creat a count_tree
    """
    ctree = init_count_tree()
    # extend t and insert to count tree
    for temp in trans:
        ex_t = expand_tran(t)
        for i in range(1, m+1):
            temp = permutations(ex_t, i)
            # convet tuple to list
            temp = [list(combination) for combination in temp]
            for t in temp:
                if check_overlap(t):
                    t.sort(cmp=tran_cmp, reverse=True)
                    ctree.add_to_tree(t)
    return ctree


def get_cut(tran, ctree, k):
    """Given a tran, return cut making it k-anonymity with mini information
    return cut is a list e.g. ['A', 'B']
    """
    ancestor = []
    cut = []
    # get all ancestors
    for t in tran:
        parents = gl_att_tree[-1][t].parent[:]
        parents.append(gl_att_tree[-1][t])
        for p in parents:
            if not p.value in ancestor:
                ancestor.append(p.value)
    ancestor.remove('*')
    # generate all possible cut for tran
    len_ance = len(ancestor)
    for i in range(1, len_ance+1):
        temp = permutations(ancestor, i)
        # convet tuple to list
        temp = [list(combination) for combination in temp]
        # remove combination with overlap
        for t in temp:
            if check_overlap(t) == False:
                del t
            elif len(t):
                cut.append(t)
    # remove cut cannot cover tran
    for t in cut:
        if check_cover(tran, t):
            del t
    # sort by support, the same effect as sorting by NCP
    # pdb.set_trace()
    cut.sort(cmp=cut_cmp)
    if __DEBUG:
        print cut
    # return 
    for t in cut:
        if t >= k:
            return t


def merge_cut(cut, new_cut):
    for t in new_cut:
        if not t in cut:
            cut.append(t)
    # merge coverd and overlaped
    cut.sort(cmp=tran_cmp, reverse=True)
    delete_list = []
    len_cut = len(cut)
    for i in range(len_cut):
        temp = cut[i]
        check_list = []
        for j in range(i, len_cut):
            t = cut[j]
            ancestor = [parent.value for parent in gl_att_tree[-1][t].parent]
            if temp in ancestor:
                check_list.append(t)
        child_list = [child.value for child in gl_att_tree[-1][temp].child]
        for c in child_list:
            if not c in check_list:
                delete_list.extend(check_list)
                break
        else:
            delete_list.append(temp)
    delete_list = list(set(delete_list))
    for t in delete_list:
        cut.remove(t)
    return cut


def R_DA(ctree, cut, k=25, m=2):
    """Recursively get cut. Each branch can be paralleled
    """
    # pdb.set_trace()
    if ctree.level > 0 and check_cover([ctree.value], cut):
        return []
    if len(ctree.child):
        for temp in ctree.child:
            new_cut = R_DA(temp, cut, k, m)
            merge_cut(cut, new_cut)
    elif ctree.level >= 1 and ctree.support < k:
        tran = ctree.prefix[:]
        tran.append(ctree.value)
        return get_cut(tran, ctree, k)
    return cut


def DA(trans, k=25, m=2):
    """Direct anonymization for transaction anonymization.
    Developed by Manolis Terrovitis
    """
    cut_cover = {}
    ctree = create_count_tree(trans, m)
    if __DEBUG:
        print "Cut Tree"
        ctree.print_tree
    cut = []
    R_DA(ctree, cut, k, m)
    return gl_cut[:]


def AA(trans, k=25, m=2):
    """Apriori-based anonymization for transaction anonymization. 
    Developed by Manolis Terrovitis
    """
    cut = []
    for i in range(1, m+1):
        ctree = init_count_tree()
        for t in trans:
            ex_t = expand_tran(t, cut)
            temp = permutations(ex_t, i)
            # convet tuple to list
            temp = [list(t) for t in temp]
            for t in temp:
                if check_overlap(t):
                    t.sort(cmp=tran_cmp, reverse=True)
                    ctree.add_to_tree(t)
        # run DA
        new_cut = R_DA(ctree, cut, k, i)
        merge_cut(cut, new_cut)
    return cut


def trans_gen(tran, cut):
    return

# read files    
def read_tree_file(treename):
    """read tree data from treename"""
    global gl_treecover
    global gl_att_tree

    treecover = 0
    leaf_to_path = {}
    nodelist = {}
    prefix = 'data/treefile_'
    postfix = ".txt"
    treefile = open(prefix + treename + postfix,'rU')
    nodelist['*'] = GenTree('*')
    if __DEBUG:
        print "Reading Tree" + treename
    for line in treefile:
        #delete \n
        if len(line) <= 1:
            break
        line = line.strip()
        temp = line.split(';')
        # copy temp
        temp.reverse()
        for i, t in enumerate(temp):
            if not t in nodelist:
                # always satisfy 
                nodelist[t] = GenTree(t, nodelist[temp[i - 1]])
    treecover = nodelist['*'].compute_support()
    if __DEBUG:
        print "Nodes No. = %d" % treecover
    gl_treecover.append(treecover)
    gl_att_tree.append(nodelist)
    treefile.close()


def readtree():
    """read tree from data/tree_*.txt, store them in gl_att_tree"""
    global gl_att_name, gl_count_tree
    print "Reading Tree"
    for t in gl_attlist:
        gl_att_name.append(gl_useratt[t])
    gl_att_name.append(gl_conditionatt[2])
    for t in gl_att_name:
        read_tree_file(t)
    # creat count tree
    gl_count_tree = []
    for k, v in gl_att_tree[-1].iteritems():
        gl_count_tree.append(k)
    # delete *, and sort reverse
    gl_count_tree.remove('*')
    gl_count_tree.sort(cmp=tran_cmp, reverse=True)
    if __DEBUG:
        print gl_count_tree


def readdata():
    """read microda for *.txt and store them in gl_databack"""
    global gl_databack
    global gl_att_cover
    global gl_useratt
    global gl_conditionatt
    userfile = open('data/demographics05test.csv', 'rU')
    conditionfile = open('data/conditions05.csv', 'rU')
    userdata = {}
    # We selet 3,4,5,6,13,15,15 att from demographics05, and 2 from condition05
    print "Reading Data..."
    for i, line in enumerate(userfile):
        line = line.strip()
        # ignore first line of csv
        if i == 0:
            continue
        row = line.split(',')
        row[2] = row[2][1:-1]
        if row[2] in userdata:
            userdata[row[2]].append(row)
        else:
            userdata[row[2]] = row
    conditiondata = {}
    for i, line in enumerate(conditionfile):
        line = line[:-2]
        # ignore first line of csv
        if i == 0:
            continue
        row = line.split(',')
        row[1] = row[1][1:-1]
        row[2] = row[2][1:-1]
        if row[1] in conditiondata:
            conditiondata[row[1]].append(row)
        else:
            conditiondata[row[1]] = [row]
    hashdata = {}
    for k, v in userdata.iteritems():
        if k in conditiondata:
            temp = []
            for t in conditiondata[k]:
                temp.append(t[2])
                if not t[2] in gl_att_cover[7]:
                    gl_att_cover[7].append(t[2])
            hashdata[k] = []
            for i in range(len(gl_attlist)):
                index = gl_attlist[i]
                hashdata[k].append(v[index])
                if not v[index] in gl_att_cover[i]:
                    gl_att_cover[i].append(v[index])
            hashdata[k].append(temp)
    for k, v in hashdata.iteritems():
        gl_databack.append(v)
    # pdb.set_trace()
    # num_analysis([t[6] for t in gl_databack[:]])
    userfile.close()
    conditionfile.close()


if __name__ == '__main__':
    #read gentree tax
    readtree()
    #read record
    readdata()
    cut = AA([row[-1] for row in gl_databack[:]])
    print "Final Cut"
    print cut

    # pdb.set_trace()
    #AA()
    print "Finish RT-Anon based on RMERGE_T\n"
    print "Finish RT-Anonymization!!"
