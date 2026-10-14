import unittest
from newdomain.citation_completion import complete
class CitationCompletion(unittest.TestCase):
 def answer(self,q):return {'sentences':[{'text':'固定的陈述','citations':[{'id':'s','quote':q}]}],'handoff':False}
 def test_complete_partial_sentence_preserves_answer(self):
  source='前句。作者称甲为乙，并说明条件。后句。';a=self.answer('甲为乙')
  b,t=complete(a,{'s':source});self.assertEqual(b['sentences'][0]['text'],a['sentences'][0]['text']);self.assertEqual(b['sentences'][0]['citations'][0]['quote'],'作者称甲为乙，并说明条件。');self.assertEqual(a,self.answer('甲为乙'));self.assertEqual(len(t),1)
 def test_trailing_attribution(self):
  b,t=complete(self.answer('甲为乙。'),{'s':'甲为乙。（《示例志》）另一条。'});self.assertEqual(b['sentences'][0]['citations'][0]['quote'],'甲为乙。（《示例志》）')
 def test_ambiguous_and_budget_noop(self):
  a=self.answer('相同');self.assertEqual(complete(a,{'s':'相同。相同。'})[0],a)
  a=self.answer('证据');self.assertEqual(complete(a,{'s':'前'*500+'证据。'},max_chars=50)[0],a)
 def test_section_crossing_noop(self):
  a=self.answer('甲。');b,t=complete(a,{'s':'前句。【另节】甲。后句。'},mode='neighbor');self.assertEqual(b,a);self.assertEqual(t,[])
 def test_false_claim_is_not_changed_or_certified(self):
  a=self.answer('甲有效');a['sentences'][0]['text']='甲有效'
  b,t=complete(a,{'s':'有人说甲有效，此说不成立。'});self.assertEqual(b['sentences'][0]['text'],'甲有效');self.assertFalse(t[0]['semantic_support_verified']);self.assertIn('不成立',b['sentences'][0]['citations'][0]['quote'])
if __name__=='__main__':unittest.main()
