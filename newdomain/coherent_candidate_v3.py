"""One opt-in source-grounded candidate; no case-specific answer selection.
Caller supplies retrieval and source records. Baseline remains independently usable.
"""
from newdomain.nh_facet_coverage import FacetIndex
from newdomain.citation_contract_v3 import messages as contract_messages
from newdomain.floor_derivation import messages as floor_messages

CONFIGURATION='source-grounded-v3'

def hydrate_ranked_context(context, restored_records):
    """Ablation: same IDs/order, restored exact source text, no reranking."""
    return {rid:restored_records[rid]['text']if rid in restored_records else text for rid,text in context.items()}

def transform(corpus, question, context, messages, source_records=None):
    if corpus=='niuhuang':return contract_messages(messages),{'configuration':CONFIGURATION,'contract':'typed-clarify-v3'}
    if corpus=='guangming':
        out,trace=floor_messages(messages,question,context,source_records)
        return out,{'configuration':CONFIGURATION,'floor':trace}
    raise ValueError('unknown corpus')
