# Coherent candidate and source-gap review, 2026-10-13

The current private four-column report covers all645 eligible unique original
questions using one explicit, opt-in routing rule. It replays existing results
whose questions and selected contexts match the rule; it does not choose the
highest-scoring saved answer per question. This is exposed-development evidence,
not a fresh end-to-end run, an untouched holdout or a deployed default.

| Corpus / origin | Candidate pass | Eligible questions | Configuration |
|---|---:|---:|---|
| 光明 original live |65|113|C1; source-derived statistics on count-trigger questions|
| 光明 supplied simulation |158|217|Same rule|
| 牛黄 original live |108|205|Focused answers and strict typed-v2 boundaries|
| 牛黄 supplied evaluation |47|110|Same rule|

All 光明:223/330, with three mechanically invalid outputs retained. All 牛黄:
155/315, with ten invalid outputs retained. The report has no missing primary
scores in this selected configuration, but107 光明 and160 牛黄 failures remain.
The narrow counting change applies to17 questions and previously improved9→14,
with five gains and no losses. The other313 光明 results stay unchanged. All315
牛黄 questions use the same focused/typed configuration, including its regressions.

`newdomain/coherent_candidate.py` takes corpus, original question, source context
and source aggregates; it has no case-ID, score, reference or saved-answer input.
The measured counting route permits exactly one catalogue and retains seven
ordinary source records. Unsupported multi-catalogue scope fails closed rather
than silently expanding the measured policy. Caller-side domain generation and
validation remain unchanged. This is an opt-in integration helper, not production
activation. `scripts/optimization_coherent_report.py` verifies source custody and
renders the same four columns in HTML and CSV.

## Additional experiment: negative result retained

`newdomain/book_evidence.py` matches titles explicitly quoted in《…》and ranks
within-book topic overlap. It never treats a longer title sharing a prefix as
the same book. Across all315 original 牛黄 questions it changed19 contexts;
all19 were freshly generated and reviewed with the same prompt and fixed rubric.
Passes stayed9/19: one gain (NH-LIVE-13), one loss (NH-SKILL-098), one invalid
output. No net improvement; the selector is not part of the coherent candidate.
The full context-selection audit preserves296 unchanged contexts. The38 calls
cost$0.03760590. This is a negative development ablation, not a new-method claim.

## Exactly what source information is missing

The earlier131 missing organization values are two institutional strings affecting
109 and22 catalogue rows. Raw values exist; global known-contact substring
replacement followed by whole-line filtering removes the corresponding lines.
They remain excluded from model inputs. A field-specific institution allowlist
or explicit scoped restoration authorization is needed before changing that.
Personal/project-contact columns G/H must remain excluded; no blanket privacy
bypass is proposed.

The same mechanism also drops a platform-total clause from raw D30, page1, line5.
A local text check finds the clause there, but no matching statement in screened
sources. This supports the reference's claim provenance for GM-045/GM-174;
it does not establish a current real-time total, remove the ambiguous entity in
GM-174, or authorize restoring the source line. The raw line is withheld from
benchmark providers. A narrow non-contact clause extraction needs scoped review
and authorization, retaining its document date and scope. No missing fields have
been restored in this continuation.

Other inputs remain genuinely missing: prior dialogue for NH:N263 (“他是不是道士啊？”),
verified speech wording for NH:R065 (“小儿液体”), and authoritative modern sources
for regulatory/clinical questions. Existing historical or promotional excerpts
must not be promoted into modern medical evidence. The institutional19-row count
for GM-077 is already in screened evidence; its remaining error concerns uncertain
entity interpretation, not those131 withheld fields.

Nine source-diagnostic annotations record these distinctions and a resolved
control. They are assistant diagnostics, not human adjudication or replacement
scores. The preselected40-live-case formal source audit is still incomplete.
All eligible originals have been exposed; a new natural batch and independent
source review are needed to claim generalization. User input/authorization is
summarized in the private `continuation-cycle3-20261013/decision-brief.md`.

## Report verification and accounting

The single current audience report remains at the existing private
`flash41-full-rerun-20261013/presentation/report.html` location. The previous
baseline report is preserved in a versioned sibling archive. HTML has exactly
four columns and645 full-case rows plus16 illustrative duplicates. The645 record
questions, selected contexts, saved answers, scores and timing sources are
checked; CSV cells round-trip to the same data. Example selection uses a fixed
hash order rather than outcomes. Independent judgments of earlier configurations
are not presented as judgments of changed answers.

Timing is explicitly separated: original313 光明 records retain original
retrieval-through-answer timing; the17 count records and315 牛黄 records have
saved generation-stage timing. There is no mixed-scope overall p95 or claimed
cross-corpus speed ranking. Twenty historical contract regressions are in the
appendix and were not rerun as part of this composite. Complete offline acceptance
passes392 tests in normal and optimized Python modes. Browser visual inspection
was blocked because the browser policy disallows local file URLs; no workaround
was attempted. Structural/content QA passed; visual QA is not claimed.

Cumulative API spend: **$37.01651325/$200 total**, including all carried prior
ledgers. Zero open reservations, zero retries, and all38 new responses report
`deepseek-flash`. Parent recorded Astra medium selection for the working task;
tools do not expose runtime model/effort, so it cannot be independently confirmed.
No uploads, GitHub push, deployment or production-default change. Local artifacts
remain private. Existing README paper acknowledgments are unchanged because no
additional upstream method or code was adopted in this continuation.
