import unittest,json
from newdomain.typed_boundaries import compile_response
class TypedBoundaryTests(unittest.TestCase):
 def response(self,content):return {'content':content,'finish_reason':'stop','stream_done':True,'usage':{'input_tokens':1,'output_tokens':1}}
 def test_explicit_enum_only_and_raw_preserved(self):
  r=self.response('{"sentences":[{"boundary":"missing"},{"text":"事实","evidence":["E1S1"]}]}')
  out,log=compile_response(r,{'missing':'资料不足。'},'evidence')
  self.assertEqual(json.loads(out['content'])['sentences'][0],{'text':'资料不足。','evidence':[]})
  self.assertIn('boundary',r['content']);self.assertEqual(out['usage'],r['usage']);self.assertEqual(len(log),1)
 def test_no_relabel_arbitrary_uncited_claim(self):
  r=self.response('{"sentences":[{"text":"全世界没有证据","citations":[]}]}')
  out,log=compile_response(r,{'missing':'资料不足。'},'citations')
  self.assertEqual(json.loads(out['content']),json.loads(r['content']));self.assertEqual(log,[])
 def test_mixed_unknown_and_duplicate_fail(self):
  for content in ['{"sentences":[{"boundary":"missing","text":"事实"}]}','{"sentences":[{"boundary":"unknown"}]}','{"sentences":[{"boundary":"missing","boundary":"missing"}]}']:
   with self.assertRaises(ValueError):compile_response(self.response(content),{'missing':'资料不足。'},'evidence')
