#!/usr/bin/env python
#coding=utf-8

# logic tree
class GenTree:
    "Generalization hierarchy(Taxonomy Tree) for Generalization"
    def __init__(self, value = None, parent = None):
        self.value = ''
        self.level = 0
        self.support = 0
        self.parent = []
        self.child = []
        # range is for ARE, all possible values are in range
        self.cover = []
        if value != None:
            self.value = value
        if parent != None:
            self.parent = parent.parent[:]
            self.parent.insert(0,parent)
            parent.child.append(self)
            self.level = parent.level + 1

    def node(self,value):
        if self.value == value:
            return self
        else:
            for tn in child:
                return child.node(value)

    def getsupport(self):
        "compute the tree's support, and store in their var support"
        if len(self.child) != 0:
            for t in self.child:
                self.support = self.support + t.getsupport()
                self.cover.extend(t.cover)
        else:
            self.support = 1
            self.cover.append(self.value)
        return self.support


class CountTree:
    "CountTree by Manolis Terrovitis"
    def __init__(self, value = None, parent = None): 
        self.parent = []
        self.value = ''
        self.node = []
        self.support = 0

class Trunk:
    "Group for Disassociation"
    def __init__(self, data, value = ['*'], level = []):
        
        self.member = data
        self.value = value[:]
        self.level = level[:]

class Group:
    "Group according to Generalization hierarchy"
    def __init__(self, data, value = ['*'], level = []):
        self.iloss = 0.0
        self.member = data
        self.value = value[:]
        self.level = level[:]

    def merge_group(self, guest, middle):
        "merge guest into hostgourp"
        while guest.member:
            temp = guest.member.pop()
            self.member.append(temp)
        self.value = middle[:]

    def merge_record(self, rtemp, middle):
        "merge record into hostgourp"
        self.member.append(rtemp)
        self.value = middle[:]



if __name__ == '__main__':

    print 'OK'
