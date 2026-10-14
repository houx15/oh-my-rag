"""Read live ledger/journal once and refresh the private progress snapshot."""
import argparse,datetime,json,os,sys
from decimal import Decimal
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from scripts.keyword_experiment import read,write,lines

def main():
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);a=p.parse_args();n=a.directory;d=n/'answers';profile=read(d/'allocation/profile.json');manifest=read(profile['manifest_path']);totals=read(profile['final_ledger_path'])['totals'];rs=lines(d/'results.jsonl');jobs=read(n/'answer-jobs.json');cumulative=str(Decimal(str(manifest['prior_spend_usd']))+Decimal(str(totals['charged_cost_usd'])))
 snapshot={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed_outputs':len(rs),'scheduled_outputs':len(jobs),'primary_cases':len({j['case_id']for j in jobs if j['corpus']!='regression'}),'regression_cases':len({j['case_id']for j in jobs if j['corpus']=='regression'}),'execution_failures':sum('execution_failure'in r for r in rs),'scored_outputs':sum(r.get('score')is not None for r in rs),'current_stage_charged_usd':totals['charged_cost_usd'],'current_stage_open_reservations':totals['open_reservations'],'reserved_open_cost_usd':totals['reserved_open_cost_usd'],'requests_dispatched':totals['requests_dispatched'],'retries':totals['retries'],'current_settled_total_usd':cumulative,'remaining_before_open_reservations_usd':str(Decimal('200')-Decimal(cumulative))}
 write(n/'progress.json',snapshot)
 path=n.parent/'LIVE-OPTIMIZATION-STATUS.json';live=read(path)
 if live.get('active_paid_run')==str(d):
  live.update(active_completed=len(rs),active_expected=len(jobs),open_reservations=totals['open_reservations'],current_stage_charged_usd=totals['charged_cost_usd'],current_stage_open_reservations=totals['open_reservations'],current_settled_total_usd=cumulative,cumulative_spend_usd=cumulative,cumulative_conservative_spend_usd=float(cumulative),liveness_verified_utc=snapshot['timestamp_utc'],checkpoint=str(n/'progress.json'))
  temp=path.with_suffix('.tmp');write(temp,live);os.replace(temp,path)
 print(json.dumps(snapshot))
if __name__=='__main__':main()
