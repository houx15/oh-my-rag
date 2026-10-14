"""Opt-in schema reminder, independently written; no output repair or retries."""
import copy,json
from newdomain import baseline


def contract(corpus):
    if corpus in ('guangming','regression'):
        return {'root':{'sentences':'array'},'sentences_min':1,'sentences_max':baseline.MAX_SENTENCES,
                'fact_fields':['text','evidence'],'text_max_chars':baseline.MAX_TEXT_CHARS,
                'evidence_max':baseline.MAX_CITATIONS,'evidence':'distinct displayed E handles only',
                'boundary':'only previously declared exact templates; evidence=[]'}
    if corpus=='niuhuang':
        return {'root':{'sentences':'array','handoff':'optional false'},'sentences_min':1,'sentences_max':3,
                'fact_fields':['text','citations'],'text_max_chars':100,
                'citation_fields':['id','segs'],'segs':'one displayed integer or two ascending endpoints, never invented',
                'boundary_fields':['boundary'],'boundary_values':['clarify','no_evidence','personal','modern_boundary'],
                'clarify':'exclusive whole answer'}
    raise ValueError('unknown corpus')


def messages(original,corpus):
    out=copy.deepcopy(original)
    out[0]['content']+='\n统一输出契约检查（仅整理前述格式要求，不改变可答内容）：'+json.dumps(contract(corpus),ensure_ascii=False)+'\n只输出此JSON对象；不要混用事实对象和边界对象字段，不要新增字段。保持所问事实、适用条件和必要限定，不以删除事实换取格式通过。'
    return out
