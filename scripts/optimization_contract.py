"""Opt-in normalization of the two protocol sentences; never repair factual claims."""
import copy
import json
from newdomain import candidate

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
