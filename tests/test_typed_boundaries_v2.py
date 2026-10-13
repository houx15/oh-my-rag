import unittest,json
from newdomain.typed_boundaries_v2 import compile_response
class TypedBoundaryV2Tests(unittest.TestCase):
 def response(self,sentence):return {'content':json.dumps({'sentences':[sentence]}),'finish_reason':'stop','stream_done':True}
 def test_exact_redundancy_is_lossless(self):
  r=self.response({'boundary':'missing','text':'资料不足。','citations':[]})
  out,log=compile_response(r,{'missing':'资料不足。'},'citations')
  self.assertEqual(json.loads(out['content'])['sentences'][0],{'text':'资料不足。','citations':[]});self.assertEqual(len(log),2)
 def test_different_claim_or_evidence_rejected(self):
  for s in [{'boundary':'missing','text':'全世界没有证据'},{'boundary':'missing','citations':[{'id':'x'}]}]:
   with self.assertRaises(ValueError):compile_response(self.response(s),{'missing':'资料不足。'},'citations')
