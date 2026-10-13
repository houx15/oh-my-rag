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
These are decision thresholds, not power guarantees. The original two-comparison stopping proposal is superseded by the sustained
optimization request: continue useful isolated hypotheses until a defensible
scoped plateau or genuine blocker, within the unchanged cumulative cap. Keep C1
if inconclusive and never tune on exposed finals as though they were unseen.

The cumulative API ceiling remains $100, from a verified baseline of
$27.69268935. The authorized live comparison used a nested $12 maximum allocation
within the existing canonical ledgers, with conservative reservation before
every call. This supersedes the earlier $6 proposal; it is not a fresh ledger
allowance. Completed accounting is reported below. No deployment or private upload.


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
establish mechanics, not semantic accuracy. The frozen live evaluation below
uses separate inference and reference files; this is logical same-host separation,
not an OS security boundary. C3B remains opt-in and has not been promoted.


## Completed paired live experiment — 2026-10-13

C3B-v2 was unchanged before and after question freeze. Eight pilot questions
came from two source groups; 40 final questions from nine other groups. Final
strata: 19 conditions, 7 comparisons, 6 scope questions, 4 factual controls,
1 numerical question, 3 unanswerable questions. Eight semantically overlapping
draft topics were replaced before freeze. This was not an exhaustive semantic
contamination audit or a new-corpus test: the corpus was previously exposed,
and questions were assistant-authored with explicit source/facet cues. Separate
inference views contain no references; the source-reviewed reference files are
for judging only. Original OCR fidelity and references are not human-certified.

Generation used approved `deepseek-flash`, with thinking disabled and unchanged
C1 retrieval/schema/caps. Sequential randomized interleaving avoids concurrent
queue contamination. Paired and pointwise rubrics used the same approved
`deepseek-v4-pro`, also with thinking disabled; their errors are correlated.

| Split | C1 both adequate | C3B both adequate | C1 p95 ms | C3B p95 ms | C1 all-in USD | C3B all-in USD |
|---|---:|---:|---:|---:|---:|---:|
| Pilot (8) | 8/8 | 8/8 | 1896.4 | 1756.9 | 0.038175 | 0.037813 |
| Fresh final (40) | 40/40 | 40/40 | 1684.8 | 1795.5 | 0.319464 | 0.316990 |
| Exposed regression (20) | 18/20 | 19/20 | 2073.2 | 2235.7 | 0.135969 | 0.138908 |

All-in includes generation, pointwise judging, and half the paired judge cost.
Final generation-only costs were $0.04635390 / $0.04622310. Final p50 latency was
1522.4 / 1544.6 ms; TTFT p50 926.5 / 981.6 ms. The preselected first question per
final group (9) was repeated after regression, with p95 1713.5 / 1821.3 ms and
generation cost $0.01014300 / $0.01014060. Provider load/cache/sampling and small
samples limit latency conclusions; this is not a throughput benchmark.

Both final passes scored all four axes (correctness, support, relevance,
completeness) and citation entailment positively on every case. No final judge
disagreements or paired adequacy transitions occurred; exact McNemar p=1.
Source-group bootstrap difference is 0 with a degenerate [0,0] interval; this
reflects the observed ceiling, **not proof of equal true accuracy**. The sample
is underpowered and poorly tests numeric generalization/cross-page acquisition.
The prespecified +5 percentage-point promotion requirement was not met.
**C1 stays default; C3B stays opt-in. No claim of novel or improved RAG.**

Regression primary/secondary adequate counts: C1 19/20 and 19/20, C3B 20/20 and
19/20. Three arm/case disagreements concern completeness on one FAQ (C1) and an
appropriate unsupported-query refusal penalized by the pointwise judge (both).
The single C3B regression advantage is exposed, rubric-sensitive evidence,
not a confirmed gain. Fresh fixed-phrase refusal counts were 3 versus 2, but
C3B declined the third unsupported request with an explanatory answer. Assistant
inspection found both arms declined all three; lexical counts are only proxies.
No fixed-phrase refusal appeared on a source-answerable fresh case.

A nonrandom post-hoc assistant spot-check of eight fresh cases found a C3B
answer missing a completed-project qualifier; another scope qualifier was
missing from both answers and the authored reference. Both judging passes
accepted them. Original frozen scores/references remain unchanged and these
concerns are recorded separately. They demonstrate why automatic agreement is
insufficient, not a human-adjudicated error rate. Next priority is independent
source-page/OCR adjudication and harder natural questions before further tuning;
then isolate evidence-pool misses and facet selection. No further paid run was
launched on these now-exposed finals.

All 154 generation outputs were valid and all **358** API jobs (154 generation,
204 judging) completed without retries or unresolved journals. New cost:
**$1.00760184**; cumulative **$28.70029119**, below the $100 ceiling and nested
$12 allocation. Response usage at pinned conservative tariffs exactly matches
the canonical-ledger delta, with zero open reservations/overage. Eleven prior
ledgers retained their hashes; only the two current canonical ledgers changed.
All frozen code/input/reference hashes and ten completed journals reconcile.
Costs are accounting estimates, not invoiced bills or transferable price claims.

Reproduction entrypoints: `python -m newdomain.experiment` for freeze/main runs,
`scripts/research_supplement.py` for frozen regression/repeat, and
`scripts/research_report.py` for offline analysis. They require authorized local
private paths/ledgers; private corpus and results are not distributed. No upstream
code, weights, prompts or data were copied; README acknowledgments describe
conceptual adaptations and measurement references precisely.
