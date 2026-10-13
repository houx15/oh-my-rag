import json
import unittest
from newdomain import candidate, clauses
from newdomain.numeric import convert, compare
from newdomain.runner import validate_row
from test_newdomain import _resp


class ClauseAblation(unittest.TestCase):
    def test_complete_long_condition_has_exact_contiguous_offsets(self):
        # Deliberately spans C1's 240-character limit; fully invented source.
        text = "对符合要求的申请单位，" + "申请材料须完整，" * 30 + "补贴最高为50%，但总额不超过20万元。"
        context = {"synthetic": text}
        old = candidate.passages_for_contexts(context)
        new = clauses.passages_for_contexts(context)
        self.assertGreater(len(old), 1)
        self.assertEqual(len(new), 1)
        self.assertEqual(new["E1S1"]["text"], text)
        self.assertEqual(text[new["E1S1"]["start"]:new["E1S1"]["end"]], text)

    def test_decimal_negation_and_exception_preserved(self):
        text = "标准为1.25万元，但不适用于试点单位。另行审核；不得叠加。"
        spans = clauses.passages_for_contexts({"synthetic": text})
        self.assertEqual("".join(p["text"] for p in spans.values()), text)
        self.assertIn("1.25万元，但不适用", spans["E1S1"]["text"])

    def test_prompt_and_resolution_share_exact_handle_map(self):
        text = "普通单位须提交完整资料，" * 22 + "补贴最高不超过5万元。例外单位适用10%。"
        results = [dict(id="synthetic", text=text, title="合成条款", locator="1")]
        messages = clauses.build_messages("补贴条件是什么？", results)
        self.assertIn("【E1S2】", messages[1]["content"])
        raw = _resp(json.dumps({"sentences": [{"text": "例外单位适用10%。", "evidence": ["E1S2"]}]}))
        canonical, meta = clauses.canonicalize(raw, {"synthetic": text})
        self.assertTrue(meta["ok"])
        self.assertEqual(json.loads(canonical["content"])["sentences"][0]["citations"][0]["quote"], "例外单位适用10%。")
        self.assertTrue(validate_row(dict(arm="C3B", context={"synthetic": text}, raw_response=raw))["ok"])

    def test_baseline_default_hook_is_identical(self):
        results = [dict(id="synthetic", text="条件甲。条件乙。", title="合成", locator="1")]
        self.assertEqual(candidate.build_messages("条件？", results), candidate.build_messages("条件？", results, passage_builder=candidate.passages_for_contexts))


class NumericDerivations(unittest.TestCase):
    def test_scale_and_decimal_are_exact_and_conditional(self):
        out = convert("12.345", "亿元", "万元", provenance="user supplied premise", scope="user_premise")
        self.assertEqual(out["value"], "123450.000")
        self.assertFalse(out["premise_verified"])
        self.assertTrue(out["derived"])
        self.assertNotIn("quote", out)
        self.assertEqual(convert("0", "毫克", "克", provenance="test", scope="document_statement")["value"], "0.000")

    def test_bad_units_values_and_scope_refused(self):
        for value, source, target, scope in [("1,000", "元", "万元", "user_premise"),
            ("NaN", "元", "万元", "user_premise"), ("1", "元", "平方米", "user_premise"),
            ("1", "亩", "平方米", "user_premise"), ("1", "元", "万元", "unknown")]:
            with self.subTest(value=value, source=source, target=target, scope=scope), self.assertRaises(ValueError):
                convert(value, source, target, provenance="synthetic", scope=scope)

    def test_scope_checked_before_comparison(self):
        left = dict(value="1", unit="万元", provenance="synthetic A", scope="document_statement", entity="合成企业", period="2026", measure="申请额")
        right = dict(left, value="10000", unit="元", provenance="synthetic B")
        self.assertEqual(compare(left, right)["relation"], "equal")
        for field in ("entity", "period", "measure", "scope"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                compare(left, dict(right, **{field: "different"}))
