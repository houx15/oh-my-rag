"""Narrow offline pilot: versioned exact facts, flat/graph parity, no API calls."""
import hashlib
import re


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def route(question):
    # A source-reviewed family router; intentionally not a general intent model.
    if not re.search(r'光明(?:区)?(?:留创园|留学人员创业园)', question):
        return None
    if re.search(r'运营方|多少钱|具体金额|每月|每平方米|资格|符合|能否|获批|名单|天气|电话|联系人|地址|申请材料|哪年|何时生效|废止', question):
        return None
    intents=[]
    if re.search(r'签.{0,8}(?:协议|约).{0,8}前',question) and re.search(r'流程|步骤|程序',question):
        intents.append('before_signing')
    if '租金' in question and re.search(r'起算|开始|从.*算|何时|什么时候',question):
        intents.append('subsidy_start')
    if '租金' in question and re.search(r'上限|最高|最多|最长|面积|年限',question):
        intents.append('subsidy_caps')
    return intents or None


def validate(bundle, sources):
    if {rid:digest(sources[rid]) for rid in bundle['source_hashes']} != bundle['source_hashes']:
        raise ValueError('source version changed')
    for fid,f in bundle['facts'].items():
        if sources[f['source_id']][f['start']:f['end']] != f['text'] or not f['text']:
            raise ValueError('invalid source span: '+fid)
    steps=bundle['ordered_steps']
    if not steps or len(steps)!=len(set(steps)) or any(x not in bundle['facts'] for x in steps):
        raise ValueError('invalid procedure')
    if bundle['signing'] not in steps:
        raise ValueError('signing milestone missing')
    expected={a:b for a,b in zip(steps,steps[1:])}
    if bundle['next'] != expected:
        raise ValueError('broken procedure graph')
    for ids in bundle['intent_facts'].values():
        if any(x not in bundle['facts'] for x in ids):
            raise ValueError('missing fact')
    if bundle['intent_facts']['before_signing'] != steps[:steps.index(bundle['signing'])]:
        raise ValueError('flat/graph procedure mismatch')


def answer(question,bundle,sources,mode='flat'):
    if mode not in ('flat','graph'):
        raise ValueError('unknown mode')
    validate(bundle,sources)
    intents=route(question)
    if intents is None:
        return {'status':'fallback','reason':'outside reviewed intent scope','facts':[]}
    ids=[]
    for intent in intents:
        if mode=='graph' and intent=='before_signing':
            current=bundle['ordered_steps'][0]; selected=[]
            while current != bundle['signing']:
                selected.append(current);current=bundle['next'][current]
        else:
            selected=bundle['intent_facts'][intent]
        ids.extend(selected)
    ids=list(dict.fromkeys(ids))
    facts=[{'id':fid,**bundle['facts'][fid]} for fid in ids]
    return {'status':'answered','intents':intents,'facts':facts,
            'answer':'\n'.join(f"{f['text']} [{f['source_id']}:{f['start']}-{f['end']}]" for f in facts)}
