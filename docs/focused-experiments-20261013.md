# Focused experiments: sources, calibration and response delivery

Status: stopped at a provider-response blocker, not a quality plateau. No paid
work remains active. Local artifacts are under
`focused-cycle5-20261013/` in the October12 task workspace; `report.html` and
`report.md` contain the detailed readout, paired answers and source annotations.
The old complete report's answer tables and scores remain unchanged.

## Results

|Experiment|Evidence|Decision|
|---|---|---|
|Calibration|12 fixed-answer controls ×2 rubrics; both agree with assistant source labels9/12|Reject clarified rubric. GM161 is now disputed; excluding that control gives9/11 for both rubrics. Original scores and historical9/12 labels remain saved.|
|Source restoration|48/74 outputs;16/37 complete pairs; raw passes11/16→13/16;2 gains,0 losses among completed pairs|GM142/GM174 source review supports distinguishing platform over1000 from381 collected rows. Partial development evidence only.|
|Scoped aggregation|Frozen24 generation jobs; first request and retry time out;0 outputs|No answer-quality claim. Offline source mode108/381, subtraction166−44=122, conditional entity count19 verified.|
|Bounded recovery v1|Offline selection picked neighboring-property transport evidence|Rejected before paid testing.|
|Bounded recovery v2|645-question routing regression changes11 selections; bounded/idempotent;24 frozen generation jobs unrun|No quality promotion; keep opt-in.|

Six of the16 complete source pairs are byte-identical cached controls. Ten pairs
have changed prompts. GM161 has a correct core count in both new arms; its richer
institution list is not counted as another repaired failure. Sixteen single-arm
outputs are retained but excluded from paired outcomes. Changed source inputs
restore131 institution fields and one platform-count paragraph under the user's
explicit public-source authority. Source hashes and operands remain local.

New synthetic questions are frozen development probes written after diagnosis,
not an independent human holdout. Reviews are assistant source judgments with
visible arms. Raw model grades remain supplemental and all original scores survive.
No broader accuracy or significance claim is justified by these selected samples.

## Latency and failure evidence

Completed non-reused source generations: original21 calls p50/p95
11.415/17.493 seconds; restored21 calls4.218/16.709 seconds. These are not the
same complete-pair subset and endpoint delay is variable: no speedup conclusion.
Four later requests (two initial requests and their one retry each) had no
headers/events and timed out after approximately61 seconds. Successful response
latencies do not absorb or hide those failures.108 successful calls returned the
exact `deepseek-v4.1-flash` model. Median time before headers was90.6% of completed
response duration; client timing cannot identify network versus upstream causes.

Warm CPU-only p95 over100 repetitions is about0.003ms for a precomputed aggregate
operation and1.08ms for Guangming facet selection. These exclude loading,
index/aggregate construction, full retrieval and inference. No training GPU or
extra model calls are required by these opt-in methods.

## Cost reconciliation

The earlier39.77140635→55.93499825 increase was16.16359190:16.0512 came from8
unknown-usage conservative settlements, and0.11239190 from known successful
usage. It was not a verified16-dollar invoice increase.

|New phase|Successful usage-based amount|Unknown-usage conservative amount|Ledger increment|
|---|---:|---:|---:|
|Initial sandbox DNS failures|0|4.012800|4.012800|
|Calibration with network access|0.203456|0|0.203456|
|Partial source comparison|0.687844|4.012800|4.700644|
|Aggregation transport stop|0|4.012800|4.012800|

Cumulative conservative accounting: **68.86469825 /200 USD**, zero open
reservations. Successful usage is verified from returned token counts; Bailian
CNY list-price amounts are conservatively booked at the same numeric USD amount,
not converted. Unknown usage uses the full2.0064 request bound. No actual invoice
was inspected, and historical unknown charges were not silently refunded.
`final-accounting.json` checks every successor's carried prior amount exactly.

## Implementation, provenance and next gate

- `newdomain/bailian_observed_transport.py`: versioned60-second read/total and
  75-second hard process deadlines; response-header and stream-event evidence.
  Old frozen adapters remain intact. The private frozen runner owns the one-retry
  limit, two-failure circuit, DNS/journal preflight, and hash-checked checkpoints.
- `newdomain/scoped_aggregation.py`: typed source-row mode/subtraction and
  conditional entity counts; operands/provenance and source scope are explicit.
- `newdomain/facet_recovery.py`: rejected offline prototype retained as evidence.
- `newdomain/facet_recovery_v2.py`: title/section/entity scope, one addition within
  existing8/4 context counts, exact book title, no reference-answer input.

The calibration protocol is conceptually informed by IRT-Judge and Reliability
without Validity. Bounded evidence experiments are informed by S2G-RAG and
CompSelect. See [verified dates, repository/license checks and method matrix](research-cycle3.md)
and README acknowledgments. No upstream code, prompts, weights or datasets were
copied; no unrecognized package was installed. No novelty or paper reproduction claim.

430 tests pass in both Python modes. The local standard HTML renderer passed
artifact validation and structural verification; headless browser was unavailable,
so source-dialog interactions and viewport screenshots were not verified.

Before more paid work, verify service recovery within a bounded allocation, carry
forward the final ledger, and preserve message/model/response hashes plus successful
journal records when reusing checkpoints. Old retired allocations must not be rerun.
Complete remaining source pairs, aggregation and facet answers before any default
promotion. This is a service blocker; budget remains and quality has not plateaued.
No deployment, push or artifact upload occurred.
