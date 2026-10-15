"""Six-case, fixed evidence diagnostic. Explicit live action; shared ledger only."""
import argparse,hashlib,json,random,sys,time
from pathlib import Path
from decimal import Decimal
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R),str(R/'scripts')]
from scripts.keyword_experiment import read,write,lines,H,start_ctx,append,caller
from scripts.grounded_prose_benchmark import Runtime
from newdomain.journal import DispatchJournal
IDS=['GM:GM-349','GM:GM-120','NH:R063','NH:NH-LIVE-07','NH:NH-LIVE-26','REG:REG-FAQ-04']

def prepare(n):
 b=n.parent;cfg=read(b/'component-A1-C1-development-20261014/configuration.json');rt=Runtime(cfg['base_runtime'],cfg['redaction_names_path'],cfg['institution_policy_path'])
 pool={x['case_id']:x for x in read(b/'dependency-swaps-offline-20261014/frozen-inputs.json')};old={x['case_id']:x for x in read(b/'component-A1-C1-development-20261014/answer-jobs.json')if x['arm']=='baseline'}
 annotations={
 IDS[0]:{'required':['Subsidy starts on agreement signing, not application','Application, initial review, re-review, expert review, admission deliberation before signing'],'optional':['Area/duration cap not mandatory for this timing/process question'],'template':'资料记载：先提出入驻申请，经过运营方资格初审、区科创中心资格复审、专家评审和入驻审议，再核发入驻通知书并签订相关协议；租金补贴自协议签订之日起算，不是申请之日。'},
 IDS[1]:{'required':['Give a supported concise introduction to Guangming','Do not claim to switch the Pad or execute an interface action'],'optional':['Any supported introductory facets sufficient; no exhaustive reference checklist'],'template':'我无法直接切换现场Pad。资料将光明区介绍为粤港澳大湾区综合性国家科学中心先行启动区，并介绍了当地利用科学资源推进科技与基层治理结合的做法。'},
 IDS[2]:{'required':['Identify Bencao Gangmu as a materia medica work by Ming Li Shizhen','Include at least one supported organizing feature or scope fact'],'optional':['1897 entries, memory register and cow-bezoar formula count not required for concise introduction'],'template':'《本草纲目》是明代李时珍编撰的本草著作，共52卷。资料介绍其内容包括序例、百病主治和药物各论，药物按十六部、六十类组织。'},
 IDS[3]:{'required':['Describe contrast between both named formulas using their respective historical records','Keep scope historical and source/version-specific; no personal-use or modern superiority claim'],'optional':['No exhaustive ingredient or dosage list required'],'template':'按本次古籍记录比较：《温病条辨》的安宫牛黄丸条文记载了黄连、郁金等组成，并述及因热而发的痉厥；《太平惠民和剂局方》的牛黄清心丸条文记载白芍药、麦门冬等组成，以及诸风、语言謇涩、心怔健忘等主治。这里比较的是所引古籍条目，不能据此替个人选择用药。'},
 IDS[4]:{'required':['Only a legend of accidental discovery is supplied','No invented discovery sequence or book documenting that discovery; express source-limited gap'],'optional':['No unrelated Wupu Bencao background'],'template':'本次资料仅记载“相传，扁鹊无意间发现了牛黄的作用”，没有交代具体发现经过，也没有提供记载这一发现过程的书籍出处。'},
 IDS[5]:{'required':['Do not fabricate a trial identifier','Explain the supplied evidence gap or inability to supply a verifiable identifier'],'optional':['Do not endorse medical claims in the FAQ'],'template':'不能编造试验编号。本次提供的FAQ没有给出可核验的试验编号，不能凭空补足出处。'}}
 jobs=[];prepared=[]
 for cid in IDS:
  j=old[cid];raw=pool[cid]['candidate_records'];base=j['context']
  if cid==IDS[0]:oracle={'D01:6:01':raw['D01:6:01'][raw['D01:6:01'].index('第十四条'):raw['D01:6:01'].index('— 6')].rstrip(),'D01:7:01':raw['D01:7:01'][:raw['D01:7:01'].index('第十五条')].rstrip()}
  elif cid==IDS[1]:
   s=raw['D37:word/document.xml:18'];a=s.index('作为粤港澳');z=s.index('\n',a);oracle={'D37:word/document.xml:18':s[a:z]}
  elif cid==IDS[2]:oracle={'MD-038':base['MD-038']}
  elif cid==IDS[3]:oracle={'MD-057-0002':base['MD-057-0002'],'MD-028-0004':base['MD-028-0004'].split('\n通行本原文：')[0]}
  elif cid==IDS[4]:oracle={'MY-005':'\n'.join(base['MY-005'].splitlines()[:2])}
  else:oracle=dict(base)
  provenance=[]
  for rid,text in oracle.items():
   source=raw.get(rid,base.get(rid));start=source.find(text);assert start>=0
   provenance.append({'source_id':rid,'start':start,'end':start+len(text),'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'quote':text})
  template={'text':annotations[cid]['template'],'citations':provenance,'manual_source_review':True,'automatic_pipeline':False}
  prepared.append({'case_id':cid,'question':j['question'],**annotations[cid],'template_answer':template,'oracle_context':oracle,'baseline_bytes':sum(len(t.encode())for t in base.values()),'oracle_bytes':sum(len(t.encode())for t in oracle.values())})
  for arm,ctx in [('baseline',base),('complete_evidence',oracle)]:
   t=time.perf_counter();msg=j['messages']
   if arm!='baseline' and ctx!=base:
    if j['corpus']=='niuhuang':
     from newdomain.citation_contract_v3 import messages
     msg=messages(rt.base.nh_messages(j['question'],ctx))
    else:
     from newdomain.candidate import build_messages
     meta=rt.base.gm['candidate'][3];msg=build_messages(j['question'],[{**meta.get(k,{}),'id':k,'text':v,'title':meta[k]['title'],'locator':meta[k]['locator']}for k,v in ctx.items()]);msg=rt.base.pipelines['baseline'].prepare_gm(j['question'],ctx,msg,meta)['messages']
   msg[0]=dict(j['messages'][0])  # Freeze baseline system instructions; only evidence payload differs.
   ctx=rt.redactor.value(ctx);msg=rt.redactor.value(msg)
   assert len(json.dumps(msg,ensure_ascii=False).encode())<=30000
   assert msg[0]['content']==j['messages'][0]['content'],'system prompt changed'
   jobs.append({**j,'qid':cid+'/'+arm,'arm':arm,'context':ctx,'messages':msg,'diagnostic_preparation_ms':(time.perf_counter()-t)*1000})
 random.Random(15102026).shuffle(jobs)
 write(n/'configuration.json',{k:cfg[k]for k in ['base_runtime','redaction_names_path','institution_policy_path']});write(n/'jobs.json',jobs);write(n/'source-review-and-templates.json',prepared)
 # Screening checks before allocation, repeated by transport at dispatch.
 from newdomain.institution_fields import screen_approved_institutions
 for j in jobs:screen_approved_institutions(j['messages'],Path(cfg['redaction_names_path']),read(cfg['institution_policy_path']))
 write(n/'freeze.json',{'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [n/'jobs.json',n/'source-review-and-templates.json',n/'configuration.json',n/'plan.md',Path(__file__)]},'calls':12,'stage_cap_usd':3,'generation_model':'deepseek-v4.1-flash','screened':True,'source_review':'assistant, not independent human gold'})
 print('FROZEN',len(jobs),'screened jobs')

def allocate(n):
 from newdomain.bailian_workspace_successor import create_successor
 b=n.parent;live=read(b/'LIVE-OPTIMIZATION-STATUS.json');assert live['active_paid_run']is None
 old=Path(live['latest_profile']);m=read(read(old)['manifest_path']);scope={path:hashlib.sha256(Path(path).read_bytes()).hexdigest()for path in m['scope_hashes']}
 for p in [n/'freeze.json',*map(Path,read(n/'freeze.json')['hashes'])]:scope[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 authority=read(b/'bailian-resume-20261013/authority.json');authority.update(total_cap_usd=200,user_instruction='User approved the three-way evidence diagnostic with 好，那我们试一下 after proposing current evidence, source-reviewed complete evidence and direct templates. Scope 6 exposed cases, 12 serial generation calls max, $3 conservative stage cap within $200 cumulative, no reviews/retries/new providers/uploads/deployment; late outputs diagnostic only.')
 d=n/'answers';d.mkdir(exist_ok=True);profile=create_successor(old,d/'allocation',authority,12,scope,bailian_route=True,public_source_policy_path=b/'public-source-restoration-20261013/institution-policy.json')
 live.update(active_paid_run=str(d),latest_profile=str(d/'allocation/profile.json'),status='evidence_ceiling_active',active_expected=12,active_completed=0);write(b/'LIVE-OPTIMIZATION-STATUS.json',live);print('ALLOCATED prior',read(profile['manifest_path'])['prior_spend_usd'])

def run(n):
 from newdomain import bailian_bounded_transport as transport
 for p,h in read(n/'freeze.json')['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
 d=n/'answers';ctx=start_ctx(d);cfg=read(n/'configuration.json');rt=Runtime(**cfg);done={r['qid']for r in lines(d/'results.jsonl')}
 with DispatchJournal(d/'calls.journal.jsonl')as journal:
  call=caller(d,ctx,transport,journal)
  for j in read(n/'jobs.json'):
   if j['qid']in done:continue
   totals=read(read(d/'allocation/profile.json')['final_ledger_path'])['totals']
   if Decimal(str(totals['charged_cost_usd']))+Decimal('2.0064')>Decimal(3):raise ValueError('stage worst-case headroom exhausted')
   item={'qid':j['qid'],'case_id':j['case_id'],'arm':j['arm'],'corpus':j['corpus']}
   try:
    raw,ms=call(j['qid'],'generation',j['messages']);item.update(raw=raw,generation_wall_ms=ms)
    t=time.perf_counter()
    try:
     a,v,g=rt.canonical({**j,'arm':'baseline'},raw)
     if v:
      for s in a['sentences']:
       for c in s['citations']:assert c['quote'] and c['quote']in j['context'][c['id']]
     item.update(answer=a,valid=v,gate=g)
    except Exception as e:item.update(valid=False,validation_error=str(e))
    item['validation_ms']=(time.perf_counter()-t)*1000;item['cached_component_sum_ms']=ms+item['validation_ms']+j['diagnostic_preparation_ms'];item['within_2s']=item['cached_component_sum_ms']<=2000
   except Exception as e:
    item['execution_error']=type(e).__name__+':'+str(e);append(d/'results.jsonl',item);print('STOP',item,flush=True);break
   append(d/'results.jsonl',item);print('DONE',j['qid'],'valid',item['valid'],'ms',round(item['cached_component_sum_ms']),flush=True)

def close(n):
 d=n/'answers';p=read(d/'allocation/profile.json');m=read(p['manifest_path']);t=read(p['final_ledger_path'])['totals'];assert t['open_reservations']==0
 total=Decimal(str(m['prior_spend_usd']))+Decimal(str(t['charged_cost_usd']));b=n.parent;live=read(b/'LIVE-OPTIMIZATION-STATUS.json');assert live['active_paid_run']==str(d)
 live.update(active_paid_run=None,status='evidence_ceiling_collected',cumulative_spend_usd=str(total),cumulative_conservative_spend_usd=float(total),remaining_cumulative_usd=str(Decimal(200)-total),open_reservations=0,active_completed=len(lines(d/'results.jsonl')));write(b/'LIVE-OPTIMIZATION-STATUS.json',live);write(n/'cost.json',{'totals':t,'cumulative_usd':str(total),'remaining_usd':str(Decimal(200)-total)});print('CLOSED',total,t)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','allocate','run','close']);p.add_argument('--directory',type=Path,required=True);p.add_argument('--live',action='store_true');a=p.parse_args()
 if a.action in ('allocate','run')and not a.live:raise ValueError('explicit --live required')
 globals()[a.action](a.directory)
