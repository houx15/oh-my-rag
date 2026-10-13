import unittest
from newdomain.ordered_context import from_retrieval
class OrderedContextTests(unittest.TestCase):
 def test_sorted_serialized_map_does_not_renumber_handles(self):
  results=[{'id':'z','text':'first evidence'},{'id':'a','text':'second evidence'}]
  context=from_retrieval(results,{'a':'second evidence','z':'first evidence'})
  self.assertEqual(list(context),['z','a'])
 def test_changed_evidence_and_duplicate_rejected(self):
  with self.assertRaises(ValueError):from_retrieval([{'id':'a','text':'changed'}],{'a':'original'})
  with self.assertRaises(ValueError):from_retrieval([{'id':'a','text':'x'},{'id':'a','text':'x'}],{'a':'x'})
