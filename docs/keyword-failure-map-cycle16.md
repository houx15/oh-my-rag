# Why eight Qwen-arm cases failed in the completed Cycle16 comparison

This explains the source-reviewed12/20 result for Cycle16's Qwen arm, not active Cycle18 outcomes. Lexical also scored12/20 but has a different failure set. Rawjudge Qwen was9/20, a different metric. Source-conditional adequacy is not factual completion.

| Case | Question topic | Concrete failure and stage |
|---|---|---|
| NH:N001 | 牛磺毒性、能否久服 | Generation silently replaces牛磺with牛黄; entity interpretation unresolved despite supported historical toxicity facts. |
| GM:GM-119 | 这项技术的应用领域 | Missing conversation antecedent; generator picks a cell technology. Real source relevance cannot prove the user's referent. |
| GM:GM-125 | 光明区发展、切换讲解 | Some relevant content, then500万/100万 subsidy claims omit high-level-talent-team and approved-review requirements. Evidence-use scope failure; not scored as a fictitious page switch. |
| GM:GM-128 | 国产中心介绍 | Names possible candidates without clear clarification or available positioning/functions; partial evidence used, task still incomplete. |
| GM:GM-064 | 光明区科研成果 | Returned text/evidence root instead of declared sentences/citations schema. Supported raw carbon-rating text is not valid delivery; available flexible computing omitted. |
| NH:R034 | 李时珍如何评价牛黄 | Unmarked牛病 conclusion attributed to李时珍; speaker binding unsupported despite other correctly cited content. |
| NH:R021 | 除邪含义 | Locates除邪逐鬼 and source attribution, but repeats it without meaning or explicit explanation-gap boundary. Partial location is not a completed explanation. |
| NH:R065 | 治小儿液体的方子 | Mixed clarification and no-evidence response fails protocol. Ambiguous symptom is unresolved; no authority to equate液体with夜啼. |

Previously missed evidence:

- N417: original lexical MD-011-0004 rank10 already had book-level valuation; Qwen additionally found explicit弘景曰 inMD-038-0008 at ranks17/19. Both dropped in Cycle16. All3Cycle17facet arms recover valuation content; dictionary retains conflicting absence framing, Qwen's short quote omits speaker/transmission chain. N417 was counted useful in Cycle16 because safe selected-source abstention was permitted; it was not factually resolved then.
- GM064: Qwen finds D30:1 inventory candidate at ranks2/3 but drops it in Cycle16. Cycle17 selects and uses it for optional10-institute/381-item overview. Control already has technical-achievement facts, so this is not a newly answered question or wholly new technical result. Protocol/policy-scope failures differ across fresh outputs.
- GM068: flexible-computing D36:241 original position5 is lost during Qwen selection. Cycle17 restores it and Qwen preserves the equal-workload40%+ condition; lexical/dictionary add the numeric claim but omit that condition. Binary pass rate hides both coverage loss and incomplete conditions.
- GM128: candidate国转中心 positioning exists but the naming ambiguity and final answer's omissions remain; selected evidence is not a correct identity decision.
- R065/GM001: night-crying/test-strip vocabulary hypotheses remain ambiguous or incomplete. Neither a guessed speech correction nor a candidate hit establishes the intended entity or a resolved answer.

Source: keyword-marginal-cycle16-20261014/source-reviewed-results.json and keyword-facet-cycle17-20261014/paired-source-review.json. All primary scores preserved; no retrospective rescoring or new paid inference used for this explanation.
