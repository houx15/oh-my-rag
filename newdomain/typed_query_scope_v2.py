"""Deterministic nonfactual boundary selection for text-only requests.
No clinical facts, reference answers, case IDs or arbitrary prose acceptance.
Uncertain cases continue to the normal source-grounded generator.
"""
import re,json
from newdomain.citation_contract_v3 import CLARIFY
CLINICAL='本次提供的是历史文献，不能据此认定对现代疾病的疗效或给出用药方案。'
PERSONAL='本次提供的历史资料不能判断您当前症状的原因或适合您的处理方法；请向合格医师核实。'

def response(question, facet_index):
    historical=any(x in question for x in ('古籍','古方','记载','主治','药典','编首','历史','歌'))
    current=any(x in question for x in ('我','经常','最近','建议','怎么办'))
    symptom=any(x in question for x in ('口腔溃疡','睡不着','容易醒','失眠'))
    clinical=any(x in question for x in ('怎么用药','能治','可以治','如何用药'))
    if symptom and (current or clinical) and not historical:
        kind='personal_current'if current else'clinical_current';text=PERSONAL if current else CLINICAL
    else:
        named='牛黄' in question or bool(re.search(r'《[^》]+》',question)) or any(n and n in question for n in list(facet_index.books)+list(facet_index.people)+list(facet_index.formulas))
        q=re.sub(r'[\s，。！？、,.!?]','',question)
        deictic=bool(re.match(r'^(?:要)?(?:这个|那个)+(?:是什么|是啥|呢|感觉|有点|$)|^(?:他|她)(?:是谁|是不是|是哪个|说的(?:这个|那个)|呢|$)|^那你说的',q))
        if not deictic or named:return None
        kind='clarify';text=CLARIFY
    return {'content':json.dumps({'sentences':[{'boundary':kind}]},ensure_ascii=False),'finish_reason':'stop','stream_done':True,'usage':{'input_tokens':0,'output_tokens':0},'actual_model':'local-typed-query-scope','requested_model':'local-typed-query-scope','local_route':kind,'display_text':text}

def compile_local(raw):
    expected={'clarify':CLARIFY,'personal_current':PERSONAL,'clinical_current':CLINICAL}
    kind=raw.get('local_route')
    if kind not in expected or json.loads(raw['content'])!={'sentences':[{'boundary':kind}]}:raise ValueError('unrecognized local boundary')
    return {'sentences':[{'text':expected[kind],'citations':[]}],'handoff':False},True,{'typed':kind,'local_boundary':True,'facts':0,'semantic_appropriateness_verified':False}
