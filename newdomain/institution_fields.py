"""Explicitly approved source-field restoration; no global name-screen bypass.

The caller supplies only institution column F and records separate preprocessing
provenance. Original datasets and paid results must remain immutable.
"""
import copy
import hashlib
import json
import re
from pathlib import Path
from .transport import PrivacyViolation, privacy_check

_CONTACT = re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)|(?<!\d)0\d{2,3}[-－ ]?\d{7,8}(?!\d)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)\d{17}[\dXx](?!\d)")
_SECRET = re.compile(r"(?:sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
_RESTRICTED = re.compile(r"联系人|联系电话|联系手机|电子邮箱|项目负责人|转化负责人|保密|仅供内部")

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()

def _institution(value):
    if not isinstance(value,str) or not value.strip() or value!=value.strip():
        raise ValueError('literal institution string required')
    if len(value)>120 or any(c in value for c in '\r\n：:') or _CONTACT.search(value) or _SECRET.search(value) or _RESTRICTED.search(value):
        raise PrivacyViolation('institution field contains restricted content')

def restore(units, column_f, source_sha256, sheet, approved_names):
    """Append missing F fields only; preserve every existing byte otherwise.

    column_f maps row locators to literal, source-derived values. No G/H or
    non-catalogue text is accepted. Existing fields must match the source.
    """
    if not re.fullmatch(r'[0-9a-f]{64}',source_sha256) or not sheet:
        raise ValueError('verified source hash and sheet required')
    approved=set(approved_names)
    if not approved:raise ValueError('explicit approved institution names required')
    for name in approved:_institution(name)
    output=copy.deepcopy(units);changes=[];seen=set()
    for unit in output:
        if unit['doc_id']!='D36':continue
        row=str(unit['locator'])
        if row in seen or not row.isdigit() or int(row)<2:raise ValueError('unique catalogue data row required')
        seen.add(row)
        if unit.get('source_sha256')!=source_sha256:raise ValueError('catalogue workbook hash mismatch')
        if row not in column_f:raise ValueError('missing source cell')
        value=column_f[row]
        existing=[x[len('单位名称：'):]for x in unit['text'].splitlines()if x.startswith('单位名称：')]
        if existing:
            if existing!=[value]:raise ValueError('existing institution differs from source')
            continue
        if value not in approved:raise ValueError('missing field not explicitly approved')
        _institution(value)
        old=unit['text'];unit['text']=old+'\n单位名称：'+value
        changes.append({'doc_id':'D36','locator':row,'sheet':sheet,'cell':'F'+row,'field':'单位名称','value':value,'cell_value_sha256':digest(value),'source_sha256':source_sha256,'before_text_sha256':digest(old),'after_text_sha256':digest(unit['text'])})
    if not changes:raise ValueError('no missing approved fields found')
    return output,changes

def screen_approved_institutions(messages, denylist_path, policy):
    """Allow full verified institution literals only, keep remaining screens.

    Does not dispatch. A later authorized transport must explicitly invoke this
    scoped screen and preserve policy hash/provider provenance. No denylist edit.
    """
    if policy.get('scope')!='D36-column-F-institution-names-only' or policy.get('approved')is not True:
        raise PrivacyViolation('explicit scoped institution authority required')
    entries=policy.get('source_cells')
    if not isinstance(entries,list)or not entries:raise PrivacyViolation('source-cell provenance required')
    approved=set()
    for entry in entries:
        value=entry.get('value');_institution(value)
        if entry.get('doc_id')!='D36' or entry.get('field')!='单位名称' or entry.get('cell')!='F'+str(entry.get('locator')) or entry.get('cell_value_sha256')!=digest(value):
            raise PrivacyViolation('invalid institution provenance')
        approved.add(value)
    raw=json.dumps(messages,ensure_ascii=False)
    if len(raw.encode())>30000:raise PrivacyViolation('outbound size bound exceeded')
    if _CONTACT.search(raw) or _SECRET.search(raw):raise PrivacyViolation('outbound contact/credential-like value blocked')
    masked=raw
    for name in sorted(approved,key=len,reverse=True):masked=masked.replace(name,'[approved institution]')
    privacy_check(masked,Path(denylist_path))
    return len(raw.encode())
