import unittest
from newdomain.query_variants import variants
class QueryVariantsTests(unittest.TestCase):
 def test_user_alias_only_retrieval_hypothesis(self):
  q='你帮我打开派的看看';r=variants(q)
  self.assertEqual(r['original'],q);self.assertIn('你帮我打开pad看看',r['alternatives']);self.assertTrue(r['events'])
 def test_no_blind_replacement(self):
  for q in ['这个门派的历史','看看党派的变化','他派的任务','派的是什么意思']:
   self.assertFalse(variants(q)['events'])
 def test_chemical_homophone_not_equated(self):
  self.assertEqual(variants('牛磺有什么作用')['alternatives'],[])
