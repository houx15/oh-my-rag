"""Bounded frozen-source embedding transport for the authorized Gold100 campaign.

One attempt, <=10 texts, <=4096 bytes each, fixed endpoint, killable deadline.
The caller owns the immutable manifest, reserve/settle ledger and dispatch journal.
This transport has no retry or cache and returns no provider error bodies.
"""
import json
import math
import multiprocessing
import os
import queue
from pathlib import Path

ENDPOINT = 'https://api.zyai.online/v1/embeddings'
MODEL = 'text-embedding-v3'
DIMS = 1024
MAX_BATCH = 10
MAX_TEXT_BYTES = 4096
MAX_RESPONSE_BYTES = 3_000_000
DEADLINE_S = 40


def payload(texts):
    if not isinstance(texts, list) or not 1 <= len(texts) <= MAX_BATCH:
        raise ValueError('expected 1..10 texts')
    if any(not isinstance(t, str) or not t.strip() or len(t.encode()) > MAX_TEXT_BYTES for t in texts):
        raise ValueError('text blank, invalid, or exceeds byte cap')
    return {'model': MODEL, 'input': texts, 'dimensions': DIMS, 'encoding_format': 'float'}


def parse_body(body, count):
    if not isinstance(body, dict) or body.get('model', MODEL) != MODEL:
        raise ValueError('unexpected embedding model')
    usage = parse_usage(body)
    data = body.get('data')
    if not isinstance(data, list) or len(data) != count:
        raise ValueError('embedding count mismatch')
    indexed = {}
    for item in data:
        if not isinstance(item, dict):
            raise ValueError('invalid embedding item')
        i = item.get('index')
        if type(i) is not int or not 0 <= i < count or i in indexed:
            raise ValueError('embedding indices missing/duplicate')
        v = item.get('embedding')
        if not isinstance(v, list) or len(v) != DIMS or any(type(x) not in (int, float) or not math.isfinite(x) for x in v):
            raise ValueError('invalid embedding vector')
        if not any(v):
            raise ValueError('zero embedding vector')
        indexed[i] = v
    return [indexed[i] for i in range(count)], usage


def parse_usage(body):
    raw = body.get('usage') if isinstance(body, dict) else None
    n = raw.get('prompt_tokens', raw.get('input_tokens')) if isinstance(raw, dict) else None
    if type(n) is not int or n < 0:
        raise ValueError('invalid usage')
    if 'total_tokens' in raw and (type(raw['total_tokens']) is not int or raw['total_tokens'] != n):
        raise ValueError('unexpected billed output tokens')
    return {'input_tokens': n, 'output_tokens': 0}


def _worker(channel, data):
    try:
        # Read the existing credential only in the spawned process; never return it.
        key = os.environ.get('ZYAI_API_KEY')
        if not key:
            env = Path(__file__).resolve().parents[2] / '.env.local'
            if env.exists():
                for line in env.read_text().splitlines():
                    if line.strip().startswith('ZYAI_API_KEY='):
                        key = line.split('=', 1)[1].strip().strip('\"\'')
        if not key:
            channel.put({'error': 'credential_missing'})
            return
        import requests
        with requests.post(ENDPOINT, headers={'Authorization': 'Bearer ' + key},
                           json=data, timeout=(8, 25), allow_redirects=False, stream=True) as response:
            if response.status_code != 200:
                channel.put({'error': 'http_' + str(response.status_code)})
                return
            chunks = []; size = 0
            for part in response.iter_content(65536):
                size += len(part)
                if size > MAX_RESPONSE_BYTES:
                    raise ValueError('response too large')
                chunks.append(part)
            channel.put({'body': json.loads(b''.join(chunks))})
    except Exception as exc:
        channel.put({'error': type(exc).__name__})
    finally:
        channel.close()


def request(texts):
    data = payload(texts)
    ctx = multiprocessing.get_context('spawn'); channel = ctx.Queue()
    proc = ctx.Process(target=_worker, args=(channel, data))
    try:
        proc.start()
        try:
            result = channel.get(timeout=DEADLINE_S)
        except queue.Empty:
            raise RuntimeError('embedding deadline or worker exit') from None
        if result.get('error'):
            raise RuntimeError('embedding worker: ' + result['error'])
        return result['body']
    finally:
        proc.join(0.1)
        if proc.is_alive():
            proc.terminate(); proc.join(2)
        if proc.is_alive():
            proc.kill(); proc.join(2)
        channel.close(); channel.cancel_join_thread()
