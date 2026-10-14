"""Apply explicit, hash-bound source amendments without overwriting the corpus.

Amendments are data with provenance, never inferred from a question/reference.
A changed source receives a new citation ID. Unmatched hashes fail closed.
"""
import copy,hashlib

def apply(records, amendments):
    out=copy.deepcopy(list(records));by={r['id']:r for r in out};changes={}
    for patch in amendments:
        rid=patch['record_id']
        if rid not in by:raise ValueError('amendment source missing')
        row=by[rid];text=row['text']
        if hashlib.sha256(text.encode()).hexdigest()!=patch['expected_text_sha256']:
            raise ValueError('amendment source version mismatch')
        if not patch.get('sources')or text.count(patch['before'])!=1:
            raise ValueError('unbound or ambiguous amendment')
        new_id=patch['amended_id']
        if new_id in by:raise ValueError('amended citation id already exists')
        row['id']=new_id;row['text']=text.replace(patch['before'],patch['after'],1)
        by.pop(rid);by[new_id]=row
        row.setdefault('metadata',{})['source_amendment']=copy.deepcopy(patch)
        changes[rid]={'amended_id':new_id,'original_text_sha256':patch['expected_text_sha256'],'amended_text_sha256':hashlib.sha256(row['text'].encode()).hexdigest(),'sources':patch['sources'],'verification':patch['verification']}
    return out,changes
