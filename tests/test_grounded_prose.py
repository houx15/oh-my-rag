import json
import unittest
from newdomain.grounded_prose import catalog,build_messages,render

def response(obj):return {'content':json.dumps(obj,ensure_ascii=False),'finish_reason':'stop','stream_done':True,'usage':{'input_tokens':10,'output_tokens':10}}
class GroundedProseTests(unittest.TestCase):
 def setUp(self):
  self.ctx={'table':'医疗传感器\n一、体外检测\n免疫检测\n二、体表监测\n心电监测\n'+'其他项目\n'*70,'policy':'（一）创新支持。支持区内龙头企业发布需求。对经评审的项目，按发榜方实际出资的20%给予最高500万元资助。\n（二）其他项目。按10%予以补贴。'}
  self.cat=catalog(self.ctx)
 def run_answer(self,parts):return render(response({'sentences':parts}),self.ctx,self.cat['fingerprint'])
 def test_long_table_ordinary_prose_retains_hierarchy(self):
  answer,_=self.run_answer([{'text':'体外检测与心电监测分属不同分类，后者列在体表监测下。','sources':['S1']}])
  self.assertEqual(answer['sentences'][0]['citations'][0]['quote'],self.ctx['table'])
  self.assertGreater(len(self.ctx['table']),300)
 def test_qualified_clause_preserves_cross_sentence_eligibility(self):
  answer,_=self.run_answer([{'qualified':'Q1'}]);text=answer['sentences'][0]['text']
  for word in ['区内龙头企业','经评审','发榜方实际出资','20%','500万元']:self.assertIn(word,text)
  self.assertNotIn('10%',text)
 def test_numeric_policy_cannot_bypass_clause(self):
  with self.assertRaisesRegex(ValueError,'numeric policy'):self.run_answer([{'text':'最高资助500万元。','sources':['S2']}])
 def test_valid_specific_boundary_modes(self):
  for kind in ['clarify','missing','modern','ui','uncertain']:
   answer,_=self.run_answer([{'boundary':kind}]);self.assertEqual(answer['sentences'][0]['citations'],[])
 def test_ui_can_accompany_facts(self):
  self.run_answer([{'boundary':'ui'},{'text':'心电监测属于体表监测。','sources':['S1']}])
 def test_partial_fact_and_clarification_is_deliverable_not_semantically_certified(self):
  answer,trace=self.run_answer([{'text':'已知分类','sources':['S1']},{'boundary':'clarify'}])
  self.assertEqual(len(answer['sentences']),2);self.assertFalse(trace['semantic_binding_verified'])
 def test_policy_summary_requires_selected_source_bound_amounts(self):
  self.run_answer([{'qualified':'Q1'},{'text':'补贴比例20%，最高500万元。','sources':['S2']}])
  with self.assertRaises(ValueError):self.run_answer([{'qualified':'Q1'},{'text':'最高补贴1000万元。','sources':['S2']}])
  with self.assertRaises(ValueError):self.run_answer([{'qualified':'Q1'},{'text':'最高补贴500万元。','sources':['S1']}])
 def test_no_separate_source_unit_mismatch(self):
  with self.assertRaises(ValueError):self.run_answer([{'qualified':'Q1','source':'S1'}])
  with self.assertRaises(ValueError):self.run_answer([{'text':'事实','sources':['S9']}])
 def test_changed_context_rejected(self):
  with self.assertRaisesRegex(ValueError,'changed'):render(response({'sentences':[{'qualified':'Q1'}]}),{'new':'别的内容'},self.cat['fingerprint'])
 def test_clipped_and_long_groups_not_truncated(self):
  for text in ['资助20%，条件尚未','资助20%。'+'未完'*700]:self.assertEqual(catalog({'x':text})['groups'],{})
 def test_full_sources_remain_in_prompt(self):
  messages,_=build_messages('比较两种传感器',self.ctx)
  for text in self.ctx.values():self.assertIn(text,messages[1]['content'])
 def test_duplicate_fields_and_incomplete_stream_rejected(self):
  raw=response({});raw['content']='{"sentences":[],"sentences":[]}'
  with self.assertRaisesRegex(ValueError,'duplicate'):render(raw,self.ctx,self.cat['fingerprint'])
  raw=response({'sentences':[{'boundary':'missing'}]});raw['stream_done']=False
  with self.assertRaisesRegex(ValueError,'envelope'):render(raw,self.ctx,self.cat['fingerprint'])

 def test_cross_page_clause_preserves_scope_and_two_exact_citations(self):
  context={'D77:3:01':'第五条 支持指定材料项目。围绕关键电\n― 3 ―','D77:4:01':'池材料。对经评审的项目按投资20%补贴，最高1000万元。\n第六条 其他事项。'}
  c=catalog(context);qid=next(k for k,v in c['groups'].items()if v.get('parts'))
  answer,_=render(response({'sentences':[{'qualified':qid}]}),context,c['fingerprint'])
  cites=answer['sentences'][0]['citations'];self.assertEqual(len(cites),2)
  self.assertIn('指定材料',answer['sentences'][0]['text']);self.assertIn('经评审',answer['sentences'][0]['text'])
  for cite in cites:self.assertIn(cite['quote'],context[cite['id']])
 def test_never_join_different_or_nonadjacent_documents(self):
  for second in ['D78:4:01','D77:5:01']:
   c=catalog({'D77:3:01':'第五条 支持指定材料。条件为电\n― 3 ―',second:'池材料。资助20%，最高1000万元。\n第六条 其他事项。'})
   self.assertFalse(any(g.get('parts')for g in c['groups'].values()))
