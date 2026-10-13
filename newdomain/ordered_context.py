"""Recover evidence-handle order from the authoritative retrieval list.

Serialized maps may sort keys. Handle numbering must follow the same ordered
retrieval sequence that constructed the prompt, never a deserialized map order.
"""

def from_retrieval(results, saved_context):
    context={}
    for row in results:
        rid=row['id']
        if rid in context:raise ValueError('duplicate retrieval ID')
        context[rid]=row['text']
    if context != saved_context:raise ValueError('retrieval evidence differs from saved context')
    return context
