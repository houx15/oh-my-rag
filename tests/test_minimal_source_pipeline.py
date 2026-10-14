import unittest
from newdomain.source_grounded_pipeline_v2 import SourceGroundedPipeline as Baseline
from newdomain.source_grounded_pipeline_v7 import SourceGroundedPipeline as Minimal
class MinimalIntervention(unittest.TestCase):
 def test_ordinary_biography_prompt_is_exact_baseline(self):
  records=[{'id':'p','text':'人物生平','metadata':{'type':'人物','姓名':'张甲'}}];t={'modern_boundary':'现代证据边界'}
  build=lambda q,c:[{'role':'system','content':'fixed'},{'role':'user','content':q}]
  a=Baseline(records,t).prepare_nh('介绍张甲的生平',{'p':'人物生平'},build)
  b=Minimal(records,t,amendments=[]).prepare_nh('介绍张甲的生平',{'p':'人物生平'},build)
  self.assertEqual(a['context'],b['context']);self.assertEqual(a['messages'],b['messages']);self.assertEqual(a['local_response'],b['local_response'])
 def test_prescribing_vs_historical_information(self):
  t={'modern_boundary':'现代证据边界'};build=lambda q,c:[{'role':'system','content':'fixed'}]
  p=Minimal([],t,amendments=[])
  for q in ['这个口腔溃疡怎么用药','牛黄如何用药治口腔溃疡']:
   self.assertEqual(p.prepare_nh(q,{},build)['local_response']['local_route'],'clinical_current')
  for q in ['牛黄能治口腔溃疡吗','有哪些可以治口腔溃疡的方子','古籍记载牛黄如何用药']:
   self.assertIsNone(p.prepare_nh(q,{},build)['local_response'])
if __name__=='__main__':unittest.main()
