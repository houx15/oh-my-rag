# Bailian continuation and public-source restoration — 2026-10-13

The user explicitly approved Alibaba Cloud Bailian generation/scoring and later
clarified that all project/corpus content is public. Institution names and the
reviewed platform-total source statement are no longer pending privacy decisions.
API keys and credentials remain secret. No keys were changed, copied to another
computer, printed, or stored in new configuration. Nothing was published.

## Latest status

The remaining337-case continuation did not complete: its first three concurrent
requests timed out, as did a serial follow-up. A separate Qwen3.8 Flash service
canary completed3 cases (2 primary passes), without establishing model superiority.
The source-restoration37-case pilot stopped before its first dispatch because
journal identities disallow the pipe character. It has0 calls and0 added cost.
The current [fairness diagnostic](fairness-diagnostic-20261013.md) takes priority;
there is no active paid run. Unified coverage is328/665 and cumulative conservative
accounting is$55.93499825/$200, with zero open reservations. Earlier account/route
success does not establish reliability for the longer evaluation requests.

## Verified serving route

The existing Token Plan main key authenticates and lists `deepseek-v4.1-flash`,
but its documented interactive-only terms exclude automated evaluation. That
route was not used for inference. The existing pay-as-you-go key also authenticates
and lists the exact requested model. A small public JSON probe returned that same
model with usage metadata. No model equivalence is inferred merely from names:
previous official DeepSeek receipts say `deepseek-flash`; Bailian receipts say
`deepseek-v4.1-flash` and explicitly identify Alibaba Cloud as provider.

Legacy `dashscope.aliyuncs.com` inference yielded three complete cases, then
suffered read timeouts (one at the original read bound, three after increasing
it within the hard deadline). All unknown-usage charges remain conservatively
settled. Switching to the current documented workspace endpoint succeeded on
all five canary calls covering four unfinished cases. The remaining337 cases
then began on that verified route. No endpoint finding is a production SLA.

Official sources:
- [Bailian DeepSeek API](https://help.aliyun.com/zh/model-studio/deepseek-api)
- [DeepSeek V4.1 Flash model/prices](https://help.aliyun.com/zh/model-studio/deepseek-v4-1-flash)
- [Token Plan scope](https://help.aliyun.com/zh/model-studio/token-plan-team-overview)

Provider transition is preserved per generation and review. Three original
DeepSeek generations were reviewed by Bailian; their answers were not regenerated.
Explicit continuations of timed-out Bailian generations count as retries in the
ledger. There are no automatic retry loops. Old successes, failures, scopes,
request hashes and ledgers remain immutable except audited admission retirement.

The USD ledger uses deliberately conservative ceilings of$2/$8 per million
input/output tokens, numerically above the published Beijing peak CNY2/CNY8
rates. These are budget ceilings, not converted invoice amounts. Report estimated
CNY and conservative USD separately; do not claim the ceilings were billed or
credit back previous unknown-usage settlements without invoice evidence.

## Source-only preprocessing version

`newdomain/institution_fields.py` restores missing institution fields only from
source column F, with workbook hash, sheet, cell, exact value and before/after
record hashes. Original files and previous results are not edited.131 missing
fields across two institutional strings are restored; the catalogue remains381
rows and now has zero missing institution fields. Contact columns G/H are not
extracted into the derivative corpus. The scoped screen admits verified full
institution strings while retaining contact/credential checks and the old name
screen elsewhere; it does not disable all screening.

One missing line from source D30 page1 is restored in its original location.
Local visual inspection confirms that “over a thousand listed achievements”
refers to the platform, whereas381 is a collected subset from10 institutions.
The title's0711 marker is retained but no year or precise effective date is
invented. “Currently” means the source's own time; it is not a verified live total.

The derivative corpus has132 changed units out of1125, with no other metadata or
text changes. Rebuilding the same C1 retrieval/routing changes context for71/330
original Guangming questions. A paired37-question experiment is prepared: all17
count-trigger cases plus20 hash-selected controls,148 planned generation/review
calls. It changes source preprocessing only; algorithm changes remain separate.
All original question text and the scoring rubric remain fixed. These exposed
questions are not a fresh natural holdout, and source diagnostics are not human
gold. No new answer-quality improvement is claimed before the paired run.

Private plans, source provenance and original failed calls are under the task's
`bailian-*` and `public-source-restoration-20261013` artifact directories. Source
values, credentials and private result artifacts are not added to this repository.
