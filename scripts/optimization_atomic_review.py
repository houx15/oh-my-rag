"""Prepare per-obligation calibrated review, separate from answer generation."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from newdomain.experiment import write_new, sha
from optimization_review import freeze

PROMPT = '''逐条核对答案与给定的来源义务，不能按关键词出现就判正确。只输出JSON，键为checks和extra_unsupported。checks为数组，每项仅含id、status、answer_quote、reason。id必须使用输入的义务id；status只能为present、missing、contradicted、ambiguous。answer_quote必须逐字截取答案中的连续片段；遗漏时为空字符串。reason简短说明。extra_unsupported为数组，记录答案中没有来源支持的额外事实的原句，没有则为空。
规则：每项义务都要核对，不跳过期间、完成状态、一次性、单项及累计上限、对象和否定。答案声称不需要某资格而来源要求该资格，判contradicted；条件只出现在引用或来源而不在答案中，不能判present。问题明确给定的前提可说明其已给定；不要求机械重复，但答案不得扩大适用范围。等义改写可present。别把“区内”误判为遗漏来源机构。拒答后出现无证据的具体到账额仍是额外无依据事实。空答案是missing，不是正确拒答。只判断提供的材料，不推断现实政策效力。不要输出思考过程。'''


def validate_verdict(content, answer, obligations):
    result=json.loads(content)
    if set(result)!={'checks','extra_unsupported'} or not isinstance(result['checks'],list) or not isinstance(result['extra_unsupported'],list):raise ValueError('atomic review schema')
    expected={r['id'] for r in obligations}
    if len(result['checks'])!=len(expected) or {c['id'] for c in result['checks']}!=expected:raise ValueError('obligation coverage')
    for c in result['checks']:
        if set(c)!={'id','status','answer_quote','reason'} or c['status'] not in ('present','missing','contradicted','ambiguous'):raise ValueError('check schema')
        if not isinstance(c['answer_quote'],str) or c['answer_quote'] not in answer:raise ValueError('invented answer quote')
        if c['status'] in ('present','contradicted') and not c['answer_quote']:raise ValueError('missing answer evidence')
    for quote in result['extra_unsupported']:
        if not isinstance(quote,str) or not quote or quote not in answer:raise ValueError('invented unsupported quote')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--annotations',type=Path,required=True);p.add_argument('--name',default='atomic-calibration');a=p.parse_args()
    items={i['qid']:i for i in json.loads(a.annotations.read_text())['cases']}
    key=json.loads((a.root/'calibration-private-key.json').read_text());old={j['qid']:j for j in json.loads((a.root/'calibration-jobs.json').read_text())};jobs=[]
    for k in key:
        body=json.loads(old[k['job']]['messages'][1]['content'])
        body['obligations']=[{n:req[n] for n in ('id','criterion','support')} for req in items[k['qid']]['requirements']]
        jobs.append({'qid':k['job'],'messages':[{'role':'system','content':PROMPT},{'role':'user','content':json.dumps(body,ensure_ascii=False)}]})
    path=a.root/f'{a.name}-jobs.json';write_new(path,jobs);freeze(path,Path(__file__).resolve().parents[1]);f=path.with_suffix('.freeze.json');z=json.loads(f.read_text());z['hashes'][str(Path(__file__).resolve())]=sha(__file__);f.write_text(json.dumps(z,indent=2)+'\n')
    print(json.dumps({'jobs':len(jobs)}))


if __name__=='__main__':main()
