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


def count_query(data, att_select, value_select):
    "input query att_select and value_select,return count()"
    count = 0
    lenquery = len(att_select)
    for temp in data:
        for i in range(lenquery):
            index = att_select[i]
            # value(list) and temp[index](value)
            value = value_select[i]
            if index != 7:
                if not temp[index] in value:
                    break
            else:
                # gen value
                flag = False
                for t in value:
                    if t in temp[index]:
                        flag = True
                if not flag:
                    break
        else:
            count += 1
    return count


def trans_to_cover(trans, att_tree):
    """Convert generated transactions to transaction cover 
    """
    c_trans = []
    for tran in trans:
        temp = []
        for t in tran:
            if len(att_tree[t].child) > 0:
                temp.extend(att_tree[t].cover)
            else:
                temp.append(t)
        c_trans.append(temp)


def average_relative_error(data, result, qd=2, s=5):
    "return average relative error of anonmized microdata,qd denote the query dimensionality, b denot seleciton of query"
    global att_cover
    are = 0.0
    lenresult = len(result)
    transform_result = []
    blist = []
    seed = math.pow(s*1.0/100, 1.0/(qd +1))
    for i in range(8):
        blist.append(math.ceil(len(att_cover[i]) * seed))
    for i in range(lenresult):
        temp = anatomy_transform(result[i])



        # pdb.set_trace()
        transform_result.extend(temp)

    num = 100
    zeroare = 0
    # pdb.set_trace()
    for turn in range(num):
        att_select = []
        value_select = []
        i = 0 
        while i < qd:
            t = random.randint(0,6)
            if t not in att_select:
                att_select.append(t)
            else:
                i -= 1
            i += 1
        att_select.append(7)
        lenquery = len(att_select)
        
        # pdb.set_trace()
        for i in range(lenquery):
            index = att_select[i]
            temp = []
            count = 0
            while count < blist[index]:
                t = random.choice(att_cover[index])
                if t not in temp:
                    temp.append(t)
                else:
                    count -= 1
                count += 1
            value_select.append(temp)
        acout = count_query(data, att_select, value_select)
        rcout = count_query(transform_result, att_select, value_select)
        if acout != 0:
            are += abs(acout - rcout) * 1.0 / acout
        else:
            zeroare += 0 
    print "Times=%d when Query on microdata is Zero" % zeroare
    if num == zeroare:
        return 0            
    return are / (num - zeroare)


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
