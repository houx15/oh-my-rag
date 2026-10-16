"""Offline R10/R09 prompt preparation and response validation; never calls an API."""
import argparse
import json
from pathlib import Path

from .baseline import Index as ChunkIndex
from .r05 import text_key
from .r09 import Index, messages, spans, validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo', action='store_true')
    parser.add_argument('--records', type=Path)
    parser.add_argument('--vectors', type=Path)
    parser.add_argument('--query-vector', type=Path)
    parser.add_argument('--question')
    parser.add_argument('--response', type=Path, help='JSON response envelope to validate')
    args = parser.parse_args()
    if args.demo:
        if any((args.records, args.vectors, args.query_vector, args.question, args.response)):
            parser.error('--demo cannot be combined with input files')
        records = {'D01:1:01': '（一）示例项目\n示例项目仅供离线演示。'}
        query = [1.0] * 1024
        vectors = {text_key(c['text']): query for c in ChunkIndex(records).chunks}
        question = '示例项目用途是什么？'
    else:
        if not all((args.records, args.vectors, args.query_vector, args.question)):
            parser.error('provide --demo or all four records/vectors/query-vector/question inputs')
        records = json.loads(args.records.read_text(encoding='utf-8'))
        vectors = json.loads(args.vectors.read_text(encoding='utf-8'))
        query = json.loads(args.query_vector.read_text(encoding='utf-8'))
        question = args.question
    chunks = Index(records, vectors).search(question, query)
    result = {'configuration': 'R10 unchanged R09', 'messages': messages(question, chunks)}
    if args.demo:
        handle = next(iter(spans(chunks)))
        raw = {'content': json.dumps([['示例项目仅供离线演示。', [handle]]], ensure_ascii=False),
               'stream_done': True, 'finish_reason': 'stop'}
        result['demo_only'] = 'Synthetic vectors and canned answer; no quality or latency evidence.'
    elif args.response:
        raw = json.loads(args.response.read_text(encoding='utf-8'))
    else:
        raw = None
    if raw is not None:
        result['validation'] = validate(raw, chunks)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if raw is not None and not result['validation']['valid']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
