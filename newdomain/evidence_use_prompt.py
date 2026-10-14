"""Prompt-only evidence-use ablation. No retrieval or validator changes."""
from copy import deepcopy

CHECK = """回答规划补充（不改变上述引用、句数、字数和JSON协议）：
先在内部把问题拆成所指对象、需要解释的内容、显示/切换等操作；不要输出分析或新的JSON字段。无法执行界面操作不代表无法解释资料：对象明确或有很强候选时，用条件表述区分候选与已确认对象，再回答可由本次资料支持的内容；不得声称已切换或打开。缺失代词上文且无法确定对象时，严格使用已有澄清协议，不任挑一条资料。
在选择证据不足话术前，逐一检查所有已给资料是否直接支持所问内容。原文支持一部分就回答该部分，只有真正缺失的部分才说明不足；不能把当前价格未知等同于历史文献没有价值记载，也不能用历史价格代替现在价格。不要把原文重复一遍当作解释；若资料没有释义，明确该证据局限，不创造现代解释。
每项拟回答事实核对对象、主语/说话者、时间、适用领域、前提、排除项、单位和上下限，保留会改变结论的限定。不能用邻接文字推断作者；不能用政策补贴代替成果介绍。优先删掉无关补充以留出限定词，不突破原有长度/句数。只输出既定协议，边界对象严格按既定格式；不要把clarify与事实或自写text混在一起。以上检查不授权添加任何资料外事实。
"""

def apply(messages,enabled=False):
    out=deepcopy(messages)
    if enabled:
        if not out or out[0].get('role')!='system':raise ValueError('system prompt required')
        out[0]['content']+='\n'+CHECK
    return out
