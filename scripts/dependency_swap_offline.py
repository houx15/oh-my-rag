"""Replay dependency swaps on frozen private cached inputs; no network imports."""
import argparse,collections,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from newdomain.dependency_swaps import select,proposals
from newdomain.evidence_pool import grams

VARIANTS={'off':(), 'procedure_only':('procedure',), 'metadata_only':('metadata',),
          'qualifier_only':('qualifier',), 'combined':('procedure','metadata','qualifier'),
          'relaxed_byte_diagnostic':('procedure','metadata','qualifier')}

def run(directory):
    freeze=json.loads((directory/'freeze.json').read_text())
    for name,h in freeze['hashes'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=h:raise ValueError('frozen input changed: '+name)
    jobs=json.loads((directory/'frozen-inputs.json').read_text())
    refs={r['qid']:set(dict(r['reference_sources']))for r in json.loads((directory/'evaluation-only.json').read_text())}
    output=[];aggregate=collections.defaultdict(collections.Counter)
    for j in jobs:
        b=j['baseline'];detected,skipped=proposals(j['question'],b,j['candidate_records'])
        original_query_coverage=set().union(*(grams(t)&grams(j['question'])for t in b.values()))
        def dependency_present(context,p):
            d=p['dependency'];return p['anchor']in context and d['source_id']in context and d['text']in context[d['source_id']]
        gaps=[p for p in detected if not dependency_present(b,p)]
        for name,enabled in VARIANTS.items():
            context,trace=select(j['question'],b,j['candidate_records'],j['views'],j['query_weights'],j['max_sources'],j['max_context_bytes'],enabled,relaxed_bytes=name=='relaxed_byte_diagnostic')
            query_coverage=set().union(*(grams(t)&grams(j['question'])for t in context.values()))
            assert original_query_coverage<=query_coverage
            changed=list(context.items())!=list(b.items());added=sorted(set(context)-set(b));removed=sorted(set(b)-set(context));reference=refs[j['case_id']]
            row={'case_id':j['case_id'],'corpus':j['corpus'],'origin':j['origin'],'variant':name,'changed':changed,'context':context,'trace':trace,
                 'baseline_bytes':j['max_context_bytes'],'result_bytes':sum(len(t.encode())for t in context.values()),'baseline_sources':len(b),'result_sources':len(context),
                 'added_ids':added,'removed_ids':removed,'modified_ids':[rid for rid in b if rid in context and b[rid]!=context[rid]],
                 'baseline_detector_gaps':len(gaps),'retained_detector_dependencies':sum(dependency_present(context,p)for p in gaps),
                 'lost_preexisting_detector_dependencies':sum(dependency_present(b,p)and not dependency_present(context,p)for p in detected),
                 'reference_ids_total':len(reference),'reference_ids_before':len(reference&set(b)),'reference_ids_after':len(reference&set(context)),
                 'lost_reference_ids':sorted((reference&set(b))-set(context)),'gained_reference_ids':sorted((reference&set(context))-set(b)),
                 'query_literal_coverage_lost':sorted(original_query_coverage-query_coverage),'semantic_displacement_review':'separate, required; literal coverage and reference IDs are imperfect proxies'}
            output.append(row);a=aggregate[j['corpus']+'/'+name];a['cases']+=1;a['changed']+=changed;a['no_op']+=not changed;a['detector_gaps_before']+=len(gaps);a['detector_gaps_repaired']+=row['retained_detector_dependencies'];a['preexisting_dependencies_lost']+=row['lost_preexisting_detector_dependencies'];a['reference_ids_before']+=row['reference_ids_before'];a['reference_ids_after']+=row['reference_ids_after'];a['reference_ids_total']+=len(reference);a['cases_with_reference_ids']+=bool(reference);a['removed_sources']+=len(removed);a['added_sources']+=len(added);a['context_bytes_before']+=row['baseline_bytes'];a['context_bytes_after']+=row['result_bytes'];a['byte_ceiling_violations']+=row['result_bytes']>row['baseline_bytes']
    result={'version':'dependency-swaps-v1','paid_calls':0,'model_generation':0,'model_grading':0,'cases':len(jobs),'variant_case_rows':len(output),'aggregate':aggregate,'rows':output,
            'limits':['Detector-defined structural repairs are not independent semantic gold.','Supplied reference IDs may be incomplete; GM maps are empty.','Plain OCR columns and noncontiguous baseline windows are not reconstructed.','No answer-quality or online latency effect measured.','Relaxed-byte variant is an unequal-budget diagnostic, not a fair live candidate.'],
            'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),ROOT/'newdomain/dependency_swaps.py']}}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=run(a.directory);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out['aggregate'],indent=2))
