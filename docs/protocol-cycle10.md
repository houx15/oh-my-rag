# Cycle10: protocol repair and isolated source effects

**C1 remains the default. No experimental candidate is promoted.** This cycle
repairs three known delivery failures deterministically and isolates the source
patch from section selection. It does not demonstrate a broad quality improvement.
The final frozen experimental adapter is `newdomain/source_grounded_pipeline_v8.py`
with `source=True, sections=True, protocol=True` and the explicit alias registry.
All factorial arms share the Cycle8-v3 generator prompt and intent policy; this is
not a renamed rerun of Cycle9-v5. The reusable protocol normalizer also repairs
Cycle9-v5 outputs without changing their generation or source selection.

## General protocol repair

`protocol_normalization.py` accepts only declared full-string, nonfactual boundary
grammar and explicitly registered source-title aliases. Empty citations are
required for boundary normalization. Unknown text, extra factual clauses,
nonempty citations, duplicate JSON keys and incomplete responses still fail
closed. No facts or citations are repaired by a second model call. Original raw
outputs and every transformation are retained.

Across **328 original-question Niuhuang output records**, offline replay repairs
four delivery failures: the three final Cycle9 losses N390/R010/R075 and one older
R010 failure. **Zero previously valid answers change; zero validity regressions.**
For the previously measured37-original Cycle9 cohort, candidate delivery becomes
34/37 →37/37. This is a mechanical replay result, not a new adequacy score or proof
that the historical content is appropriate for current medical intent. The
separate reviewer still finds coverage and selected-citation issues in repaired
answers. Old raw scores remain unchanged.

The title alias 《本草经疏》 →《神农本草经疏》 is explicitly grounded in the local
record's catalogue/transcription metadata. Its record hash and exact note were
independently checked for this frozen corpus. The normalizer itself does not
validate the full record hash at runtime; the frozen manifest binds this run.
Do not advertise this as automatic proof of aliases in arbitrary future sources.
No generic substring/suffix alias guessing is allowed. The newly generated 《普》
from 普曰 remains rejected, correctly preserving a substantive attribution guard.

## Controlled ablations

A preparation scan covers all **318 original questions**. Exactly11 preparations
change under the source/section factors; all11 plus3 unchanged controls from each
corpus were evaluated. The other307 preparations are unchanged, but this does not
create a new318-question accuracy estimate. All GM behavior is unchanged.

| Frozen cohort | Baseline + protocol | Source only | Sections only | Both |
|---|---:|---:|---:|---:|
| 17 original questions, raw adequacy | 10/17 | 10/17 | 9/17 | 9/17 |
| 17 originals, delivered validity | 17/17 | 16/17 | 17/17 | 16/17 |
| 6 separately authored synthetic checks, raw adequacy | 5/6 | 5/6 | 5/6 | 5/6 |
| 6 checks, delivered validity | 6/6 | 6/6 | 6/6 | 6/6 |

The source-only factor replaces the exact missing-text anchor inside the already
selected window. It validates the complete original record first and introduces
a new source-version ID; it does not retrieve another record, choose a new window
or reorder evidence. Ten original preparations contain the patch anchor.
This isolates it more cleanly than Cycle9's amendment adapter, which regenerated
windows while rewriting source IDs.

The sections factor uses literal names from source headers and exact-offset,
budgeted windows. It can prepend a uniquely matched record and drop the last
existing one, so it is **section-aware source selection plus window extraction**,
not a pure window-only treatment. Only one original preparation changes under this
factor. Literal matching can include negated or incidental mentions; no semantic
intent-classifier claim is made. Source-driven development tests use other
synthetic book sections. No old F01–F06 wording or expected answer was used for tuning.

All arms use the same approved Bailian deepseek-v4.1-flash, decoding settings,
reference construction and judge rubric. Identical generation/review inputs share
verified outputs; shared rows are not independent replications. A source-text
change can alter stochastic wording even when the changed passage is irrelevant
to the question, so a raw score difference alone is not causal evidence of a
specific factual improvement.

## Independent source review and negative results

A separate read-only assistant first reviewed16 original outputs, then reviewed
28 deduplicated factorial and12 independent-check outputs with random IDs and
without arm labels or scores. No second repository writer or paid reviewer was
created. The reviewer uses the same model family, had seen related development
examples, and authored the six new checks: this is useful label-blinded review,
**not independent human gold or cross-model validation**.

The review verifies a real provenance benefit for R006: the restored speaker
opening supports a claim that the unamended selected passage cannot attribute.
R019 gains supported historical coverage; R034 trades one supported facet for
another. In R090 the source-arm wording improves excerpt scope even though the
raw judge score falls. N390 gains better selected-citation support. These mixed
observations do not justify an adjusted accuracy number.

The new 《普》 failure is an appropriate rejection, not a title-alias defect to
bypass. The section-changed original 夜啼 answer improves a bibliographic quote but
adds unnecessary historical quantities to an ambiguous utterance. The combined
arm therefore loses one raw pass on the original cohort and is not promoted.

On the separately authored S05 check, section selection recovers the correct
圣惠方 source attribution. However the chosen citation stops before that
attribution and contains the preceding 总微论 instead. The baseline correctly
abstains from its truncated context but fails the corpus-level task. Both remain
raw failures. Retrieval coverage alone has not solved claim-to-selected-citation
entailment. Other checks preserve historical speaker distinctions and personal-use
boundaries; some classification citations still omit the continuous speaker-to-list
connection. The raw5/6 scores do not certify every cited sentence.

The six Cycle9 frozen rewrites and prior H05/T01–T12 are unchanged. The six new
checks were separately authored before outputs, frozen after code, and never used
for subsequent code tuning. They use reviewer-selected source records with fixed
initial windows, so they test source-window transfer rather than a fresh
end-to-end embedding retrieval pipeline. Their same-corpus overlap remains.

## Resource use and reproducibility

This cycle completed **79 paid requests**, known-token peak-rate estimate
**CNY0.565424**. Cumulative conservative ledger: **$82.03191625/$200**. All reservations
settled; zero retries, new unknown usage or >20s outputs. No paid work remains active.
The CNY tariff amount is carried numerically as a conservative USD ceiling, not
an exchange-rate conversion or invoice. Only the existing provider/model was used.

Original factorial warm p95 ranges from
4.754s to
6.190s; maximum
6.679s.
Small samples, local routes and reused outputs prevent a general latency-gain claim.
**468 offline tests pass; all8 new tests pass under Python-O using imported unittest
discovery.** Direct test-file execution would omit the two later-defined factor
isolation tests; recorded validation used imported discovery. Frozen input hashes,
exact quote substrings, response hashes, journals and settlements are verified.

Private bundle `protocol-cycle10-20261014/` contains plans, frozen questions,
all jobs/raw outputs, source-masked review inputs, private lineage, protocol replay,
impact scan, ledger, scripts, verification and report. It depends on the existing
local corpus and earlier runtime bundles; it is not a portable public benchmark.
No credentials, new packages, upstream code, pushes, uploads or deployments were
introduced. The original corpus and existing default implementations are unchanged.

## Research connection and stopping point

The existing [dated literature matrix](research-cycle3.md) and
[Cycle9 source attribution analysis](source-grounded-cycle9.md) remain applicable:
exact evidence spans and bounded coverage are independent engineering informed
conceptually by S2G-RAG/CompSelect, while evaluator reliability and validity motivate
separate source review. No new paper implementation or novelty claim is added.
This cycle uses only the previously credited ancient-text transcription amendment;
the new title alias comes from existing local metadata, not an external codebase.

The useful result is a bounded protocol fix plus a cleaner negative ablation.
Further prompt or section-heuristic tuning on these now-exposed examples would
not resolve evaluation validity. A subsequent development cycle should use a new
adjudicated source set and test claim-to-selected-span entailment, section intent
and long-section coverage before another freeze. No further paid optimization is
justified by this small selected set alone, and no production promotion is made.
