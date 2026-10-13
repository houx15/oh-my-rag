# Case-report and request-allocation provenance checkpoint

The main private report now presents **光明 C1 and 牛黄 K**, the best broader
validated configurations available for their respective corpora. There is no
established single cross-corpus winner. C15T remains experimental, and C1 remains
default. Other variants are reference material only. This is an interim checkpoint,
not final current-version cross-corpus validation.

## Actual supplied questions and missing coverage

The original question CSV contains 181 real-user-labeled and 239 simulated rows.
Screening retained 113 and 217 respectively. The original report's 10 user cases
match original CSV question text exactly. The revised reference appendix adds all
26 earlier evaluated C1 user cases (11 development, 15 earlier final), also exact
matches. It lists the remaining 77 screened user questions with **MISSING** answer,
score and timing; 68 privacy-excluded user rows remain excluded. Dataset labels
are provenance, not independent proof of the original speaker.

K's frozen dependency hash matches the actual `20261008/1-牛黄知识内容/chunks.jsonl`.
Its final 120 questions are all explicitly synthetic; none equals a question in
`eval/gold.jsonl`, derived from the supplied workbook (283 live, 112 evaluation).
K's synthetic result is not evidence of real-user performance. The original
workbook was not reparsed in this continuation; the extraction script, derived
rows, freeze and corpus hashes provide the audited linkage. An offline inventory
identifies 35 live and 38 evaluation questions with document-oriented, apparently
non-personal wording; this is only heuristic screening, not an approved/frozen
provider payload or a representative benchmark.

The main report contains 180 observed answers: 光明 C1's 10 supplied user questions
and 50 supplied curated questions, then 牛黄 K's 120 synthetic questions. Reference
material contains 326 observed answers and 77 explicit missing-output rows.
Every table has exactly Question / Our answer / Score / Response time. HTML and
CSV cells were verified equal. Prior 300-row and expanded 403-row artifacts are
preserved. No new answers, scores or timings were generated to repair reporting.

The ten unfinished C15T repeated paired model reviews TR-015–TR-024 are marked
MISSING alongside the completed assistant scores for both arms (20 annotations,
10 missing review jobs). They are never counted as completed or scored zero.

## Score and timing comparability

光明 keeps its original primary model scores; the main comparison was C1 44/60
accepted by both judges versus C2P 36/60. Primary C1 alone scored 48/60. 牛黄 K
keeps both reviewers separately: primary 118/120, independent 116/120, both 115/120.
All failures and disagreements remain visible. Four 0–2 semantic axes plus
entailment/completeness and the frozen mechanical checks determine adequacy.
References/OCR are not human gold; different acceptance rules are not calibrated
cross-corpus metrics. No averaging or pooling is performed.

光明 timing is parent-observed provider-transport `full_ms`, excluding retrieval.
牛黄 timing is top-level worker `full_ms`, including live query embedding, retrieval,
generation/local routing, construction and validation. It excludes initial corpus
setup, external queueing and judging. K's warm-index and mixed provider-cache
conditions are disclosed. These time columns cannot be ranked across corpora.
光明 answer prose comes from raw model sentences; K uses its saved delivered final
sentences after deterministic source-span construction, not intermediate handles.

## Where the call allowance comes from

The immutable local manifest sets `request_cap=1800`; `SpendLedger.reserve`
enforces it in repository code. This was not an external provider or tool-permission
rejection. The manifest note explicitly names the user-authorized cumulative $100
cap but does not identify who selected 1,800. The accessible parent-history tool
returned no turns; local artifact/session searches did not recover the original
selection command or a user instruction for this exact number. **Its administrative
versus user-selected provenance remains unresolved.** Absence of a receipt is not
permission to relabel a constraint as administrative.

The nested $12 limit has clearer provenance: `newdomain.experiment.freeze()` writes
that constant to `budget-freeze.json`. Its baseline is $27.69268935 cumulative,
including $17.06934615 from 11 historical ledgers plus $10.62334320 in current
ledgers. It is a runner suballocation inside the unchanged user $100 ceiling;
this continuation does not raise it.

Current canonical final ledger: 1,800 settled calls, $5.19508608. Current dev:
752 settled calls, $10.25406612. Historical total: $17.06934615. Cumulative:
**$32.51849835**, global remainder $67.48150165, nested remainder $7.17419100.
All 11 historical hashes match; all 11 renewal batches are closed; zero open
reservations. No paid call, canonical modification, manifest edit or counter reset
occurred during this provenance/report repair.

## Prepared extension and remaining work

The earlier task's smallest remaining scope is **190 calls**: 10 paired reviews,
then 120 generations and 60 reviews for the original 60-question 光明 comparison.
Four bounded batches would have 10 / 72 / 72 / 36 calls, taking final-stage requests
from 1,800 to 1,990 without resetting them. A review temporarily reserves roughly
$2.77 and a generation $0.63; serial settlement and all global/stage/nested caps
remain mandatory. Four $4 batch ceilings are not a $16 spending grant. Actual
settled costs are expected to be much smaller, but cannot be guaranteed in advance.

`newdomain.request_allocation` prepares and appends hash-chained **proposal-only**
records. It validates canonical snapshots, closed batches, cumulative and nested
caps, and fixed call accounting. It cannot change live ledgers/manifests, authorize
dispatch or write a canonical JSON ledger. Nine synthetic tests cover immutable
inputs, minimal scope, chain/duplicate/tamper handling, non-dispatching status,
wrong targets, changed caps and unresolved state. Live activation is deliberately
not integrated while the original request allowance's authority remains unknown.
A recorded authority determination is needed from the original allocating context:
if administrative, the existing user optimization scope permits a reviewed bounded
append-only extension; if user-selected, explicit authorization to raise that exact
ceiling is needed. No new tool permission is implicated by this code-level gate.

The new two-corpus request expands beyond the 190-call proposal. Comparable tests
must first freeze corpus-specific baseline adapters, any candidate differences,
source-grounded criteria, privacy-screened supplied-user and curated strata, and a
shared end-to-end timing boundary. For a 60-question 牛黄 paired test using current
live query embedding per arm, up to 120 embeddings + 120 generations + 60 reviews
would add 300 calls (fewer generations only when the frozen local route applies).
Thus an upper planning bound is **490 additional calls / final total 2,290**, not
an already granted allowance. Existing provider/model rates and source scope must
be rechecked; no historical K120 rerun or candidate upgrade is silently counted as
fresh validation. Prepared inventory is not a frozen test; human/source adjudication
and runtime compatibility remain outstanding.

Full acceptance after this change: **350 tests pass normally and under `python -O`,
zero skips** (337 earlier + 4 new reporting tests + 9 proposal tests). No push,
deployment, upload, new provider or external implementation was used.
