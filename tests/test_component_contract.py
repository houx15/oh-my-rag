import copy,unittest
from newdomain.component_contract import contract,messages
from newdomain import baseline
class ContractTests(unittest.TestCase):
 def test_does_not_mutate_evidence_or_original(self):
  source=[{'role':'system','content':'old rules'},{'role':'user','content':'question and exact evidence'}];saved=copy.deepcopy(source)
  result=messages(source,'niuhuang')
  self.assertEqual(source,saved);self.assertEqual(result[1:],source[1:]);self.assertTrue(result[0]['content'].startswith('old rules'))
 def test_gm_uses_existing_limits(self):
  c=contract('guangming');self.assertEqual(c['text_max_chars'],baseline.MAX_TEXT_CHARS);self.assertEqual(c['sentences_max'],baseline.MAX_SENTENCES);self.assertEqual(c['evidence_max'],baseline.MAX_CITATIONS)
 def test_unknown_domain_rejected(self):
  with self.assertRaises(ValueError):contract('unknown')
if __name__=='__main__':unittest.main()
