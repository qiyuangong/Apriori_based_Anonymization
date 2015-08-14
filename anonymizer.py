"""
run DA and AA with given parameters
"""

# !/usr/bin/env python
# coding=utf-8
from Apriori_based_Anon import AA, DA, trans_gen
from utils.read_data import read_data, read_tree
from utils.evaluation import average_relative_error
from utils.save_result import save_to_file
import sys
# Poulis set k=25, m=2 as default!

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        FLAG = True
    elif sys.argv[1] == 'DA':
        FLAG = False
    else:
        FLAG = True
    # read gentree tax
    ATT_TREES = read_tree()
    # read record
    DATA = read_data()
    # remove duplicate items
    for i in range(len(DATA)):
        DATA[i] = list(set(DATA[i]))
    if FLAG:
        print "Begin AA"
        CUT = AA(ATT_TREES, DATA)
    else:
        print "Begin DA"
        CUT = DA(ATT_TREES, DATA)
    print "Final Cut"
    print CUT
    result = trans_gen(DATA, CUT)
    # save_to_file(result)
    print "Finish T-Anonymization!!"
    print "Begin Evaluation"
    are = average_relative_error(ATT_TREES, DATA, result)
    print "Average Relative Error: %.2f" % are
