import copy
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from eval.optimization.budget import AuthorizationError,AuthorizationManifest,SpendLedger
from newdomain.batch import activate,BatchPolicy,file_sha,close_batch,remaining_timeout
from newdomain.transport import LiveContext,LiveAuthorizationError

class BatchRenewalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.path=self.root/'manifest.json';self.deny=self.root/'deny.json';self.deny.write_text('[]')
        data={'authorized':True,'currency':'USD','spend_cap_usd':100,'original_total_cap_usd':100,'prior_spend_usd':0,'prior_runs':[],'final_eval_reserve_usd':30,'max_input_tokens':6000,'max_output_tokens':800,'request_cap':1800,'max_retries':0,'selector_deadline_s':30,'global_deadline_s':1,'max_concurrency':3,'models':{m:{'input_per_1m':1,'output_per_1m':0,'verified':True,'context_tokens_upper_bound':10} for m in ['deepseek-flash','deepseek-v4-pro']}}
        self.path.write_text(json.dumps(data));self.manifest=AuthorizationManifest.load(self.path)
        for stage in ['dev','final']:SpendLedger(self.root/f'ledger.{stage}.json',self.manifest,stage=stage)
        self.ledger=SpendLedger(self.root/'ledger.final.json',self.manifest,stage='final');r=self.ledger.reserve('deepseek-flash',100000,1);self.ledger.settle(r['id'],{'input_tokens':100000,'output_tokens':1})
        with self.ledger._locked():self.ledger._state['deadline_epoch']=time.time()-10
        self.before=self.ledger.snapshot();self.profile=self.root/'profile.json';self.profile.write_text(json.dumps({'manifest_path':str(self.path),'manifest_sha256':file_sha(self.path),'dev_ledger_path':str(self.root/'ledger.dev.json'),'final_ledger_path':str(self.root/'ledger.final.json'),'redaction_names_path':str(self.deny)}))
        self.jobs=[{'qid':f'Q{i}-{arm}','messages':[{'role':'system','content':'test'},{'role':'user','content':'synthetic'}]} for i in range(24) for arm in ['C1','C9S']];self.jobs_path=self.root/'scope-jobs.json';self.jobs_path.write_text(json.dumps(self.jobs));(self.root/'scope-cases.json').write_text(json.dumps([{'qid':f'Q{i}'} for i in range(24)]));self.receipt=self.root/'batch.json'
    def tearDown(self):self.tmp.cleanup()
    def active(self):
        activate(profile_path=self.profile,root=self.root,name='scope',reason='Explicit synthetic test continuation; no provider calls.',output=self.receipt)
        p=BatchPolicy(self.receipt,self.path,'final',self.deny);l=SpendLedger(self.root/'ledger.final.json',self.manifest,stage='final',batch_policy=p);p.bind_jobs(l,self.jobs_path,'deepseek-flash',self.jobs);return p,l
    def test_original_deadline_and_history_preserved(self):
        p,l=self.active();after=l.snapshot();self.assertEqual(after['deadline_epoch'],self.before['deadline_epoch']);self.assertEqual(after['reservations'],self.before['reservations']);self.assertEqual(after['totals'],self.before['totals']);self.assertEqual(len(after['batch_renewals']),1)
        with self.assertRaises(AuthorizationError):self.ledger.reserve('deepseek-flash',10,1)
        with self.assertRaises(LiveAuthorizationError):LiveContext(manifest_path=self.path,redaction_names_path=self.deny,stage='final')
        ctx=LiveContext(manifest_path=self.path,redaction_names_path=self.deny,stage='final',batch_path=self.receipt);self.assertEqual(ctx.batch_policy.id,p.id)
    def test_open_reservations_count_toward_cap(self):
        p,l=self.active();r=l.reserve('deepseek-flash',3000000,1)
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',1000001,1)
        l.settle(r['id'],{'input_tokens':1000,'output_tokens':1});r=l.reserve('deepseek-flash',3000000,1);l.settle(r['id'],None)
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',1000000,1)
    def test_model_retry_and_expiry_rejected(self):
        p,l=self.active()
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1,is_retry=True)
        with self.assertRaises(AuthorizationError):p.admit(l.snapshot(),'unapproved',0,False)
        with patch('newdomain.batch.time.time',return_value=p.event['deadline_epoch']+1):
            with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1)
    def test_phase_limit_survives_reconstruction(self):
        p,l=self.active()
        for _ in range(48):
            r=l.reserve('deepseek-flash',10,1);l.settle(r['id'],{'input_tokens':10,'output_tokens':1})
        l=SpendLedger(self.root/'ledger.final.json',self.manifest,stage='final',batch_policy=BatchPolicy(self.receipt,self.path,'final',self.deny))
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1)
        reviews=[{'qid':f'Q{i}','messages':[]} for i in range(24)];path=self.root/'scope-axis-jobs.json';path.write_text(json.dumps(reviews));p.bind_jobs(l,path,'deepseek-v4-pro',reviews)
        for _ in range(24):
            r=l.reserve('deepseek-v4-pro',10,1);l.settle(r['id'],{'input_tokens':10,'output_tokens':1})
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-v4-pro',10,1)
        self.assertEqual(len([r for r in l.snapshot()['reservations'] if r.get('batch_id')==p.id]),72)
    def test_changed_job_or_scope_rejected(self):
        p,l=self.active();self.jobs_path.write_text('[]')
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1)
    def test_changed_original_deadline_rejected(self):
        p,l=self.active()
        with l._locked():l._state['deadline_epoch']+=1
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1)
    def test_changed_prior_reservation_rejected(self):
        p,l=self.active()
        with l._locked():l._state['reservations'][0]['created_epoch']+=1
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1)
    def test_receipt_and_ledger_must_agree(self):
        p,l=self.active()
        with l._locked():l._state['batch_renewals'][0]['reason']='rewritten history'
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1)
    def test_concurrent_admission_cannot_double_spend(self):
        p,l=self.active();barrier=threading.Barrier(2);out=[]
        def run():
            other=SpendLedger(self.root/'ledger.final.json',self.manifest,stage='final',batch_policy=p);barrier.wait()
            try:other.reserve('deepseek-flash',3000000,1);out.append('accepted')
            except AuthorizationError:out.append('rejected')
        threads=[threading.Thread(target=run) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(5);self.assertFalse(t.is_alive())
        self.assertCountEqual(out,['accepted','rejected'])
    def test_active_batch_cannot_be_duplicated(self):
        self.active()
        with self.assertRaises(AuthorizationError):activate(profile_path=self.profile,root=self.root,name='scope',reason='duplicate',output=self.root/'other.json')
    def test_unbound_model_and_wrong_review_questions_rejected(self):
        p,l=self.active()
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-v4-pro',10,1)
        path=self.root/'scope-axis-jobs.json';rows=[{'qid':f'Wrong{i}'} for i in range(24)];path.write_text(json.dumps(rows))
        with self.assertRaises(AuthorizationError):p.bind_jobs(l,path,'deepseek-v4-pro',rows)

    def test_closure_preserves_history_and_blocks_new_calls(self):
        p,l=self.active();before=l.snapshot();close_batch(self.receipt,'completed synthetic work')
        after=l.snapshot();self.assertEqual(before['reservations'],after['reservations']);self.assertEqual(before['batch_renewals'],after['batch_renewals'])
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1)
        new=activate(profile_path=self.profile,root=self.root,name='scope',reason='separately recorded next synthetic batch',output=self.root/'next.json')
        self.assertEqual(new['previous_sha256'],p.event['sha256']);self.assertEqual(len(l.snapshot()['batch_renewals']),2)
    def test_cannot_close_unresolved_reservation(self):
        p,l=self.active();l.reserve('deepseek-flash',10,1)
        with self.assertRaises(AuthorizationError):close_batch(self.receipt,'incomplete')
    def test_worker_wall_time_cannot_cross_batch_deadline(self):
        p,l=self.active()
        with patch('newdomain.batch.time.time',return_value=p.event['deadline_epoch']-2):self.assertEqual(remaining_timeout(p,60),2)
        with patch('newdomain.batch.time.time',return_value=p.event['deadline_epoch']+1):
            with self.assertRaises(AuthorizationError):remaining_timeout(p,60)

    def test_removing_batch_tag_cannot_reset_accounting(self):
        p,l=self.active();r=l.reserve('deepseek-flash',10,1);l.settle(r['id'],{'input_tokens':10,'output_tokens':1})
        with l._locked():l._state['reservations'][-1].pop('batch_id')
        with self.assertRaises(AuthorizationError):l.reserve('deepseek-flash',10,1)


    def test_explicit_candidate_arm_pinned(self):
        self.jobs=[dict(j,qid=j['qid'].replace('C9S','C10D')) for j in self.jobs];self.jobs_path.write_text(json.dumps(self.jobs))
        with self.assertRaises(AuthorizationError):activate(profile_path=self.profile,root=self.root,name='scope',reason='test',output=self.receipt)
        event=activate(profile_path=self.profile,root=self.root,name='scope',reason='test',output=self.receipt,candidate_arm='C10D')
        self.assertEqual(event['candidate_arm'],'C10D')
        p=BatchPolicy(self.receipt,self.path,'final',self.deny);l=SpendLedger(self.root/'ledger.final.json',self.manifest,stage='final',batch_policy=p);p.bind_jobs(l,self.jobs_path,'deepseek-flash',self.jobs)
        wrong=[dict(j,qid=j['qid'].replace('C10D','C9S')) for j in self.jobs]
        with self.assertRaises(AuthorizationError):p.bind_jobs(l,self.jobs_path,'deepseek-flash',wrong)


    def test_nondefault_baseline_is_explicit_and_pinned(self):
        self.jobs=[dict(j,qid=j['qid'].replace('C1','C10D').replace('C9S','C12P')) for j in self.jobs];self.jobs_path.write_text(json.dumps(self.jobs))
        with self.assertRaises(AuthorizationError):activate(profile_path=self.profile,root=self.root,name='scope',reason='test',output=self.receipt,candidate_arm='C12P')
        event=activate(profile_path=self.profile,root=self.root,name='scope',reason='test',output=self.receipt,candidate_arm='C12P',baseline_arm='C10D')
        self.assertEqual(event['baseline_arm'],'C10D')
        p=BatchPolicy(self.receipt,self.path,'final',self.deny);l=SpendLedger(self.root/'ledger.final.json',self.manifest,stage='final',batch_policy=p);p.bind_jobs(l,self.jobs_path,'deepseek-flash',self.jobs)
        with self.assertRaises(AuthorizationError):p.bind_jobs(l,self.jobs_path,'deepseek-flash',[dict(j,qid=j['qid'].replace('C10D','C1')) for j in self.jobs])


    def test_activation_rejects_insufficient_whole_batch_request_allowance(self):
        limited=copy.deepcopy(self.manifest);limited.request_cap=72
        with patch('newdomain.batch.AuthorizationManifest.load',return_value=limited):
            with self.assertRaisesRegex(AuthorizationError,'remaining request allowance'):
                activate(profile_path=self.profile,root=self.root,name='scope',reason='synthetic cap check',output=self.receipt)
        self.assertFalse(self.receipt.exists())
        self.assertEqual(self.ledger.snapshot().get('batch_renewals',[]),[])
    def test_activation_accepts_exact_whole_batch_request_allowance(self):
        limited=copy.deepcopy(self.manifest);limited.request_cap=73
        with patch('newdomain.batch.AuthorizationManifest.load',return_value=limited):
            event=activate(profile_path=self.profile,root=self.root,name='scope',reason='synthetic exact cap check',output=self.receipt)
        self.assertEqual(event['max_calls'],72)
        self.assertEqual(event['baseline_totals']['requests_dispatched'],1)

if __name__=='__main__':unittest.main()
