#!/usr/bin/env python
#coding=utf-8
import string

#generate tree from treeseed
def gen_ICD9CODX_tree():
    "disease tree is more complex, so we need treeseed to simplify definition"
    treeseed = open('data/treeseed_disease.txt','rU')
    treefile = open('data/treefile_disease.txt','w')

    for line in treeseed:
        # get low bound tree leaf
        title = '' 
        temp = line.split(';')
        #separate special value
        if temp[0][0] != 'E' and temp[0][0] != 'V':
            now = string.atoi(temp[0])
            bottom = string.atoi(temp[1].split(',')[0])
            top = string.atoi(temp[1].split(',')[1])
            if now > bottom:
                treefile.write(line)
                continue    
            index = line.find(';')
            while bottom <= top:
                stemp = str(bottom)
                if bottom < 100 and bottom >= 0:
                    stemp = '0' + stemp
                if bottom < 10 and bottom >= 0:
                    stemp = '0' + stemp
                treefile.write(stemp + line[index:])
                bottom = bottom + 1
        else:
            title = temp[0][0]
            now = string.atoi(temp[0][1:])
            bottom = string.atoi(temp[1].split(',')[0][1:])
            top = string.atoi(temp[1].split(',')[1][1:])
            if now > bottom:
                treefile.write(line)
                continue    
            index = line.find(';')
            while bottom <= top:
                stemp = str(bottom)
                if bottom < 10:
                    stemp = '0' + stemp
                treefile.write(title + stemp + line[index:])
                bottom = bottom + 1
    treeseed.close()
    treefile.close()

def gen_income_tree():
    "We split this tree by i,100,1000,10000,*(5 layers) min = -40 000, max = 200 000"
    treefile = open('data/treefile_income.txt','w')
    for i in range(-40000, 200001):
        i1 = i / 100
        i2 = i / 1000
        i3 = i / 10000
        temp = '%d;%d,%d;%d,%d;%d,%d;*\n' % (i, i1 * 100 , i1 * 100 + 99, i2*1000,\
         i2*1000 + 999, i3*10000, i3*10000 + 9999)
        treefile.write(temp)
    treefile.close()
    return

def gen_DOBYY_tree():
    "We define a birth year tree with min = 1900 and max = 2010, and coverage splited by 5, 10, 50 year"
    treefile = open('data/treefile_DOBYY.txt','w')
    for i in range(1900, 2011):
        i1 = i / 5
        i2 = i / 10
        i3 = i / 50
        temp = '%d;%d,%d;%d,%d;%d,%d;*\n' % (i, i1 * 5 , i1 * 5 + 4, i2*10,\
             i2*10 + 9, i3*50, i3*50 + 49)
        treefile.write(temp)
    treefile.close()

if __name__ == '__main__':
    # gen_income_tree()
    # gen_DOBYY_tree()
    
