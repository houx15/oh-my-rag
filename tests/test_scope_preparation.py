import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimization_scope import paired_jobs,INSTRUCTION

class ScopePreparationTests(unittest.TestCase):
    def fixture(self):return ([{'qid':'Q-C1','messages':[{'role':'system','content':'base'},{'role':'user','content':'question'}]}],[{'job':'Q-C1','qid':'Q','arm':'C1','context':{'source':'unchanged'}}])
    def test_isolated_prompt_and_unchanged_baseline(self):
        b,m=self.fixture();saved=copy.deepcopy((b,m));jobs,meta=paired_jobs(b,m);lookup={j['qid']:j for j in jobs}
        self.assertEqual(lookup['Q-C1']['messages'],b[0]['messages']);self.assertEqual(lookup['Q-C9S']['messages'][0]['content'],'base'+INSTRUCTION);self.assertEqual(lookup['Q-C9S']['messages'][1],b[0]['messages'][1]);self.assertEqual((b,m),saved);self.assertTrue(all(x['context']==m[0]['context'] for x in meta))
    def test_nonbaseline_rejected(self):
        b,m=self.fixture();m[0]['arm']='C8U'
        with self.assertRaises(ValueError):paired_jobs(b,m)
    def test_missing_metadata_rejected(self):
        b,m=self.fixture()
        with self.assertRaises(ValueError):paired_jobs(b,[])
    def test_request_cap_preserved(self):
        b,m=self.fixture();b[0]['messages'][0]['content']='a'*40000
        with self.assertRaises(ValueError):paired_jobs(b,m)
if __name__=='__main__':unittest.main()
