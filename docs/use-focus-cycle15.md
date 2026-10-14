# Cycle15: task-focused evidence use, with unchanged validation

Completed 2026-10-14. Fourteen exposed original questions (8 targets,6 controls;
8 Guangming,6 Niuhuang), two freshly generated arms in frozen randomized order.
Evidence, original user messages, source-address instructions, model/settings,
answer budget and validators are identical within each pair. The experimental
system-only addition uses source-header/literal-name matching for biographies,
question wording for definitions/introductions, and reminders about qualifications,
uncertain referents and unavailable UI actions. No case IDs or answer facts are
hard-coded. No extra inference stage or external implementation is introduced.

## Results and decision

| Measurement | Fresh baseline | Task-focused |
|---|---:|---:|
| Raw judge passes |5/14|4/14|
| Masked assistant source-usefulness |6/14|9/14|
| Excluding explicitly borderline passes |4/14|5/14|
| Mechanical validity |13/14|14/14|
| Actual warm end-to-end p50 |5.129s|4.585s|
| Actual warm end-to-end p95 / maximum |7.898s|8.851s|

All28 outputs received separate masked source review. Same model family and prior
related context remain biases; this is not human gold. No binary source-usefulness
loss was observed, but only one gain concerns previously unused content, and that
gain is borderline. **The frozen gate required at least2 content rescues and no
new material control failure: it failed. No promotion; no fresh confirmation run.**
A lower median does not establish speed improvement; p95 is the maximum with only
14 requests per arm. No significance or population/generalization claim is made.

| Gain / remaining failure | Source-backed interpretation |
|---|---|
| GM126: abstention → candidate park facts | Only content rescue; borderline. Acknowledges missing literal name but calls the proposed park directly related, without fully resolving noisy wording or development scope. |
| GM119: asserted referent → conditional candidate | Scope/uncertainty repair, borderline; not newly recovered content and still not actual referent resolution. |
| GM124: unsupported display capability removed | Useful safety-system explanation survives in both; UI-capability correction, not content rescue. |
| N170 biography; N325 historical definition | Both fresh baseline and candidate are source-useful (N325 borderline). More focused biography/richer historical classification is secondary, not a binary gain. Original judge penalizes candidate N170; preserve that disagreement. |
| GM071/072 | GM071 discusses the transfer center and counts rather than actual selected technologies; GM072 still entirely refuses a limited district introduction. Usable evidence remains unused. |
| GM127 | Eligible new/moving financial institutions omitted; buildings/bases again appear as subsidy recipients. Exact citations do not repair the claim. |
| N466 | Properties/book lists do not answer substance identity; historical forms remain unused, and a quotation does not support the added processing-method claim. |
| R095 | Baseline raw clarification fails the existing mixed-boundary contract. Candidate becomes deliverable by answering about an unconfirmed book. Neither is useful; validity gain is not task success. |

The previous generic checklist also failed to establish content-use gain
([Cycle14](use-prompt-cycle14.md)). This stops the tested generic/task-focused
prompt-only line. It does not establish that every possible prompting, retrieval,
model or claim-planning method is exhausted. The immediate bottleneck is robust
source-grounded task/qualifier selection during generation, compounded by noisy
references and sparse nonhuman review. Another prompt-only confirmation without
passing the predefined gate would not justify a performance claim.

## Fresh-check disposition and reproducibility

Eight independently authored same-source synthetic phrasings were frozen after
implementation and before the reviewer saw this prompt or outputs. Four target
and four control cases cover both corpora. Hash:
`71a1ee409a3aef2710f8b689c71814dbac21b0cc5b9721317f36a7b9e64e66c0`.
Sixteen paired jobs are prepared but **UNRUN, zero calls**. They remain private and
frozen; no scores or confirmation success are claimed. These would test the same
parent evidence/entities, not new-corpus retrieval. Cycle14's separately frozen
8 checks also remain unrun. Do not treat prepared jobs as completed evaluations.

Each pilot answer measures a single monotonic interval from warm original-query
retrieval and prompt construction through provider generation and canonical
validation. Cold startup, uncached embedding network and separate grading are
excluded. No keyword or embedding network calls. All27 valid answers preserve
all raw factual text; the single invalid answer is R095 baseline. Both complete
system prompts, raw JSON, canonical answers and source contexts remain recorded.
83/83 delivered citations are exact selected-source substrings; this is provenance,
not entailment. All164 inherited/new scope hashes match. Actual generation and
judge model IDs are `deepseek-v4.1-flash` through the existing approved Bailian route.

56 paid dispatches:28 generation and28 judges; all settled, no retries, unknown
usage or open reservations in Cycle15. Increment **0.38709**, cumulative conservative
ledger **86.45485345/200USD**. Across Cycle14+15:136 dispatches, increment2.95489;
Cycle14 contains1 unknown-usage judge timeout charged conservatively, not zeroed.
Accounting is a conservative tariff ledger, not an invoice or currency conversion.
490 offline tests and17 focused Python-O checks pass. No provider/privacy change,
external code installation, upload, push or deployment. C1 default unchanged.

Implementation: `newdomain/evidence_use_prompt_v2.py`,
`scripts/run_evidence_use_v2.py`, `tests/test_evidence_use_prompt_v2.py`.
Reproduction requires existing authorized private corpus/cache/runtime paths;
this is not a redistributable benchmark. These are independent local engineering
hypotheses, not a reproduction of a new paper. Existing README paper credits and
license notices remain unchanged in scope; no unused method is attributed as used.

Private evidence directory: `/Users/monkey/Documents/Codex/2026-10-12/task/use-focus-cycle15-20261014/`:
`report.html`, fixed jobs, full stage trace, all28 masked reviews, raw/source score
summaries, confirmation gate/freeze, scope verification, journals and settlement.
[Canonical report](technical-report.md) connects these results to the academic
failure matrix and preserves the keyword/vocabulary and selection negatives.
