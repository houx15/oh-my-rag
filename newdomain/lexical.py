"""Opt-in C11B: preserve the strongest lexical hit if it matches the anchor doc."""
def preserve_lexical(selected, lexical_hit):
    if len(selected)>8:raise ValueError('unchanged eight-chunk budget required')
    if not selected or lexical_hit is None:return list(selected)
    if lexical_hit['doc_id']!=selected[0]['doc_id']:return list(selected)
    if lexical_hit['id'] in {c['id'] for c in selected}:return list(selected)
    return list(selected[:7])+[lexical_hit]
