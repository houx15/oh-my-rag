import unittest
from newdomain.evidence_selector import preview,select
class EvidenceSelectorTests(unittest.TestCase):
 def test_span_identity(self):
  t='前文'*100+'性凉证据'+'后文'*100
  for s in preview(t,'性凉')['spans']:self.assertEqual(s['text'],t[s['start']:s['end']])
 def test_unknown_and_duplicate_fail_closed(self):
  for content in ['{"ids":["evil"]}','{"ids":["a","a"]}','{"ids":[]}']:
   result,trace=select({'content':content,'finish_reason':'stop','stream_done':True},{'a':'source'},{'b':'baseline'},2)
   self.assertTrue(trace['fallback']);self.assertEqual(result,{'b':'baseline'})
 def test_only_visible_records(self):
  result,trace=select({'content':'{"ids":["a"]}','finish_reason':'stop','stream_done':True},{'a':'source'},{'b':'baseline'},2)
  self.assertEqual(result,{'a':'source'});self.assertFalse(trace['fallback'])
