import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimization_review_compact import compact
class ReviewCompactionTests(unittest.TestCase):
    def fixture(self):return {'required_source':{'D:1':'完整来源含引文'},'retrieved_source':{'D:2':'另一来源'},'answers':{'A':{'sentences':[{'text':'回答','citations':[{'id':'D:1','quote':'含引文'}]}]}}}
    def test_retains_sources_text_and_handles_without_mutation(self):
        b=self.fixture();old=copy.deepcopy(b);out=compact(b);self.assertEqual(b,old);self.assertEqual(out['required_source'],b['required_source']);self.assertEqual(out['retrieved_source'],b['retrieved_source']);self.assertEqual(out['answers']['A']['sentences'][0],{'text':'回答','citations':[{'id':'D:1'}]})
    def test_missing_quote_not_silently_removed(self):
        b=self.fixture();b['answers']['A']['sentences'][0]['citations'][0]['quote']='未提供的来源'
        with self.assertRaises(ValueError):compact(b)
if __name__=='__main__':unittest.main()
