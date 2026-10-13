"""Generation CLI: --live for paid dispatch, default dry-run with cost estimation."""
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
    ap = argparse.ArgumentParser(prog="newdomain.cli_generate")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--resume", action="store_true",
                    help="Resume a prior interrupted run (requires --live)")
    ap.add_argument("--profile", type=Path, default=None)
    ap.add_argument("--stage", default="dev", choices=["dev", "final"])
    ap.add_argument("--mode", default="C2P", choices=["B0", "C1", "C3B", "C2P", "C2R"])
    ap.add_argument("--corpus", required=True, type=Path)
    ap.add_argument("--questions", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--freeze", type=Path)
    args = ap.parse_args()
    if args.resume and not args.live:
        print("ERROR: --resume requires --live", file=sys.stderr)
        return 2
    if args.live and args.stage == "final" and args.freeze is None:
        print("ERROR: final runs require --freeze", file=sys.stderr)
        return 2

    for p, what in [(args.corpus, "Corpus"), (args.questions, "Questions")]:
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

    out_file = args.output / f"{args.stage}-{args.output.name}-results.jsonl"
    if out_file.exists() and not args.resume:
        print(f"ERROR: output already exists: {out_file}", file=sys.stderr)
        return 2

    if not args.live:
        return _dry_run(args)

    return _live(args)


def _dry_run(args) -> int:
    from newdomain.transport import estimate_cost
    from newdomain.profile import load_profile, ProfileError

    n_q = len(json.loads(args.questions.read_text()))
    est = {"mode": "dry_run", "stage": args.stage, "arm": args.mode,
           "n_questions": n_q, "estimated_requests": n_q}

    if args.profile is not None:
        try:
            profile = load_profile(args.profile)
            manifest = Path(profile["manifest_path"])
            cost = estimate_cost(manifest, n_requests=n_q)
            est.update(cost)
        except (ProfileError, Exception) as e:
            print(f"ERROR: profile invalid: {e}", file=sys.stderr)
            return 2
    else:
        est["note"] = "No profile; generic estimate only."

    print(json.dumps(est, ensure_ascii=False, indent=1))
    return 0


def _live(args) -> int:
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

    if args.resume and not args.live:
        print("ERROR: --resume requires --live", file=sys.stderr)
        return 2

    from newdomain.generation import run_live_v2, run_cycle2
    revision = args.output.name
    try:
        if args.mode in ("B0", "C1", "C3B"):
            run_live_v2(args.stage, [args.mode], revision,
                        output_dir=args.output,
                        casefile=args.questions,
                        corpus_path=args.corpus,
                        live_context=ctx,
                        resume=args.resume, freeze_file=args.freeze)
        else:
            run_cycle2(args.stage, [args.mode], revision,
                        output_dir=args.output,
                        casefile=args.questions,
                        corpus_path=args.corpus,
                        live_context=ctx,
                        resume=args.resume, freeze_file=args.freeze)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
