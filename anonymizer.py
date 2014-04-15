#!/usr/bin/env python
#coding=utf-8
from Apriori_based_Anon import AA, DA, trans_gen
from read_data import read_data, read_tree
# Poulis set k=25, m=2 as default!

if __name__ == '__main__':
    #read gentree tax
    att_tree = read_tree()
    #read record
    trans = read_data()
    # remove duplicate items
    for i in range(len(trans)):
        trans[i] = list(set(trans[i]))
    cut = DA(att_tree, trans)
    # cut = AA(att_tree[-1], trans)
    print "Final Cut"
    print cut
    result = trans_gen(trans, cut)
    print "Finish T-Anonymization!!"
