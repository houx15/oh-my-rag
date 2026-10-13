# Continuing optimization evidence log

Goal and stopping rules: [OPTIMIZATION_GOAL.md](../OPTIMIZATION_GOAL.md).
C1 is still default; no deployment or publication retry is authorized here.
Private results are retained outside this repository; code and tests remain here.

| Experiment | Hypothesis / split | Evidence | Decision |
|---|---|---|---|
| C2P historical | More context/longer answers; exposed 60 | Both-judge adequacy 36/60 vs C1 44/60, p95 2.041 vs 1.931 s | Negative; do not use as fresh test |
| C3B-v1 | Exact clause handles without packing | 46/60 exposed prompts exceed fixed request cap | Reject mechanically |
| C3B-v2 | Packed complete clauses; frozen fresh 40 | 40/40 vs 40/40, p95 +6.6%; source audit reveals missed conditions | No promotion; ceiling not plateau |
| R1 source review | Fresh-context model sees only question/source on nine exposed cases | Finds scope concerns, but copies a schema placeholder into several obligation fields | Not usable as automatic gold; preserve raw output |
| R1 blinded answer review | 41 anonymous original/control answers | Misses explicit condition reversal and several omissions; false alarm on a complete control | Reject as promotion judge |
| R2 atomic review | Per-obligation status plus exact answer span | First unseen controls: 7/8 errors, 0/12 false alarms; missed date inside compound criterion | Failed gate; those controls are now development data |
| R3 separate predicates | Same reviewer, independently checked source predicates | New frozen controls: 8/8 errors, 0/16 false alarms, 24/24 schema-valid | Limited diagnostic gate passed; not general validity |
| C4Q proposed ablation | Targeted material-scope self-check; same C1 retrieval/schema/caps | Prepared offline on exposed development cases | Await calibrated review gate |
| C4N proposed ablation | Two adjacent pages replace low-ranked chunks; same top-8 cap | Prepared offline; no oracle source IDs | Await calibrated review gate |

Local review flags now cover narrow negated-obligation and refusal-followed-by-
positive-payment-assertion patterns. They remain review hints, not general
semantic correctness or automatic answer repairs. Constructed negatives and
legitimate uncertainty statements are tested separately.

R2 has a preregistered 20-control unseen diagnostic gate: identify all eight
explicit constructed errors, at most one false alarm among twelve complete or
paraphrased controls, and all outputs must satisfy the schema/quote contract.
Those controls are assistant-authored/source-checked, not human gold. Passing
supports further diagnostic work, not general judge validity. Failed controls
become development data; never silently retest them as unseen.

Paid work uses the existing canonical ledgers, original cumulative $100 ceiling
and nested allocation, with durable dispatch journals and no retries. The
remaining authorization deadline and budget are operational boundaries, not
scientific stopping criteria. No practical plateau has been established.

Development generation completed 27/27 structurally valid outputs. Review then
exposed a false missing-condition judgment, incomplete evidence supplied to the
reviewer, and retyped-quote errors. The repaired source view includes all actually
retrieved passages; answer sentence IDs replace free-form copied quotes. Remaining
review disagreements and schema violations are unresolved evaluation outcomes,
not automatic candidate losses. A protocol disclaimer is not an unsupported
business fact. Candidate selection requires source adjudication, not raw counts.

A 16-question scenario holdout in four development-disjoint source families was
frozen before answers, with separate inference questions and source obligations.
The corpus and related topics were previously exposed; lexical overlap audit is
not a semantic independence guarantee. C1/C4Q/C4N are unchanged for this comparison.
Arm-masked assistant review packets preserve a private mapping; this masking is
not equivalent to a fully independent human reviewer. No plateau claimed.

## Completed continuation: 2026-10-13

The proposed C4Q/C4N experiments above are now completed. On the frozen 16-case
scenario set, raw pointer-review adequacy was C1 13/16, C4Q 14/16, C4N 14/16.
These are **diagnostic model judgments**, not defensible gold accuracy: source
review found an ambiguous question, unsupported payment substitution, and judge
false positives on exact protocol disclaimers. No default promotion follows.
Provider transport p95 was 2145/2103/2033 ms respectively; generation cost was
$0.0184434/$0.0190338/$0.0184197. These timings exclude retrieval.

An approved stronger-model ablation used identical C1 messages on those 16 cases.
It produced 12/16 schema-valid answers, p95 2973 ms, generation cost $0.07892412.
All four invalid outputs omitted the evidence key on an exact fixed protocol
sentence. A local, narrowly scoped normalizer repairs that contract discrepancy
in replay (16/16), without changing business facts, citations, or provider usage.
This adaptive replay is not a fresh model-quality gain. A report-only pricing fix
replaced an erroneous flash tariff with the manifest's actual requested-model
tariff; the original incorrect report is preserved privately.

A question-only missing-record guard was frozen before 20 new focused questions.
It routed 10/12 explicitly unavailable-record questions and 0/8 answerable policy
controls. Reusing unchanged baseline fallbacks yielded 20/20 valid hybrid outputs
versus baseline 19/20; the avoided failure was structural, not a demonstrated
factual hallucination. Two paraphrases fell through correctly. It matched none
of 330 exposed regression questions. Avoided calls are a counterfactual projection,
not measured new provider responses or a broad semantic quality improvement.

C8U explicitly distinguishes unknown premises from false premises. On an initial
12-case set and a separate 12-case confirmation, arm-masked assistant source review
found one clear C1 error corrected by C8U in each set. This is only two discordant
pairs (exploratory exact two-sided sign-test p=0.5); it does not establish broad
superiority. References in the initial set also had policy-scope and unrequested-
computation ambiguity. Confirmation raw judge totals were C1 12/12 versus C8U
10/12, while the judge missed C1's premise error and incorrectly flagged two C8U
protocol sentences. Confirmation generation cost was $0.0142605/$0.0151281;
p95 was 1978/2112 ms. C8U remains experimental.

`newdomain.guardrails` exposes opt-in record routing and exact protocol normalization.
Local responses identify their deterministic origin and contain no fabricated model
usage. The existing C1 entry point remains unchanged. The uncertainty prompt and
all source-review tooling remain experiment scripts, not production deployment.

This continuation dispatched 456 provider jobs, including unsuccessful evaluator
calibration attempts, costing $1.24491114 at pinned conservative tariffs. Cumulative
spend is $29.94520233 of $100. Output usage matches the canonical ledger delta;
all dispatch journals reconcile, zero reservations remain open, and all eleven
historical ledger hashes match. No provider retry was used.

**No practical plateau is established.** Several inexpensive changes lack reliable
broad gains; narrow contract fixes are reproducible, and premise reasoning remains
promising. Next priorities are policy/version applicability resolution, a separate
calibrated evaluation family, and a larger preregistered premise test with paired
source-family uncertainty. Training or a new provider is not implicitly approved.
Human review would improve validity but is not a prerequisite for continued
independent work. An authorization deadline or publication block is not a plateau.

## Broader uncertainty replication and next hypothesis

The unchanged C8U prompt was replicated on 32 new Chinese questions across eight
policy document families, with eight each for unknown premises, known-satisfied
conditions, known-unsatisfied conditions, and numerical/comparison cases. These
families differ from the earlier C8U sets, but the corpus and some families were
used in other research. Exact question nonoverlap is not semantic independence.
Questions, sources, inference requests, criteria and review rubric were frozen
before inspecting answers; both arms used identical retrieved evidence.

All 64 outputs were valid. Conservative arm-masked assistant source review found
30/32 adequate for both C1 and C8U: one C8U win and one loss, with a shared failure
on a question explicitly restricted to two eligibility conditions. C1 changed a
comparison role and got its numerical difference wrong. C8U added a false claim
that an explicitly annual contract amount lacked a stated period. Five borderline
wording/applicability concerns were retained separately, not silently promoted to
hard errors. No hard unsupported-assertion or qualifier-omission error was found
under this limited review; this is not proof those rates are zero.

The paired adequacy difference is 0 percentage points. A descriptive bootstrap
resampling eight source families (20,000 draws, seed 20261013) spans -9.375 to
+9.375 percentage points. This small clustered sample cannot establish equivalence
or a plateau. Generation cost was C1 $0.0377331 versus C8U $0.0400575 (+6.2%);
transport p95 was 1946 versus 2025 ms (+4.0%). C1 remains unchanged.

A separate same-provider fresh-context review received anonymous paired answers
and five explicit error axes. All 32 reviews satisfied the schema. It detected
the role/comparison error but accepted the shared requested-scope failure. It
noticed the annual-period contradiction in notes yet did not flag the premise
axis. Exact protocol sentences were no longer flagged as unsupported facts.
This improves one known evaluator defect but does not validate the reviewer as
a promotion judge. Raw model and assistant judgments remain separate.

This replication used 96 calls, costing $0.32477976 including reviews. Cumulative
charge is $30.26998209, with zero open reservations and all historical ledger
hashes unchanged. Every run reconciles against its journal and canonical ledger.

**Next: C9S requested-scope preservation.** The isolated prompt instructs the
model to retain explicit question facts, answer the requested subset of conditions
before discussing overall eligibility, and preserve compared roles and periods.
It changes neither retrieval nor C1 defaults. The implementation and four tests
are in `scripts/optimization_scope.py` and `tests/test_scope_preparation.py`.
Twenty-four new scenarios on different pages within the eight exposed families
are frozen privately: eight local-condition questions, eight known numerical/
comparison/scope questions, and eight unknown controls. All 48 paired requests
pass offline privacy and request-budget screening. No answers have been generated;
this is not an evaluated improvement.

The development authorization expired at 2026-10-13 16:40:02 UTC and the final
window at 16:48:51 UTC. The replication generation and reviews completed inside
the final window; no paid calls were started afterward. The next experiment is
blocked on renewing the existing authorization through its normal controls while
preserving the cumulative ledger. Deadlines were not reset or bypassed. Offline
preparation is complete; no practical plateau is claimed. No Git push or direct
parent-thread message was attempted in this continuation.

Local validation: 284 tests passed in normal Python and again under `python -O`;
`git diff --check` passed. The added preparation tests verify baseline preservation,
unchanged evidence/user messages, request-size enforcement and rejection of a
non-C1 starting arm. Review tests reject duplicate answers, omitted obligations
and string values masquerading as boolean error flags.

## Administrative deadline clarification and C9S discovery

The earlier stopping note overstated the provenance of the 24-hour deadline.
Inspection established a local manifest duration plus ledger-creation timestamp,
not an expired provider credential/tool permission or a verified user-selected
24-hour restriction. Under the sustained optimization request, an audited bounded
batch now supplements that guardrail. Original deadlines, manifests, reservations
and charges were not reset. See [bounded-batch mechanics](bounded-batches.md).

C9S discovery completed all 72 calls within one recorded batch, costing
$0.23371596. Cumulative spend at closure was $30.50369805, zero open reservations.
All 48 answers were structurally valid. Masked assistant source review found
C1 20/24 versus C9S 23/24: three corrected requested-scope false refusals, no
clear new error, and one shared remaining refusal. Exact paired sign-test p=0.25;
three discordant examples do not establish general superiority. The descriptive
eight-family bootstrap interval is +4.17 to +25 percentage points and should not
be mistaken for reliable small-sample coverage or traffic-weighted performance.

Generation cost was $0.0272025/$0.0283689 (+4.3%); transport p95 was
2122/1943 ms (-8.4%) for C1/C9S. Eight unknown controls and eight numerical/scope
controls showed no clear new failure. Actual-amount wording in two hypothetical
calculation answers remains a separate borderline concern. Human gold and source
transcription validation are still unavailable; C1 is unchanged.

The completed batch was closed by an appended audit event. The unchanged C9S
prompt now has a separately frozen 24-question confirmation in eight families
disjoint from its discovery set, balanced across local-condition, numeric/
comparison and unknown-control questions. Those families were exposed in earlier
other experiments, so this is not a new-corpus claim. The new batch records the
same 72-call, one-hour, $4 charged-plus-reserved constraints and cumulative cap.

C9S confirmation generation completed 48/48 valid answers. Preliminary masked
assistant source review is C1 22/23 versus C9S 23/23: one corrected refusal that
ignored certifications explicitly supplied by the question. A financial boundary
case was excluded because a definition elsewhere in the source contradicts the
frozen reference's strict-threshold assumption. Original references are preserved;
post-generation errata are diagnostic, not silently relabeled fresh gold.

Confirmation generation cost was $0.0281250/$0.0293382; transport p95 was
2016/1825 ms. Costs, validity and latency include all 24 answers per arm, even
though quality excludes the ambiguous case. Across discovery plus confirmation,
there are four assistant-adjudicated wins and zero losses in 47 eligible pairs
(exploratory exact sign-test p=0.125). This remains targeted, small-sample evidence;
C1 is unchanged and no plateau is claimed.

The 24 confirmation reviews remain pending. Their first preflight exceeded the
unchanged 30 KB request limit because quote copies duplicated retained source
text. A tested lossless compaction preserved all sources and citation IDs, and
all revised requests passed screening before any review dispatch. Subsequently,
automatic approval review rejected a live command whose budget-root date was
mistyped. Per the explicit instruction to stop on an actual approval rejection,
no live retry was attempted. The corrected canonical root is verified and its
no-network dry run passes. This is a real tool-review stop, distinct from the
administrative runner deadline. The active batch still has 24 calls available,
zero reservations open, and its original one-hour deadline unchanged.

Cumulative spending is $30.56116125, including $0.0574632 for confirmation
production of answers and no confirmation-review charge. The next scientific
hypothesis is document-wide threshold/exception definitions: distinguish missing
nonadjacent evidence from interpretation errors before changing retrieval. The
newly exposed ambiguous case must not be reused as an unseen test.


### C9S confirmation review closure

After coordination explicitly authorized one corrected canonical-path retry,
tool review accepted the command. All 24 paired reviews completed; all 72 calls
reconcile to $0.20743104, cumulative $30.71112909, with zero open reservations
and all eleven historical ledger hashes unchanged. The batch is closed through
an appended audit event. The earlier pending/denied note is a preserved checkpoint,
not the current status.

Full-set structural validity remains 24/24 for each arm. Conservative assistant
quality remains 22/23 versus 23/23, with one ambiguous reference per arm excluded.
Raw paired model review instead reports 24/24 versus 23/24: it accepts C1 on the
ambiguous boundary case after seeing the logged definition erratum, but misses
C1's contradiction of certifications explicitly supplied in a different question.
This disagreement prevents treating model-review counts as gold or claiming a
confirmed general improvement. The ambiguous case is not silently relabeled.
All 24 answers per arm remain in cost and timing denominators. The generation
and transport figures above stand; reviews cost an additional $0.14996784.
C1 remains unchanged. The nonadjacent-definition retrieval hypothesis remains
untested, and these targeted results do not establish a practical plateau.


### C10D: nonadjacent definitions, completed development test

An opt-in deterministic selector adds at most one exact definition chunk from
the top-ranked document within the unchanged eight-chunk context. Multiple
candidate definition pages/sentences cause abstention from enrichment; no
cross-document definition lookup, per-case IDs or answer labels are used.
C1 defaults remain unchanged. The project code was written independently.

Twenty-four questions were frozen before generation in four previously exposed
source families: eight boundary, eight matched near-boundary and eight unknown/
nonnumeric controls. Corpus/topics are not unseen and labels are assistant
source-reviewed, not human gold. Complete reference-chunk coverage rose from
1/24 to 19/24; 19 insertions had zero wrong-reference-document joins and zero
listed reference-chunk displacements. Source bundles include definitions that
some controls do not strictly need, so this is not a necessary-evidence recall
estimate. Compiled multi-policy documents with conflicting definitions are
skipped. Synthetic tests also cover wrong-document rejection and local exception
retention; these checks cannot certify the initial retrieval anchor's identity.

Masked assistant adjudication: C1 17/24, C10D 19/24, two wins and zero losses
(exact paired sign-test p=0.5). Boundary adequacy is 3/8 versus 5/8; matched
controls 6/8 each; unknown/nonnumeric controls 8/8 each under conservative
interpretation, with three borderline wording concerns each recorded separately.
All 48 answers are valid. Four-family descriptive bootstrap: 0 to +16.67 pp;
this is weak targeted development evidence, not broad promotion evidence.

Raw paired model review reports 17/24 versus 21/24. It misses both arms' incorrect
100-boundary answer and a candidate answer whose opening denial contradicts its
later correct rule. It also penalizes a terse unknown refusal that the conservative
assistant review treated as a borderline explanation issue. Original judgments
are retained separately; no majority vote converts them into gold.

Generation cost: $0.0255951/$0.0251286; transport p95: 1969/1872 ms for C1/C10D.
Mean local retrieval including selection: 2.505/2.506 ms; selector build 5.44 ms.
These small-sample timings are not production end-to-end p95. All 72 calls cost
$0.20449182, cumulative $30.91562091; zero open reservations, no retries, eleven
prior ledger hashes verified. The batch is closed. Relevant normal and optimized
Python regressions passed 109 tests.

Failure localization: three numeric interpretation errors persist even with
the definition present, including answers that quote the right rule and then
contradict it. Two unanswered questions miss the local procedural page even
though it ranks first in BM25: fusion/document-diversity pushes it out of the
final context. Next isolate protection of the strongest lexical hit from logical
consistency prompting. No plateau or default promotion is claimed.


### C11B: protect a same-document strongest lexical hit

C11B independently preserves the BM25 rank-one chunk when it is absent from C1's
final context and belongs to the same document as C1's first result. It replaces
only the eighth chunk, without definition enrichment or prompt changes. An
unrestricted exposed-data probe found a cross-document hit; the implemented
same-document guard rejects that join. This does not certify role identity within
a document. Normal and optimized regressions passed 113 tests.

Frozen development: 24 new questions in four known families, balanced target,
matched-role/limit, and unknown/actual-record controls. Eleven insertions produce
no wrong-reference-document join or listed reference-chunk loss; full reference
bundle coverage rises 3/24 to 6/24 (some bundles contain contextual pages not
strictly needed). Masked assistant adequacy rises 17/24 to 21/24, four wins and
zero losses; paired sign-test p=0.125, four-family descriptive bootstrap 0 to
+37.5 pp. Raw paired model review agrees on these adequate-count totals.
All 48 answers valid. Generation costs $0.0252858/$0.0259047; transport p95
1800/1928 ms (+7.1%); mean retrieval including selection 2.371/3.480 ms.

A material adverse transition remains: on one pair with identical prompts,
C1 refuses and C11B emits a correct computed number with a wrong policy cap and
subject scope. Both are inadequate, so net-adequacy hides the increased harm.
This is sampling variability rather than an established selector effect, but
must not be discarded. A shared comparison also joins the wrong approval-role
branch. No default promotion. The 72 calls cost $0.20157414, cumulative
$31.11719505, zero open reservations; batch closed.

A separately frozen broader set covers 24 questions in eight families disjoint
from development. After dispatch began but before answer inspection, the audit
found all 24 paired prompts identical: C11B did not activate. This run is therefore
an unchanged-context repeated-C1 stability control, NOT confirmation of retrieval
benefit. Preserve the original preregistration and this deviation. Both arms score
23/24 under masked assistant review, sharing an explicit-negation error. All 48
answers valid. The zero-difference bootstrap is degenerate and establishes no
accuracy equivalence. Transport p95 differs 2303/1995 ms despite identical prompts,
illustrating small-sample/provider variability. Generation cost $0.0280401/
$0.0279477. All 72 calls cost $0.20280612, cumulative $31.32000117; no unresolved
reservations or retries. Prior ledger hashes verified; batch closed.

Future efficacy confirmation must audit intervention activation before dispatch.
No useful benefit can be attributed to an inactive retrieval intervention. Next
isolate predicate interpretation with identical definition-enriched evidence,
keeping lexical preservation out of that comparison. C1 stays default.


### C12P: predicate-consistency prompt — rejected

C12P appends an independently written generic instruction to interpret scoped
operators, explicit negation and unknown premises before writing a consistent
conclusion. It uses exactly the same C10D contexts in all 24 pairs; no lexical
preservation, reference answers or question-specific thresholds enter the prompt.
It is not symbolic execution or a VeNRA reproduction. Explicit baseline/candidate
pins allow only reviewed arm pairs while retaining all previous receipt meanings.
Normal and optimized regressions passed 116 tests.

Twenty-four frozen new questions cover six known families: 12 boundary/negation,
6 matched and 6 unknown controls. Existing failure patterns and corpus are exposed.
Fourteen reference-page bundles are fully present; other bundles may contain
unneeded contextual pages. Four source-answerable queries in each arm remain
unanswered because local evidence is missing.

Masked assistant adequacy: C10D 14/24 versus C12P 15/24, three wins and two losses;
paired sign-test p=1.0, six-family descriptive bootstrap -8.33 to +16.67 pp.
All 48 answers structurally valid. The candidate repairs some explicit-premise
errors but introduces an inclusive-duration mistake and denies a provided
negative premise on other questions. Both arms still contradict themselves or
give a correct institution with an incorrect boundary/branch explanation.
Raw model review scores 18/24 each, missing several such contradictions. Thus
no reliable improvement or promotion is supported.

Generation cost $0.0257718/$0.0270570 (+5.0%); transport p95 1932/1897 ms.
The 72 calls cost $0.20045364, cumulative $31.52045481, zero open reservations,
all prior hashes verified, batch closed. A temporary execution-transport drop
occurred before review dispatch; read-only verification found exactly 48 generation
calls and no review journal/reservation before reconnecting. No provider call
was retried or duplicated.

The broader C11B unchanged-context control's model reviewer scored 24/24 for both,
missing the shared explicit-negation error found by source review. Agreement
continues to be insufficient evidence of validity. The next lexical check will
verify active insertions before dispatch rather than treat an inactive broader
sample as an efficacy replication.


### Active C11B confirmation and final accounting

The completed [outcome record](research-cycle3-outcome.md) reports the final
24-case confirmation: assistant adequacy 19/24 versus 22/24, four wins and one
loss; five active pairs account for all four wins and no losses. A citation-only
sensitivity gives 20/24 versus 22/24. The unchanged-prompt regression and model
review disagreements remain explicit. All 48 outputs are structurally valid.
The 72 calls cost $0.18814926, with generation p95 1820/1877 ms.

Original C1 hashes reproduce on all 60 regression questions. C11B changes 1/60
and 12/330 exposed contexts, with no baseline-cited chunk displaced in the 60.
These are coverage checks, not new answer-quality measurements. Final cumulative
spend is $31.70860407; all seven audited batches are closed, zero reservations
remain, and eleven historical hashes match. The final tracked offline suite
passes 155 tests in normal Python and 155 with -O. C1 remains default.

The outcome record defines a scoped stopping point for the tested cheap prompt/
bounded-context family, its uncertainty, and the next typed-condition hypothesis.
It does not claim a global RAG plateau or treat budget or weak judges as proof
that improvement is impossible.

### C13T: typed scalar source conditions, first development result

Parent requested substantive continuation beyond the narrow prior stopping point.
The independently implemented compiler preserves exact source offsets, normalizes
units with Decimal, interprets document-scoped above/below definitions and local
endpoint exceptions, and distinguishes unresolved entity/time binding from scalar
comparison. It never issues an automatic eligibility decision. A small explicit
measure ontology limits coverage; this is not learned extraction or VeNRA.

On 24 frozen natural-style questions in six exposed families, C10D and C13T share
identical retrieved contexts. All 48 outputs are valid. Arm-masked assistant source
review: 18/24 versus 21/24, three wins and no losses; descriptive family interval
0 to +29.17 percentage points. Exact two-sided paired sign-test p=0.25. Gains
concern role consistency and explicit premises, not demonstrated arithmetic
execution. Guidance accompanying the table is a confound to isolate next.
Shared errors remain: ignored local question scope, a strict numerical boundary,
and wrong approval-role reasoning despite a correct final yes/no.

Generation cost $0.0274212/$0.0389184 (+41.9%); transport p95 2022/2043 ms (+1.1%).
All 72 generation/review calls cost $0.22046280, cumulative $31.92906687. Batch
closed; no open reservations, retries or historical hash changes. No promotion.
Questions are newly authored, not naturally collected traffic or human gold.
See private `typed-conditions-20261013` for frozen artifacts and adjudications.

Full acceptance coverage is restored: [test-count reconciliation](test-coverage-reconciliation.md)
explains 301 + 15 = 316, and why the previous 155 tracked-only run omitted 161
legacy tests. None were deleted or skipped. Fourteen new compiler tests bring
full normal and optimized discovery to 330 passing tests each.

The reusable `scripts/optimization_case_report.py` produces private four-column
HTML, Markdown and per-section lossless CSV exports. The checkpoint includes all
156 rows in six declared cohorts, user-provided and curated cases separately;
primary C1 and experimental variants are not pooled. Raw prose, recorded scores,
response IDs, timestamps and exact transport durations are traceable in private
verification receipts. HTML cells and CSV round trips were checked exactly.
