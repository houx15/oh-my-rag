"""Explicit new user scope: retire old admission and carry all spend into successor.
Historical reservations, totals, fingerprints and deadlines are never reset.
An interrupted setup leaves old admission retired and no ready new scope.
"""
import copy
from contextlib import ExitStack
from decimal import Decimal
import json
from pathlib import Path
import time
import uuid
from eval.optimization.budget import AuthorizationManifest, AuthorizationError, SpendLedger
from newdomain.batch import digest, file_sha, validate_audit
from newdomain.profile import load_profile, verify_profile
from newdomain.experiment import write_new


def create_successor(profile_path, destination, authority, request_cap, scope_hashes):
    from newdomain.paths import _ensure_outside_repo
    destination=_ensure_outside_repo(Path(destination),'Successor allocation')
    if destination.exists():raise AuthorizationError('successor destination must be new; never restart or overwrite')
    if not isinstance(authority,dict) or authority.get('total_cap_usd') not in (100,200) or not authority.get('user_instruction') or not authority.get('source_thread'):
        raise AuthorizationError('explicit new user scope required')
    if type(request_cap)!=int or not 1<=request_cap<=4000:raise AuthorizationError('bounded new request allocation required')
    if not scope_hashes:raise AuthorizationError('frozen scope hashes required')
    for path,h in scope_hashes.items():
        if file_sha(path)!=h:raise AuthorizationError('scope input changed')
    profile=load_profile(Path(profile_path));verify_profile(profile,'final')
    old_path=Path(profile['manifest_path']);old=AuthorizationManifest.load(old_path)
    ledgers={stage:SpendLedger(Path(profile[stage+'_ledger_path']),old,stage=stage) for stage in ('dev','final')}
    prior=[];total=Decimal(0);requests=0
    for item in old._raw.get('prior_runs',[]):
        if file_sha(item['path'])!=item['sha256']:raise AuthorizationError('historical ledger changed')
        state=json.loads(Path(item['path']).read_text())
        if state['totals']['open_reservations']:raise AuthorizationError('historical open reservation')
        prior.append(copy.deepcopy(item));total+=Decimal(str(state['totals']['charged_cost_usd']));requests+=state['totals']['requests_dispatched']
    if total!=Decimal(str(old._raw['prior_spend_usd'])):raise AuthorizationError('prior sum mismatch')
    with ExitStack() as stack:
        for stage in ('dev','final'):stack.enter_context(ledgers[stage]._locked())
        states={stage:ledgers[stage]._state for stage in ledgers}
        for s in states.values():
            if s.get('successor_allocation') or s['halted'] or s['totals']['open_reservations']:raise AuthorizationError('unresolved or already retired state')
        validate_audit(states['final'])
        closed={c['batch_id'] for c in states['final'].get('batch_closures',[])}
        if any(e['id'] not in closed for e in states['final'].get('batch_renewals',[])):raise AuthorizationError('old batch not closed')
        for stage,s in states.items():total+=Decimal(str(s['totals']['charged_cost_usd']));requests+=s['totals']['requests_dispatched']
        authorized_cap=Decimal(str(authority['total_cap_usd']))
        if authorized_cap < Decimal(str(old._raw.get('original_total_cap_usd',100))):raise AuthorizationError('successor may not silently reduce the cumulative cap')
        remaining=authorized_cap-total
        if remaining<=0:raise AuthorizationError('cumulative cap exhausted')
        destination.mkdir(parents=True)
        event={'id':uuid.uuid4().hex,'recorded_epoch':time.time(),'authority':authority,'successor_directory':str(destination.resolve()),'old_manifest_sha256':file_sha(old_path),'prior_cumulative_usd':str(total),'prior_cumulative_requests':requests,'scope_hashes':scope_hashes,'request_cap':request_cap,'old_state_sha256':{stage:digest(s) for stage,s in states.items()}}
        event['sha256']=digest(event);write_new(destination/'authority-receipt.json',event)
        # Persist retirement on both locked ledgers before deriving their carried hashes.
        for stage,s in states.items():
            s['successor_allocation']=event;ledgers[stage]._persist_locked()
            path=Path(profile[stage+'_ledger_path']);prior.append({'path':str(path),'sha256':file_sha(path),'spent':s['totals']['charged_cost_usd']})
        raw=copy.deepcopy(old._raw)
        raw.update(authorized=True,status_note='User-authorized optimization scope; all prior accounting carried; no new provider, no uploads or deployment.',spend_cap_usd=float(remaining),final_eval_reserve_usd=float(remaining),request_cap=request_cap,global_deadline_s=86400,max_concurrency=3,max_retries=0,prior_runs=prior,prior_spend_usd=float(total),original_total_cap_usd=float(authorized_cap),prior_requests_dispatched=requests,authority_receipt_sha256=file_sha(destination/'authority-receipt.json'),scope_hashes=scope_hashes)
        raw['models']={k:v for k,v in raw['models'].items() if k in ('deepseek-flash','text-embedding-v3')}
        write_new(destination/'manifest.json',raw)
        manifest=AuthorizationManifest.load(destination/'manifest.json')
        for stage in ('dev','final'):SpendLedger(destination/f'ledger.{stage}.json',manifest,stage=stage)
        new_profile=dict(profile,manifest_path=str(destination/'manifest.json'),manifest_sha256=file_sha(destination/'manifest.json'),dev_ledger_path=str(destination/'ledger.dev.json'),final_ledger_path=str(destination/'ledger.final.json'))
        write_new(destination/'profile.json',new_profile)
        write_new(destination/'ready.json',{'authority_receipt_sha256':file_sha(destination/'authority-receipt.json'),'manifest_sha256':file_sha(destination/'manifest.json'),'prior_cumulative_usd':str(total),'prior_cumulative_requests':requests})
    return new_profile
