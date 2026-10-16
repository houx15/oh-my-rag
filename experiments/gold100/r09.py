"""R09: intact lexical units, source section context and bounded exact-term coverage.
No case IDs, gold labels or prior answers enter inference. All facts remain exact
source slices; section hints carry original source offsets for independent auditing.
"""
import json
import re
from .r08 import Index as PreviousIndex, PERSONAL, UNSAFE as OLD_UNSAFE
from .r06 import Index as CoreIndex
from .baseline import validate as common_validate

UNSAFE=re.compile(OLD_UNSAFE.pattern+r'|锉|末|剂|分许|少许|调|吮|傅|摩之|系之|囊|鼻下|吞|咽|服下|送下')
HEADING=re.compile(r'(?m)^\s*[（(][一二三四五六七八九十百]+[）)][^\n]{2,65}')
SYSTEM="""你是资料问答助手。当前日期2026-10-15。仅按给定原文回答，不补写记忆中的事实。
输出JSON数组：[["回答",["E1S1"]],["另一回答",[]]]。引用必须是实际存在的完整编号。引用在本地还原为原文给用户。通常1至3项；简洁但所有必要条件必须保留。不要输出推理或检查表。
作答前核对：用户问题是否完整？残句要先问清；语音近似名称只能条件式识别。不能操作现场页面，但应介绍已有内容，不能整体拒答。个人问题的边界先于古籍事实。
逐项覆盖：所问实体、对比双方、金额基数、门槛、或/且、比例、上限、期限、例外、适用范围。做简单换算或差值时复核数字；资料块或引用编号边界不等于原文分页，连续的数字不可截断。原文单位不完整时承认残缺，不猜补单位或指数。
section_context是从同一文件前文提取的原始栏目标题，只适用于本块开头至下一个新标题前；续页数值须与这个标题对应。同文件不同项目不可混用。先搜齐所有证据再说未载，不能先断言缺资料又在后文给出该内容。连续原句被截在半句话仍是连续原话，可注明未引完整。
政策条款必须说明材料年份/有效期与当前申请需核实；拿到资格不等于已发款。旧计划、在建、预计日期不能证明现在已完成或尚未开始，第一句就应说当前状态不能确认，不能先说可以/没有再补需核实。一般事后资助不等于所有事项免事前认定。原文数字包括不包括本数按对应条款。
目录总数看完整统计，不以展示样例数作总数；记录数不是去重方剂数。问题问方剂时，要用正文的组方或独立方文判断，标题中提到方名的讨论条目不算新增方剂；分别列出方剂和病候论述。古人发现传说的出处与一般药物书籍不同，不能用后者冒充前者的记载。
古代上品不是现代质量或安全等级；不同古书观点可以不同，不作无依据统一解释。古书药名/主治不能对应现代疾病、疗效或个人适用。个人用药：不自行开始、配制或调整现有药物，不建议凭古籍先停药；立即联系医生药师核对具体药品，急症立即急救。正文和显示引文都不能含剂量、服法、配制或外用操作。
original_content_withheld表示原文部分内容被过滤，不表示原文没有这些内容。必要时明确说原文有被省略的组方/用法内容，不复述；历史病候仍应如实概述，不能把未设主治栏目误作未记载病候。只使用可见安全编号，不按被隐藏的信息自行编写医学方案。
"""

class Index(PreviousIndex):
    def __init__(self,records,source_vectors):
        super().__init__(records,source_vectors)
        self.section_at={};current={}
        ordered=[]
        for rid,text in records.items():
            m=re.fullmatch(r'(D\d+):(\d+):(\d+)',rid)
            if m:ordered.append((m.group(1),int(m.group(2)),int(m.group(3)),rid))
        for doc,page,part,rid in sorted(ordered):
            self.section_at[rid]=current.get(doc)
            found=list(HEADING.finditer(records[rid]))
            if found:
                h=found[-1];current[doc]={'source_id':rid,'start':h.start(),'end':h.end(),'text':h.group()}

    def search(self,question,query_vector,k=8):
        out=[dict(c) for c in super().search(question,query_vector,k)]
        core_ids={c['id'] for c in CoreIndex.search(self,question,query_vector,k)}
        terms=re.findall(r'[“「]([^”」]{1,12})[”」]',question)
        choice=re.search(r'是([\u3400-\u9fff]{1,3})还是([\u3400-\u9fff]{1,3})',question)
        if choice:terms.extend(choice.groups())
        terms=list(dict.fromkeys(t for t in terms if t.strip()))
        if terms:
            lexical={c['source_id']:i for i,c in enumerate(self.hybrid.base.search(question,100))}
            ranked=sorted(self.records,key=lambda rid:(-sum(t in self.records[rid].split('目录字段：')[0] for t in terms),lexical.get(rid,10000),rid))
            for rid in ranked[:3]:
                text=self.records[rid];body=text.split('目录字段：')[0]
                hits=[body.find(t) for t in terms if t in body]
                if not hits:continue
                start=max(0,min(hits)-180);end=min(len(text),start+1000)
                intervals=[(c['start'],c['end']) for c in out if c['source_id']==rid]
                pending=[(start,end)]
                for lo,hi in intervals:
                    parts=[]
                    for a,b in pending:
                        if b<=lo or a>=hi:parts.append((a,b))
                        else:
                            if a<lo:parts.append((a,lo))
                            if b>hi:parts.append((hi,b))
                    pending=parts
                for a,b in pending:
                    if b>a and text[a:b].strip():out.append({'id':f'{rid}@{a}:{b}','source_id':rid,'start':a,'end':b,'text':text[a:b],'personal_use':bool(PERSONAL.search(question))})
        for c in out:
            rid=c['source_id']
            if rid not in self.section_at:continue
            hint=self.section_at[rid]
            before=[h for h in HEADING.finditer(self.records[rid]) if h.end()<=c['start']]
            if before:
                h=before[-1];hint={'source_id':rid,'start':h.start(),'end':h.end(),'text':h.group()}
            if hint:c['section_context']=hint
        # Only source supplements may be discarded; original R06 evidence survives.
        while sum(len(c['text'])for c in out)>9000 or len(json.dumps(messages(question,out),ensure_ascii=False).encode())>29500:
            removable=[i for i,c in enumerate(out) if c['id'] not in core_ids]
            if not removable:raise ValueError('core evidence exceeds outbound limit')
            out.pop(removable[-1])
        return out


def units(text,personal=False):
    # Natural lines/sentences preserve numeric tokens. Long uninterrupted clauses
    # remain intact: a soft length target is not permission to split 50 into5/0.
    for m in re.finditer(r'[^。！？；;\n]+[。！？；;\n]*|[。！？；;\n]+',text):
        clause=m.group()
        if not clause.strip() or (personal and UNSAFE.search(clause)):continue
        yield clause


def spans(chunks):
    return {f'E{i}S{j}':{'id':c['id'],'quote':t}
            for i,c in enumerate(chunks,1)
            for j,t in enumerate(units(c['text'],c.get('personal_use')),1)}


def messages(question,chunks):
    mapping=spans(chunks);groups=[]
    for c in chunks:
        us=[[h,v['quote']]for h,v in mapping.items()if v['id']==c['id']]
        withheld=any(UNSAFE.search(m.group()) for m in re.finditer(r'[^。！？；;\n]+',c['text'])) if c.get('personal_use') else False
        g={'source':c['source_id'],'span':[c['start'],c['end']],'units':us}
        if c.get('derived'):g['derived']=True
        if c.get('section_context'):g['section_context']=c['section_context']
        if withheld:g['original_content_withheld']='原文含操作或用量等内容，本展示已省略，不可称原文未载。'
        groups.append(g)
    return [{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps({'question':question,'sources':groups},ensure_ascii=False,separators=(',',':'))}]


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
