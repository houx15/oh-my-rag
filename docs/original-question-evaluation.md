# Original-question evaluation and conversational failure modes

The current rerun prioritizes original supplied questions verbatim. It does not
turn short spoken turns into polished standalone exam questions, infer missing
conversation, or treat the old synthetic benchmark as measured user coverage.
Results and accounting are appended only after the frozen run completes.

## Source audit

The supplied 牛黄 workbook contains 283 live utterances and 112 evaluation rows.
Its existing labels mark 204 live answers as poor and 46 evaluation answers as
correct; these describe the supplied older system outputs, not the current
pipeline, and are not verified human gold. Earlier local prototype files matched
29 distinct question strings corresponding to 33 workbook rows (30 live and
three evaluation rows). That does not establish current-system coverage.

The new scope retains 331 eligible source rows after 64 conservative privacy
exclusions, then merges 16 exact duplicates into 315 distinct questions: 205
live and 110 evaluation questions. Original row aliases remain in the private
provenance: 14 repeated live rows and two evaluation rows identical to live
questions share the corresponding saved outcome; no eligible source row is lost. The 120 polished synthetic cases are historical reference only.
Dates, environment and device fields exist, but explicit conversation IDs and
preceding dialogue do not. No context was fabricated.

On the eligible, pre-existing development portion, 23/145 live utterances have
at most eight characters; overlapping simple lexical flags identify 46 with
demonstratives/elliptical expressions, 52 with spoken particles and 11 with
repeated substrings. These are heuristic transcript features, not verified ASR
errors or population frequencies. Existing development/test labels are retained;
this source-exposed rerun is not an untouched generalization benchmark.

## Academic interpretation and next bounded tests

| Observed/evidenced issue | Research problem | Testable next change | Resource and validity boundary |
|---|---|---|---|
| Short referential questions without preceding dialogue | Clarification-need prediction and conversational grounding | Keep the raw turn; ask one specific source-grounded clarification when the referent is missing | First test prompt-only versus existing route; no invented dialogue; report unnecessary clarification separately |
| Imperatives such as opening a book become unrelated historical summaries | Intent recognition across action and information requests | Explicitly distinguish document QA from a UI action and state capability limits | CPU-only intent labels may help, but heuristics require held-out natural-turn tests |
| Irrelevant evidence plus broad “not documented” refusal | Evidence sufficiency versus retrieval failure | Separate missing referent, missing corpus evidence and missing retrieved evidence | Preserve retrieval trace; do not reward unsupported global absence claims |
| Curated results look strong while original-question coverage is absent | Dataset representativeness and construct validity | Original-live results first; curated results in a separate stratum | No pooled headline that disguises origin or privacy exclusions |
| Both corpora mutate one tokenizer singleton | Reproducibility and software interference | Isolate tokenizer state; compare frozen prompt hashes before provider dispatch | All 330 光明 hashes verified unchanged after isolation; no accuracy-gain claim |

A relevant in-window paper is **RAC: Retrieval-Augmented Clarification for
Faithful Conversational Search**, first submitted **2026-01-16**. The author
version identifies ECIR 2026 (March 29–April 2) as the definitive venue;
independent publisher publication metadata was not verified here.
[Original paper](https://arxiv.org/abs/2601.11722),
[method and implementation details](https://arxiv.org/html/2601.11722v1).
It grounds clarification generation in retrieved passages and trains with SFT
and preference optimization. Crucially, it assumes queries require clarification;
it does not solve our decision of *whether* to ask. Its LLaMA-3.1-8B experiments
use A100 80GB GPUs, so full training reproduction is outside this Mac-only run.

The [paper-linked repository](https://github.com/RayaneA7/RAC-Retrieval-augmented-clarifcation)
was inspected at `c4cb121e136a8cf62f71a218648d8fbdad599123`. GitHub's license
endpoint returned 404; no root license was visible. Its README excludes augmented
Qulac/ClariQ data because of ClueWeb licensing. No code was installed, copied or
executed, and no trained RAC component is claimed as implemented. This is a
prospective research reference, not an implementation acknowledgment.

The source-backed clarification hypothesis is established engineering applied to
these transcripts, not a novelty claim. Before future tuning, reserve coarse
source blocks (date/device/environment) as imperfect session proxies, or obtain
real session IDs. Design any spoken synthetic variants from development patterns
only, label them synthetic, and measure raw originals separately. Do not train or
select a candidate using the freshly scored test portion.

## Completed generation and primary review — 2026-10-13

| Question origin | Distinct questions | Strict Flash passes | Rate | Completed-request P95 |
|---|---:|---:|---:|---:|
| 光明 original live | 113 | 60 | 53.1% | 2.379 s |
| 光明 supplied simulation | 217 | 158 | 72.8% | Reported in private full records |
| 牛黄 original live | 205 | 55 | 26.8% | 3.024 s |
| 牛黄 supplied evaluation | 110 | 35 | 31.8% | Reported in private full records |

All 665 primary review requests finished: 330 光明, 315 牛黄 and 20 separate
regressions. One 牛黄 review returned malformed JSON and remains unscored in the
denominator; one 牛黄 generation suffered a stream disconnection and remains a
failure. No provider request was retried. The separate regression set scored
19/20. Overall primary results are 218/330 光明 and 90/315 牛黄. These are strict
model judgments, not accuracy against human gold.

Generation was already requested through `deepseek-flash`. The new role change
uses the same API ID for all current primary judge/review requests; official
October 13 metadata/pricing identified that alias as DeepSeek-V4.1-Flash. API
aliases do not prove the exact historical backend version. This run changes
coverage and review rubric as well as reviewer role, so it is not a controlled
Pro-versus-Flash model ablation. No generation candidate was tuned on these
results. The old 115/120 synthetic result cannot be directly compared as a
regression or improvement on this different population.

Of 665 outcomes, 168 光明 generations were reused only when question, prompt
hash, context and settings matched exactly; all primary scores are new. The
other 497 are new outcomes. Mechanical validity was 327/330 光明, 296/315 牛黄,
and 20/20 regressions. Latency runs from retrieval through answer processing,
excludes scoring and queue wait, includes instrumentation, and preserves the
original timing for reused answers. Transport failures are counted in quality
coverage but excluded from completed-request latency quantiles. These local
concurrency-three timings are not a production-load guarantee.

## Execution and accounting evidence

The explicitly renewed scope carries all 13 historical ledger files and the
prior cumulative $32.51849835 into a successor allocation under the same $100
ceiling. Both old admissions are retired; no old counters, reservations or
fingerprints were reset. The new core run used 1,472 requests: 492 generation,
315 query embeddings and 665 reviews. Five 牛黄 local routes made no generation
API call. New accounted cost is **$1.89523590**, cumulative **$34.41373425**,
remaining **$65.58626575**. One unknown-usage stream failure was charged at the
full conservative reservation. All reservations are settled, with zero retries
and zero overage. These are ledger charges under pinned tariffs, not invoices.

The frozen-prompt guard also caught cross-corpus tokenizer interference before
the affected request reached the provider. Loading 牛黄 domain terms altered
shared jieba state and changed eight 光明 prompts. A fresh independent stock
`jieba.Tokenizer` restored all 330 frozen prompt hashes. The old pre-network
failed journal entry remains intact; its first actual dispatch uses a distinct
incident-linked entry. Campaign runner versions and incident receipts are kept
for reproducibility. This fix restores the intended behavior and is not claimed
as an accuracy improvement.

Offline acceptance: **356 tests pass normally and under `python -O`**, without
skips. An initial restricted test invocation failed to create existing cache
fixtures; the authorized runs passed. Production defaults remain unchanged.

## Completed independent check

Eighty case IDs were selected before generation/scoring: 20 original-live and
10 other supplied questions per corpus, plus all 20 regressions. A fresh
GLM-5.3 coding-plan reviewer received only screened questions, answers and source
excerpts, with tools denied and primary scores/model identities withheld.

| Stratum | N | Flash passes | GLM passes | Both pass | Same verdict |
|---|---:|---:|---:|---:|---:|
| 光明 sampled questions | 30 | 18 | 20 | 16 | 24 |
| 牛黄 sampled questions | 30 | 6 | 12 | 4 | 20 |
| Fixed-context/unsupported regressions | 20 | 19 | 17 | 17 | 18 |

All 80 have valid independent judgments; 18 verdicts disagree. Neither judge is
human gold. The source excerpts, unvalidated references, rubric and mechanical
gate are shared, so different providers do not remove correlated errors. The
20 existing regressions use the C1 contract over fixed policy/historical contexts
or unsupported requests; they are not an exhaustive production 牛黄 safety suite.

Eight initial attachment-based sessions returned only the first case of each
pack. Those eight valid partial judgments were retained; only the remaining 72
unscored cases were delivered as 36 inline two-case sessions. There was no
outcome-based reselection and no repeated generation or primary review. All 44
coding-plan session receipts report $0, not independently verified invoices;
internal CLI HTTP retry behavior was not independently observed. Core ledger
request/retry counts above refer to the metered DeepSeek/embedding transports.

A source spot-check found a concrete primary-judge rationale error: it treated
absence from the reference-source subset as a citation defect even though the
cited record was present in the answer evidence. The answer independently failed
user intent. Original scores remain unchanged; this is an assistant diagnostic,
not substitute human adjudication.

The private final presentation leads with original-live performance and contains
exactly 光明 / 牛黄 sections, four columns, illustrative successes/failures and
expandable full coverage. All 645 corpus cases are included; 20 regressions and
technical provenance remain in the separate developer appendix. No publication,
corpus upload, deployment, candidate promotion or GitHub push occurred.
