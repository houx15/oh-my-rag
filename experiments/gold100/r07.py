"""R07: same R06 retrieval, compact source handles and personal-use quote filtering.

Handles resolve locally to exact source spans before the unchanged common validator.
No reference answers or case IDs are read. Reused-vector timing follows R06.
"""
import json
import re
from .r06 import Index as RetrievalIndex
from .baseline import validate as common_validate

PERSONAL = re.compile(r'自行|自己.{0,8}(?:服|吃|配)|家人|孩子|儿童服用|备孕|怀孕|误吃|误服|中毒|我.{0,15}(?:服用|用药)|先吃|长期服用')
UNSAFE = re.compile(r'用法|每服|每丸|日.{0,2}服|服.{0,2}次|研|捣|炼|煎|煮|浸|为丸|为末|[零〇一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖拾半\d]+\s*[钱兩两分丸升合匙滴枚]')
SYSTEM = '''你是资料问答助手。当前日期2026-10-15。仅依据资料，直接完整回答每个问点，不罗列无关背景。
输出紧凑JSON数组：[["回答文字",["引文编号"]],["另一回答",[]]]。通常1至3项，复杂问题可增加；优先合并同一问点，总回答尽量不超过250字，但不可为省字漏掉必要条件。不输出思考、原文抄写或其他字段。每个事实引用最少的支持编号，澄清、资料不足和安全提醒可用空数组。编号在本地还原为原文展示给用户。
比较双方并保持对象归属；保留门槛、或/且、金额基数、比例、上限、期限和例外。可由给定数值直接换算或相减，不能把等值单位说成矛盾。相邻页同一项目的续文须结合标题判断，不能把别的项目条款补进来。缺失时明确缺哪项并指出核实渠道。
目录统计是当前给定资料记录数，不能改称古书全部方剂数；标题出现方名不代表该条就是一首独立方剂，要结合正文区别方剂和论述。古书概述的约数与当前目录精确计数分开。
先核对整段结论再输出，开头不能先作确定断言、末尾又撤回。旧计划既不能证明现在已发生也不能证明尚未发生；有效期已过要说明现行需核实，不推断续期。名称含糊先条件式匹配或澄清；不能操作界面，但可回答内容。连续原文即使末尾未成句仍可确认为连续片段，不因截断就否认它。
古籍是历史观点，不是现代疗效、安全或个人适用证明。个人用药问题只给必要边界与专业就医方向，急症立即急救，不能先试药；正文和所选引用均不可含剂量、服法、配制步骤，缺少此类片段不妨碍说明资料不足。'''

class Index(RetrievalIndex):
    def search(self, question, query_vector, k=8):
        personal = bool(PERSONAL.search(question))
        return [dict(c, personal_use=personal) for c in super().search(question, query_vector, k)]


def spans(chunks):
    out = {}
    for i, c in enumerate(chunks, 1):
        n = 0
        # Filter entire natural clauses before length splitting, so a dosage tail
        # cannot reappear merely because its unsafe prefix fell in an earlier unit.
        for match in re.finditer(r'[^。！？；;\n]+[。！？；;\n]*|[。！？；;\n]+', c['text']):
            clause = match.group(0)
            if c.get('personal_use') and UNSAFE.search(clause):
                continue
            for start in range(0, len(clause), 100):
                text = clause[start:start + 100]
                if text.strip():
                    n += 1
                    out[f'E{i}S{n}'] = {'id': c['id'], 'quote': text}
    return out


def messages(question, chunks):
    mapping = spans(chunks)
    # Keep source block membership/order visible while avoiding repeated long IDs.
    groups = []
    for c in chunks:
        units = [[h, v['quote']] for h, v in mapping.items() if v['id'] == c['id']]
        if units:
            groups.append({'source': c['source_id'], 'span': [c['start'], c['end']],
                           'derived': bool(c.get('derived')), 'units': units})
    return [{'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': json.dumps({'question': question, 'sources': groups}, ensure_ascii=False, separators=(',', ':'))}]


def validate(raw, chunks):
    canonical = raw.get('content', '')
    meta = {'ok': False, 'errors': []}
    try:
        assert raw.get('stream_done') is True and raw.get('finish_reason') == 'stop', 'incomplete envelope'
        obj = json.loads(canonical)
        assert isinstance(obj, list) and obj, 'nonempty answer array required'
        mapping = spans(chunks); sentences = []
        for row in obj:
            assert isinstance(row, list) and len(row) == 2, 'answer pair required'
            text, refs = row
            assert isinstance(text, str) and text.strip(), 'nonempty text required'
            assert isinstance(refs, list) and all(isinstance(h, str) and h in mapping for h in refs), 'unknown or ineligible evidence handle'
            sentences.append({'text': text, 'citations': [mapping[h] for h in dict.fromkeys(refs)]})
        canonical = json.dumps({'sentences': sentences}, ensure_ascii=False)
        meta['ok'] = True
    except (ValueError, TypeError, AssertionError, KeyError) as ex:
        meta['errors'].append(str(ex))
    result = common_validate(canonical, chunks)
    result.update(canonicalization=meta, canonical_content=canonical)
    if not meta['ok']:
        result['valid'] = False
        result['errors'] += meta['errors']
    return result
