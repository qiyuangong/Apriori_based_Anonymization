import unittest
import pdb
from apriori_based_anon import apriori_based_anon
from models.gentree import GenTree

# Build a GenTree object
ATT_TREE = {}


def init_tree():
    global ATT_TREE
    ATT_TREE = {}
    root = GenTree('*')
    ATT_TREE['*'] = root
    lt = GenTree('A', root)
    ATT_TREE['A'] = lt
    ATT_TREE['a1'] = GenTree('a1', lt, True)
    ATT_TREE['a2'] = GenTree('a2', lt, True)
    rt = GenTree('B', root)
    ATT_TREE['B'] = rt
    ATT_TREE['b1'] = GenTree('b1', rt, True)
    ATT_TREE['b2'] = GenTree('b2', rt, True)


class test_Apriori_based_Anon(unittest.TestCase):
    def test_AA(self):
        init_tree()
        trans = [['a1', 'b1', 'b2'],
                 ['a2', 'b1'],
                 ['a2', 'b1', 'b2'],
                 ['a1', 'a2', 'b2']]
        _, result = apriori_based_anon(ATT_TREE, trans, 'AA', 2, 2)
        self.assertEqual(result[2], {'a1': 'A', 'a2': 'A'})

    def test_DA(self):
        init_tree()
        trans = [['a1', 'b1', 'b2'],
                 ['a2', 'b1'],
                 ['a2', 'b1', 'b2'],
                 ['a1', 'a2', 'b2']]
        _, result = apriori_based_anon(ATT_TREE, trans, 'DA', 2, 2)
        self.assertEqual(result[2], {'a1': 'A', 'a2': 'A'})


if __name__ == '__main__':
    unittest.main()
