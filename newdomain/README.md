# New-domain evaluation

Repository-owned B0/C1/C2P/C2R inference adapters, saved-result reporting and
explicitly authorized generation/judging. Original external artifacts remain
unchanged. Recovery infrastructure has changed; inference contracts and judge
rubric text are preserved.

## Offline use

Run from the repository with its Python environment:

```sh
python -m newdomain.runner help
python -m newdomain.runner replay --results /private/saved-results.jsonl
python -m newdomain.cli_report --results /private/saved-results.jsonl \
  --judge /private/judge.jsonl --audit-dir /private/audit
python -m unittest discover -s tests -p 'test_newdomain*.py'
```

`runner prepare` builds retrieval/prompts without generation. All private paths
are explicit. Use `--help` for each CLI. The report distinguishes mechanical
validity, semantic adequacy, adequacy gated by valid complete generation, and
both-judge agreement. Token totals are not dollar charges. Dollar comparisons
must include the authoritative ledger, failures and judge calls.

Historical audit packs and verdicts are checked against available hashes. The
historical manifest does not pin the arm mapping: the report records its current
digest and discloses this provenance limitation. Current digests are not trusted
signatures. Group bootstrap uses supplied labels, which may only identify
questions rather than independent source families.

## Paid entrypoints

`cli_generate` and `cli_judge` default to dry-run; use explicit `--live --profile`
only within the approved budget/provider/privacy scope. The private profile
pins the authorization manifest hash, canonical `ledger.dev.json` and
`ledger.final.json` beside it, and redaction denylist. Existing ledger history
must be present; copying manifests to create a fresh allowance is prohibited.
Final runs require `--freeze` with frozen input hashes.

Both generation runners and both judges use an exclusive process lock before
preflight, an input/config/code identity header, and a durable started/terminal
journal. Results are flushed before their hash is recorded as completed.
`--resume` verifies the whole saved run before workers start. It makes no calls
for completed jobs and fails closed for unknown, failed, in-flight, missing,
duplicate or altered results. Old outputs without these records are usable for
offline reports, not paid resume. Imported legacy judge reuse is report-only.
Changing implementation intentionally invalidates resume of that run.

A completed paid response that fails the answer contract remains a completed
attempt with `valid=false`; it is never automatically paid for again. Judge
parse/transport failures stop the run and require investigation. Parallel workers
already dispatched at the time of a failure may finish and remain accounted for.

The `newdomain` synthetic suite blocks sockets and calls actual runner entrypoints
with synthetic provider responses. No live benchmark or claimed research gain
is established by passing those tests.

## Opt-in research variant

`--mode C3B` in prepare/generation uses complete-clause packing with the C1
retrieval and answer contract. It is not promoted: only offline prompt and
mechanical tests have run. `research_diagnostics` compares representation and
prompt size on exposed saved contexts without provider calls. See the research
plan for the rejected first variant and exact interpretation limits.
