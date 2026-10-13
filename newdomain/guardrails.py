"""Opt-in local safeguards; C1 defaults and provider accounting are unchanged.

Record routing uses only explicit query premises. Contract normalization supplies
empty evidence only for the exact two protocol sentences. Neither creates facts,
citations, provider usage or a claim of human-reviewed correctness.
"""
import copy
import json
import re
from newdomain import candidate

REFUSAL='本次资料未包含回答该问题所需的依据。'


def route_missing_record(question):
    q=re.sub(r'\s+','',question)
    unknown=bool(re.search(r'未指名|未具名|(?:未|没有|没)(?:提供|说明|给出|告知).{0,12}(?:名称|名字|哪家|身份|申请记录|审批记录|到账记录|支付记录)',q))
    if not unknown:return None
    # Explicitly supplied records or a request that excludes actual-record
    # questions must not be turned into an unnecessary refusal.
    if re.search(r'(?:已提供|提供了|附有|给出如下).{0,8}(?:到账明细|到账记录|支付记录|银行流水|审批记录)',q):return None
    if re.search(r'(?:不问|不查询|不需要知道|不涉及|并非询问).{0,8}(?:实际|具体|到账|审批结果)',q):return None
    actual=bool(re.search(r'(?:到账|实际收到|已经收到|获批).{0,14}(?:多少|几|金额|数额)|(?:给出|报出|确认|确定).{0,40}(?:到账额|到账金额|审批结果|审批结论|被接收|被批准)|(?:一定|确定).{0,12}(?:获批|被批准|入园)',q))
    if not actual:return None
    return {'sentences':[{'text':REFUSAL,'citations':[]}],'handoff':False}


def route_receipt(question):
    answer=route_missing_record(question)
    return {'routed':answer is not None,'answer':answer,'engine':'local_missing_record_rule' if answer else 'unchanged_C1_fallback',
            'model_usage':None,'provenance':'deterministic_protocol_not_model'}


FIXED = {'本次资料未包含回答该问题所需的依据。', '以上为资料记载的转述，不构成投资或医疗建议。'}


def normalize_protocol_sentences(response):
    trace=[]
    if not isinstance(response,dict) or not isinstance(response.get('content'),str):return response,trace
    try:parsed=json.loads(response['content'],object_pairs_hook=candidate._no_dup_keys,parse_constant=candidate._no_nonfinite)
    except (ValueError,TypeError):return response,trace
    if not isinstance(parsed,dict) or set(parsed)!={'sentences'} or not isinstance(parsed['sentences'],list):return response,trace
    for i,sentence in enumerate(parsed['sentences']):
        if isinstance(sentence,dict) and set(sentence)=={'text'} and sentence['text'] in FIXED:
            sentence['evidence']=[];trace.append({'sentence_index':i,'operation':'assemble_empty_evidence_for_exact_protocol_sentence','origin':'deterministic_protocol_not_model'})
    if not trace:return response,trace
    result=copy.deepcopy(response);result['content']=json.dumps(parsed,ensure_ascii=False);return result,trace


def guarded_call(question, fallback):
    """Skip provider dispatch only for an explicit local boundary decision.

    The fallback retains its existing authorization, privacy and ledger path.
    Local outputs are explicitly marked; no model response or usage is invented.
    """
    decision=route_receipt(question)
    if decision['routed']:
        return dict(decision, cost_usd=0.0)
    return fallback(question)
