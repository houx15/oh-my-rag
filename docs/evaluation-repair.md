# Offline evaluation repair after the C1/C3B comparison

The original 40-question scores and references remain frozen. A post-hoc,
assistant-reviewed diagnostic now covers nine selected questions, all six
original strata and six source groups. It records 26 answer obligations,
source-page spans, derived premises, and refusal criteria in private artifacts.
Selection is purposive, not random or held out; these are not independent human
annotations, and screened OCR text is not certified original-page evidence.

## Concrete discrepancies and corrected criteria

- Two answers omit a prior-period eligibility scope that the old reference also
  omitted. A stricter scope-preservation axis flags both. The original question
  emphasized rates/caps, so whether the qualifier had to be restated needs
  adjudication; do not retroactively treat an expanded rubric as old human gold.
- One C3B answer omits a completed-project eligibility condition that appears in
  the old reference and citation. C1 retains it; both model passes accepted both.
  Under a no-eligibility-broadening rule, require the condition in the answer or
  establish it explicitly as a question premise. Citation presence alone does
  not repair an overbroad answer.
- Regression judging penalized an appropriate refusal for not supplying
  unavailable facts. Correct criteria accept a justified evidence boundary while
  separately checking for fabricated facts elsewhere in the answer.

The new annotations distinguish requested facts from material scope conditions,
not every neighboring provision. They bind recipient, time period, rate basis,
per-item/annual caps and conjunctions to source spans. Numerical derivations
retain the question premise, formula, units and cap. Missing information is an
explicit reviewed absence premise, not a fabricated source quotation. All
private excerpts and answer-level annotations remain outside Git.

## What the diagnostic can and cannot do

`scripts/research_criteria.py` verifies pinned input hashes and source-span
membership, and checks **answer text only**, excluding reference answers and
citation quotes. It flags three of eighteen inspected original answers for
surface omissions. Nine assistant-written complete examples and twelve targeted
deletion controls behave as designed. This is a mechanics check, not an unseen
accuracy estimate or evidence of a better model judge.

Two constructed semantic errors remain unflagged: negating a condition while
mentioning its words, and appending a fabricated payment after a refusal. They
are retained as explicit blind spots. Surface matches always return
`surface_present_needs_semantic_review`, never entailment or correctness.
Paraphrases, role swaps, negation and contradictions require source-aware review.
No new quality score is computed; no final scores are overwritten.

```sh
python scripts/research_criteria.py --root /private/experiment \
  --annotations /private/experiment/repair-annotations.json \
  --output /private/experiment/repair-diagnostic.json
python -m unittest discover -s tests -p 'test_research_criteria.py'
```

The three synthetic tests verify source-anchor rejection, missing-scope/wrong-cap
flags, and non-acceptance of negation based on lexical presence. There are no API
calls or new dependencies. Frozen generation/candidate code remains unchanged.

## Next feasible experiment

1. Independently review the nine source regions and eighteen answers, blinded to
   arm, including omission/negation/false-refusal controls. Estimate 2–4 human
   hours; no GPU or API cost. Resolve the task-scope ambiguity before a strict
   rubric is frozen. Until a person does this, label annotations as assistant
   source review, not human gold.
2. Separate omission, contradiction, scope broadening and justified refusal.
   Add unseen paraphrase and wrong-recipient/cap controls. A judge must distinguish
   these before it can evaluate another paid optimization.
3. Freeze a new source-family split with natural, less leading questions and
   source obligations before model answers. Isolate condition retention with the
   same retrieval/model/output budget; test missing-page retrieval separately.
   The current forty questions and repair sample are exposed development data.

No further paid optimization is authorized by this diagnostic alone. Current
cumulative spend remains $28.70029119; this repair cost $0 in API usage. C1 stays
default. The publication retry was rejected by automatic approval review; no
alternate publication route was attempted.
