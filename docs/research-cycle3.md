# Research plan: evidence completeness and evaluation validity

Literature window: **2025-10-12 through 2026-10-12**, inclusive. This is a targeted
review. Submission, revision and publication dates are distinguished below.
Implementation status: recovery/reporting integration plus an opt-in C3B clause
packing ablation and typed numeric utilities. No new method has established an
answer-quality improvement. No unrecognized external code was installed
or executed, and no upstream source or prompts were copied.

## Failure-to-method matrix

| Measured failure class | Academic question | Bounded test |
|---|---|---|
| Missing conditions, caps and exceptions | Query-conditioned evidence coverage versus claim entailment | Preserve complete exact clauses; hold C1 retrieval/model/output contract constant. Measure needed-clause coverage and answer omission separately. |
| Cross-page evidence absent | Candidate-pool recall versus selector failure | Diagnose pool misses first; ablate bounded section continuation separately from selection. |
| Avoidable refusal | Selective prediction with sufficient evidence | Label answerability independently; report false refusals and unsupported answers separately. Do not suppress refusals globally. |
| Conversion/count/comparison mistakes | Typed compositional numerical reasoning | Independent Decimal conversion with units and operand provenance; refuse ambiguous units/scopes. Row counts are not unique-entity or real-world totals. |
| Judge disagreement and OCR uncertainty | Measurement validity, reference contamination and rubric sensitivity | Review source regions, blind arm order, perturb order/rubric, include omission/contradiction controls; preserve original scores. |
| C2P longer chunks/answers regress | Context selection under a fixed budget; confounded interventions | Separate clause boundaries, facet selection and context expansion. Record negative results; do not infer all compression/expansion fails. |

These are established research problems. Chinese qualifier preservation and
scope-aware arithmetic are testable engineering hypotheses here, not novelty
claims. Exact quotation establishes string provenance, not semantic entailment.

## Original sources and reproducibility

- **S2G-RAG**, [arXiv 2604.23783](https://arxiv.org/abs/2604.23783), first
  submitted 2026-04-26; [ACL July 2026 proceedings](https://aclanthology.org/2026.acl-long.1185/),
  DOI `10.18653/v1/2026.acl-long.1185`. Official paper-linked
  [repository](https://github.com/nianaaa/S2G-RAG), inspected commit
  `5d842a67a0a99a7b545bbad0dc402ceaae0e5eff`, had no LICENSE. Its trained
  sufficiency/gap controller and sentence pointers motivate independently written
  exact-span experiments; no code or prompts may be presumed permissively
  licensed. Full reproduction needs model/training artifacts and GPU resources;
  Mac reproduction is unverified.
- **CompSelect / Less is More**, [arXiv 2502.11811](https://arxiv.org/abs/2502.11811),
  first submitted 2025-02-17 **outside** the window, revised 2026-01-27 and
  published at WWW 2026, DOI `10.1145/3774904.3792158`. Eligible as an in-window
  publication, not a new preprint. [Official repository](https://github.com/zqc1023/CompSelect),
  commit `9a57c3ecde06064f77ae338b7c3a6a5b948c7a13`, had no LICENSE. Gold-answer
  substring extraction/truncation paths are training/oracle machinery; never
  expose final answers to a deployed selector. A local budgeted selector would
  be an adaptation, not its trained system or benchmark reproduction.
- **SURE-RAG**, [arXiv 2605.03534](https://arxiv.org/abs/2605.03534), first
  submitted 2026-05-05, revised 2026-07-24; PRAI submission is not verified
  acceptance. Claim–passage support/refutation/insufficiency and calibration
  are relevant diagnostics. A candidate repository had an Apache-2.0 license,
  but author linkage was unverified and it exposed toy/precomputed backends,
  not a full paper reproduction. No implementation adopted. Its benchmark
  ranking reversal cautions against assuming transfer to this domain.
- **Diagnosing Reliability of LLM-as-a-Judge via Item Response Theory**,
  [arXiv 2602.00521](https://arxiv.org/abs/2602.00521), first submitted
  2026-01-31, revised 2026-05-29; author-reported ICML acceptance. Linked
  `elu-lab/IRT-Judge` returned 404 during review; software license and
  reproducibility remain unverified. Start with descriptive disagreement and
  controlled rubric variations rather than fitting IRT to two judges/60 items.
- **Reliability without Validity**, [arXiv 2606.19544](https://arxiv.org/abs/2606.19544),
  first submitted 2026-06-17. Agreement/consistency need not establish human
  alignment. No official runnable repository or venue publication was verified.
- Exclude [FinAgent-RAG](https://arxiv.org/abs/2605.05409): withdrawn
  2026-07-05 for methodological errors. Do not reuse search-snippet gains.

## Experiments and resources

1. Validate evaluation labels against sources and adjudicate a balanced sample
   of agreements and disagreements. Estimated human review: 2–4 hours for a
   modest calibration sample, depending on source complexity.
2. CPU-only exact-clause boundary variant; then independent facet-aware selection.
   Same C1 candidate pool, context budget, answer schema, generation model and
   token cap. No extra inference calls initially; measure local overhead.
3. Separate typed numerical conversion/comparison variant. Never run generated
   code; retain operands/units/scope and label computed answers as derived.
4. Sufficiency diagnostics first. A learned verifier or iterative retrieval adds
   latency/cost and requires separate calibration; defer heavy training/GPU work.

Old finals are exposed diagnostics. Freeze new Chinese questions and source
requirements before selecting a candidate. Report question origin and corpus,
entity and template overlap; synthetic/source-reviewed/model-judged labels must
not be called human gold. Run paired interleaved C1/candidate tests and retain
regressions. Measure first-pass validity, per-judge and intersection adequacy,
clause coverage, supported claims, false refusal, p50/p95/TTFT, and all-in dollar
cost including judges and failures. Use source-group uncertainty where valid
group labels exist and disclose when they do not.

Proposed practical gate: at least +5 percentage points adequacy, no new invalid
outputs/regression failures or supported-claim deterioration, p95 within +10%.
These are decision thresholds, not power guarantees. Stop after two development
comparisons without a Pareto improvement; keep C1 if inconclusive. Never tune
following final exposure.

The cumulative API ceiling remains $100. Last verified spending was
$27.69268935; a new $6 allocation including at least $2 final/regression reserve
is a proposal, not an estimate or separate fresh allowance. Verify the shared
canonical ledger and reserve conservatively before every paid call. No new
paid research has run at this checkpoint. No deployment or private upload.


## Implemented offline ablations — 2026-10-13

`newdomain/clauses.py` provides **C3B-v2**, an independently written adaptation
of exact sentence-pointer evidence representation and compact clue grouping.
It reuses C1 retrieval, original chunks, system prompt, answer schema, generation
model/caps and canonical validation. Only handle boundaries change: complete
clauses are packed toward 240 characters; one longer clause stays whole within
its original chunk. S2G-RAG and CompSelect are conceptual acknowledgments, not
code/model/prompt dependencies or reproduced benchmarks. This does not repair
clauses already cut by the upstream chunker or recover absent pages.

Offline diagnosis reused the 60 exposed C1 contexts. All **60 rebuilt C1 prompt
hashes matched** their saved originals. These are development diagnostics, not
a fresh quality test. Clause instances repeat across contexts and are not
independent samples or human-verified necessary facts.

| Variant | Mean handles/prompt | Mean prompt bytes | Budget rejection count |
|---|---:|---:|---:|
| C1 | 22.27 | 15,162.85 | 0/60 |
| C3B-v1: one handle per clause | 212.60 | 25,409.50 among 14 accepted only | **46/60** |
| C3B-v2: packed complete clauses | 22.45 | 15,175.38 | 0/60 |

**Negative result retained:** C3B-v1's metadata explosion makes it unsuitable
for paid testing under the unchanged request limit. C3B-v2 has the same source
chunks and avoids 383 internal splits among 12,756 syntactically delimited
clause instances. This is a representation property, **not evidence of better
answers, correct OCR, entailment or necessary-clause coverage**. Single-pass
mean prompt construction was about 0.075 ms for C1 versus 0.235 ms for C3B-v2;
this excludes retrieval/model/validation and is not end-to-end latency evidence.
API calls and charges for these diagnostics: **zero**.

Reproduce locally with the private saved result path:

```sh
python -m newdomain.research_diagnostics --results /private/exposed-results.jsonl
python -m newdomain.runner prepare --corpus /private/corpus.jsonl \
  --questions /private/development.json --output /private/prepared --mode C3B
```

`newdomain/numeric.py` independently implements fixed Decimal conversions and
scope-checked comparisons. It is **not wired to automatic answer generation**.
It returns operand provenance, a derived flag and `premise_verified=false`;
ambiguous values, unsupported units and mismatched entity/period/measure scopes
are rejected. No paper or upstream repository is credited for this arithmetic.

Synthetic tests cover long conditions, negation/decimal preservation, exact
handle resolution, unchanged C1 defaults, numeric scales, incompatible units
and comparison scope. Real runner recovery tests also include C3B. These tests
establish mechanics, not semantic accuracy. Fresh frozen Chinese evaluation
custody is still unresolved; no paid C3B evaluation or promotion has occurred.
