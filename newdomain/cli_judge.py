"""Judge CLI: --live for paid judging, default dry-run with cost estimation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from newdomain.paths import _ensure_outside_repo, _ensure_parent_for_output


def main() -> int:
    ap = argparse.ArgumentParser(prog="newdomain.cli_judge")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--profile", type=Path, default=None)
    ap.add_argument("--stage", default="dev", choices=["dev", "final"])
    ap.add_argument("--results", required=True, type=Path)
    ap.add_argument("--questions", required=True, type=Path)
    ap.add_argument("--corpus", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--name", default="judge")
    ap.add_argument("--mode", default="v2", choices=["v2", "cycle2"])
    ap.add_argument("--freeze", type=Path)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    if args.resume and not args.live:
        print("ERROR: --resume requires --live", file=sys.stderr)
        return 2
    if args.live and args.stage == "final" and args.freeze is None:
        print("ERROR: final runs require --freeze", file=sys.stderr)
        return 2

    for p, what in [(args.results, "Results"), (args.questions, "Questions"),
                     (args.corpus, "Corpus")]:
        if not p.exists():
            print(f"ERROR: {what} not found: {p}", file=sys.stderr)
            return 2
        try:
            _ensure_outside_repo(p, what)
        except RuntimeError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
    try:
        _ensure_parent_for_output(args.output, "Output directory")
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    out_file = args.output / f"{args.stage}-{args.name}-judge.jsonl"
    if out_file.exists() and not args.resume:
        print(f"ERROR: output already exists: {out_file}", file=sys.stderr)
        return 2

    if not args.live:
        n = sum(1 for l in open(args.results) if l.strip())
        print(json.dumps({
            "mode": "dry_run", "n_results": n,
            "estimated_judge_requests": n,
            "model": "deepseek-v4-pro",
            "note": "Dry-run: no credentials, no ledger, no network."}, indent=1))
        return 0

    if args.profile is None:
        print("ERROR: --live requires --profile", file=sys.stderr)
        return 2

    from newdomain.profile import load_profile, verify_profile, ProfileError
    from newdomain.transport import LiveContext, LiveAuthorizationError

    try:
        profile = load_profile(args.profile)
        paths = verify_profile(profile, args.stage)
        ctx = LiveContext(
            manifest_path=paths["manifest_path"],
            redaction_names_path=paths["redaction_names_path"],
            stage=args.stage,
            expected_ledger_path=paths.get("ledger_path"))
    except (ProfileError, LiveAuthorizationError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    from newdomain.judge import judge_live_v2, judge_cycle2
    try:
        if args.mode == "cycle2":
            judge_cycle2(args.stage, [str(args.results)], args.name,
                          dataset=args.questions.name,
                          output_dir=args.output,
                          casefile=args.questions,
                          corpus_path=args.corpus,
                          redaction_names_path=paths["redaction_names_path"],
                          live_context=ctx, resume=args.resume, freeze_file=args.freeze)
        else:
            judge_live_v2(args.stage, [str(args.results)], args.name,
                           output_dir=args.output,
                           casefile=args.questions,
                           corpus_path=args.corpus,
                           live_context=ctx, resume=args.resume, freeze_file=args.freeze)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
