#!/usr/bin/env python
#coding=utf-8
from Apriori_based_Anon import AA, DA, trans_gen
from read_data import read_data, read_tree
from evaluation import average_relative_error
from save_result import save_to_file
import sys
# Poulis set k=25, m=2 as default!

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        flag = True
    elif sys.argv[1] == 'DA':
        flag = False
    else:
        flag = True
    #read gentree tax
    att_tree = read_tree()
    #read record
    trans = read_data()
    # remove duplicate items
    for i in range(len(trans)):
        trans[i] = list(set(trans[i]))
    if flag:
        print "Begin AA"
        cut = AA(att_tree, trans)
    else:
        print "Begin DA"
        cut = DA(att_tree, trans)
    # cut = AA(att_tree[-1], trans)
    print "Final Cut"
    print cut
    result = trans_gen(trans, cut)
    save_to_file(result)
    print "Finish T-Anonymization!!"
    print "Begin Evaluation"
    are = average_relative_error(att_tree, trans, result)
    print "Average Relative Error: %.2f" % are
