# oh-my-rag

Chinese document-grounded QA research with explicit evidence handles, offline
validation, budgeted provider calls and paired evaluation.

This is an **integration checkpoint**, not a production release or a demonstrated
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
all 60 exposed prompts. Answer-quality/latency gains remain unmeasured.
`newdomain/numeric.py` is independent engineering, not a paper reproduction,
and is not automatically routed into answers. Existing B0/C1/C2 methods retain
their local provenance in module documentation.
