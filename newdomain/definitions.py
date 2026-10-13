"""Opt-in C10D: exact, scoped definition evidence under the C1 chunk budget.

No answer labels, document IDs, page tables, model calls or C1-default changes.
Multiple definition pages/sentences in a document are treated as ambiguous.
"""
import re
from collections import defaultdict

_DEFINITION = re.compile(r'本(?:办法|措施|规程)(?:中有关数据|所称|中)[^。；]{0,160}本数[^。；]*[。；]')


class DefinitionSelector:
    def __init__(self, chunks):
        grouped = defaultdict(list)
        for chunk in chunks:
            text = re.sub(r'\s+', '', chunk['text'])
            matches = {m.group(0) for m in _DEFINITION.finditer(text)}
            if matches:
                grouped[chunk['doc_id']].append((chunk, matches))
        self.definitions = {}
        self.ambiguous_documents = set()
        for doc, entries in grouped.items():
            pages = {str(c['locator']) for c, _ in entries}
            sentences = set().union(*(s for _, s in entries))
            if len(pages) != 1 or len(sentences) != 1:
                self.ambiguous_documents.add(doc)
                continue
            self.definitions[doc] = min((c for c, _ in entries), key=lambda c: (c['start'], c['id']))

    def select(self, selected):
        """Keep the first seven ranked chunks; add at most one anchor-doc page.

        Already-present definitions, empty results and ambiguous documents leave
        ranking untouched. Short lists grow by at most one, never beyond eight.
        A retrieval anchor can itself be wrong: this mechanism cannot certify
        query/document identity or interpretation; false joins need evaluation.
        """
        if len(selected) > 8:
            raise ValueError('C10D requires the unchanged eight-chunk budget')
        if not selected:
            return list(selected)
        definition = self.definitions.get(selected[0]['doc_id'])
        if definition is None or definition['id'] in {c['id'] for c in selected}:
            return list(selected)
        return list(selected[:7]) + [definition]
