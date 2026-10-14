"""Opt-in typed clarification emission; never accept arbitrary uncited prose."""
import copy,json
from newdomain.typed_boundaries_v2 import compile_response

CLARIFY='请补充您指的是哪位人物、哪本书、哪个方剂或哪件事，以及想了解的具体内容。'


def messages(original):
    out=copy.deepcopy(original)
    out[0]['content']+='\n最终输出检查：根必须是对象 {"sentences":[...]}，不能直接输出数组。事实对象用text和citations；citations中的segs只能用已显示的有效段号。问题缺失对象、且没有提供上文时，只输出 {"sentences":[{"boundary":"clarify"}]}，系统将显示“'+CLARIFY+'”。clarify必须独占整个回答，不能夹带事实句，也不能自行写无引用的澄清句。明确对象可答时不要选clarify。个人当前症状/用药建议不能用历史方剂剂量代替；可简述历史记载，并使用personal边界，不给个人处方。'
    return out


def process(response, context, templates, processor):
    def unique(pairs):
        obj={}
        for k,v in pairs:
            if k in obj:raise ValueError('duplicate key')
            obj[k]=v
        return obj
    if response.get('finish_reason')!='stop' or not response.get('stream_done'):raise ValueError('incomplete response')
    obj=json.loads(response['content'],object_pairs_hook=unique)
    if obj=={'sentences':[{'boundary':'clarify'}]}:
        return {'sentences':[{'text':CLARIFY,'citations':[]}],'handoff':False},True,{'typed':'clarify','semantic_appropriateness_verified':False,'facts':0}
    wire,trace=compile_response(response,templates,'citations')
    result=processor(wire,context)
    answer=json.loads(result['response']['content'])if result.get('response',{}).get('content')else None
    return answer,result.get('candidate_gate',{}).get('status')=='mechanically_valid',{'typed':trace,'processed':result}
