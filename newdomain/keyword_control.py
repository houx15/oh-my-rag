"""Original-query lexical + identical fusion control, without keyword inference."""
from newdomain.evidence_pool import grams, weighted_overlap

def select(search, question, queries, baseline, k):
    if queries:
        return search.select(question, queries, baseline, k)
    if k < 1:
        raise ValueError('positive context budget required')
    pool, _ = search.pool.build(question, {}, k=20)
    views = [list(baseline), list(pool)]
    scores = {}
    for view in views:
        for rank, rid in enumerate(view):
            scores[rid] = scores.get(rid, 0) + 2 / (61 + rank)
    selected = list(baseline)[:max(1, k // 2)]
    for rid in sorted(scores, key=lambda key: (-scores[key], key)):
        if len(selected) == k:
            break
        if rid not in selected:
            selected.append(rid)
    context, windows = {}, {}
    for rid in selected:
        if rid in baseline:
            context[rid] = baseline[rid]
            continue
        text = search.records[rid]
        qg = grams(question)
        offsets = list(range(0, max(1, len(text) - 899), 450)) + [max(0, len(text) - 900)]
        start = max(offsets, key=lambda a: (weighted_overlap(search.pool.idf, grams(text[a:a + 900]) & qg), -a))
        context[rid] = text[start:start + 900]
        windows[rid] = [start, min(len(text), start + 900)]
    return context, {'views': views, 'hypotheses': [], 'selected': selected,
                     'original_retained': list(baseline)[:max(1, k // 2)],
                     'new_source_windows': windows, 'control': 'original lexical plus identical weighted fusion'}
