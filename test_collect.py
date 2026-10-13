import unittest
from collect import merge

class MergeTest(unittest.TestCase):
    def test_overlap_replaces_and_preserves_history(self):
        old=[{'timestamp':'2026-01-01','count':5},{'timestamp':'2026-01-02','count':1}]
        new=[{'timestamp':'2026-01-02','count':3},{'timestamp':'2026-01-03','count':0}]
        result=merge(old,new)
        self.assertEqual([r['count'] for r in result],[5,3,0])
        self.assertEqual(merge(result,new),result)

if __name__=='__main__': unittest.main()
