"""Cross-process regression for floating-point term accumulation and selection."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from newdomain.evidence_pool import weighted_overlap

WORKER = r'''
import json
from newdomain.keyword_hypotheses import KeywordSearch
from newdomain.keyword_control import select
from newdomain.keyword_selection import select as alternative
out={}
for corpus, topic in [('guangming','科技材料补贴'),('niuhuang','本草文献作者')]:
    # Identical term sets in different orders must tie exactly. Long sources
    # also exercise earliest-window selection and all keyword selectors.
    records={'base':'原始保留材料','last':'无关资料'}
    for i in range(35):
        words=topic if i%2 else topic[::-1]
        records['r%02d'%i]=words+'\n'+('其他文字'*240)+topic*4+('其他文字'*240)+topic*4
    records['a']='共同标题\n'+topic*300
    records['z']=records['a']
    search=KeywordSearch(records,lambda s:list(s))
    baseline={'base':records['base'],'last':records['last']}
    out[corpus]={'pool':search.pool.build(topic,{},20),'tie':KeywordSearch({'a':records['a'],'z':records['z']},lambda s:list(s)).pool.build(topic,{},2),'original':select(search,topic,[],baseline,2),'expanded':search.select(topic,[topic[::-1]],baseline,2)}
    for mode in ['equal_rrf','token_coverage']:
        out[corpus][mode]=alternative(search,topic,[topic[::-1]],baseline,2,mode,lambda s:list(s))
print(json.dumps(out,ensure_ascii=False,sort_keys=True))
'''

class RetrievalDeterminismTests(unittest.TestCase):
    def test_precise_sum_preserves_real_difference(self):
        weights={'a':1e16,'b':1.0,'c':1.0}
        self.assertEqual(weighted_overlap(weights, {'a','b','c'}),1e16+2)
        self.assertGreater(weighted_overlap(weights, {'a','b','c'}),weighted_overlap(weights, {'a'}))
    def test_both_corpora_across_hash_seeds(self):
        outputs=[]
        for seed in [0,1,2,7,14,19]:
            outputs.append(subprocess.check_output([sys.executable,'-c',WORKER],cwd=Path(__file__).resolve().parents[1],env={**os.environ,'PYTHONHASHSEED':str(seed)},text=True))
        self.assertEqual(len(set(outputs)),1)
        result=json.loads(outputs[0])
        for data in result.values():
            ids=data['tie'][1]['body_top20']
            self.assertLess(ids.index('a'),ids.index('z'))
            self.assertEqual(data['original'][0]['base'],'原始保留材料')
