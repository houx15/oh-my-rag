"""Audited administrative batches under an unchanged provider/spending manifest.

A batch supplements an old runner deadline; it never replaces that deadline or
resets a ledger. Renewal events and immutable receipts are hash chained. Ordinary
contexts do not inherit permission from a batch. Limits are checked under the
canonical reservation lock, including open and conservatively settled calls.
"""
import hashlib
import json
import math
from pathlib import Path
import time
import uuid
from decimal import Decimal
from eval.optimization.budget import AuthorizationError, AuthorizationManifest, SpendLedger

MODELS = {'deepseek-flash':48, 'deepseek-v4-pro':24}
ARM_PAIRS = {('C1','C9S'),('C1','C10D'),('C1','C11B'),('C10D','C12P'),('C10D','C13T'),('C14E','C14T'),('C1','C15T')}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_chain(events):
    previous=None;ids=set()
    if not isinstance(events,list):raise AuthorizationError('invalid batch history')
    for event in events:
        body={k:v for k,v in event.items() if k!='sha256'}
        if body.get('previous_sha256')!=previous or digest(body)!=event.get('sha256') or body.get('id') in ids:
            raise AuthorizationError('batch history chain mismatch')
        ids.add(body['id']);previous=event['sha256']



def validate_audit(state):
    events=state.get('batch_renewals',[]);validate_chain(events)
    for e in events:
        if state['deadline_epoch']!=e['original_deadline_epoch'] or digest(state['reservations'][:e['baseline_reservations_count']])!=e['baseline_reservations_sha256']:
            raise AuthorizationError('renewal historical snapshot changed')
    closures=state.get('batch_closures',[]);validate_chain(closures)
    for c in closures:
        records=[r for r in state['reservations'] if r.get('batch_id')==c['batch_id']]
        if digest(records)!=c['reservations_sha256']:raise AuthorizationError('closed batch reservations changed')


def activate(*, profile_path, root, name, reason, output, candidate_arm="C9S", baseline_arm="C1"):
    """Record one explicitly scoped batch; no network, deadline reset or new ledger."""
    from newdomain.profile import load_profile,verify_profile
    from newdomain.paths import _ensure_outside_repo
    root=_ensure_outside_repo(Path(root),'Private batch');output=_ensure_outside_repo(Path(output),'Batch receipt')
    if not isinstance(reason,str) or not reason.strip():raise AuthorizationError('recorded continuation reason required')
    profile=load_profile(Path(profile_path));paths=verify_profile(profile,'final');manifest=AuthorizationManifest.load(paths['manifest_path'])
    if not manifest.live_allowed() or manifest.max_retries!=0:raise AuthorizationError('existing authorization or no-retry constraint invalid')
    prior=Decimal(0)
    raw=manifest._raw
    for old in raw.get('prior_runs',[]):
        if file_sha(old['path'])!=old['sha256']:raise AuthorizationError('historical ledger changed')
        state=json.loads(Path(old['path']).read_text())
        if state['totals']['open_reservations']:raise AuthorizationError('historical reservation unresolved')
        prior+=Decimal(str(state['totals']['charged_cost_usd']))
    if prior!=Decimal(str(raw.get('prior_spend_usd',0))):raise AuthorizationError('prior accounting mismatch')
    if Decimal(str(manifest.spend_cap_usd))+prior>Decimal(str(raw.get('original_total_cap_usd',100))):raise AuthorizationError('cumulative cap widened')
    jobs=root/f'{name}-jobs.json';cases=root/f'{name}-cases.json';rows=json.loads(jobs.read_text());case_rows=json.loads(cases.read_text())
    if (baseline_arm,candidate_arm) not in ARM_PAIRS:raise AuthorizationError('unapproved arm pair')
    ids={c['qid'] for c in case_rows}
    if len(ids)!=24 or len(case_rows)!=24 or len(rows)!=48 or len({j['qid'] for j in rows})!=48:raise AuthorizationError('expected frozen 24-case/48-generation batch')
    if {j['qid'] for j in rows}!={q+'-'+arm for q in ids for arm in (baseline_arm,candidate_arm)}:raise AuthorizationError('unexpected generation arms or questions')
    ledger=SpendLedger(paths['ledger_path'],manifest,stage='final',simulated=False)
    with ledger._locked():
        state=ledger._state
        dev=json.loads(Path(profile['dev_ledger_path']).read_text())
        if state['halted'] or dev['halted'] or state['totals']['open_reservations'] or dev['totals']['open_reservations']:raise AuthorizationError('unresolved canonical state')
        validate_audit(state)
        required_calls=sum(MODELS.values())
        if state['totals']['requests_dispatched']+required_calls>manifest.request_cap:
            raise AuthorizationError('insufficient remaining request allowance for complete batch')
        events=state.get('batch_renewals',[]);now=time.time()
        closures=state.get('batch_closures',[]);validate_chain(closures)
        closed={c['batch_id'] for c in closures}
        if any(e['deadline_epoch']>now and e['id'] not in closed for e in events):raise AuthorizationError('another batch remains active')
        body={'id':uuid.uuid4().hex,'recorded_epoch':now,'deadline_epoch':now+3600,'original_deadline_epoch':state['deadline_epoch'],
              'reason':reason.strip(),'kind':'administrative_batch_under_existing_user_scope','stage':'final','max_calls':72,'model_max_calls':MODELS,
              'additional_committed_cap_usd':'4','max_retries':0,'manifest_path':str(paths['manifest_path']),'manifest_sha256':file_sha(paths['manifest_path']),
              'ledger_path':str(paths['ledger_path']),'denylist_path':str(paths['redaction_names_path']),'denylist_sha256':file_sha(paths['redaction_names_path']),
              'generation_jobs_path':str(jobs),'generation_jobs_sha256':file_sha(jobs),'review_jobs_path':str(root/f'{name}-axis-jobs.json'),
              'case_path':str(cases),'case_sha256':file_sha(cases),'question_ids':sorted(ids),'candidate_arm':candidate_arm,'baseline_arm':baseline_arm,
              'baseline_reservations_sha256':digest(state['reservations']),'baseline_reservations_count':len(state['reservations']),
              'baseline_totals':dict(state['totals']),'previous_sha256':events[-1]['sha256'] if events else None}
        event=dict(body,sha256=digest(body))
        with output.open('x',encoding='utf-8') as f:
            json.dump(event,f,ensure_ascii=False,indent=2);f.flush()
            import os
            os.fsync(f.fileno())
        state.setdefault('batch_renewals',[]).append(event)
    return event


class BatchPolicy:
    def __init__(self,path,manifest_path,stage,denylist_path):
        self.path=Path(path).resolve();self.event=json.loads(self.path.read_text());e=self.event
        if digest({k:v for k,v in e.items() if k!='sha256'})!=e.get('sha256'):raise AuthorizationError('batch receipt hash mismatch')
        if stage!='final' or e.get('stage')!=stage or str(Path(manifest_path).resolve())!=e.get('manifest_path') or str(Path(denylist_path).resolve())!=e.get('denylist_path'):raise AuthorizationError('batch scope mismatch')
        if e.get('model_max_calls')!=MODELS or type(e.get('max_calls')) is not int or e['max_calls']!=72 or e.get('additional_committed_cap_usd')!='4' or e.get('max_retries')!=0:raise AuthorizationError('batch limits changed')
        for field in ('recorded_epoch','deadline_epoch'):
            if isinstance(e.get(field),bool) or not isinstance(e.get(field),(int,float)) or not math.isfinite(e[field]):raise AuthorizationError('invalid batch time')
        if not 0<e['deadline_epoch']-e['recorded_epoch']<=3600:raise AuthorizationError('batch window widened')
        if (e.get('baseline_arm','C1'),e.get('candidate_arm','C9S')) not in ARM_PAIRS:raise AuthorizationError('unapproved arm pair')
        self.id=e['id'];self.check_files()

    def check_files(self):
        if json.loads(self.path.read_text())!=self.event:raise AuthorizationError('batch receipt changed')
        for field,hashfield in [('manifest_path','manifest_sha256'),('denylist_path','denylist_sha256'),('generation_jobs_path','generation_jobs_sha256'),('case_path','case_sha256')]:
            if file_sha(self.event[field])!=self.event[hashfield]:raise AuthorizationError('batch input scope changed')

    def check_deadline(self,state):
        validate_audit(state)
        e=self.event;events=state.get('batch_renewals',[])
        closures=state.get('batch_closures',[]);validate_chain(closures)
        if any(c['batch_id']==self.id for c in closures):raise AuthorizationError('batch is closed')
        if e not in events or str(Path(e['ledger_path']).resolve())!=str(Path(e['manifest_path']).parent/'ledger.final.json'):raise AuthorizationError('batch is not recorded on canonical ledger')
        if state['deadline_epoch']!=e['original_deadline_epoch']:raise AuthorizationError('original deadline changed')
        n=e['baseline_reservations_count']
        if digest(state['reservations'][:n])!=e['baseline_reservations_sha256']:raise AuthorizationError('historical reservations changed')
        if any(r.get('batch_id')!=self.id for r in state['reservations'][n:]):raise AuthorizationError('untagged or foreign reservation in active batch')
        if not e['recorded_epoch']<=time.time()<=e['deadline_epoch']:raise AuthorizationError('batch execution window expired or not started')
        self.check_files()

    def bind_jobs(self,ledger,path,model,rows):
        self.check_files();path=Path(path).resolve();e=self.event
        expected=e['generation_jobs_path'] if model=='deepseek-flash' else e['review_jobs_path'] if model=='deepseek-v4-pro' else None
        if str(path)!=expected or len(rows)!=MODELS.get(model):raise AuthorizationError('unexpected batch job file or count')
        expected_ids={q+'-'+arm for q in e['question_ids'] for arm in (e.get('baseline_arm','C1'),e.get('candidate_arm','C9S'))} if model=='deepseek-flash' else set(e['question_ids'])
        if {r['qid'] for r in rows}!=expected_ids:raise AuthorizationError('batch question scope changed')
        binding={'batch_id':self.id,'model':model,'path':str(path),'sha256':file_sha(path)}
        with ledger._locked():
            self.check_deadline(ledger._state)
            bindings=ledger._state.setdefault('batch_job_bindings',[]);found=[b for b in bindings if b['batch_id']==self.id and b['model']==model]
            if found and found!=[binding]:raise AuthorizationError('batch jobs already bound differently')
            if not found:bindings.append(binding)

    def admit(self,state,model,estimate,is_retry):
        self.check_deadline(state)
        if is_retry or model not in MODELS:raise AuthorizationError('batch retry/model forbidden')
        bindings=[b for b in state.get('batch_job_bindings',[]) if b['batch_id']==self.id and b['model']==model]
        if len(bindings)!=1 or file_sha(bindings[0]['path'])!=bindings[0]['sha256']:raise AuthorizationError('batch jobs unbound or changed')
        records=[r for r in state['reservations'] if r.get('batch_id')==self.id]
        if len(records)>=72 or sum(r['model']==model for r in records)>=MODELS[model]:raise AuthorizationError('batch call limit reached')
        committed=sum(Decimal(str(r['est_cost_usd'] if r['state']=='open' else r['charged_usd'])) for r in records)
        if committed+Decimal(str(estimate))>Decimal('4'):raise AuthorizationError('batch charged-plus-reserved cap exceeded')


def remaining_timeout(policy, default):
    remaining=policy.event['deadline_epoch']-time.time()
    if remaining<=0:raise AuthorizationError('batch execution window expired')
    return min(default,remaining)


def close_batch(path, reason):
    e=json.loads(Path(path).read_text());policy=BatchPolicy(path,e['manifest_path'],'final',e['denylist_path']);manifest=AuthorizationManifest.load(Path(e['manifest_path']));ledger=SpendLedger(Path(e['ledger_path']),manifest,stage='final')
    if not isinstance(reason,str) or not reason.strip():raise AuthorizationError('closure reason required')
    with ledger._locked():
        validate_audit(ledger._state)
        events=ledger._state.get('batch_renewals',[])
        if e not in events:raise AuthorizationError('batch receipt missing from ledger')
        records=[r for r in ledger._state['reservations'] if r.get('batch_id')==e['id']]
        if any(r['state']=='open' for r in records):raise AuthorizationError('batch reservations unresolved')
        closures=ledger._state.setdefault('batch_closures',[]);validate_chain(closures)
        if any(c['batch_id']==e['id'] for c in closures):raise AuthorizationError('batch already closed')
        body={'id':uuid.uuid4().hex,'batch_id':e['id'],'recorded_epoch':time.time(),'reason':reason.strip(),'calls':len(records),'charged_usd':str(sum(Decimal(str(r['charged_usd'])) for r in records)),'reservations_sha256':digest(records),'previous_sha256':closures[-1]['sha256'] if closures else None}
        event=dict(body,sha256=digest(body));closures.append(event)
    return event
