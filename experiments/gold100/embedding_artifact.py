"""Reconcile frozen embedding requests into a source/query vector artifact.

This is an offline reader. It cannot dispatch or retry requests. Failed, missing,
changed, ambiguous or unclosed calls prevent artifact construction.
"""
import hashlib
import json
from pathlib import Path
from .embedding_transport import MODEL, payload, parse_body


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def compile_vectors(directory):
    root = Path(directory)
    for path, digest in read(root / 'freeze.json')['hashes'].items():
        if sha(path) != digest:
            raise ValueError('frozen input changed')
    jobs = read(root / 'embedding-jobs.json')
    identities = {(j['kind'], j['id']) for j in jobs}
    if len(identities) != len(jobs):
        raise ValueError('duplicate job identity')
    events = [json.loads(line) for line in (root / 'calls.journal.jsonl').read_text().splitlines()]
    states = {}
    for event in events:
        key = event['key']
        if event['status'] == 'started' and key not in states:
            states[key] = event
        elif event['status'] == 'terminal' and key in states and states[key]['status'] == 'started' and event.get('success') is True:
            states[key] = event
        else:
            raise ValueError('failed or ambiguous journal')
    if len(states) != len(jobs) or any(v['status'] != 'terminal' for v in states.values()):
        raise ValueError('incomplete journal')
    totals = read(root / 'allocation/ledger.final.json')['totals']
    if totals['open_reservations'] != 0 or totals['retries'] != 0 or totals['requests_dispatched'] != len(jobs):
        raise ValueError('ledger not completely reconciled')
    source = {}; queries = {}; evidence = []
    for job in jobs:
        data = payload(job['texts'])
        digest = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        key = '|'.join([job['id'], job['kind'], digest, MODEL])
        event = states[key]
        path = root / 'responses' / ('call-' + hashlib.sha256((job['kind'] + job['id']).encode()).hexdigest() + '.json')
        if sha(path) != event.get('result_sha256'):
            raise ValueError('response content changed')
        row = read(path)
        hashes = [hashlib.sha256(text.encode()).hexdigest() for text in job['texts']]
        if row['request_sha256'] != digest or row['text_sha256'] != hashes or hashes != job['text_sha256'] or row['model'] != MODEL:
            raise ValueError('request/response identity mismatch')
        # Reuse the transport validator independently of the saved success flag.
        vectors, _ = parse_body({'model': row['model'], 'usage': row['usage'],
                                'data': [{'index': i, 'embedding': v} for i, v in enumerate(row['vectors'])]}, len(hashes))
        for h, vector in zip(hashes, vectors):
            if job['kind'] == 'corpus':
                if h in source:
                    raise ValueError('duplicate corpus text dispatch')
                source[h] = vector
            elif job['kind'] == 'query':
                if len(hashes) != 1 or h in queries:
                    raise ValueError('ambiguous query timing/vector')
                ms = row['elapsed_ms']
                if type(ms) not in (int, float) or not 0 < ms < 1e9:
                    raise ValueError('invalid query latency')
                queries[h] = {'vector': vector, 'elapsed_ms': ms}
            else:
                raise ValueError('unknown embedding purpose')
        evidence.append({'response_path': str(path), 'response_sha256': sha(path)})
    return {'model': MODEL, 'source_vectors': source, 'query_vectors': queries,
            'response_evidence': evidence, 'frozen_request_sha256': sha(root / 'freeze.json'),
            'query_latency_rule': 'Add recorded fresh query embedding elapsed_ms to retrieval+generation+validation for every R05 question.'}
