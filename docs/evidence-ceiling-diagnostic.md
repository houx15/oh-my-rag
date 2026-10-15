# Evidence ceiling diagnostic — October 15, 2026

## Before execution

User accepts a direction-setting test of current retrieved evidence, source-reviewed complete evidence, and direct structured answers. Six exposed cases fixed in advance: GM349 (missing preceding procedure), GM120 (introduction/unsupported interface action), NH R063 (broad introduction), NH-LIVE07 (historical comparison), NH-LIVE26 (missing discovery details), REG-FAQ04 (no fabricated trial ID). This is purposive diagnosis, not a representative/held-out benchmark or human gold.

A: fresh baseline generation from frozen existing context. B: fresh same-model/prompt-family/parser generation from source-reviewed focused context, with complete evidence for explicitly frozen required facets. C: manually prepared structured response rendered without generation. C measures preparation/template feasibility and includes author labor; it is not an automatic general pipeline. B changes source selection, length and distraction, so a gain does not uniquely establish missing retrieval as cause. For missing facts, complete evidence means enough to state a bounded gap, not manufacturing the unknown. No new sources, models or privacy policy changes.

Freeze required/optional facets, source spans, prepared answers, prompts, code hashes and shuffled order before dispatch. Hold model (approved Bailian deepseek-v4.1-flash, thinking off), renderer and parser constant for A/B. Use fresh A/B generations; no paid grader: assistant source audit with explicit facets and unchanged mechanical validity, not independent human gold. Preserve raw outputs and all failures. No post-outcome prompt tuning. One sample per arm is diagnostic only; classify discrepancies cautiously.

Limit:12 serial generation calls maximum, no retries, conservative stage cap$3 and shared cumulative cap$200. Existing ledger reserve-before-dispatch and historical carry-forward required; stop on first transport failure. Unknown usage is charged conservatively. No extra review calls. Direct user “好，那我们试一下” authorizes this bounded diagnostic after the proposed three-way comparison.

Two-second requirement stays the success gate. Existing collection transport may finish late to reveal answer quality; late outputs are failures for deadline-qualified success and are never claimed as timely service. Latency excludes queue/client delivery and reports cached preparation separately. This diagnostic is not a deployment or runtime-deadline implementation. Stop interpreting slow but good answers as product wins.

Decision: if B cannot reliably satisfy verified facets, inspect generation/contract/model; if B repairs A, prioritize prepared evidence; if only C works, consider explicit narrow deterministic paths. Neither6cases nor assistant-prepared answers establish broad improvement. Original confirmation cohort untouched. No push, upload, deployment, new provider or paid model change.

## Completed result

All12fresh generation calls completed, zero dispatch failures/retries and zero open reservations. The brief host disconnect did not block this batch; no calls were replayed. Cost$0.063908; conservative cumulative$122.04494745/$200, remaining$77.95505255. Baseline/default unchanged; no push, upload or deployment.

| Six deliberately selected exposed cases | Current evidence A | Focused complete evidence B | Prepared record answer C |
|---|---:|---:|---|
| Mechanically valid generated output |5/6|6/6|Not the same generated schema; exact prepared-source spans checked6/6|
| Required facets satisfy assistant source review |4/6|5/6, one uncertain|6/6by prior manual construction/review, not blind accuracy|
| Both valid and required facets satisfied |3/6|5/6|Not a comparable automatic-pipeline rate|
| Complete generated response within2seconds |0/6|0/6|Only local known-case render measured; not client SLA|
| Cached component p50 |3.713s|3.816s|0.0017–0.0119ms for six individual warm renders|
| Observed range |2.874–5.775s|2.700–4.536s|Excludes manual preparation, loading, routing and client delivery|

These are descriptive assistant source judgments against frozen required facets, not an LLM judge score, independent human gold, or a statistically established baseline win. A/B preserve identical system instructions, model, output parser and temperature. B changes evidence admission, amount, segmentation and distraction; source-count/byte equality is not imposed in an evidence-ceiling test. Prepared contexts shrink from11,287→1,212bytes(GM349),15,243→519(GM120),4,353→2,669(R063),4,379→2,670(LIVE07),2,888→102(LIVE26); FAQ stays510bytes with byte-identical prompts. Do not generalize this as “more context is better.”

### What each comparison establishes

- **GM349:** A omits application, preliminary review and re-review. B names all five pre-signing steps and the correct subsidy start. This supports a repairable evidence-selection defect. In both answers, the first subsidy citation says “上述协议” without its antecedent; agreement evidence appears in the second sentence's citation. Answer-level coverage is present, but standalone citation dependency remains imperfect. This is not a perfect citation audit pass.
- **GM120:** A unnecessarily abstains. B gives a source-supported introduction. That passage already existed in A: this is consistent with improved evidence focus/use, not new retrieval recall. Neither answer falsely claims to switch the Pad. One sample cannot separate context influence from stochastic generation.
- **NH R063:** both satisfy the concise-introduction requirement. No need to demand optional drug-count or heritage-register facts. No meaningful quality gain.
- **NH-LIVE07:** both provide historically scoped comparisons. B is shorter and uses two selected source versions; A mentions an additional version. Both remain source-specific rather than asserting a universal modern formulation. No new correctness gain established.
- **NH-LIVE26:** A explicitly discusses missing discovery/book-account evidence. B reports the legend and missing discovery sequence but uses a generic boundary for the book-source subquestion, leaving completeness uncertain. Less context does not guarantee better coverage. A's title-only citation is not independent proof of absence; that statement is bounded to the supplied context.
- **REG-FAQ04:** both refuse to invent an identifier. A incorrectly cites the fixed disclaimer and is mechanically invalid; B passes. **Prompts are identical**, so this difference is a stochastic contract failure, not a benefit of curated evidence. The FAQ's medical claims are not endorsed.

Two source-content improvements (GM349 and GM120) are useful leads. The valid-and-facet3→5difference also includes one identical-prompt validity fluctuation and one uncertain completeness loss; it is not a clean two-case causal treatment effect. No resampling or confidence interval is meaningful as evidence of broad efficacy from these six deliberately chosen, source-reviewed, historically exposed cases and one sample per arm.

### Prepared answers and verification

All six C answers were frozen before dispatch alongside required/optional facets and exact source offsets/hashes. The offline renderer verifies each span against the frozen source and adds citations; no model call. They satisfy the intended facets by assistant review. This is case-specific preparation, including manual wording and source selection, not proof that an automatic router can produce correct answers to new questions. C has no comparable automatic mechanical-validity rate and its tiny lookup/render time cannot be substituted for full service latency.

Raw responses, prompts, reviewer notes, JSON summary, deterministic rendered answers and a four-column HTML comparison remain private under `evidence-ceiling-20261015`. Original source/context artifacts and confirmation cohort were unchanged. Frozen prompts were screened before allocation and again at dispatch. Analysis verifies12unique outputs, expected returned model, unchanged frozen hashes and exact prepared citation spans. No paid grader was used. No implementation or prompt was tuned after seeing these outputs.

### Decision

This diagnostic does **not** support the claim that the current model cannot answer well. It can answer the two prominent failed questions once their evidence is complete or focused. Invest next in independently preparing complete evidence for a small set of recurring question families, including source dependencies and verified boundaries; evaluate on new paraphrases and compound requests. Keep flat records as the control for any graph implementation.

However, evidence curation alone does **not** solve latency (both arms0/6under2seconds), and even focused evidence does not guarantee subquestion completeness or citation-contract compliance. For the hard2second target, pursue a narrowly validated prepared-record/direct-render path where appropriate, and separately evaluate faster approved generation routes for the remaining requests. No new paid experiment is initiated by this conclusion. Keep baseline and this diagnostic separate until broader independent testing shows a reliable gain.
