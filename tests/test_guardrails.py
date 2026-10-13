import json
import unittest
from unittest.mock import Mock
from newdomain.guardrails import guarded_call, normalize_protocol_sentences
from newdomain.candidate import validate


class GuardrailTests(unittest.TestCase):
    def test_local_boundary_never_dispatches_or_fakes_usage(self):
        provider=Mock(side_effect=AssertionError('no provider allowed'))
        result=guarded_call('未提供企业名称，请确认它今天到账金额。',provider)
        provider.assert_not_called();self.assertIsNone(result['model_usage']);self.assertEqual(result['cost_usd'],0)
        self.assertTrue(validate(json.dumps(result['answer'],ensure_ascii=False),{})['ok'])

    def test_fallback_preserves_call_and_result(self):
        result=object();provider=Mock(return_value=result);q='普通企业的补贴政策比例是多少？'
        self.assertIs(guarded_call(q,provider),result);provider.assert_called_once_with(q)

    def test_exact_protocol_normalization_unchanged_mechanics(self):
        raw={'content':json.dumps({'sentences':[{'text':'以上为资料记载的转述，不构成投资或医疗建议。'}]},ensure_ascii=False)}
        out,trace=normalize_protocol_sentences(raw)
        self.assertEqual(len(trace),1);self.assertEqual(json.loads(out['content'])['sentences'][0]['evidence'],[])


if __name__=='__main__':unittest.main()
