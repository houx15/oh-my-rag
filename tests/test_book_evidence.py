import unittest
from newdomain.book_evidence import BookEvidence
class BookEvidenceTests(unittest.TestCase):
 def setUp(self):
  self.index=BookEvidence({'a':'【《本经》】\n牛黄逐鬼原文。','b':'【《本经疏》】\n牛黄逐鬼原文。','c':'【典籍档案·《本经》】\n本经成书介绍。'})
 def test_exact_title_does_not_match_suffix(self):
  ctx,t=self.index.select('《本经》牛黄逐鬼的原文在哪里',{'c':'archive'})
  self.assertIn('a',ctx);self.assertNotIn('b',ctx);self.assertEqual(t['exact_titles'],['本经'])
 def test_no_quoted_book_preserves_context(self):
  baseline={'z':'old'};ctx,t=self.index.select('牛黄逐鬼原文',baseline)
  self.assertEqual(ctx,baseline);self.assertEqual(t['promoted'],[])
 def test_missing_topic_does_not_guess(self):
  ctx,t=self.index.select('《本经》',{'z':'old'});self.assertEqual(ctx,{'z':'old'})
