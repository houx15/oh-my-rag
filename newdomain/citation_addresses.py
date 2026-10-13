"""Prompt-only citation address bounds; never repair or reinterpret citations."""
import copy,json

def messages(original, counts):
    if not isinstance(counts,dict)or not counts:raise ValueError('source segment counts required')
    if any(not isinstance(k,str)or type(n)is not int or n<1 for k,n in counts.items()):raise ValueError('invalid source count')
    out=copy.deepcopy(original)
    if not out or out[0].get('role')!='system':raise ValueError('system prompt required')
    ranges={rid:[0,n-1]for rid,n in counts.items()}
    out[0]['content']+='\n引用地址校验提示：下面是每份已给资料实际显示的有效段号闭区间。段号不是章节号或句子号；仅有<0>的资料只能引用0，不得猜测正文另有段1。segs只能是单个段号[n]或连续区间起止[a,b]，不能列出三个或更多离散段号。正文含书名时，仅能用该书名实际出现于其资料中的引用；不要把人物档案标题改造成书名。不能定位时不要编造引用。有效段号：'+json.dumps(ranges,ensure_ascii=False)
    return out
