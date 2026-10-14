import unittest
from newdomain.keyword_hypotheses import KeywordSearch
from newdomain.keyword_selection import select

class SelectionTests(unittest.TestCase):
 def setUp(self):
  self.records={'a':'牛黄 作者','b':'牛黄 作者 来源','c':'牛黄 贵 古籍','d':'无关资料'}
  self.search=KeywordSearch(self.records,lambda s:s.split())
 def test_preserve_source_and_budget(self):
  for mode in ['equal_rrf','token_coverage']:
   ctx,tr=select(self.search,'牛黄 贵',['牛黄 作者'],{'a':'牛黄 作者'},1,mode,str.split)
   self.assertEqual(ctx,{'a':'牛黄 作者'})
 def test_new_attribute_coverage(self):
  ctx,tr=select(self.search,'牛黄 贵',['牛黄 作者'],{'a':'牛黄 作者','b':'牛黄 作者 来源'},2,'token_coverage',str.split)
  self.assertEqual(list(ctx),['a','c'])
  self.assertIn('贵',tr['query_terms'])
  for rid,text in ctx.items():self.assertIn(text,self.records[rid])
 def test_empty_fallback_and_unknown_guess(self):
  base={'a':'牛黄 作者','b':'牛黄 作者 来源'}
  self.assertEqual(select(self.search,'牛黄',[],base,2,'equal_rrf',str.split)[0],base)
  ctx,tr=select(self.search,'牛黄',['不存在假设'],base,2,'token_coverage',str.split)
  self.assertNotIn('不存在假设',tr['query_terms'])
 def test_reject_invalid_mode(self):
  with self.assertRaises(ValueError):select(self.search,'牛黄',[],{},2,'answer_oracle',str.split)
if __name__=='__main__':unittest.main()
