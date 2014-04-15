# from pylab import *
import pdb
import math
import random


_DEBUG = True

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



def gen_to_cover(att_trees, result):
    """
    Transform generlized result set to coverage result set
    """
    gen_cover = []
    for t in result:
        temp = []
        for i in range(len(t)):
            temp.append(get_cover(att_trees[i], t[i]))
        gen_cover.append(temp)
    return gen_cover


def count_query(data, att_select, value_select):
    "input query att_select and value_select,return count()"
    count = 0
    lenquery = len(att_select)
    for record in data:
        for i in range(lenquery):
            index = att_select[i]
            value = value_select[i]
            flag = False
            for t in value:
                if t in record[index]:
                    flag = True
                    break
            if not flag:
                break
        else:
            count += 1
    return count


def average_relative_error(att_trees, data, result, qd=2, s=0.5):
    "return average relative error of anonmized microdata,qd denote the query dimensionality, b denot seleciton of query"
    are = 0.0
    len_att = len(att_trees)
    blist = []
    att_roots = [t['*'] for t in att_trees]
    att_cover = []
    seed = math.pow(s*1.0/100, 1.0/(qd +1))
    # transform generalized result to coverage
    tran_result = gen_to_cover(att_trees, result)
    # compute b for each attributes
    for i in range(len_att):
        blist.append(int(math.ceil(att_roots[i].support * seed)))
    if _DEBUG:
        print "blist %s" % blist
    # query times, normally it's 1000
    q_times = 10
    zeroare = 0
    for i in range(len_att):
        att_cover.append(att_roots[i].cover.keys())
    pdb.set_trace()
    for turn in range(q_times):
        att_select = []
        value_select = []
        i = 0
        # select QI att
        att_select = random.sample(range(0, len_att-1), qd)
        # append SA. So len(att_select) == qd+1
        att_select.append(len_att-1)
        if _DEBUG:
            print "ARE %d" % turn
            print "Att select %s" % att_select
        for i in range(qd+1):
            index = att_select[i]
            temp = []
            count = 0
            temp = random.sample(att_cover[index], blist[index])
            value_select.append(temp)
        acout = count_query(data, att_select, value_select)
        rcout = count_query(tran_result, att_select, value_select)
        if acout != 0:
            are += abs(acout - rcout) * 1.0 / acout
        else:
            zeroare += 1 
    print "Times = %d when Query on microdata is Zero" % zeroare
    if q_times == zeroare:
        return 0            
    return are / (q_times - zeroare)


def num_analysis(attlist):
    """plot distribution of attlist"""
    import operator
    temp = {}
    for t in attlist:
        t = int(t)
        if not t in temp.keys():
            temp[t] = 1
        else:
            temp[t] += 1
    # sort the dict
    items = temp.items()
    items.sort()
    value = []
    count = []
    for k, v  in items:
        value.append(k)
        count.append(v)
    # pdb.set_trace()
    xlabel('value')
    ylabel('count')
    plt.hist(count, bins=value, normed=1, histtype='step', rwidth=0.8)
    # legend(loc='upper left')
    # grid on
    grid(True)
    show()
