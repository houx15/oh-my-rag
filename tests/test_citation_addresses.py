import unittest
from newdomain.citation_addresses import messages
class CitationAddressTests(unittest.TestCase):
 def test_bounds_do_not_change_question_or_sources(self):
  p=[{'role':'system','content':'base'},{'role':'user','content':'original question and exact sources'}];r=messages(p,{'x':1,'y':3})
  self.assertEqual(p[0]['content'],'base');self.assertEqual(r[1],p[1]);self.assertIn('"x": [0, 0]',r[0]['content']);self.assertIn('"y": [0, 2]',r[0]['content'])
 def test_rejects_missing_or_invalid_counts(self):
  for counts in [{},{'x':0},{'x':True}]:
   with self.assertRaises(ValueError):messages([{'role':'system','content':'base'}],counts)
