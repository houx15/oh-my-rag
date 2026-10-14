import unittest,json
from newdomain.protocol_normalization import normalize
from newdomain.section_windows import select
class ProtocolNormalization(unittest.TestCase):
 def raw(self,s):return {'content':json.dumps({'sentences':s},ensure_ascii=False),'finish_reason':'stop','stream_done':True}
 def test_boundary_grammar_preserves_facts(self):
  facts={'text':'源文支持的句子','citations':[{'id':'s','segs':[0]}]}
  r,tr=normalize(self.raw([facts,{'boundary':'no_evidence','text':'本次资料不足以回答这一部分，不能补写。'}]),{}, {'no_evidence':'固定边界'})
  self.assertEqual(json.loads(r['content'])['sentences'],[facts,{'boundary':'no_evidence'}]);self.assertEqual(len(tr),1)
 def test_nonboundary_claims_never_discarded(self):
  for text in ['可以每天服用三次','本次资料不足以回答这一部分，不能补写。此药有效。','不能据此判断个人现在能否服用；请向合格医师核实。每日一克']:
   s={'boundary':'personal','text':text};r,tr=normalize(self.raw([s]),{}, {'personal':'固定边界'});self.assertEqual(json.loads(r['content'])['sentences'],[s]);self.assertEqual(tr,[])
 def test_nonempty_citation_not_erased(self):
  s={'boundary':'no_evidence','text':'本次资料不足以回答这一部分，不能补写。','citations':[{'id':'x','segs':[0]}]};r,tr=normalize(self.raw([s]),{}, {'no_evidence':'固定边界'});self.assertEqual(tr,[])
 def test_alias_explicit_and_cited(self):
  a=[{'alias':'《甲书》','canonical':'《校定甲书》','source_ids':['s'],'evidence':'catalogue alias'}];s={'text':'《甲书》记载原文','citations':[{'id':'s','segs':[0]}]}
  r,tr=normalize(self.raw([s]),{'s':'《校定甲书》原文'}, {},a);self.assertIn('《校定甲书》',r['content']);self.assertEqual(len(tr),1)
  self.assertEqual(normalize(self.raw([s]),{'other':'《校定甲书》'}, {},a)[1],[])
 def test_duplicate_and_incomplete_rejected(self):
  with self.assertRaises(ValueError):normalize({'content':'{"sentences":[],"sentences":[]}','finish_reason':'stop','stream_done':True},{},{})
  with self.assertRaises(ValueError):normalize({'content':'{}','finish_reason':'length','stream_done':True},{},{})
 def test_sections_are_bounded_exact_and_unambiguous(self):
  text='《示例志》\n【序言】'+('前言。'*60)+'【产地】甲地。乙地。【采制】秋日采集。'
  out,tr=select(text,'请介绍产地内容',60);self.assertEqual(out,'《示例志》\n【产地】甲地。乙地。');self.assertEqual(text[tr['start']:tr['end']],'【产地】甲地。乙地。')
  self.assertIsNone(select(text,'介绍产地和采制',60));self.assertIsNone(select(text,'哪里生产',60));self.assertLessEqual(len(out),60)
if __name__=='__main__':unittest.main()

class FactorIsolation(unittest.TestCase):
 def test_source_patch_preserves_window_and_order(self):
  from unittest.mock import patch
  import hashlib
  from newdomain.source_grounded_pipeline_v8 import SourceGroundedPipeline
  text='《示例书》\n【释名】旧。余文。';records=[{'id':'a','text':text,'metadata':{}},{'id':'b','text':'对照','metadata':{}}]
  a={'record_id':'a','amended_id':'a-v2','expected_text_sha256':hashlib.sha256(text.encode()).hexdigest(),'before':'旧。','after':'新。','sources':['source'],'verification':'fixture'}
  with patch('pathlib.Path.read_text',return_value=json.dumps({'amendments':[a]})):
   p=SourceGroundedPipeline(records,{},source=True)
  build=lambda q,c:[{'role':'system','content':'fixed '+json.dumps(c,ensure_ascii=False)}]
  out=p.prepare_nh('介绍条目',{'a':text,'b':'对照'},build)
  self.assertEqual(list(out['context']),['a-v2','b']);self.assertEqual(out['context']['a-v2'],text.replace('旧。','新。'));self.assertEqual(out['context']['b'],'对照')
 def test_section_resolves_unique_book_record_only(self):
  from newdomain.source_grounded_pipeline_v8 import SourceGroundedPipeline
  records=[{'id':'book','text':'目录','metadata':{'type':'书目','书名':'示例书'}},{'id':'chapter','text':'《示例书》\n【产地】甲地。乙地。【采制】秋采。','metadata':{'出处典籍':'《示例书》'}}]
  p=SourceGroundedPipeline(records,{},sections=True);build=lambda q,c:[{'role':'system','content':'fixed'}]
  out=p.prepare_nh('示例书的采制段内容',{'book':'目录'},build)
  self.assertIn('chapter',out['context']);self.assertNotIn('甲地',out['context']['chapter']);self.assertIn('秋采',out['context']['chapter'])
