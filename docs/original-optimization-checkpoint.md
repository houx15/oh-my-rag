# Original-question optimization checkpoint, 2026-10-13

No candidate in this checkpoint is promoted to the default. Primary generation
and scoring calls use `deepseek-flash`, verified as the V4.1 Flash alias on the
same day. This is source-grounded development evidence, not human gold.

| Experiment | Comparable completed cases | Original/baseline passes | Candidate passes | Decision |
|---|---:|---:|---:|---|
| Direct-subject property evidence, 牛黄 | 15 original live | 7 fresh reviews | 9 fresh reviews | Narrow evidence, no broad promotion |
| Answer-focus suffix, 牛黄 | 149 of315 | 37 original reviews | 72 fresh reviews | Partial; retain for investigation only |
| Same answer-focus suffix, 光明 | 20 of30 generated/reviewed | 13 original reviews | Invalid comparison | Evidence-order harness error; fresh reviews pending |

The property experiment has three gains and one loss; the two discovery cases
both improve, while the13 exposed transfer cases have no net gain. All300
nontriggering 牛黄 contexts remain byte-identical offline. It supplements direct
subject entries and preserves competing historical accounts with four sources;
it does not establish modern medical truth. The implementation is a narrow
experimental selector, not a general medical-answer lookup.

The answer-focus experiment changes only a system-prompt suffix: directly answer
the requested dimension, preserve scope, distinguish subjects and historical
claims, avoid unsupported missing-context guesses. It uses fixed original
retrieval evidence and the unchanged K/C1 schemas and scoring rubric. The 光明 evaluation harness incorrectly canonicalized handles against sorted map
order instead of original retrieval order. Its20 scores are invalid for comparing
the method. Raw outputs are preserved; all20 answers were reconstructed offline
from the original ordered retrieval evidence and pass mechanical validation.
Fresh review is pending, without regenerating. `ordered_context.py` and regression
tests prevent this source-binding error. No global promotion is justified.
Original-review versus fresh-review noise remains a confound for the partial 牛黄 result.

The declared batch is345 cases: all315 eligible unique 牛黄 questions plus30
preselected 光明 validation questions. It stopped on a local outbound-size check
before reviewing NH:R094; its generation is saved. There are170 generations,
169 original review records (20 invalid for comparison),175 never-generated
cases,176 outstanding original reviews plus20 corrected-answer reviews,339 dispatched
calls, zero retries, zero open reservations. Do not rerun completed calls. Repair
review evidence budgeting and enforce original retrieval order (preserving the answer and its cited sources),
freeze a continuation, and reuse every saved result under auditable custody.
This is **not a completed full 牛黄 retest**. Failures remain in the declared scope.

Forty additional 光明 questions are reserved from further tuning. All supplied
questions have previously been evaluated, so this reservation is not an untouched
independent holdout. No extra natural conversation batch has been supplied yet.

## Next causal experiments

The strongest unresolved distinction is retrieval coverage versus evidence
selection versus interpretation. Use a small fixed development subset to compare
original top4/top8 against query-conditioned selection from the existing top20
pool. Keep generation fixed and record selected IDs, exact preview spans,
selection failures, quality, latency and cost. `evidence_selector.py` implements
this bounded selector and fail-closed tests; it has not yet made paid calls.
Only if this fails because relevant evidence is absent from the pool, test query
alternatives or corpus partitions with cross-partition fallback. Do not bolt on
all techniques at once. Reference-source oracle diagnostics are allowed only in
explicit diagnostic runs, never as production retrieval input.

`entity_bridge.py` independently links catalogue names to detailed source pages
without rewriting the original question. Offline it finds four changes outside
the reserved 光明 subset, including the previously missed D30:7:01 detail page.
No answer-quality improvement has yet been measured. `query_variants.py` stores
the user's guarded 派的→pad retrieval hypothesis and conventional document terms;
it is tested but not integrated or promoted. These are candidate methods, not
features claimed to improve quality.

Public web research is separate from private question processing. Any later
web-assisted answers must form a separate open-world cohort. No private queries
or corpus text were sent to public search, no external code installed, no upload,
GitHub push or deployment occurred.

## Accounting and model transition

Property cycle:45 requests, $0.04067310. Partial answer-focus cycle:339 requests,
$0.35134020. Prior cumulative spending $34.41373425; current **$34.80574755**.
All dispatches settled, zero retries/open reservations. User now authorizes
**$200 total**, not additional. The active manifest remains its original $100
scope; tested successor code can apply the explicit $200 amendment while carrying
all previous accounting. Do not edit the active frozen manifest or reset ledgers.

User requests GPT-6 Astra with medium reasoning for the working task. Active
runtime settings are not exposed here; the checkpoint does not claim a verified
model switch. Continue in the requested configuration after this safe handoff.

Private evidence lives under `/Users/monkey/Documents/Codex/2026-10-12/task/` in
`property-fix-cycle-20261013/`, `answer-focus-cycle-20261013/`, and
`original-source-audit-20261013/`. Raw outputs stay outside the repository.
