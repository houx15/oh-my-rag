import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from optimization_contract import normalize_protocol_sentences


class ContractTests(unittest.TestCase):
    def test_only_exact_boundary_can_omit_evidence(self):
        original={'content':json.dumps({'sentences':[{'text':'本次资料未包含回答该问题所需的依据。'}]},ensure_ascii=False),'usage':{'input_tokens':10,'output_tokens':5}}
        out,trace=normalize_protocol_sentences(original)
        self.assertEqual(json.loads(out['content'])['sentences'][0]['evidence'],[])
        self.assertEqual(out['usage'],original['usage']);self.assertNotIn('evidence',json.loads(original['content'])['sentences'][0]);self.assertEqual(len(trace),1)

    def test_fabrication_appended_to_boundary_is_not_normalized(self):
        r={'content':json.dumps({'sentences':[{'text':'本次资料未包含回答该问题所需的依据。但已到账123万元。'}]},ensure_ascii=False)}
        self.assertEqual(normalize_protocol_sentences(r),(r,[]))

    def test_fact_and_unknown_fields_not_repaired(self):
        for s in [{'text':'收益是123万元。'},{'text':'本次资料未包含回答该问题所需的依据。','extra':True}]:
            r={'content':json.dumps({'sentences':[s]},ensure_ascii=False)};self.assertEqual(normalize_protocol_sentences(r),(r,[]))

    def test_duplicate_json_keys_not_silently_overwritten(self):
        r={'content':'{"sentences":[],"sentences":[]}'};self.assertEqual(normalize_protocol_sentences(r),(r,[]))


if __name__=='__main__':unittest.main()
