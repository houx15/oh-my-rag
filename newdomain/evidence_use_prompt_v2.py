"""Task-focused generation instructions; immutable evidence and validators."""
from copy import deepcopy
import re

COMMON="""本次作答焦点（仍遵守上方全部JSON、引用、长度和边界校验）：
先匹配用户要完成的任务，再选事实。资料含该对象的部分相关内容时，应在该范围内回答，不能因为缺少完整简介而整题拒答；但用户明确问某一领域/细节而资料不含时，必须保留证据不足结论，不能以别的主题填充。不同对象的资料即使相邻也不能互换。
每句必须直接服务本题；无关补充整句删除。不要为凑满句数加药性、补贴或书目。政策若要提及，须同时保留谁可申请、地点/时间/租期/面积、比例、上限及排除项；篇幅不够就省略该非必要政策，不能用“符合条件”替代具体条件或把受益人写成楼宇。界面请求不能声称可以或已经切换/打开；它不妨碍回答有证据的内容。缺失指代不能由检索排名补全；只能用原协议允许的澄清/证据不足形式，不添加新字段或自由边界句。
"""

FOCUS={
 'person':'任务是介绍明确人物。首句写资料支持的人物身份/经历，其余只补充主要经历或著述。不得插入药材主治、性味或配方作为人物介绍；著作中某条药材不等于该人物本人意见。',
 'definition':'任务是说明对象是什么。首句应讲资料支持的身份、来源或形态，不能只列性味、归经、主治或书名。若只有历史采集/分类记载，要明确其历史范围；不足以给现代定义时如实说明，不能把历史分类强写为现代事实。',
 'introduction':'任务是介绍对象。先给至少一项与对象直接相关的实质内容，资料只覆盖一个侧面就明确该范围，不能以缺少全景简介为由拒绝所有内容。口语名称不确定时只作明确条件式候选介绍，不能确认猜测。展品身份未证实时只介绍资料记载的成果，不声称它就是现场展品。',
 'general':'逐项回答所问的有据内容，保持历史/当前、对象及说话者界限；不以重复原文替代不存在的解释，不编造缺失定义。'
}

def focus(question,context):
    for text in context.values():
        m=re.match(r'【名医[·：]([^（(·】]+)',text)
        if m and m.group(1)in question and re.search(r'介绍|讲|了解',question):return 'person'
    if re.search(r'什么是|是什么|是个什么',question):return 'definition'
    if re.search(r'介绍|简介|讲讲|讲解',question):return 'introduction'
    return 'general'

def apply(messages,question,context,enabled=False):
    out=deepcopy(messages)
    if enabled:
        if not out or out[0].get('role')!='system':raise ValueError('system prompt required')
        out[0]['content']+='\n'+COMMON+'\n'+FOCUS[focus(question,context)]
    return out
