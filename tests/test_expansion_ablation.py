import unittest
from types import SimpleNamespace
from newdomain.expansion_ablation import select
from newdomain.keyword_control import select as control
class Pool:
 idf={}
 def build(self,q,unused,k):return ({x:''for x in (['a','c','d']if q=='original'else['d','e'])},{})
class ExpansionTests(unittest.TestCase):
 def test_off_matches_control(self):
  s=SimpleNamespace(pool=Pool(),records={'a':'alpha','b':'beta','c':'gamma','d':'delta','e':'epsilon'})
  self.assertEqual(select(s,'original',[],{'a':'alpha','b':'beta'},2)[0],control(s,'original',[],{'a':'alpha','b':'beta'},2)[0])
 def test_provenance_and_budget(self):
  s=SimpleNamespace(pool=Pool(),records={'a':'alpha','b':'beta','c':'gamma','d':'delta','e':'epsilon'})
  c,t=select(s,'original',['expanded'],{'a':'alpha','b':'beta'},2)
  self.assertEqual(len(c),2);self.assertEqual(next(iter(c)),'a');self.assertFalse(t['hypotheses_are_evidence']);self.assertEqual(t['span_query'],'original only')
if __name__=='__main__':unittest.main()
