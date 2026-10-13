import unittest,json
from newdomain.query_plan import parse,candidate_pool,select_context
from newdomain.evidence_pool import EvidencePool
class QueryPlanTests(unittest.TestCase):
 def response(self,obj):return {'content':json.dumps(obj),'finish_reason':'stop','stream_done':True}
 def test_original_and_uncertainty_preserved(self):
  q='口语原话';p=parse(self.response({'queries':[{'text':'候选名称','uncertain':True}],'missing_context':False}),q)
  self.assertEqual(p['original'],q);self.assertTrue(p['queries'][0]['uncertain'])
 def test_answer_fields_not_allowed(self):
  with self.assertRaises(ValueError):parse(self.response({'queries':[],'missing_context':False,'answer':'杜撰答案'}),'问题')
 def test_baseline_kept_and_pool_bounded(self):
  index=EvidencePool({'a':'原始证据','b':'候选名称说明','c':'其他资料'})
  p={'queries':[{'text':'候选名称','uncertain':True}]}
  got,trace=candidate_pool(index,'原话',p,{'a':'原始证据'},k=2)
  self.assertEqual(list(got),['a','b'])

 def test_missing_context_does_not_guess(self):
  index=EvidencePool({'a':'原始证据','b':'人物资料'})
  ctx,trace=select_context(index,'他是谁',{'queries':[{'text':'某人','uncertain':True}],'missing_context':True},{'a':'原始证据'},1)
  self.assertEqual(ctx,{'a':'原始证据'});self.assertEqual(trace['promoted'],[])
