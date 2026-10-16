# v0.1.0 — Gold100 R10 research checkpoint

This release selects `experiments.gold100.r09.Index`, `messages`, and `validate`,
with `experiments.gold100.confirmation.measure` for fresh end-to-end timing.
R10 was confirmation of unchanged R09, not a new algorithm. The algorithm files
are unchanged from campaign closure `e40e9c8115d2f8896eadd44327dffd78dd961183`.
Historical C1/default adapters elsewhere in this repository are not the release
entry point. This is an integration library with an offline CLI, not a hosted service.

## Measured state

R10: 80/100 semantic passes, 100/100 mechanical validity, measured mean
6219.807 ms and p95 8508.669 ms. Baseline: 54/100 semantic, 75/100 mechanical,
mean 5.261 seconds. The joint quality/latency target was **not met**.
R09's 83/100 and 5680.119 ms used an estimated uncached latency; that is not
the R10 measurement. These are exposed development-set assistant reviews,
not independent generalization or expert validation. See the
[full campaign record](gold100-optimization-results.md).

## Install and run without credentials

Use Python 3.9–3.12, normal interpreter mode (do not use `python -O`: frozen
validators contain assertions). From a fresh checkout:

```sh
git clone --branch v0.1.0 git@github.com:houx15/oh-my-rag.git
cd oh-my-rag
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-gold100.txt
.venv/bin/python -m unittest discover -s tests -p 'test_gold100_*.py'
.venv/bin/python -m experiments.gold100.quickstart --demo
```

The demo exercises retrieval, prompt construction, exact citation resolution and
validation using synthetic vectors and a canned response. It makes no API calls
and is not a quality benchmark. Existing repository read access is required.

## Use your authorized corpus

Supply UTF-8 JSON files outside Git (for example under ignored `runs/local/`):

- `records.json`: object mapping stable source record IDs to exact source text.
  Preserve the original corpus partition, record order/IDs, catalog fields and
  text when reproducing the campaign. IDs `D01:1:01` denote document/page/part;
  arbitrary IDs work but do not enable the document/page section logic.
- `vectors.json`: object mapping SHA-256 of each exact baseline chunk's UTF-8
  text to its 1024-dimensional embedding. Enumerate chunks with
  `experiments.gold100.baseline.Index(records).chunks` and hash with
  `experiments.gold100.r05.text_key(chunk['text'])`. Chunk size is 500 characters,
  overlap 80; embed unchanged text, not record IDs or reference answers.
- `query-vector.json`: a fresh 1024-number embedding of the question, using the
  same embedding model/route as the source vectors. Do not use synthetic demo
  vectors for real retrieval.

```sh
.venv/bin/python -m experiments.gold100.quickstart \
  --records runs/local/records.json --vectors runs/local/vectors.json \
  --query-vector runs/local/query-vector.json --question '你的问题' \
  > runs/local/request.json
```

Send the `messages` field through your authorized generation adapter. Save its
response as `{"content":"<model output JSON array as a string>",
"stream_done":true,"finish_reason":"stop"}` only when the stream actually
completed with that finish reason. Rerun the same command with
`--response runs/local/response.json` to resolve citations and validate; invalid
responses exit with status 1. Display `validation.parsed` only when `valid` is
true. Mechanical validity does not establish semantic support.

For application integration:

```python
from experiments.gold100.r09 import Index
from experiments.gold100.confirmation import measure

index = Index(records, source_vectors)  # warm initialization outside timing
result = measure(question, index, embed, generate, record_request)
# embed(question) -> fresh vector; generate(messages) -> response envelope above
# record_request(chunks, messages) persists the actual request locally
if not result['validation']['valid']:
    raise ValueError(result['validation']['errors'])
answer = result['validation']['parsed']
```

The callbacks are supplied by the integrating application. Existing budget-gated
transports require a new authorized manifest, ledger and privacy configuration;
historical campaign allocations are closed and must not be reused. Do not bypass
those gates. The offline CLI does not dispatch, retry, or create paid experiments.

## Frozen provider configuration and external prerequisites

Generation: Alibaba Cloud Bailian workspace route
`https://<YOUR_WORKSPACE_ID>.cn-beijing.maas.aliyuncs.com/compatible-mode/v1/chat/completions`,
model `deepseek-v4.1-flash`, temperature 0.2, thinking disabled, max output 800,
streaming with usage, no retries. See `newdomain/bailian_bounded_transport.py`
for the original request contract. Credentials are colleague-owned placeholders:
`DASHSCOPE_SEARCH_API_KEY=<YOUR_KEY>` and `BAILIAN_WORKSPACE_ID=<YOUR_WORKSPACE_ID>`.
Embedding: `https://api.zyai.online/v1/embeddings`, `text-embedding-v3`, dimensions
1024, float encoding, `ZYAI_API_KEY=<YOUR_KEY>`. See
`experiments/gold100/embedding_transport.py`. Never commit credentials or log
authorization headers. Provider access/availability is an external prerequisite.

Exact benchmark reproduction additionally requires the privately held screened
corpus, 3279 source vectors, frozen corpus routing, 100 questions/rubric and
campaign runner/ledger artifacts. These are intentionally not uploaded with this
tag; obtain authorized copies from the repository owner. New data or model routes
are a new configuration and do not inherit R10's scores. The frozen system prompt
contains date 2026-10-15; changing it also changes the configuration. No live
provider or paid benchmark run is performed as part of packaging this release.
