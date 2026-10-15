# Complete-answer deadline — October 15, 2026

User requirement: **the complete, validated answer must arrive within 2,000 ms**. This is a per-request cap, not first-token latency or a p95 allowance. Maximize supported, mechanically valid, adequate answers delivered within that cap; count timeouts, incomplete/invalid answers and missing measurements in the scheduled denominator. Keep adequacy, deadline misses, coverage and costs separate to avoid rewarding fast abstention or dropped qualifiers.

## Existing evidence

Offline reanalysis of all204scheduled A1/C1 outputs finds202observed generation timings and **zero complete answers within2seconds** in any arm or corpus. Two interrupted generations have unknown timing and cannot count as success. An interrupted review still has an observed generation. All three arms therefore have0/68deadline-qualified successes under even the historical optimistic timing scope.

| Arm | Observed generations | Median generation | Median preparation | First-token arrivals over2seconds |
|---|---:|---:|---:|---:|
| Baseline |67|3,895ms|17ms|49/67|
| A1 reminder |67|4,159ms|20ms|56/67|
| C1 packing |68|4,143ms|25ms|54/68|

Validation medians are under1ms. Historical component sums exclude queueing, cold initialization and final network delivery, and are not an end-to-end SLA measurement. The0/204result already fails this necessary lower-scope check; raw quality scores remain unchanged. Streaming sooner alone does not satisfy the requirement.

The historical October12C1 final p95of1.931seconds covered a different60-question cohort/configuration; its20regressions had p952.406seconds. A p95below2seconds is not a per-request cap and cannot certify today's route. Do not select a model or pipeline by comparing these unequal cohorts.

## Required execution and evaluation contract

Start one monotonic deadline when the request enters the application, before queueing, retrieval and prompt construction. Generation receives only the remaining budget; validation and delivery must fit before expiry. No late answer can be counted as successful. Abort/cancel late work, record timeout separately, preserve unknown-usage reservations conservatively and reconcile receipts; cancellation is not proof the provider charged nothing. Do not retry within this budget or present an unvalidated partial answer as complete. Timeout notification is a service failure, not an adequate answer. Ordinary client/network delivery cannot be guaranteed by the existing offline harness.

**Current status:** this is the required acceptance contract and an implemented offline scoring gate, not a deployed cancellation mechanism. Existing frozen collection transports retain their historical120/125second collection bounds and20second diagnostic label for reproducibility; they do not meet the new service contract. Do not launch those unchanged runners as a compliant2second experiment. No service endpoint has been deployed or modified.

## Prioritized speed/quality work

1. Measure latency feasibility on already-approved provider/model routes before another retrieval ablation. Current first-token latency consumes the entire budget on most cases. Use the same screened questions, randomized paired order, concurrency and cold/warm reporting; stop routes that cannot deliver complete valid responses by2seconds. Do not assume a differently named model is faster.
2. Reduce generated formatting overhead using existing exact-source handles/local rendering, while preserving necessary conditions, caps, comparisons and citation validation. Prefer concise task-specific answers over a fixed truncation that can cut facts or JSON. Test output length and required-facet retention together. The previous longer-context/answer regression is evidence against indiscriminate expansion, not proof that arbitrary shortening works.
3. Preserve B2's useful dependency swap as an isolated option: one exposed case gained required procedure evidence with859fewer context bytes. It has no measured generation-speed benefit. Add source-reviewed positive dependency cases before broad promotion. Avoid extra online graders, serial expansion calls or repair loops on the response path.
4. Evaluate an exact-query, versioned cache only for eligible repeated requests. Bind corpus version, permissions, model/prompt/validator version and answer validity; invalidate on changes. Report cache hits and cold misses separately. No cache exists from this change, and cached benchmark answers must not masquerade as fresh model performance.

Next live experiment must replace the earlier44-call B2-only proposal with a latency-first design and explicit bounded paid scope. No paid run or budget allocation was initiated. Shared conservative spend remains$121.98103945/$200. Remaining funds are not automatically spent by this offline analysis.

## Reproduction

`scripts/time_cap_report.py --results <saved-results.jsonl> --output <analysis.json>` records the input SHA256, per-corpus/arm scheduled denominators, missing timing, deadline misses, quality-within-deadline and component medians. Five unit tests cover the exact boundary, late answers, invalid/unsupported fast answers, missing measurements/scores and invalid caps. All source artifacts and original experiment outcomes are unchanged. No new external method attribution is needed for this local evaluation metric.
