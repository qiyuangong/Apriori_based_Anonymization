#!/usr/bin/env python
#coding=utf-8

# Read data and read tree fuctions for INFORMS data
# user att ['DUID','PID','DUPERSID','DOBMM','DOBYY','SEX','RACEX','RACEAX','RACEBX','RACEWX','RACETHNX','HISPANX','HISPCAT','EDUCYEAR','Year','marry','income','poverty']
# condition att ['DUID','DUPERSID','ICD9CODX','year']

from generalization import GenTree


__DEBUG = False


def read_tree(flag=0):
    """read tree from data/tree_*.txt, store them in att_tree
    """
    print "Reading Tree"
    if flag:
        return read_tree_file('ICD9CODX')
    else:
        return read_tree_file('even')

  
def read_tree_file(treename):
    """read tree data from treename
    """
    leaf_to_path = {}
    att_tree = {}
    prefix = 'data/treefile_'
    postfix = ".txt"
    treefile = open(prefix + treename + postfix,'rU')
    att_tree['*'] = GenTree('*')
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
            if not t in att_tree:
                # always satisfy 
                att_tree[t] = GenTree(t, att_tree[temp[i - 1]])
    if __DEBUG:
        print "Nodes No. = %d" % att_tree['*'].support
    treefile.close()
    return att_tree


def read_data():
    """read microda for *.txt and return read data
    """
    data = []
    conditionfile = open('data/conditions05.csv', 'rU')
    print "Reading Data..."
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
            conditiondata[row[1]].append(row[2])
        else:
            conditiondata[row[1]] = [row[2]]
    conditionfile.close()
    return conditiondata.values()
