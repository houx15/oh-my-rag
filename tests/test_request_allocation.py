import copy
import json
import tempfile
import unittest
from pathlib import Path
from eval.optimization.budget import AuthorizationManifest, AuthorizationError, _fresh_state
from newdomain.request_allocation import build_proposal, append_proposal
from newdomain.batch import digest

class RequestAllocationTests(unittest.TestCase):
    def setUp(self):
        self.m=AuthorizationManifest({"authorized":True,"spend_cap_usd":90,"final_eval_reserve_usd":30,"max_input_tokens":1,"max_output_tokens":1,"request_cap":0,"global_deadline_s":60,"original_total_cap_usd":100,"prior_spend_usd":10})
        self.f=_fresh_state(self.m,"final",False);self.d=_fresh_state(self.m,"dev",False)
        self.b={"baseline_current_ledgers_usd":"0","additional_cap_usd":"12"}
        self.p={"classification":"unresolved","evidence":"Original selection record unavailable; no assumption of authority"}
    def make(self,**kw):return build_proposal(self.m,self.f,self.d,self.b,provenance=self.p,**kw)
    def test_exact_minimal_scope_and_no_live_authority(self):
        originals=copy.deepcopy((self.f,self.d,self.m._raw,self.b))
        p=self.make();self.assertEqual(p['additional_calls'],190)
        self.assertEqual([x['max_calls'] for x in p['scopes']],[10,72,72,36])
        self.assertFalse(p['authorizes_dispatch']);self.assertEqual(originals,(self.f,self.d,self.m._raw,self.b))
    def test_append_only_chain_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'allocation.proposals.jsonl';p=self.make();append_proposal(path,p);first=path.read_bytes()
            with self.assertRaises(AuthorizationError):append_proposal(path,p)
            self.assertEqual(first,path.read_bytes())
            self.p['evidence']='Additional provenance evidence';p2=self.make(previous=p['sha256']);append_proposal(path,p2)
            self.assertTrue(path.read_bytes().startswith(first));self.assertEqual(len(path.read_text().splitlines()),2)
    def test_cannot_write_canonical_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(AuthorizationError):append_proposal(Path(d)/'ledger.final.json',self.make())
    def test_tampered_proposal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.make();p['additional_calls']=191
            with self.assertRaises(AuthorizationError):append_proposal(Path(d)/'a.proposals.jsonl',p)
    def test_self_signed_dispatch_flag_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=self.make();p['authorizes_dispatch']=True;p['sha256']=digest({k:v for k,v in p.items() if k!='sha256'})
            with self.assertRaises(AuthorizationError):append_proposal(Path(d)/'a.proposals.jsonl',p)
    def test_changed_nested_cap_rejected(self):
        self.b['additional_cap_usd']='13'
        with self.assertRaises(AuthorizationError):self.make()
    def test_cumulative_widening_rejected(self):
        self.m.spend_cap_usd=91
        with self.assertRaises(AuthorizationError):self.make()
    def test_unresolved_halt_rejected(self):
        self.f['halted']={'reason':'unknown settlement'}
        with self.assertRaises(AuthorizationError):self.make()
    def test_unknown_provenance_rejected(self):
        self.p['classification']='user_limit_assumed_administrative'
        with self.assertRaises(AuthorizationError):self.make()
