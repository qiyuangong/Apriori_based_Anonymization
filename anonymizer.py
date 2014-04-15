#!/usr/bin/env python
#coding=utf-8
from Apriori_based_Anon import Apriori_based_Anon
from read_data import read_data, read_tree
# Poulis set k=25, m=2 as default!

if __name__ == '__main__':
    #read gentree tax
    att_tree = read_tree()
    #read record
    trans = read_data()
    # init AA
    aa = Apriori_based_Anon(att_tree)
    # remove duplicate items
    for i in range(len(trans)):
        trans[i] = list(set(trans[i]))
    # cut = aa.DA(trans)
    cut = aa.AA(trans[:])
    print "Final Cut"
    print cut
    result = aa.trans_gen(trans, cut)
    print "Finish T-Anonymization!!"
