"""Offline full-roster source-custody, privacy and budget-planning checks."""
import argparse,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from scripts.keyword_experiment import read,write,lines
from newdomain.grounded_prose import catalog,render
from newdomain.institution_fields import screen_approved_institutions

def main():
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--diagnostic',type=Path,required=True);a=p.parse_args();n=a.directory;b=n.parent;jobs=read(n/'answer-jobs.json');live=read(b/'LIVE-OPTIMIZATION-STATUS.json');profile=read(live['latest_profile']);policy=read(b/'public-source-restoration-20261013/institution-policy.json');checks=0;groups=0;prompt_bytes=0;fail=[]
 by_id={j['qid']:j for j in jobs}
 for j in jobs:
  if 'preparation_failure'in j:fail.append(j['qid']);continue
  screen_approved_institutions(j['messages'],Path(profile['redaction_names_path']),policy)
  prompt_bytes+=len(json.dumps(j['messages'],ensure_ascii=False).encode())
  if j['arm']!='candidate':continue
  base=by_id[j['case_id']+'/baseline'];assert j['context']==base['context'];checks+=1;c=catalog(j['context'])
  for qid,g in c['groups'].items():
   raw={'content':json.dumps({'sentences':[{'qualified':qid}]}),'finish_reason':'stop','stream_done':True,'usage':{'input_tokens':1,'output_tokens':1}}
   out,_=render(raw,j['context'],c['fingerprint']);quote=out['sentences'][0]['citations'][0];assert quote['quote']in j['context'][quote['id']];groups+=1
  for sid,source in c['sources'].items():
   assert source['text']in j['messages'][1]['content']
 assert not fail,fail
 diagnostic=read(a.diagnostic/'answers/settlement.json');calls=diagnostic['totals']['requests_dispatched'];cost=diagnostic['totals']['charged_cost_usd'];total_calls=2*len(jobs);projection=cost/calls*total_calls;remaining=200-float(live['cumulative_spend_usd'])
 # Planning scenarios only: actual reservations use the pinned full context
 # ceiling (1m tokens/call), and actual usage settles each call. This is not a
 # replacement tokenizer proof or an invoice guarantee.
 generation_byte_scenario=prompt_bytes*2/1e6+len(jobs)*800*8/1e6
 review_max_byte_scenario=len(jobs)*(30000*2+800*8)/1e6
 out={'matched_case_inputs':checks,'exact_whole_clause_renders':groups,'all_generation_prompts_screened':True,'preparation_failures':fail,'scheduled_outputs':len(jobs),'max_paid_calls':total_calls,'generation_reuse':0,'historical_exposure':True,'remaining_cumulative_allowance':remaining,'diagnostic_proportional_cost_estimate':projection,'generation_byte_count_scenario':generation_byte_scenario,'maximum_review_byte_scenario':review_max_byte_scenario,'combined_byte_scenario':generation_byte_scenario+review_max_byte_scenario,'planning_not_tokenizer_proof':True,'three_full_context_inflight_reservations':3*(2+.0064),'decision':'Proceed only after diagnostic closure; no promotion. Ledger enforces200 cumulative cap and stops on admission failure; no automatic retries. Most pessimistic all-call full-context billing cannot fit, so complete execution is not guaranteed under adversarial usage; paid actuals determine remaining headroom.'}
 write(n/'offline-verification.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
