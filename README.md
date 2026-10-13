# oh-my-rag

Chinese document-grounded QA research with explicit evidence handles, offline
validation, budgeted provider calls and paired evaluation.

This is a **research checkpoint**, not a production release or a demonstrated
research improvement. C1 remains the reference candidate. On the historical
60-question comparison, both-judge adequacy was **44/60 for C1 versus 36/60 for
C2P**, with p95 latency **1.931 versus 2.041 seconds**. The judges and OCR-derived
references are not human gold. Longer passages and answers regressed in that
trial; those questions are now exposed diagnostics.

## Run locally

Use Python 3.9 or later on macOS/Linux. The existing environment uses
`numpy==2.0.2`, `jieba==0.42.1` and `requests==2.32.5`; no new dependencies were
installed for this checkpoint. Live TLS/provider compatibility must be checked
in the intended environment before spending.

```sh
python -m newdomain.runner help
python -m unittest discover -s tests -p 'test_newdomain*.py'
python -m unittest discover -s tests -p 'test_research_methods.py'
```

The published synthetic tests require no private corpus or network. Other legacy
local suites can depend on private fixtures and are not a portable benchmark.
See [runner documentation](newdomain/README.md) and the
[research plan](docs/research-cycle3.md).

## Data and recovery

Private corpora, questions, ledgers and results are excluded from publication.
New-domain paths are explicit and external to the repository. Existing private
legacy files remain local. Code and reusable tests belong in this repository.

Paid entrypoints default to dry-run. Explicit `--live --profile` requires a
verified private authorization profile and existing canonical ledgers. Generation
and judging hold a run lock and journal dispatch before calling the provider.
`--resume` reuses only completed, hash-pinned results with unchanged inputs and
implementation. In-flight, failed, corrupt or unbound results require manual
investigation. Old unjournaled outputs are report-only. Final runs also require
`--freeze`. No automatic retry, deployment or artifact upload is provided.

## Research acknowledgments

The proposed experiments and evaluation protocol are informed by
[S2G-RAG (ACL 2026)](https://aclanthology.org/2026.acl-long.1185/),
[CompSelect / Less is More (WWW 2026)](https://arxiv.org/abs/2502.11811),
[IRT-Judge](https://arxiv.org/abs/2602.00521), and
[Reliability without Validity](https://arxiv.org/abs/2606.19544).
These are **research references, not implemented model reproductions**. No
upstream code, prompts, weights or datasets from those projects are included.
The research plan records dates, repository checks and license limitations.
The opt-in `newdomain/clauses.py` C3B variant independently adapts exact
sentence-pointer representation and compact clause grouping, conceptually
informed by S2G-RAG and CompSelect. It reuses C1's inference contract and is not
either paper's trained system. Offline ablations rejected an initial variant
that exceeded the request limit on 46/60 prompts; complete-clause packing fits
all 60 exposed prompts. The completed fresh comparison found no measured
quality gain and higher p95 latency; C1 remains the default.
`newdomain/numeric.py` is independent engineering, not a paper reproduction,
and is not automatically routed into answers. Existing B0/C1/C2 methods retain
their local provenance in module documentation.

## Completed frozen comparison — 2026-10-13

| Evidence | C1 | C3B packed clauses |
|---|---:|---:|
| Fresh Chinese final: both-rubric adequacy | 40/40 | 40/40 |
| Fresh final: p50 / p95 seconds | 1.522 / 1.685 | 1.545 / 1.796 |
| Fresh final: generation + judging USD | 0.319464 | 0.316990 |
| Exposed 20-case regression: both-rubric adequacy | 18/20 | 19/20 |
| Preselected 9-case repeat: p95 seconds | 1.714 | 1.821 |

**Retain C1.** C3B produced no measured fresh quality gain and had 6.6% higher
p95 latency. The regression difference is one case, with rubric disagreement;
it is not reliable evidence of improvement. All 154 generation outputs were
valid; 358 total generation/judge calls completed without retries or unresolved
jobs. New accounted spend was **$1.00760184**, cumulative **$28.70029119 / $100**,
with zero open reservations and exact response-to-ledger reconciliation.
These are conservative pinned-tariff charges, not a provider invoice.

Questions were frozen before answers; inference files excluded reference
answers. The final is assistant-authored on a previously exposed corpus, with
explicit source/facet prompts, only one numeric case, and weak coverage of
cross-page retrieval. Both judge passes use the same model with different
rubrics. A source spot-check found a C3B qualifier omission and a shared omission
also absent from the reference, despite agreement. The ceiling score and its
degenerate bootstrap interval are **not human gold or an equivalence proof**.

See the [research results and limitations](docs/research-cycle3.md) and
[integration acceptance evidence](docs/integration-acceptance.md). Private
Chinese QA, source-audit notes, frozen files and ledgers remain local. No deployment.

The [offline evaluation repair](docs/evaluation-repair.md) records source-bound
obligations, three observed omission flags, and explicit semantic blind spots.
It preserves frozen scores and requires source-aware adjudication before further
paid optimization; assistant source review is not independent human gold.

The continuing objective and plateau rules are in
[OPTIMIZATION_GOAL.md](OPTIMIZATION_GOAL.md); the
[optimization log](docs/optimization-log.md) tracks new work beyond this completed
comparison. Publication is blocked, but safe local research continues.
