"""Report CLI: offline reporting from saved results, judge scores and audit verdicts.

Usage:
  PYTHONPATH=repo .venv/bin/python -m newdomain.cli_report \
      --results /path/to/results.jsonl \
      [--judge /path/to/judge.jsonl] \
      [--audit-dir /path/to/audit/] \
      [--output stdout]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from newdomain.paths import _ensure_outside_repo


def main() -> int:
    ap = argparse.ArgumentParser(prog="newdomain.cli_report")
    ap.add_argument("--results", required=True, type=Path)
    ap.add_argument("--judge", type=Path, default=None,
                    help="Primary judge scores JSONL")
    ap.add_argument("--audit-dir", type=Path, default=None,
                    help="Independent audit directory (mapping.json + verdict files)")
    ap.add_argument("--output", type=Path, default=None,
                    help="Write JSON to file instead of stdout")
    args = ap.parse_args()

    if not args.results.exists():
        print(f"ERROR: results not found: {args.results}", file=sys.stderr)
        return 2
    try:
        _ensure_outside_repo(args.results, "Results")
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    for path, label in ((args.judge, "Judge"), (args.audit_dir, "Audit"), (args.output, "Report")):
        if path is not None:
            try:
                _ensure_outside_repo(path, label)
            except RuntimeError as e:
                print(f"ERROR: {e}", file=sys.stderr)
                return 2

    from newdomain.report import full_report
    try:
        rep = full_report(args.results, judge_path=args.judge,
                           audit_dir=args.audit_dir)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    if args.output:
        if args.output.exists():
            print(f"ERROR: output exists: {args.output}", file=sys.stderr)
            return 2
        with args.output.open("x", encoding="utf-8") as fh:
            fh.write(json.dumps(rep, ensure_ascii=False, indent=1))
        print(f"written: {args.output}")
    else:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
