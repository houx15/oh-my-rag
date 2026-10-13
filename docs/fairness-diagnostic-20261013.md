# Fairness audit and next experiments

The low strict-pass rates combine real system failures with measurement defects.
On48 stratified original questions (24 per corpus;12 original passes and12
failures each), assistant source review found:

| Review verdict | Guangming | Niuhuang | Total |
|---|---:|---:|---:|
| Supported original pass |11|11|22|
| Definite false pass |0|0|0|
| Genuine failure |9|4|13|
| False failure |2|4|6|
| Disputed / ambiguous |2|5|7|

These are sample counts, not population rates or human gold. Three of the six
false failures have high-confidence source evidence; the
other three false failures depend partly on the open-ended answer standard.
The13 genuine failures have9 high-confidence and4 medium-confidence judgments.
The reviewer saw scores and rationales; this was not a blinded independent review.
No raw answers or scores were rewritten. The original40 source annotations are
reused, with6 overlapping this sample, giving82 unique source-reviewed questions;
they are not pooled as82 mutually exclusive fairness labels.

## Denominators and mechanisms

The complete report has645 corpus questions:330 Guangming and315 Niuhuang.
Original user questions are113 and205 respectively (318 total), with original
primary passes65 and108. All-case passes remain223 and155.20 historical
fixed-context regression cases are separate. A pass requires all four axes=2,
both evidence booleans=true and valid output; a fail does not mean wholly wrong.

- GM015/GM016: valid life-science examples failed because they differed from
  reference examples. R089's existence question was penalized for not listing
  all reference books/counts. These are reference anchoring/coverage inflation.
- GM161: disputed. The last sentence can negate the whole supported count answer,
  or refer only to the unknown exhaustive district-wide total. The main audit now
  records ambiguous rather than an unqualified false pass. Both interpretations,
  the original full score and the earlier audit snapshot are retained. A lexical
  abstention flag does not decide the semantic label.
- GM048/GM146: relevant floor/transport source pages did not reach the context.
  Diagnose candidate recall versus evidence selection before changing generation.
- GM090: independent source-column aggregation verifies the modal application
  field108/381. Missing aggregation routing, not an arithmetic hallucination.
- GM045/GM174: the source platform-total line was deleted by preprocessing;
 381 is a subset, not the platform's total. Later focused source comparisons are recorded separately.
- N263 and other deictic questions lack dialogue context. References cannot
  establish the antecedent merely by naming one. N392 additionally violates the
  explicit one-sentence request regardless of its ambiguous antecedent.
- N322: a citation-schema error makes the displayed answer empty even though
  the raw text cautiously attributes a historical legend. Mechanical validity
  and semantic grading need separate diagnoses.
- Several Niuhuang references infer modern single-ingredient efficacy or equate
  historical terms without source support. Source-faithful historical reporting
  must not be punished for declining such inference. This audit is not medical
  validation. Text passes also do not verify UI opening/page-turning actions.

## Research linkage and acknowledgments

The existing [research matrix](research-cycle3.md) documents the requested
October12,2025–October12,2026 window, submission versus publication dates,
original papers, repository/license checks and resource limitations.
[S2G-RAG](https://aclanthology.org/2026.acl-long.1185/) informs the independently
written bounded evidence/claim-address experiments; [CompSelect](https://arxiv.org/abs/2502.11811)
informs fixed-budget selection ablations, not an implemented trained system.
[IRT-Judge](https://arxiv.org/abs/2602.00521) and
[Reliability without Validity](https://arxiv.org/abs/2606.19544) inform the
measurement-validity protocol; no IRT model was fitted. No external code,
prompts, weights or datasets were copied. SURE-RAG remains a proposed diagnostic
reference, not an adopted implementation. Existing dependency notices remain.
These are known research problems with local engineering hypotheses, not novelty
claims. Paper benchmark improvements do not establish transfer to this corpus.

## Focused next steps, not another broad sweep

1. Calibrate acceptable-answer sets for open examples, existence questions,
   historical attribution, contradictions and clarification. Human-review the
   disputed cases; use reference paraphrase and contradiction controls. Preserve
   original scores alongside any newly versioned rubric. Estimated human work:
   1–2 hours for this calibration subset, not a full gold set.
2. Fix the prepared source-pilot journal identity in a new frozen successor;
   compare old/restored input with everything else fixed. Separately test the
   modal-field/alias/count-scope operator. Neither depends on a new package/GPU.
3. Freeze fresh questions and source requirements before selecting a bounded
   evidence-recovery variant. Measure pool recall, selected evidence, answer
   omissions and false refusals separately. Keep both-domain regressions and
   abstention controls. Exposed645 remain regression data, not a fresh holdout.

A30-question two-arm generation+judge test requires120 calls. Estimate cost
from frozen token counts and obtain a shared-ledger allocation first; never
reset cumulative spend. Report paired gains/regressions, p50/p95/TTFT and total
cost including judges and failed requests. Unknown-usage DeepSeek failures can
consume a conservative$2.0064 each, requiring first-failure stop. No such new
paid experiment was dispatched during this diagnostic.

## Execution status and negative results

Bailian generation/review began and returned `deepseek-v4.1-flash`, but the fresh
unified run remains328/665 complete:321 official-provider pairs,4 Bailian pairs,
and3 official generations reviewed by Bailian. Later workspace calls timed out.
Qwen's separate3-case,6-call check returned `qwen3.8-flash`,3/3 valid and2/3
primary passes; generation3.90–4.43s. Do not merge model/provider versions.
The37-case public-source pair stopped on an invalid journal ID before any call.
This is a local harness failure, not an answer-quality result.

Accounting remains$55.93499825/$200 conservative USD ceiling, zero reservations.
Bailian CNY numeric tariffs are booked as numerically identical USD ceilings,
not invoice dollars or FX conversion. No active paid run, upload, push or deployment.

Earlier negative results remain: C2P44→36/60 against C1 and higher p95;
complete-clause packing did not establish gain; global query planning and exact
book selection did not transfer reliably. Bridge6/12→12/12 comprises4 question
clusters repeated3 times. Citation9/30→14/30 includes6 gains and1 regression.
These exposed pilots cannot replace the interrupted broad confirmation.

Local report, full48 source packs/annotations, old40 annotations, reproducibility
notebook, canonical report manifest and QA receipts are outside Git in the
fairness-diagnostic-20261013 artifact directory. The existing complete report
keeps all original answer tables and links to this diagnostic. HTML passed
structural packaging checks; installed headless Chromium was unavailable, so
visual/browser verification was not completed. No browser was installed.
