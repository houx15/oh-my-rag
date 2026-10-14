"""Opt-in repair for two diagnosed selection facets; no answer/case labels.

Historical named-author valuation and research-achievement introductions only.
The candidate pool, original protection, budgets and quote windows stay bounded.
"""
import re
from newdomain.evidence_pool import grams, weighted_overlap
from newdomain.keyword_control import select as control

def mode(question, records):
    people = set()
    for text in records.values():
        m = re.match(r'【名医[·：]([^（(·】]+)', text)
        if m and m.group(1) in question:
            people.add(m.group(1))
    if people and re.search(r'贵|价格|价值|价钱', question):
        return 'historical_valuation', people
    if re.search(r'科研成果|科技成果|研究成果', question) and not re.search(r'多少|几项|数量|政策|补贴|申请|这个|这项|该项|那项', question):
        return 'research_achievements', set()
    return None, set()

def select(search, question, queries, baseline, k):
    initial, trace = control(search, question, queries, baseline, k)
    facet, people = mode(question, search.records)
    if facet is None:
        return initial, {**trace, 'facet_mode': None, 'facet_changed': False}
    views = trace['views'];scores = {}
    for i, view in enumerate(views):
        for rank, rid in enumerate(view):
            scores[rid] = scores.get(rid, 0) + (2 if i < 2 else 1) / (61 + rank)
    qg = set().union(*(grams(q) for q in [question] + list(queries)))
    pool = {}
    for rid in scores:
        if rid in baseline:
            pool[rid] = baseline[rid]
        else:
            body = search.records[rid]
            offsets = list(range(0, max(1, len(body) - 899), 450)) + [max(0, len(body) - 900)]
            start = max(offsets, key=lambda a: (weighted_overlap(search.pool.idf, grams(body[a:a + 900]) & qg), -a))
            pool[rid] = body[start:start + 900]
    def attributed_value(text):
        for person in people:
            marker = person[-2:] + '曰'
            if marker not in text:
                continue
            section = text.split(marker, 1)[1]
            next_speaker = re.search(r'(?:[\u4e00-\u9fff]{1,4}|《[^》]+》)曰[：:]', section)
            if next_speaker:
                section = section[:next_speaker.start()]
            if re.search(r'贵|价|值', section):
                return True
        return False
    # A named laboratory is a constraint, never supplied by generated queries.
    labs = re.findall(r'[\u4e00-\u9fff]{2,8}实验室', question)
    def labels(rid, text):
        compact = re.sub(r'\s+', '', text)
        if facet == 'historical_valuation':
            if not search.records.get(rid, text).startswith('【《') or not re.search(r'贵|价|值', compact):
                return set()
            return {'valuation', *({'attributed_valuation'} if attributed_value(compact) else set())}
        if labs and not any(lab in compact for lab in labs):
            return set()
        found = set()
        section = search.records.get(rid.rsplit(':', 1)[0] + ':01', text) if ':' in rid else text
        headings = text.split('\n', 1)[0] + '\n' + section.split('\n', 1)[0]
        if re.search(r'成果名称[：:]|代表性科研成果', headings):
            found.add('concrete_result')
        if re.search(r'(?:收集|汇集|上线|包含).{0,24}项.{0,6}(?:科技|科研)?成果', compact):
            found.add('results_inventory')
        return found
    tags = {rid: labels(rid, text) for rid, text in pool.items()}
    # Protect original answer-bearing facets before positional metadata, while
    # retaining at least the same half-budget of original records.
    selected = [rid for rid in baseline if tags.get(rid)][:k]
    for rid in baseline:
        if len(selected) >= max(1, k // 2):
            break
        if rid not in selected:
            selected.append(rid)
    protected = list(selected)
    # Preserve answer-bearing records from the initial fused selection as well.
    def preserve_existing(rid):
        # A bounded, already-selected result slide may omit its lab name. Keep
        # its evidence without using that omission to admit new lab candidates.
        heading = pool[rid].split('\n', 1)[0]
        return bool(tags.get(rid)) or (facet == 'research_achievements' and rid in initial
                                      and bool(re.search(r'代表性科研成果', heading)))
    preserved = [rid for rid in selected if preserve_existing(rid)]
    for rid in dict.fromkeys(list(baseline) + list(initial)):
        if len(selected) < k and rid not in selected and preserve_existing(rid):
            selected.append(rid);preserved.append(rid)
    order = ['attributed_valuation', 'valuation'] if facet == 'historical_valuation' else ['results_inventory', 'concrete_result']
    added = []
    for label in order:
        if len(selected) == k:
            break
        if any(label in tags.get(rid, set()) for rid in selected):
            continue
        candidates = [rid for rid in scores if rid not in selected and label in tags[rid]]
        if candidates:
            rid = min(candidates, key=lambda key: (-scores[key], key));selected.append(rid);added.append(rid)
    for rid in sorted(scores, key=lambda key: (-scores[key], key)):
        if len(selected) == k:
            break
        if rid not in selected:
            selected.append(rid)
    context, windows = {}, {}
    qg = set().union(*(grams(q) for q in [question] + list(queries)))
    for rid in selected:
        if rid in baseline:
            context[rid] = baseline[rid]
            continue
        text = search.records[rid]
        offsets = list(range(0, max(1, len(text) - 899), 450)) + [max(0, len(text) - 900)]
        start = max(offsets, key=lambda a: (weighted_overlap(search.pool.idf, grams(text[a:a + 900]) & qg), -a))
        context[rid] = text[start:start + 900]
        windows[rid] = [start, min(len(text), start + 900)]
    return context, {**trace, 'selected': selected, 'new_source_windows': windows,
                     'facet_mode': facet, 'facet_changed': context != initial, 'original_retained': protected,
                     'preserved_original_facets': [rid for rid in preserved if rid in baseline],
                     'preserved_existing_facets': preserved, 'added_facet_records': added,
                     'candidate_facet_tags': {rid: sorted(v) for rid, v in tags.items() if v}}
