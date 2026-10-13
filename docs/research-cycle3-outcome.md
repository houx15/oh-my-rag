# Research continuation outcome — 2026-10-13

C1 remains the default. The strongest new candidate, C11B, repairs a narrow
retrieval-selection failure by retaining a missing strongest lexical chunk from
the already selected document. Targeted gains replicated when the intervention
activated, but broad superiority and safe promotion remain unestablished.

## Completed isolated comparisons

Adequacy below is conservative arm-masked assistant source adjudication, not
human gold. Questions and obligations were frozen before answers; the corpus and
failure concepts were already exposed. Every row has 24 paired questions and
48 structurally valid generation outputs. Costs exclude review unless indicated.

| Comparison | Adequate baseline → candidate | Paired wins / losses | Generation USD, baseline / candidate | Transport p95 ms, baseline / candidate | Decision |
|---|---:|---:|---:|---:|---|
| C1 → C10D definition retrieval | 17 → 19 | 2 / 0 | .0255951 / .0251286 | 1969 / 1872 | Narrow development evidence; interpretation errors remain |
| C1 → C11B lexical preservation, development | 17 → 21 | 4 / 0 | .0252858 / .0259047 | 1800 / 1928 | Promising targeted retrieval repair |
| C1 → C11B, broader inactive control | 23 → 23 | 0 / 0 | .0280401 / .0279477 | 2303 / 1995 | All prompts identical; no intervention efficacy evidence |
| C10D → C12P consistency prompt | 14 → 15 | 3 / 2 | .0257718 / .0270570 | 1932 / 1897 | Reject; regressions and contradictions |
| C1 → C11B, active-format confirmation | 19 → 22 | 4 / 1 | .0248772 / .0251697 | 1820 / 1877 | Narrow benefit replicated; retain opt-in |

The final confirmation uses full policy titles and eight families disjoint from
C11B development. Pre-dispatch inspection verified five changed contexts across
three families, no wrong-reference-document insertion and no reference-page
loss. The five active pairs yield four wins and no losses; nineteen unchanged
pairs yield one loss. This is deliberately enriched query wording, not a natural
traffic sample. One win repairs source attribution/time-anchor reasoning while
both final numerical decisions were correct. Counting that baseline as adequate
changes the total to 20/24 versus 22/24, three wins and one loss. The primary
family-bootstrap interval is -4.17 to +33.33 percentage points. Small-sample
latency differences exclude retrieval and are not production p95 estimates.

The unchanged-prompt loss reverses an explicit premise in its opening conclusion,
even though the explanation later supplies the correct condition. Earlier C11B
development also contained an unchanged-prompt transition from refusal to a
correct computed number with a wrong cap and subject scope. Both answers were
inadequate, so aggregate adequacy concealed a material change in error severity.
Neither transition establishes a selector-caused regression; both remain visible.

## Academic interpretation and evaluation limits

The [literature-to-failure matrix](research-cycle3.md) distinguishes candidate
recall, evidence selection, claim sufficiency, typed numerical reasoning and
measurement validity. The C11B result localizes some failures to fusion/context
selection: a relevant rank-one BM25 chunk existed but was discarded. C10D shows
that supplying a definition does not ensure correct operator interpretation.
C12P shows that a generic consistency instruction cannot reliably repair this.
These are established problems and local hypotheses, not novelty claims.

The paired model reviewer reports the same final aggregate 19/24 versus 22/24,
but disagrees on individual cases: it misses the contradictory opening and does
not flag the attribution issue, while penalizing an unknown-record refusal.
Earlier controls also missed explicit negation. Agreement is not validity.
OCR and authored references still require independent source adjudication;
small clustered synthetic samples cannot estimate deployment accuracy.

C1's original 60 context and prompt hashes all reproduce. C11B changes only one
of those contexts and displaces no baseline-cited chunk. On 330 exposed mixed
questions it activates on 12 (3.64%); these are offline coverage checks, not fresh
answer-quality regressions or a representative traffic distribution. Even perfect
repairs of those twelve would reach at most 3.64 percentage points on that
particular collection before losses. No broad five-point gain is established.

## Scope boundary and next experiment

There is a defensible practical stopping point for the tested family of cheap,
single-pass prompt and bounded context tweaks: clause packing, generic premise
prompts and stronger-model trials have not produced stable broad improvements;
useful retrieval repairs have narrow reach, and explicit role/operator errors
persist with the correct evidence present. This is not a global RAG plateau,
proof that other selectors fail, or a budget/authorization blocker. C11B merits
further natural-query validation, not default promotion.

The next materially different hypothesis is policy/subsection/role-aware typed
condition extraction followed by independently checked operators and units.
Correct arithmetic alone cannot repair a wrong beneficiary, period or rule.
A next study should first independently adjudicate original source/OCR and a
balanced natural holdout, then isolate extraction from execution using correct
operand controls and abstention controls. A local rule prototype needs no GPU;
learned verification or iterative retrieval adds inference and validation costs.
Allow an estimated 2–4 hours of source review for an initial calibration sample;
this is a planning estimate, not measured effort. No trained verifier, generated
code executor, new provider or third-party implementation was adopted here.

## Reproduction, costs and custody

Reusable selectors, prompts, preparation/reporting scripts and tests are committed
locally. README credits identify only conceptual methods actually used; later
papers are literature context, not retroactive implementation attribution. No
upstream code, weights or prompts were copied. See [the detailed log](optimization-log.md)
and [audited batch contract](bounded-batches.md) for mechanics and negative results.
Private questions, sources, answers, arm mappings, hashes and canonical ledgers
remain outside Git. The final handoff contains a 13-case source-adjudication
packet and per-run frozen artifacts; selected disagreements are not an error-rate
sample. Review labels remain editable separately from preserved original scores.

The five comparisons above used 360 provider calls and cost $0.99747498 including
reviews. Cumulative pinned-tariff accounting is **$31.70860407 / $100**;
$4.01591472 was added since the original $27.69268935 baseline, leaving
$7.98408528 in the nested $12 allocation and $68.29139593 globally. All seven
recorded audited batches are closed, zero reservations remain open, the audit
chain validates and all eleven historical ledger hashes match. No provider retry
was used. These estimates are not provider invoices. No upload, push or deployment.

Final tracked offline suite: **155 tests pass in normal Python and 155 under
`python -O`**. Bytecode writing was disabled. Tests cover local behavior and
accounting constraints, not semantic answer correctness or independently verified
OCR. Original C1 behavior remains unchanged.
