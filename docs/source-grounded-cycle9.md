# Cycle9: source repair, attribution and historical coverage

The single final opt-in configuration is **source-grounded-cycle9-v5**, implemented
by `newdomain/source_grounded_pipeline_v7.py`. **C1 remains the default**: a real
historical-source repair is demonstrated, but judge instability, delivery failures
and frozen retrieval failures prevent a broad superiority claim.

## One coherent comparison

| Cohort | Cycle8-v3 baseline → final Cycle9-v5 raw adequacy | Interpretation |
|---|---|---|
| 78 original questions frozen before pilot (54 Niuhuang,24 Guangming) | 34/78 → 40/78 | Exposed development regression; source/input equivalence verified |
| Niuhuang subset | 17/54 → 23/54 | Same provider/model/rubric; explicit versioned source amendment |
| Guangming subset | 17/24 → 17/24 | Algorithm unchanged; common outputs shared |
| All 31 affected originals plus 6 stable controls | 10/37 → 17/37 | A separate 37-question diagnostic cohort, not pooled with78 |
| Six newly frozen synthetic wordings | 6/6 → 5/6 | Same-corpus transfer, not independent human gold |

The 78-question display has156 rows, **not 156 fresh generations**. For each final
input, the replay first compares ordered evidence, messages and local response
against the baseline. Exactly unchanged preparations reuse the baseline output;
changed preparations use the frozen final experiment. Canonical processing is
rerun and must produce identical answer/validity. The selection rule never reads
scores and never chooses the best earlier answer. Full lineage and hashes are in
`release/equivalence.json`. Unchanged GM controls cannot establish a new GM gain.

Raw gains: NH:R034, NH:N412, NH:R006, NH:R019, NH:R090, NH:R066.
Raw losses: none.
Mechanical validity: 77/78 → 76/78.
All 37 originals in the final direct experiment: validity
37/37 → 34/37.
These are model scores, not adjusted source-verified accuracy. Three attribution
gains are near-duplicate questions, not three independent generalization units.

## What changed and what the sources actually establish

The original local `MD-038-0008` skips from `莫之能出也` to `然。因其病`.
Its metadata calls it complete despite the missing speaker opening. The available
local scan metadata does not cover volume 50, so it cannot validate this passage.
Two public transcriptions restore `时珍曰：牛之黄，牛之病也…`.
They are two versions on one platform, **not independent facsimile verification**.

`source_amendments.py` applies a unique, exact replacement only to the expected
whole-text SHA256. The amended copy receives the new citation ID
`MD-038-0008-WS2629543`; original files remain untouched. The JSON patch records
both pinned source revisions, normalization, retrieval date and verification
limits. `speaker_evidence.py` derives exact marked-span offsets from supplied
sources. These are general data/provenance mechanisms, with no question IDs or
gold-answer lookup in inference.

R006/R019/R034 now cite an explicit speaker marker for the historical view.
Earlier attributions were unsupported by the damaged local excerpt, but public
transcriptions show that the historical claim itself was not necessarily false.
Conservative attribution alone had suppressed valid history; the source fix is
therefore more important than adding a stronger refusal instruction.

The final configuration removes the global scope suffix that regressed ordinary
coverage. It retains targeted attribution aids and historical-description
coverage. Direct current prescribing requests keep the existing local boundary;
personal symptom boundaries remain intact. Ancient statements are descriptions
of a text, not evidence of modern efficacy or personal treatment suitability.

## Negative results and remaining limits

The global scope/speaker variant on 78 originals scored 34/78 → 35/78, with 4 gains
and 3 losses; audit found both coverage changes and judge misreading. A source-only
amendment comparison on 33 originals scored 16/33 → 14/33 despite fixing the three
attribution cases. These are mixed results, not cumulative improvements.

The first coverage variant introduced a boundary enum rejected by the old
canonical processor; it is retained as a failed experiment. The corrected variant
uses the existing enum. Final direct tests still reject N390 for a source-title
alias mismatch and R010/R075 for mixed boundary fields. No repair or retry was
performed after the new frozen tests were exposed.

Frozen F01 still retrieves the wrong section/window for the requested 发明
comparison; F02 retrieves catalogue summaries and abstains despite relevant formula
records elsewhere in the corpus. Its conditional raw pass is not retrieval success. F06 refuses unsupported current occupancy data correctly, but its
shared answer incorrectly extends a five-to-seven-floor empty-tenant statement
to the eighth floor; the judge passes it. These failures block any claim that
exact citations or raw adequacy alone prove semantic correctness. F03 preserves
personal-use boundaries; F05's 46-floor total remains conditional on continuous
numbering excluding0F. H05 and the earlier T01–T12 freeze are unchanged and were
not used for tuning.

Two exact serialized judge-input payloads have contradictory historical labels
(N079,R040). This demonstrates evaluator instability without additional judging
calls. Source audits are by the same implementing assistant, unblinded, and keep
raw grades untouched; they are not independent human gold. Synthetic questions
were written after code freeze but share corpus/templates. Niuhuang synthetic
contexts are BM25-frozen and do not test a fresh embedding-retrieval pipeline.

## Academic question to measured method

| Observed failure | Established research problem | Method actually tested | Evidence / next test |
|---|---|---|---|
| Cross-page and requested-facet omission | Budgeted evidence selection and sufficient support | Existing exact-span/facet coverage, conceptually informed by S2G-RAG and CompSelect | Larger context alone regressed; targeted coverage still needs correct section routing |
| Compiler versus quoted speaker | Attribution fidelity and provenance granularity | Exact speaker markers plus hash-bound source versions | Three original cases regain supported historical attribution; frozen paraphrase fails retrieval |
| Missing source text versus abstention | Corpus validity and answerability under incomplete evidence | Explicit data amendment; historical versus current-intent routing | Strict abstention without source repair suppresses valid history; no modern efficacy inference |
| Same answer graded inconsistently | Reliability versus validity of model evaluation | Exact-input disagreement checks and source-visible paired audit | No IRT model implemented; independent blinded adjudication remains needed |
| Floor/rate/count errors | Scoped symbolic derivation and entity/denominator control | Existing conditional floor arithmetic; no new numeric algorithm this cycle | F05 conditional success; F06 source-detail false pass retained |

The dated paper/repository/license matrix remains in [research-cycle3.md](research-cycle3.md).
S2G-RAG first appeared April 26, 2026 and has an ACL 2026 publication. CompSelect's
February 17, 2025 first submission is outside the requested October 12, 2025–October 12, 2026
window; its January 2026 revision and WWW 2026 publication are within it. It must not
be called a newly submitted in-window paper. No unlicensed repository code,
weights, prompts or new packages were copied or run. These independently written
CPU methods are not trained-paper reproductions and make no novelty claim.

The next useful research step is a blinded, adjudicated set separating corpus
completeness, historical attribution, answer coverage and current intent. A small
source review is estimated at 2–4 reviewer hours; this is a planning estimate, not
measured labor. Only then should a new freeze test section-aware routing and
boundary-schema reliability. No more prompt variants on these now-exposed cases
are counted as independent validation. No new GPU training is justified here.

## Cost, latency and reproducibility

Across five paid phases: **623 calls**, **CNY4.865454** known-token peak-rate
estimate, no retries, no new unknown usage, no open reservations after completion.
Conservative cumulative accounting: **$81.46649225/$200**. CNY tariff numbers are booked
at the same numeric USD value as a conservative ceiling; this is not FX or an invoice.
Existing Bailian deepseek-v4.1-flash only, temperature 0.2, max 800 tokens,serial calls.
All completed Cycle9 outputs remain below 20s; slowest observed phase output is
15.191s.

The final direct 37-original experiment has baseline/candidate warm p95
6.513s / 5.487s.
The 78-question replay includes inherited timings and shared outputs, so it is not
a fresh latency trial. Twenty seconds remains the SLA threshold, not the transport
timeout. Earlier cycle8's 20.762s tail remains in history.

460 offline tests pass; all 10 new focused tests also pass under Python-O. Frozen
input hashes, source offsets, job hashes, canonical replay and ledger settlements
are checked in the private run bundle. No production promotion, push, deployment
or artifact upload occurred. The original source corpus is unchanged.

Private bundle: `source-grounded-cycle9-20261014/` contains frozen jobs, all raw
outputs, journals, summaries, audits, `build_release.py`, `verify.py`, test logs and
`report.html`. It requires the existing approved local corpus and prior preparation
bundle; it is not a portable public benchmark. No credentials are included.
