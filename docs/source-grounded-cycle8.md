# Source-grounded cycle8: paired validation and evaluation reconciliation

This opt-in configuration uses the existing approved Alibaba Cloud Bailian
`deepseek-v4.1-flash` for generation and unchanged-rubric judgment. There is no
per-question answer selection. The default remains unchanged pending the results
and source-level limitations below; no production deployment was performed.

## Why the historical Niuhuang numbers differ

The old108/205 is the complete typed-v2 report selected by domain, with reused
results explicitly recorded. It is not the interrupted coherent-fresh run.
All205 saved report scores match their typed-run records. Both old generator and
judge returned `deepseek-flash` through `https://api.deepseek.com/v1`; both new
ones return `deepseek-v4.1-flash` through the existing Bailian workspace endpoint.
Model names do not establish identical underlying weights.

All205 retrieved source ID/text mappings match across runs, but197prompt evidence
sequences differ. The new prompt additionally bounds citation addresses. Both use
temperature0.2, max800outputtokens, disabled thinking and JSONobject mode. The
rubric/pass rule is unchanged, but the judging model changed. Reference fields
match for204/205; R094's reference-source payload differs. Compiler failures and
invalid-answer payload handling also differ.167historical generation hashes were
reconstructed;38reused-generation cases have no new request in that journal.

Thus108→80 is not a controlled retrieval/model regression. Cross-run transitions
are63pass→pass,45pass→fail,17fail→pass,80fail→fail. This cycle fixes the current
provider/model and performs paired comparisons, retaining every original score.

## One application-facing configuration

`newdomain/source_grounded_pipeline_v2.py` exposes `SourceGroundedPipeline`:

- `prepare_nh(question, baseline_context, build_messages)` applies the same
  corpus-derived book/person/formula coverage for every question, bounds context
  to four records, emits exact contiguous source windows with original offsets,
  and returns either approved messages or a strict local nonfactual boundary.
- `canonical_nh(raw, context, processor)` retains existing factual validation;
  only explicit, exact typed clarification/current-symptom boundaries can bypass
  factual citations. Arbitrary uncited prose is never accepted.
- `prepare_gm(...)` consumes the existing recovered/public source context and
  adds an arithmetic plan only when a relevant source explicitly supplies the
  floor range. It distinguishes above/below ground and states the continuous
  numbering/no0F convention. It does not change H05's unmatched wording trigger.

The pipeline is transport-independent and accepts the existing retrieval/message/
validation adapters. Evaluation uses this same class; case IDs, references and
scores are not inputs. Earlier module versions remain immutable for reproduction.
No new provider, model training, embedding service, GPU or third-party package is
required. Current-symptom and pronoun rules are intentionally limited heuristics,
not general medical intent or conversational-state understanding.

## Academic problems and actual engineering tests

| Failure | Research problem | Actual method/ablation | Resource/limit |
|---|---|---|---|
| Book/author/formula evidence omitted | Query-conditioned coverage under fixed budget | Corpus metadata links, explicit named-facet allocation, exact section windows | CPU only; four contexts,900characters/source; metadata is not proof of authorship/influence |
| Needed clause after truncated prefix | Evidence localization versus candidate recall | Retain header plus one source-addressed body window | No extra generation call; quotes still require semantic interpretation |
| Nonfactual clarification rejected | Selective prediction and structured output validity | Exact typed clarification; separate local current-symptom boundary | Zero generation call for local routes; no arbitrary prose exemption |
| Floor range repeated instead of counted | Typed numerical reasoning and operand scope | Source-grounded above/below arithmetic plan | No generated-code execution; conditional count, not surveyed building dimensions |
| Restoration changes ranking | Confounded retrieval interventions | Old rank/restored hydration versus restored-source ranking | Tiny diagnostic ablation, no ranking adoption justified |
| Model scores conflict with evidence | Reliability versus validity | Fixed rubric/raw scores plus separate source-visible assistant audit | Not blinded or human gold; no adjusted accuracy or generalization claim |

Evidence coverage and source-window experiments continue the conceptual
acknowledgments to [S2G-RAG](https://aclanthology.org/2026.acl-long.1185/) and
[CompSelect](https://arxiv.org/abs/2502.11811). Evaluation separation is informed by
[IRT-Judge](https://arxiv.org/abs/2602.00521) and
[Reliability without Validity](https://arxiv.org/abs/2606.19544).
See [research-cycle3](research-cycle3.md) for first-submission/publication dates,
official repositories and license limitations within the requested
2025-10-12–2026-10-12window. No upstream code, prompts, assets, weights or datasets
were copied or run, and no learned controller/selector/IRT model was reproduced.
Floor arithmetic and typed query boundaries are independent engineering; they are
not attributed as implementations of unused papers. No novelty claim is made.

## Scope and validation

The first pilot covers22 exposed originals plus four retrieval-only and two
hydration diagnostics. The second frozen configuration covers all32 original
Niuhuang questions whose evidence or local route changes, eight hash-selected
unchanged Niuhuang controls, six Guangming controls, and12synthetic wording checks
frozen before implementation. Selection is by pipeline behavior, not judge scores.

Original questions are exposed development evidence. Synthetic questions are
source/task-designed by the same assistant and not external human holdout.
Synthetic Niuhuang baselines use frozen BM25 contexts because no cached query
embedding exists; these are context-transfer tests, not full fresh-query E2E.
Identical prompts may share a journal-verified output and are explicitly marked.
No source-audit verdict replaces the unchanged model score.

All450offline tests pass; the eleven new focused tests also pass with Python-O.
An initial sandboxed full-suite invocation failed because existing tests write
inside the repository; the authorized rerun passed. No test failure was hidden.


## Final measured result

| Cohort | Current Bailian reference | Single final candidate |
|---|---:|---:|
| Targeted Niuhuang originals |12/43|17/43|
| Guangming original controls |4/6|5/6|
| Originals together |16/49|22/49|
| Pre-frozen synthetic wording |5/12|10/12|

Originals have10raw gains and4losses; synthetics5gains and0losses. Five original
Guangming controls and two synthetic controls share identical-prompt outputs;
these are not independent improvement samples. All original candidate outputs
are mechanically valid49/49versus48/49; synthetic12/12versus10/12. Mechanical
validity does not establish factual correctness.

The final configuration is `source-grounded-cycle8-v3`. The completed116-output
validation exposed a pronoun-rule error on an explicitly named oral-ulcer
medication question. A versioned correction now distinguishes that request from
missing-reference clarification and narrows the pronoun pattern.114records
passed exact preparation and canonical-output identity checks and retain their
original scores; two changed local outputs were rejudged. Three additional
original questions affected by the corrected rule received fresh paired checks.
The final122display records therefore cover49originals and12synthetic pairs;
only affected outputs were rerun, never chosen by score. Final NH coverage is all
36evidence/local-route changes plus7unchanged controls. It is not a fresh rerun
of all205Niuhuang originals or an update to the old80/205denominator.

A representative real fix is NH:R004, asking how the *Bencao Gangmu* describes
Niuhuang's historical `ding jingshen` effect. The baseline says the specific
text was not provided, citing only a catalogue summary. The candidate retrieves
MD-038-0008's main-entry indications window and quotes the exact phrase with its
recorded attribution. The source is shown verbatim in the private report; this
is recovery of a historical passage, not modern efficacy validation. N350/N353
recover the cooling-versus-neutral descriptions; R021 recovers a missed exact
phrase. GM048 now derives42above+4below=46with an explicit counting convention.
H05's unmatched floor-range wording remains untouched and visible.

## Negative results and promotion decision

Do not treat all raw gains as source-confirmed improvements. R090 turns absence
of an explicit relationship into an overly strong negative statement; R006/R019
still risk confusing an author's own views with people quoted in a book. The
selected main-entry text contains an anomalous transition in its commentary,
so speaker attribution cannot be certified from this excerpt. T01 recovers both
similar book titles but overstates what absence from a catalogue excerpt proves
about a whole book. N417 still misses a historical person's statement quoted by
a later author; R042 lacks classification criteria; R077 misses core indications.

N095/N079 losses involve near-equivalent answers judged inconsistently. The
additional N412/R075 losses expose a real coverage tradeoff: a boundary avoids
modern efficacy/medication claims unsupported by historical evidence but may
omit useful historical content the user wanted. No loss is relabeled as a pass.
T10 reveals a synthetic-criterion scope problem: the question asks for the main
tower and the answer distinguishes42main-tower floors from a46range-based total;
a frozen criterion favoring46must not override the actual question.

All22pilot pairs and51of61final pairs have source-visible assistant review. It
is unblinded, performed by the implementer, not independent human gold, and is
never converted to adjusted accuracy. The combined candidate is **not promoted**.
The concrete next bottlenecks are cited-speaker/whole-source scope, intent-sensitive
historical versus modern answers, and source/OCR/reference adjudication. These
are demonstrated failure classes, not a claim that exposed tests cannot be useful.

The pilot's raw result was5/22to7/22; retrieval-only arms0/4. Source windows
helped some answers even where the judge rejected them. The tiny old-rank/restored
hydration ablation did not establish a ranking advantage and is not adopted.

## Latency, cost and verification

The final comparison retains115actual warm measurements, each labeled with its
measurement phase: p50 **4.066s**, p95 **5.580s**, maximum **20.762s**; one exceeds
the20s target. The outlier is GM067, an identical-prompt shared control, not
proof that the new method caused delay. NH-original p95 is6.787sreference versus
4.705scandidate, but the candidate includes12local boundaries, so this is not a
pure model-speed comparison. Cache reuses have no invented fresh measurement.

Core validation process preparation is3.136s, including3.084sindex/cache work.
This starts inside the process and excludes interpreter startup/earlier imports;
OS disk cache is uncontrolled. Uncached embeddings, UI/TTS and offline judgment
are excluded from response latency. Synthetic NH fixed-context checks are labeled
separately; no new embedding API was called.

All four dispatch phases together: **305calls** (145generation,160review),
945221input and32027output tokens, **CNY2.146658**peak-rate estimate. Cumulative
conservative accounting is **$76.60103825/$200**, with0retries,0newunknown-usage
settlements and0open reservations. Old conservative settlements remain. CNY
rates are booked at the same numeric USD ceiling, not an FX conversion/invoice.

450offline tests pass;11new focused tests also pass underPython-O. Frozen input
hashes, every successful response/journal, unchanged scores, replay equivalence
and costs reconcile. Report QA is structural, not browser visual inspection.
Private artifacts are in `source-grounded-cycle8-20261014`, with baseline
reconciliation, phase jobs/manifests/journals, full answers, source audits,
equivalence proofs, summary, verification and four-column HTML. Nothing was
uploaded, pushed or deployed; no unrecognized code was installed or executed.
