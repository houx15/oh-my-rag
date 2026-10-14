import json, unittest
from newdomain.source_grounded_pipeline_v3 import SourceGroundedPipeline,HISTORICAL_LIMIT
from newdomain.source_grounded_pipeline_v2 import SourceGroundedPipeline as Baseline
from newdomain.typed_boundaries_v2 import compile_response

class ScopeAndHistory(unittest.TestCase):
 def setUp(self):
  self.templates={'no_evidence':'不足','personal':'个人限制','modern_boundary':'现代限制'}
  self.context={'a':'某书所录历史资料'}
 def build(self,q,c): return [{'role':'system','content':'root'},{'role':'user','content':q+json.dumps(c,ensure_ascii=False)}]
 def test_clinical_history_does_not_mutate_evidence(self):
  q='可以治口腔溃疡吗'
  b=Baseline([],self.templates).prepare_nh(q,self.context,self.build)
  p=SourceGroundedPipeline([],self.templates).prepare_nh(q,self.context,self.build)
  self.assertEqual(b['local_response']['local_route'],'clinical_current')
  self.assertIsNone(p['local_response']);self.assertEqual(list(b['context'].items()),list(p['context'].items()))
  self.assertEqual(b['messages'][1],p['messages'][1])
 def test_personal_route_remains_boundary(self):
  p=SourceGroundedPipeline([],self.templates).prepare_nh('最近经常失眠怎么办',self.context,self.build)
  self.assertEqual(p['local_response']['local_route'],'personal_current')
 def test_ablation_factors_are_independent(self):
  q='牛黄可以治口腔溃疡吗'
  c=SourceGroundedPipeline([],self.templates,scope=False).prepare_nh(q,self.context,self.build)
  s=SourceGroundedPipeline([],self.templates,coverage=False).prepare_nh(q,self.context,self.build)
  self.assertIsNone(c['local_response']);self.assertIsNotNone(s['local_response'])
  self.assertNotIn('证据归属与范围检查',c['messages'][0]['content'])
  self.assertIn('证据归属与范围检查',s['messages'][0]['content'])
 def test_boundary_is_exact_enum_not_arbitrary_prose(self):
  p=SourceGroundedPipeline([],self.templates)
  raw={'content':json.dumps({'sentences':[{'boundary':'historical_limit'}]}),'finish_reason':'stop','stream_done':True}
  out,_=compile_response(raw,p.templates,'citations')
  self.assertEqual(json.loads(out['content'])['sentences'][0],{'text':HISTORICAL_LIMIT,'citations':[]})
  raw['content']=json.dumps({'sentences':[{'boundary':'historical_limit','text':'可以服用'}]})
  with self.assertRaises(ValueError):compile_response(raw,p.templates,'citations')
if __name__=='__main__':unittest.main()
