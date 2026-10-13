"""Opt-in source-bound scalar condition compiler, independently implemented.

No corpus IDs, gold answers, learned extractor, generated code, or automatic
eligibility decisions. Scope is retained as exact source text and remains
unverified. Normalized numbers are derived annotations, never source quotations.
"""
import json
import re
from decimal import Decimal, localcontext
from newdomain import candidate

NUMBER = r"(?:[0-9]+(?:\.[0-9]+)?|[一二三四五六七八九十])"
UNIT = r"(?:万平方米|平方米|亿元|万元|元|个月|月|年|%|％|次|项|家)"
OPS = {"不得超过":"le", "不得低于":"ge", "不高于":"le", "不超过":"le", "最高不超过":"le", "最高":"le", "不低于":"ge", "不少于":"ge", "超过":"gt", "低于":"lt", "以上":None, "以下":None}
PATTERN = re.compile(r"(?P<pre>最高不超过|不得超过|不得低于|不高于|不超过|不低于|不少于|超过|低于|最高)?(?P<n>"+NUMBER+r")(?P<u>"+UNIT+r")(?P<post>以上|以下)?(?P<local>[（(](?:不含本数|含本数)[）)])?")
UNITS = {"亿元":("CNY", "100000000"),"万元":("CNY","10000"),"元":("CNY","1"),"年":("months","12"),"个月":("months","1"),"月":("months","1"),"%":("percent","1"),"％":("percent","1"),"平方米":("area","1"),"万平方米":("area","10000"),"次":("count:次","1"),"项":("count:项","1"),"家":("count:家","1")}
CN = dict(zip("一二三四五六七八九十",map(str,range(1,11))))
MEASURES = ("年产值增速","增速","年产值","单笔资助金额","资助金额","连续运营","实际运营成本","实际支出","实缴资本","注册资本","合同金额","使用面积")
ALIASES = {"年产值增速":"增速","单笔资助金额":"资助金额"}


def compact(text):
    positions=[i for i,c in enumerate(text) if not c.isspace()]
    return "".join(text[i] for i in positions),positions


def span(text, positions, start, end):
    lo,hi=positions[start],positions[end-1]+1
    return {"start":lo,"end":hi,"text":text[lo:hi]}


def quantities(text):
    clean,positions=compact(text);rows=[]
    for m in PATTERN.finditer(clean):
        # Never parse a suffix of an unsupported Chinese numeral or negative.
        if m.start() and clean[m.start()-1] in "零一二三四五六七八九十百千万亿两负-0123456789.":continue
        if re.search(r'(?:不一定|并非|未必)$',clean[:m.start()]):continue
        left=max(clean.rfind(c,0,m.start()) for c in "。；;！？\n")+1
        ends=[clean.find(c,m.end()) for c in "。；;！？"]
        right=min([e+1 for e in ends if e>=0] or [len(clean)])
        prefix=clean[left:m.start()];measure=None
        hits=[(prefix.rfind(v),len(v),v) for v in MEASURES if v in prefix]
        if hits:
            _,_,v=max(hits);measure=ALIASES.get(v,v)
        dim,factor=UNITS[m['u']]
        with localcontext() as ctx:
            ctx.prec=100;value=format(Decimal(CN.get(m['n'],m['n']))*Decimal(factor),'f')
        rows.append({"span":span(text,positions,m.start(),m.end()),"scope_span":span(text,positions,left,right),"measure":measure,"value":value,"dimension":dim,"operator_token":m['post'] or m['pre'],"local":m['local'],"entity_scope":"unresolved","time_scope":"annual" if measure in ("年产值","增速") else "unresolved"})
    return rows


def definitions(context):
    # Interpret only explicit quoted document-wide data definitions. Conflicts
    # or absent definitions leave above/below unresolved; never guess defaults.
    found={}
    for cid,text in context.items():
        clean,pos=compact(text)
        for sentence in re.finditer(r"本(?:办法|措施|规程)(?:中有关数据|所称|中)[^。；]{0,180}本数[^。；]*[。；]",clean):
            for part in re.finditer(r"((?:[“\"](?:以上|以下|不超过|最高不超过|最高)[”\"])+)(?:均)?(不包括|包括|不含|含)本数",sentence[0]):
                inclusive=not part[2].startswith('不')
                ref={"chunk":cid,**span(text,pos,sentence.start()+part.start(),sentence.start()+part.end())}
                for token in re.findall(r"[“\"]([^”\"]+)[”\"]",part[1]):
                    found.setdefault((cid.split(':')[0],token),[]).append((inclusive,ref))
    return found


def compile_ledger(question, context, limit=12):
    defs=definitions(context);premises=quantities(question);conditions=[]
    qmeasures={x['measure'] for x in premises if x['measure']}
    for cid,text in context.items():
        for q in quantities(text):
            token=q['operator_token']
            if not token:continue
            op=OPS[token];definition=None
            if token in ('以上','以下'):
                values=defs.get((cid.split(':')[0],token),[])
                flags={v[0] for v in values}
                inclusive=None
                if len(flags)==1:inclusive=values[0][0];definition=values[0][1]
                if q['local']:inclusive='不含' not in q['local'];definition=None
                if inclusive is not None:op=('g' if token=='以上' else 'l')+('e' if inclusive else 't')
            row={"chunk":cid,**q,"operator":op,"definition_span":definition,"numeric_comparisons":[]}
            # Pure scalar relation, not an entity/time join or eligibility claim.
            # Multiple user quantities for a measure are deliberately unresolved.
            matches=[p for p in premises if p['measure'] is not None and p['measure']==q['measure'] and p['dimension']==q['dimension']]
            if op and len(matches)==1:
                p=matches[0];a,b=Decimal(p['value']),Decimal(q['value'])
                truth={'ge':a>=b,'gt':a>b,'le':a<=b,'lt':a<b}[op]
                row['numeric_comparisons']=[{"question_span":p['span'],"scalar_test":truth,"semantic_binding_verified":False}]
            conditions.append(row)
    # Query-measure overlap only; no reference/gold selection. Preserve source
    # order within priority classes and disclose truncation.
    conditions.sort(key=lambda c:0 if c['measure'] in qmeasures else 1)
    return {"method":"typed-source-conditions-v2","question_quantities":premises,"conditions":conditions[:limit],"omitted_conditions":max(0,len(conditions)-limit),"eligibility_verified":False}


def augment(question,selected):
    context={c['id']:c['text'] for c in selected};ledger=compile_ledger(question,context)
    messages=candidate.build_messages(question,selected)
    instruction="""附加材料是本地确定性标量条件表，不是参考答案。value已换算为dimension单位（months是月、CNY是元、percent是百分数点）。operator的gt/ge/lt/le分别是严格大于/大于等于/严格小于/小于等于，null是未解析。span及definition_span可回查原文。entity_scope为unresolved，time_scope也可能未解析；scope_span只是所在句子，不代表已验证主体或条款。numeric_comparisons只比较数字，semantic_binding_verified=false时必须先核对同一政策、条款、对象、审核类别、期间及局部例外，不能把标量真值直接当整体资格。不同维度不可混用。没有列出的条件仍以原文为准。未知事实不是否定事实；只判断用户所问范围。最终仍按原输出协议引用原证据句柄，不能引用此表作为原文证据。"""
    # Avoid duplicate long source paragraphs; exact offsets and small spans
    # remain in inference, full provenance stays in local metadata.
    view=json.loads(json.dumps(ledger,ensure_ascii=False))
    for row in view['conditions']:
        row['scope_span']={k:v for k,v in row['scope_span'].items() if k!='text'}
    for row in view['question_quantities']:
        row.pop('scope_span',None)
    appendix=instruction+'\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))
    # Bound annotation volume without dropping original evidence.
    while len(appendix.encode())>8500 and view['conditions']:
        view['conditions'].pop();view['omitted_conditions']+=1
        appendix=instruction+'\n'+json.dumps(view,ensure_ascii=False,separators=(',',':'))
    messages=[dict(m) for m in messages];messages[-1]['content']+='\n'+appendix
    if len(json.dumps(messages,ensure_ascii=False).encode())>candidate.MAX_REQUEST_BYTES:
        raise ValueError('typed annotation request cap exceeded')
    return messages,ledger
