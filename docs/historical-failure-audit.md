# Historical original-question failure audit — 2026-10-14

Read-only assistant audit of all318 retained original-question records:113 Guangming and205
Niuhuang. All question/answer records read; disputed cases received deeper source
inspection. Not uniform human word-by-word source adjudication, not current accuracy.
64 sensitive live questions were excluded upstream; Niuhuang’s315 presentation
records came from331 screened rows with16 duplicate aliases.

The frozen historical presentation records snapshot has SHA256
`9cc2d3a76944f02264379bc2cbb95b966df65ac514848e5f8a0c05ab03f8fd36`.
It contains645 unique output records; original318 combine96gm-c1,
17gm-c1-catalogue-counts and205nh-focused-typed-v2. They use a historical direct
DeepSeek route and are not the current Bailian Cycle12 baseline. The full saved
review is local at `keyword-cycle12-20261014/historical-audit-thread.md` beneath
`/Users/monkey/Documents/Codex/2026-10-12/task/`.

| Primary mutually exclusive classification | Guangming | Niuhuang |
|---|---:|---:|
| No material defect found |56|58|
| Scorer/reference overconstraint |8|15|
| Unresolved |27|58|
| Adequate source unavailable |1|25|
| UI request |2|12|
| Final-context evidence missing |7|14|
| Retrieved evidence unused |4|6|
| Source preprocessing loss |3|0|
| Aggregation |1|0|
| ASR/entity interpretation |1|0|
| Condition/scope omission |1|0|
| Explicit task misunderstood |1|3|
| Citation attribution/support gap |0|8|
| Protocol failure |1|6|
| Total |113|205|

Located defects total56 (19GM/37NH), including21retrieval,10use,8citation,
7protocol and10other. The114 no-material-defect findings are not gold-certified
correct answers.85 unresolved must not be silently counted correct. The23
scorer/reference errors do not yield a corrected accuracy estimate.

Examples: GM048 omitted D29:2:01 floor range -4F–42F (later targeted repair exists);
GM090 requires full catalogue108/381 aggregation; GM124 already retrieved
D36:330 safety-interlock facts but ignored them; GM142 confused platform超千项
with collected381 after source processing loss (restored in later versions).
N417 lacked historical valuation in final context; N265 already had valuation
but did not use it, with current-price ambiguity. N350 needed contrasting凉
source; N257 misunderstood an English translation task. R012/R098 had relevant
source text but insufficient selected citation support.

The audit identifies8 citation gaps despite exact quotation provenance. A separately
reported1206-quotation tally has not been reverified against a reproducible
quotation-check artifact here and is not treated as a verified denominator.
Exact matching does not establish claim entailment. Ten historical raw-judge false
passes: GM006,GM142; NHN350,R013,R050,R012,R098,R035,R038,R015.
Seven historical mechanical failures: GM148; NHR006,R019,R034,R090,N322,R118.
Cycle10's replay repairs are a different version/sample; do not claim all7 fixed.
Historical N390 citation findings likewise must not be transferred across versions.

The five high-level research categories, current examples and experiment chronology
are maintained in the [canonical technical report](technical-report.md). Original
raw scores and historical reports remain unchanged; audit judgments are additional
assistant evidence, not replacement labels or a human-gold benchmark.
