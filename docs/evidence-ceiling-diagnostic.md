# Evidence ceiling diagnostic — October 15, 2026

## Before execution

User accepts a direction-setting test of current retrieved evidence, source-reviewed complete evidence, and direct structured answers. Six exposed cases fixed in advance: GM349 (missing preceding procedure), GM120 (introduction/unsupported interface action), NH R063 (broad introduction), NH-LIVE07 (historical comparison), NH-LIVE26 (missing discovery details), REG-FAQ04 (no fabricated trial ID). This is purposive diagnosis, not a representative/held-out benchmark or human gold.

A: fresh baseline generation from frozen existing context. B: fresh same-model/prompt-family/parser generation from source-reviewed focused context, with complete evidence for explicitly frozen required facets. C: manually prepared structured response rendered without generation. C measures preparation/template feasibility and includes author labor; it is not an automatic general pipeline. B changes source selection, length and distraction, so a gain does not uniquely establish missing retrieval as cause. For missing facts, complete evidence means enough to state a bounded gap, not manufacturing the unknown. No new sources, models or privacy policy changes.

Freeze required/optional facets, source spans, prepared answers, prompts, code hashes and shuffled order before dispatch. Hold model (approved Bailian deepseek-v4.1-flash, thinking off), renderer and parser constant for A/B. Use fresh A/B generations; no paid grader: assistant source audit with explicit facets and unchanged mechanical validity, not independent human gold. Preserve raw outputs and all failures. No post-outcome prompt tuning. One sample per arm is diagnostic only; classify discrepancies cautiously.

Limit:12 serial generation calls maximum, no retries, conservative stage cap$3 and shared cumulative cap$200. Existing ledger reserve-before-dispatch and historical carry-forward required; stop on first transport failure. Unknown usage is charged conservatively. No extra review calls. Direct user “好，那我们试一下” authorizes this bounded diagnostic after the proposed three-way comparison.

Two-second requirement stays the success gate. Existing collection transport may finish late to reveal answer quality; late outputs are failures for deadline-qualified success and are never claimed as timely service. Latency excludes queue/client delivery and reports cached preparation separately. This diagnostic is not a deployment or runtime-deadline implementation. Stop interpreting slow but good answers as product wins.

Decision: if B cannot reliably satisfy verified facets, inspect generation/contract/model; if B repairs A, prioritize prepared evidence; if only C works, consider explicit narrow deterministic paths. Neither6cases nor assistant-prepared answers establish broad improvement. Original confirmation cohort untouched. No push, upload, deployment, new provider or paid model change.
