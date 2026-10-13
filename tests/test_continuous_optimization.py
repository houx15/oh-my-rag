"""Synthetic safeguards for candidate isolation and atomic review evidence."""
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimization_ablation import neighbors
from optimization_atomic_review import validate_verdict


class ContinuousTests(unittest.TestCase):
    def test_neighbors_bounded_and_does_not_mutate_baseline(self):
        class Index:pass
        ix=Index();ix.chunks=[{'id':str(i),'doc_id':'d','locator':str(i),'start':0,'text':'x'} for i in range(1,12)]
        baseline=[ix.chunks[i-1] for i in (5,8,9,10,11,1,2,3)];before=[dict(c) for c in baseline]
        got=neighbors(ix,baseline)
        self.assertEqual(baseline,before);self.assertEqual(len(got),8)
        self.assertEqual(len({c['id'] for c in got}),8)
        self.assertEqual([c['id'] for c in got][-2:],['6','4'])

    def test_missing_obligation_cannot_pass(self):
        with self.assertRaises(ValueError):validate_verdict(json.dumps({'checks':[],'extra_unsupported':[]}),'answer',[{'id':'scope'}])

    def test_invented_quote_rejected(self):
        c={'id':'scope','status':'present','answer_quote':'not in answer','reason':'x'}
        with self.assertRaises(ValueError):validate_verdict(json.dumps({'checks':[c],'extra_unsupported':[]}),'answer',[{'id':'scope'}])

    def test_extra_claim_requires_actual_answer_span(self):
        c={'id':'scope','status':'missing','answer_quote':'','reason':'x'}
        v={'checks':[c],'extra_unsupported':['invented span']}
        with self.assertRaises(ValueError):validate_verdict(json.dumps(v),'answer',[{'id':'scope'}])


if __name__=='__main__':unittest.main()

from optimization_pointer_review import validate as validate_pointer

class PointerReviewTests(unittest.TestCase):
    def test_unknown_pointer_cannot_pass(self):
        v={'checks':[{'id':'scope','status':'present','answer_ids':['A9'],'reason':'x'}],'extra_unsupported':[]}
        with self.assertRaises(ValueError):validate_pointer(json.dumps(v),{'A1':'answer'},['scope'])

    def test_missing_and_present_evidence_contract(self):
        v={'checks':[{'id':'scope','status':'missing','answer_ids':['A1'],'reason':'x'}],'extra_unsupported':[]}
        with self.assertRaises(ValueError):validate_pointer(json.dumps(v),{'A1':'answer'},['scope'])
        v['checks'][0].update(status='present',answer_ids=['A1'])
        self.assertEqual(validate_pointer(json.dumps(v),{'A1':'answer'},['scope'])['checks'][0]['status'],'present')
