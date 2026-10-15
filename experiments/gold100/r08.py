"""R08: source-ordered dependencies, catalog coverage and explicit evidence omissions.

Handles resolve locally to exact source spans before the unchanged common validator.
No reference answers or case IDs are read. Reused-vector timing follows R06.
"""
import json
import re
from .r06 import Index as RetrievalIndex
from .baseline import validate as common_validate
from .r03 import norm
from collections import defaultdict

PERSONAL = re.compile(r'自行|自己.{0,8}(?:服|吃|配)|家人|孩子|儿童服用|备孕|怀孕|误吃|误服|中毒|我.{0,15}(?:服用|用药)|先吃|长期服用')
UNSAFE = re.compile(r'组成|配方|外用|佩带|佩戴|蜜和|和丸|调下|汤下|涂|敷|灌|吹入|含化|用法|每服|每丸|日.{0,2}服|服.{0,2}次|研|捣|炼|煎|煮|浸|为丸|为末|[零〇一二三四五六七八九十百千壹贰叁肆伍陆柒捌玖拾半\d]+\s*[钱兩两分丸升合匙滴枚]')
SYSTEM = '''你是资料问答助手。当前日期2026-10-15。仅依据资料，直接完整回答每个问点，不罗列无关背景。
输出紧凑JSON数组：[["回答文字",["引文编号"]],["另一回答",[]]]。通常1至3项，复杂问题可增加；优先合并同一问点，总回答尽量不超过250字，但不可为省字漏掉必要条件。不输出思考、原文抄写或其他字段。每个事实引用最少的支持编号，澄清、资料不足和安全提醒可用空数组。编号在本地还原为原文展示给用户。
比较双方并保持对象归属；保留门槛、或/且、金额基数、比例、上限、期限和例外。可由给定数值直接换算或相减，不能把等值单位说成矛盾。相邻页同一项目的续文须结合标题判断，不能把别的项目条款补进来。缺失时明确缺哪项并指出核实渠道。
目录统计是当前给定资料记录数，不能改称古书全部方剂数；标题出现方名不代表该条就是一首独立方剂，要结合正文区别方剂和论述。古书概述的约数与当前目录精确计数分开。
先核对整段结论再输出，开头不能先作确定断言、末尾又撤回。旧计划既不能证明现在已发生也不能证明尚未发生；有效期已过要说明现行需核实，不推断续期。名称含糊先条件式匹配或澄清；不能操作界面，但可回答内容。连续原文即使末尾未成句仍可确认为连续片段，不因截断就否认它。
古籍是历史观点，不是现代疗效、安全或个人适用证明。个人用药问题只给必要边界与专业就医方向，急症立即急救，不能先试药；正文和所选引用均不可含剂量、服法、配制步骤，缺少此类片段不妨碍说明资料不足。'''

SYSTEM += """
先在心中逐项核对问句：实体、比较双方、条件、期限、算术、资料时点；只输出最终答案，不输出推理。宁可多写必要条件，不补无关例子。严格使用E数字S数字的已有引文编号，不能把来源序号当引用编号。
同一D文件按页码顺序排列；下一页开头若无新项目标题，结合前页末尾标题判断续文归属。不能把一个行业专用政策当成所有企业的一般政策；同一资料中不同主体的条款分别查找。政策问答注明资料版本或有效期及当前申请需核实，不承诺仍可申请。
目录统计的总数看“相关条目共”而非“展示”；展示只是样例。目录标题和古书概述不等于正文的类别，能见组成或明确方名的完整处方与讨论用药的条文分别回答。
证据omitted_chars大于0表示为展示安全或空白处理而省略了内容，绝不据此声称原文无成分、主治、剂量或用法。个人用药只说不能据古方判断个人适用，不复述操作；古籍品级不能等同现代质量或安全等级。材料未直接支持的现代病名、功效解释一律不补写。
"""

class Index(RetrievalIndex):
    def search(self, question, query_vector, k=8):
        original = super().search(question, query_vector, k)
        # Retain every R06 span, then add exact uncovered source intervals.
        out = [dict(c) for c in original]
        intervals = defaultdict(list)
        for c in original:
            if not c.get('derived'):
                intervals[c['source_id']].append((c['start'], c['end']))
        used = sum(len(c['text']) for c in out)

        def add(rid, start=0, end=None):
            nonlocal used
            text = self.records[rid]
            end = min(len(text), end if end is not None else len(text))
            pending = [(start, end)]
            for lo, hi in intervals[rid]:
                parts = []
                for a, b in pending:
                    if b <= lo or a >= hi:parts.append((a,b))
                    else:
                        if a < lo:parts.append((a,lo))
                        if b > hi:parts.append((hi,b))
                pending = parts
            for a,b in pending:
                if b <= a or not text[a:b].strip() or used + b-a > 8500:continue
                out.append({'id':f'{rid}@{a}:{b}', 'source_id':rid,
                            'start':a, 'end':b, 'text':text[a:b]})
                intervals[rid].append((a,b)); used += b-a

        nq = norm(question)
        books = [b for b in self.catalog.books if len(b)>=3 and b in nq]
        books = [b for b in books if not any(b!=v and b in v for v in books)]
        if re.search('哪几|哪些|论述|方剂|种类|类别', question):
            for book in sorted(books)[:2]:
                ids = self.catalog.children.get(book, [])
                # A small complete group is useful for distinguishing a formula
                # from a passage mentioning it. Do not infer a missing type field.
                if len(ids)<=40:
                    for rid in ids:add(rid, 0, 220)
        if re.search('典籍|本草|古籍|书籍',question) and re.search('哪些|哪几',question) and re.search('朝代|以前|之前|时期',question):
            # Broad chronology queries need source metadata beyond top-k matches.
            # Include all book headers/metadata; no era-specific answer table.
            eras=['先秦','秦','汉','魏晋南北朝','隋','唐','五代','宋','金','元','明','清','民国','现代']
            cutoff=next((i for i,e in enumerate(eras) if re.search(re.escape(e)+r'(?:代|朝)?(?:以前|之前)',question)),None)
            ids=sorted(self.catalog.books.values())
            if cutoff is not None:
                ids=[rid for rid in ids if self.catalog.meta[rid].get('朝代') in eras[:cutoff]]
            for rid in ids:
                text=self.records[rid];pos=text.rfind('目录字段：')
                if pos>=0:add(rid,pos)
            for rid in ids:add(rid,0,300)
        if re.search('申请|补贴|奖励|办法|政策|扶持|资助|申报|保险|投资',question):
            docs={c['source_id'].split(':')[0] for c in original if not c.get('derived')}
            # Lexical matches in already retrieved documents recover another
            # beneficiary's clause without adding an unrelated policy source.
            extra=[c for c in self.hybrid.base.search(question,30)
                   if c['source_id'].split(':')[0] in docs]
            for c in extra[:8]:add(c['source_id'],c['start'],c['end'])
        # Keep document relevance order, but restore physical page order inside it.
        group_order={}
        def key(c):
            rid=c['source_id'];m=re.fullmatch(r'(D\d+):(\d+):(\d+)',rid)
            group=m.group(1) if m else rid
            group_order.setdefault(group,len(group_order))
            return (group_order[group],int(m.group(2)) if m else 0,
                    int(m.group(3)) if m else 0,c['start'])
        keys={c['id']:key(c) for c in out}
        out.sort(key=lambda c:keys[c['id']])
        personal=bool(PERSONAL.search(question))
        out=[dict(c,personal_use=personal) for c in out]
        original_ids={c['id'] for c in original}
        # Respect the existing outbound byte limit without dropping R06 evidence.
        while len(json.dumps(messages(question,out),ensure_ascii=False).encode())>29500:
            removable=[i for i,c in enumerate(out) if c['id'] not in original_ids]
            if not removable:raise ValueError('base evidence exceeds outbound limit')
            out.pop(removable[-1])
        return out


def spans(chunks):
    out = {}
    for i, c in enumerate(chunks, 1):
        n = 0
        # Filter entire natural clauses before length splitting, so a dosage tail
        # cannot reappear merely because its unsafe prefix fell in an earlier unit.
        pattern = r'[^。！？；;\n]+[。！？；;\n]*|[。！？；;\n]+' if c.get('personal_use') else r'[^。！？；;]+[。！？；;]*|[。！？；;]+'
        for match in re.finditer(pattern, c['text']):
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
        if units or c.get('personal_use'):
            groups.append({'source': c['source_id'], 'span': [c['start'], c['end']],
                           'derived': bool(c.get('derived')),
                           'omitted_chars': len(c['text'])-sum(len(u[1]) for u in units), 'units': units})
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
