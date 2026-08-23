import unittest,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from lambda_ninemap_v9_1 import *

class TestNineMap(unittest.TestCase):
    def test_shared_skeleton(self):
        for c in (0,3,6):
            cols=[set(column(h,c)) for h in GENERATORS.values()]
            self.assertEqual(cols[0],cols[1])
            self.assertEqual(cols[1],cols[2])

    def test_one_or_three(self):
        for h in GENERATORS.values():
            for c in range(9):
                for t in column(h,c):
                    self.assertEqual(len(set(t)),1 if c==0 else 3)

    def test_tracks(self):
        for h in GENERATORS.values():
            for c in range(9):
                C=column(h,c)
                for q in range(3):
                    self.assertEqual(sorted(t[q] for t in C),list(range(9)))

    def test_partition(self):
        states=[(i,j,k) for i in range(9) for j in range(9) for k in range(9)]
        counts={1:0,2:0,3:0}
        for t in states:
            counts[len(set(t))]+=1
        self.assertEqual(counts,{1:9,2:216,3:504})

    def test_codec(self):
        self.assertEqual(len({rank_to_u9cube(R) for R in range(216)}),216)

if __name__=='__main__':
    unittest.main()
