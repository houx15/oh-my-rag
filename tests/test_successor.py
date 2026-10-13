import copy
import json
import tempfile
import unittest
from pathlib import Path
from eval.optimization.budget import AuthorizationManifest, SpendLedger, AuthorizationError
from newdomain.successor import create_successor
from newdomain.batch import file_sha
from newdomain.transport import LiveContext, PriorLedgerError

class SuccessorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.p=Path(self.tmp.name)
        raw={'authorized':True,'spend_cap_usd':100,'final_eval_reserve_usd':30,'request_cap':100,'max_input_tokens':6000,'max_output_tokens':800,'global_deadline_s':86400,'max_concurrency':3,'max_retries':0,'prior_runs':[],'prior_spend_usd':0,'original_total_cap_usd':100,'models':{'deepseek-flash':{'input_per_1m':.3,'output_per_1m':1.2,'verified':True,'context_tokens_upper_bound':100},'deepseek-v4-pro':{'input_per_1m':1,'output_per_1m':3,'verified':True}}}
        self.mp=self.p/'manifest.json';self.mp.write_text(json.dumps(raw));self.m=AuthorizationManifest.load(self.mp)
        self.ledgers={s:SpendLedger(self.p/f'ledger.{s}.json',self.m,stage=s) for s in ('dev','final')}
        r=self.ledgers['final'].reserve('deepseek-flash',100,1);self.ledgers['final'].settle(r['id'],{'input_tokens':100,'output_tokens':1})
        self.old={s:copy.deepcopy(l.snapshot()) for s,l in self.ledgers.items()}
        self.deny=self.p/'deny.json';self.deny.write_text('[]');self.scope=self.p/'cases.json';self.scope.write_text('[]')
        self.profile=self.p/'profile.json';self.profile.write_text(json.dumps({'manifest_path':str(self.mp),'manifest_sha256':file_sha(self.mp),'dev_ledger_path':str(self.p/'ledger.dev.json'),'final_ledger_path':str(self.p/'ledger.final.json'),'redaction_names_path':str(self.deny)}))
        self.auth={'total_cap_usd':100,'user_instruction':'Rerun with Flash under existing cumulative cap','source_thread':'test-only'}
    def create(self):return create_successor(self.profile,self.p/'next',self.auth,10,{str(self.scope):file_sha(self.scope)})
    def test_carry_forward_retire_and_reserve_new_scope(self):
        p=self.create();raw=json.loads(Path(p['manifest_path']).read_text())
        self.assertEqual(raw['prior_requests_dispatched'],1);self.assertEqual(raw['request_cap'],10)
        self.assertAlmostEqual(raw['prior_spend_usd']+raw['spend_cap_usd'],100)
        self.assertNotIn('deepseek-v4-pro',raw['models'])
        for s,l in self.ledgers.items():
            state=l.snapshot()
            for k in ['reservations','totals','deadline_epoch','manifest_fingerprint']:self.assertEqual(state[k],self.old[s][k])
            with self.assertRaisesRegex(AuthorizationError,'retired'):l.reserve('deepseek-flash',100,1)
        ctx=LiveContext(manifest_path=Path(p['manifest_path']),redaction_names_path=self.deny,stage='final');r=ctx.ledger.reserve('deepseek-flash',100,1);ctx.ledger.settle(r['id'],{'input_tokens':100,'output_tokens':1})
        self.assertEqual(ctx.ledger.snapshot()['totals']['requests_dispatched']+raw['prior_requests_dispatched'],2)
    def test_second_allocation_rejected(self):
        self.create()
        with self.assertRaises(AuthorizationError):create_successor(self.profile,self.p/'another',self.auth,10,{str(self.scope):file_sha(self.scope)})
    def test_incomplete_successor_fail_closed(self):
        p=self.create();(self.p/'next/ready.json').unlink()
        with self.assertRaisesRegex(PriorLedgerError,'incomplete'):LiveContext(manifest_path=Path(p['manifest_path']),redaction_names_path=self.deny,stage='final')
    def test_scope_mutation_rejected(self):
        p=self.create();self.scope.write_text('[1]')
        with self.assertRaisesRegex(PriorLedgerError,'scope changed'):LiveContext(manifest_path=Path(p['manifest_path']),redaction_names_path=self.deny,stage='final')
    def test_open_reservation_prevents_retirement(self):
        self.ledgers['dev'].reserve('deepseek-flash',100,1)
        with self.assertRaises(AuthorizationError):self.create()
        self.assertNotIn('successor_allocation',self.ledgers['final'].snapshot())
    def test_wrong_cap_authority_rejected(self):
        self.auth['total_cap_usd']=101
        with self.assertRaises(AuthorizationError):self.create()

    def test_explicit_total_cap_increase_preserves_prior_accounting(self):
        self.auth['total_cap_usd']=200
        p=self.create();raw=json.loads(Path(p['manifest_path']).read_text())
        self.assertEqual(raw['original_total_cap_usd'],200)
        ctx=LiveContext(manifest_path=Path(p['manifest_path']),redaction_names_path=self.deny,stage='final')
        ctx._check_prior()
        self.assertAlmostEqual(raw['prior_spend_usd']+raw['spend_cap_usd'],200)
        self.assertEqual(raw['prior_requests_dispatched'],1)
        self.assertGreater(raw['prior_spend_usd'],0)
        self.assertEqual(self.ledgers['final'].snapshot()['totals'],self.old['final']['totals'])

    def test_bailian_authority_and_tariff_preserve_history(self):
        with self.assertRaises(AuthorizationError):create_successor(self.profile,self.p/'wrong',self.auth,10,{str(self.scope):file_sha(self.scope)},bailian_route=True)
        self.assertNotIn('successor_allocation',self.ledgers['final'].snapshot())
        self.auth['provider']='Alibaba Cloud Bailian pay-as-you-go'
        p=create_successor(self.profile,self.p/'bailian',self.auth,10,{str(self.scope):file_sha(self.scope)},bailian_route=True)
        raw=json.loads(Path(p['manifest_path']).read_text())
        self.assertEqual(set(raw['models']),{'bailian-deepseek-v4.1-flash'})
        self.assertEqual(raw['provider_route']['model'],'deepseek-v4.1-flash')
        self.assertEqual(self.ledgers['final'].snapshot()['totals'],self.old['final']['totals'])
