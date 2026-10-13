# Timeout diagnosis and concrete evaluation evidence

## What the timeouts establish

The four approximately61-second failures were `requests.ReadTimeout` exceptions.
The application sets `timeout=(5,60)` for connect/read and a75-second parent
process deadline. All four reported `headers_received=False; events=0`; the
60-second local read-inactivity limit terminated them before the75-second process
limit. No HTTP504/429/5xx or provider error body was received. Calling this a
confirmed provider outage would overstate the evidence.

No explicit environment/system proxy was returned by Python's effective proxy
lookup, including in the network-enabled execution context. This does not rule
out a transparent intermediary or network stall. Provider queueing/prefill is
plausible but unproven; there are no failed-response request IDs or server timings.
Failed prompts were13,830 and14,507 bytes.84 source-stage successes ranged from
7,282 to26,797 bytes; the five successes immediately before the failures took
2.06–3.50 seconds. A deterministic size cutoff is not supported. Time and prompt
size are confounded, so this does not rule out load-dependent size effects.

Across228 journal events from the four phases, maximum simultaneous started
requests was1 and unterminated requests0. The worker closes its HTTP session and
is joined/terminated by the parent. No local concurrency leak was found; other
clients on the provider account cannot be excluded. Increasing the timeout would
hide a poor-latency outcome rather than demonstrate a repair. No timeout,
security/network setting, proxy setting, or credential was changed.

One non-inference connection check succeeded: DNS228ms, TCP283ms, TLS558ms with
default certificate validation. Then exactly **one** ledger-gated115-byte JSON
canary, with **zero retries**, returned the exact requested model and valid JSON
in1.677s (headers1.542s),17 input/6 output tokens. This rules out a persistent total
outage at check time, not the earlier stall or full-size workload unreliability.
No bulk run was resumed solely on this tiny-request result. Next meaningful gate
is a bounded representative-size continuation with checkpoint reuse, not an
unbounded retry loop. The existing client timeout itself is working as configured;
no recoverable timeout/concurrency implementation defect was demonstrated.

## Actual question, answer, source and scorer examples

Score order below: correctness / support / relevance / completeness. These are
original stored model scores; source judgments are assistant review, not human gold.

**False failure — GM015**

Question:「有哪些科技成果与生命类？」

Answer:「资料记载，共收集381项科技成果，其中生命类科技成果166项。
生命类成果包括：科技赋能再生与护理：干细胞冻干粉与私密护理产品的前沿应用（深圳理工大学）；星际冰表面环境模拟装置（深圳先进光源研究院）；科技赋能生命解密与再生：干细胞技术的前沿应用（深圳理工大学）。」

Original score1/1/1/1, fail; citation entailment true. Scorer reason:
「仅列3项且未含参考中噬菌体、脑电给气、甲基化PCR等示例」.
D36 rows197,307,288 classify these actual examples as生命类. The open request does
not require the reference's exact examples. This is reference-example lock-in,
not demonstrated factual failure.

**False pass, with interpretation caveat — GM161**

Question:「请介绍一下光明区有哪？ 拿，拿多少项科技成果？」

Actual first sentence:「光明区相关单位共收集381项科技成果，其中信息类171项、生命类166项、材料类44项。」
The middle sentence lists8 institution counts. Actual last sentence:
「本次资料未包含回答该问题所需的依据。」

Original score2/2/2/2, pass, both Boolean checks true. Scorer reason:
「分类与总数有原文支持，单位明细有可复算统计支持；末句边界声明合理。」
CALC:D36 and D30page1 support381 source-collection records and category counts;
they do not support claiming the entire requested answer lacks evidence after
answering it. The unqualified last sentence has no explicit separate referent.
I retain the assistant whole-answer false-pass label, not a claim that381 is
numerically false and not a mechanical inference from an abstention flag.

The lexical co-occurrence flag was downgraded to a review trigger; the individually
re-read GM161 label was not changed. Counts therefore remain22 supported passes,
1 false pass,13 true failures,6 false failures,6 ambiguous. If a human interprets
the last sentence narrowly as “the exhaustive district-wide total is unknown,”
GM161 should instead be ambiguous:22/0/13/6/7. This sensitivity is explicit. In the
new source-restoration run both arms omit this generic sentence and answer the
core count correctly; those are different saved answers, not a revision of the
old control and not an additional counted repair.

**True pipeline failure — GM048**

Question:「呃，这个氪金。 科技金融大厦一共有多少层呀？」

Answer:「资料未直接写明光明科技金融大厦的总层数，但入驻信息中出现的最高楼层为三十八楼。
资料记载该大厦建筑高度195.3米，是光明区第一高楼。
本次资料未包含回答该问题所需的依据。」

Original score0/0/1/0, fail. Reason:
「未答总层数；引用最高38楼及高度均不支撑层数，且未用42层依据」.
D29page2 visually shows楼层层数−4F–42F; D35page1 states主楼42层. These passages
were missing from retrieved context. Highest occupied floor38 is not the building
floor count. This is a retrieval/evidence-selection failure, not proof the generator
ignored evidence it had. Floor answer should preserve above/below-ground scope.

**True pipeline failure — GM090**

Question:「哪个应用领域的成果最集中？」

Answer:「本次资料未包含回答该问题所需的依据。」

Original score0/0/0/0, fail. Reason:
「未作答，仅称资料不足，但所供参考已给出最集中领域及统计。」
Independent read-only count of D36 sheet1 C2:C382 gives the full-field mode
「科学研究和技术服务业-研究和试验发展-自然科学研究和试验发展」,
108/381≈28.35%. The failure is missing whole-table aggregation/routing. A few
retrieved rows cannot justify that mode; the reference alone is not the evidence.

## Known usage versus conservative accounting

The earlier39.77140635→55.93499825 ledger increase16.16359190 comprises
0.11239190 known-token list-price amount and16.0512 unknown-usage conservative
settlements. It is not a verified invoice increase.

This focused cycle including the one canary has known-token list-price CNY
**0.891382** and conservative unknown-usage budget settlements **12.0384**.
The latter comprises two initial local-DNS failures and four later pre-header
read timeouts; do not treat them as six confirmed billed generations. Across
Bailian work since the39.77140635 checkpoint, known-token CNY is1.0037739 and
unknown-usage conservative settlements28.0896. Numeric CNY list-price amounts
are booked at the same numeric USD amount as a conservative ceiling, not FX.
No actual invoice was accessed.

Current cumulative conservative total: **68.86478025/200 USD**. Zero open
reservations, zero active paid calls. Successful canary increment0.000082; no
new unknown settlement. All prior charges and zero-dispatch allocation history
are retained. No deployment, push or upload.
