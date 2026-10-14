"""Offline set/rank accounting, deliberately separate from relevance judgments."""

def analyze(baseline, vocabulary_trace, model_trace):
    traces = {'vocabulary': vocabulary_trace, 'small_model': model_trace}
    for trace in traces.values():
        if len(trace.get('views', [])) < 2:
            raise ValueError('expanded trace must retain original lexical view')
        if list(trace['views'][0]) != list(baseline):
            raise ValueError('original selected view changed')
    original = list(model_trace['views'][1])
    if original != vocabulary_trace['views'][1]:
        raise ValueError('original lexical controls differ')
    base = set(baseline)
    original_pool = base | set(original)
    pools = {a: set().union(*(set(v) for v in t['views'][2:])) for a, t in traces.items()}
    result = {'original_selected': list(baseline), 'original_lexical_top20': original}
    for arm, trace in traces.items():
        selected = set(trace['selected'])
        if not selected <= original_pool | pools[arm]:
            raise ValueError('selected record absent from candidate pool')
        result[arm] = {
            'queries': trace['hypotheses'],
            'pool_new_vs_original': sorted(pools[arm] - original_pool),
            'selected_new_vs_baseline': sorted(selected - base),
            'selected_new_vs_original_pool': sorted(selected - original_pool),
            'baseline_records_dropped': sorted(base - selected),
            'view_ranks': {rid: [v.index(rid) + 1 if rid in v else None for v in trace['views']]
                           for rid in sorted(original_pool | pools[arm])},
        }
    result['model_unique_pool_vs_original_and_dictionary'] = sorted(pools['small_model'] - original_pool - pools['vocabulary'])
    result['model_unique_selected_vs_original_and_dictionary'] = sorted(set(model_trace['selected']) - original_pool - pools['vocabulary'])
    return result
