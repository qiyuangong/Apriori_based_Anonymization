# from pylab import *
import pdb
import math
import random


_DEBUG = False

def NCP(gen_tran, att_tree):
    """Compute NCP (Normalized Certainty Penalty) 
    when generate record to middle.
    """
    ncp = 0.0
    # exclude SA values(last one type [])
    for i in range(len(gen_tran) - 1):
        # if support of numerator is 1, then NCP is 0
        if att_tree[gen_tran[i]].support == 1:
            continue
        ncp +=  att_tree[gen_tran[i]].support * 1.0 / att_tree['*'].support
    return ncp


def get_cover(att_tree, node):
    """
    Transform generlized value to coverage( list)
    """
    if not isinstance(node, list):
        return att_tree[node].cover
    cover = []
    for t in node:
        cover.extend(get_cover(att_tree, t))
    return cover


def gen_to_cover(att_tree, result):
    """
    Transform generlized result set to coverage result set
    """
    gen_cover = []
    for record in result:
        temp = []
        for t in record:
            temp.extend(get_cover(att_tree, t))
        temp = list(set(temp))
        gen_cover.append(temp)
    return gen_cover


def count_query(data, value_select):
    "input query att_select and value_select,return count()"
    count = 0
    for record in data:
        for t in value_select:
            if t in record:
                break  
        else:
            count -= 1
        count += 1
    return count


def average_relative_error(att_tree, data, result, qd=2, s=0.5):
    "return average relative error of anonmized microdata,qd denote the query dimensionality, b denot seleciton of query"
    are = 0.0
    b = 0
    att_cover = att_tree['*'].cover.keys()
    seed = math.pow(s*1.0/100, 1.0/(qd +1))
    # transform generalized result to coverage
    tran_result = gen_to_cover(att_tree, result)
    # compute b 
    b = int(math.ceil(att_tree['*'].support * seed))
    if _DEBUG:
        print "b %d" % b
    # query times, normally it's 1000
    q_times = 100
    zeroare = 0
    for turn in range(q_times):
        value_select = []
        if _DEBUG:
            print "ARE %d" % turn
        value_select = random.sample(att_cover, b)
        acout = count_query(data, value_select)
        rcout = count_query(tran_result, value_select)
        if acout != 0:
            are += abs(acout - rcout) * 1.0 / acout
        else:
            zeroare += 1 
    print "Times = %d when Query on microdata is Zero" % zeroare
    if q_times == zeroare:
        return 0            
    return are / (q_times - zeroare)


