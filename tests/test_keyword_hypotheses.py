import json,unittest
from newdomain.keyword_hypotheses import KeywordSearch,parse
class KeywordHypothesisTests(unittest.TestCase):
 def test_schema_rejects_answers_and_duplicate_keys(self):
  for s in ['{"queries":[],"answer":"x"}','{"queries":[],"queries":[]}','{"queries":[1]}']:
   with self.assertRaises(ValueError):parse({'content':s,'stream_done':True,'finish_reason':'stop'})
 def test_nonphonetic_guesses_allowed(self):
  self.assertEqual(parse({'content':'{"queries":["演示资料管理"]}','stream_done':True,'finish_reason':'stop'}),['演示资料管理'])
 def test_original_and_source_provenance(self):
  e=KeywordSearch({'a':'LivePad pad 数据展示','b':'药物 牛黄 性味'},lambda s:s.split())
  v=e.vocabulary('帮我打开');self.assertTrue(any(x['term']=='LivePad'for x in v))
  for x in v:self.assertIn(x['term'],e.records[x['source_id']])
  self.assertEqual(json.loads(e.messages('原始口语')[1]['content'])['original_conversational_question'],'原始口语')
 def test_guesses_never_become_context(self):
  e=KeywordSearch({'a':'原始材料','b':'演示资料管理','c':'第三证据'},lambda s:s.split())
  ctx,tr=e.select('原始材料',['演示资料管理','凭空的未知猜测'],{'a':'原始材料'},2)
  self.assertEqual(list(ctx)[0],'a');self.assertIn('b',ctx)
  for rid,t in ctx.items():self.assertIn(t,e.records[rid])
  self.assertEqual(tr['views'][0],['a'])
 def test_empty_plan_exact_fallback_and_bounded_context(self):
  e=KeywordSearch({'a':'已有证据','b':'测试'*900},lambda s:s.split());base={'a':'已有证据'}
  self.assertEqual(e.select('问题',[],base,2)[0],base)
  ctx,tr=e.select('问题',['测试'],base,2);self.assertLessEqual(len(ctx['b']),900)
 def test_truncated_response_rejected(self):
  with self.assertRaises(ValueError):parse({'content':'{"queries":[]}','stream_done':False,'finish_reason':'stop'})
