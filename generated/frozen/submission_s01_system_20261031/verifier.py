"""Independent post-seal equivalence audit; no inference or RAW observations.

Uses existing frozen metric functions and their archived reference targets.
Does not import the composition runtime or overwrite any prior artifact.
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from compare_missing_latency import first_notices
from score_cyber import decode_interval_prediction
from score_continuous import set_summary
from score_physical_metadata import compare_targets, predicted_targets

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'run/system_composition_v1'
OUT = ROOT / 'evaluation/SYSTEM_COMPOSITION_V1_VALIDATION.json'
PLAN = ROOT / 'protocol/SYSTEM_COMPOSITION_PLAN.json'
EXPECTED_PLAN = '0d3a9cdb5c3ab69dde035b8a7970d7c503ebc7cc6dfb9de00a3ece5d3434ebfd'
HYBRID = ROOT / 'run/ml_raw_segmented'
CYBER = ROOT / 'run/cyber_composition_v2'
REFERENCES = [
    HYBRID / 'PHYSICAL_METADATA_COMPARISON.json',
    CYBER / 'EVALUATION.json', CYBER / 'MISSING_LATENCY_COMPARISON.json',
    ROOT / 'evaluation/RAW_AUDIT_VALIDATION.json',
    ROOT / 'run/legacy_continuous/EVALUATION.json',
    ROOT / 'run/legacy_historical/EVALUATION.json',
]
CHECKS = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def require(value, label):
    if not value:
        raise AssertionError(label)
    CHECKS.append(label)


def sealed(folder):
    seal = read(folder / 'PREDICTIONS_SEAL.json')
    require(seal['truth_read'] is False, f'{folder.name}: truth boundary')
    for name, digest in seal['files'].items():
        path = (folder / name).resolve()
        require(path.is_relative_to(folder.resolve()), f'{folder.name}: confined member {name}')
        require(sha(path) == digest, f'{folder.name}: sealed member {name}')
    return seal


def project_physical(w):
    p = w['physical']; old = w['legacy_export']
    return dict(window_index=w['window_index'], window_start_s=w['window_start_s'],
                window_end_s=w['window_end_s'], available=w['available'],
                emitted_s=p['component_emitted_s'], last_report_used_s=p['last_report_used_s'],
                physical_event=p['event'], physical_source=p['source'],
                legacy_event=old['event'], legacy_location=old['location'],
                zip_original_location=old['original_location'], legacy_top3=old['original_top3'],
                **{key:p[key] for key in ('source_route','fallback_reason','hybrid_source_changed',
                   'eligible_diagnosis_ids','ml_status_report_counts','selected_ml_diagnosis')})


def project_integrity(w):
    i = w['integrity']
    return dict(window_index=w['window_index'], window_start_s=w['window_start_s'],
                window_end_s=w['window_end_s'], available=w['available'],
                emitted_s=i['component_emitted_s'], last_report_used_s=i['last_report_used_s'],
                integrity_status=i['status'], integrity_sources=i['sources'],
                integrity_diagnoses=i['diagnoses'], interval_diagnosis=True,
                asserts_current_ongoing_corruption=w['asserts_current_ongoing_corruption'])


def main():
    if OUT.exists():
        raise FileExistsError('Preserve this audit; choose a successor output')
    previous = {p.relative_to(ROOT).as_posix():sha(p) for p in REFERENCES}
    plan = read(PLAN)
    require(sha(PLAN) == EXPECTED_PLAN, 'Expected frozen composition plan')
    require(sha(ROOT/'runtime/system_replay.py') == plan['runtime_sha256'], 'Frozen runtime unchanged')
    for name, digest in plan['input_sha256'].items():
        require(sha(ROOT/name) == digest, 'Frozen input '+name)
    seals = {p.name:sealed(p) for p in (RUN, HYBRID, CYBER)}
    require(seals[RUN.name]['protocol_sha256'] == EXPECTED_PLAN, 'Output plan seal')
    doc = read(RUN/'prediction.json'); hdoc = read(HYBRID/'hybrid_predictions.json')
    cyber = read(CYBER/'prediction.json'); ml = read(HYBRID/'prediction.json')
    native_path = ROOT/'run/legacy_continuous/predictions.json'
    require(sha(native_path) == hdoc['zip_prediction_sha256'] == cyber['legacy_predictions_sha256'], 'Same exact native ZIP input')
    native = read(native_path)['windows']
    require(doc['component_lineage'] == plan['input_sha256'], 'Complete lineage preserved')
    require(doc['protocol_sha256'] == EXPECTED_PLAN and doc['runtime_sha256'] == plan['runtime_sha256'], 'Output provenance')
    require(all(doc[k] is False for k in ('truth_read','component_inference_reexecuted',
            'new_independent_performance_result','malicious_intent_inferred',
            'persistent_corruption_inferred','component_performance_changed')), 'Scope flags retained')
    prefix = ROOT/'run/raw_physical_prefix/RESULT.json'
    require(doc['physical_filter'] == dict(method='R11',available=False,reason=read(prefix),evidence_sha256=sha(prefix)), 'Static R11 unavailability provenance')

    windows=doc['completed_windows']; messages=doc['messages']
    require(len(windows)==doc['windows']==len(hdoc['windows'])==len(cyber['window_diagnoses'])==180, 'All180 windows')
    require([w['window_index'] for w in windows]==list(range(180)), 'Unique ordered window IDs')
    projected_physical=[]; projected_integrity=[]
    for w,h,c in zip(windows,hdoc['windows'],cyber['window_diagnoses']):
        p=project_physical(w); i=project_integrity(w)
        require(p=={k:h[k] for k in p}, f'Physical projection W{w["window_index"]}')
        require(i=={k:c[k] for k in i}, f'Integrity projection W{w["window_index"]}')
        require(w['emitted_s']==max(h['emitted_s'],c['emitted_s']) and
                w['last_report_used_s']==max(h['last_report_used_s'],c['last_report_used_s']), f'Window publication W{w["window_index"]}')
        require(w['scope']=='observed_interval' and w['kind']=='completed_window' and
                all(w[k] is False for k in ('changes_current_availability','asserts_current_ongoing_corruption',
                                            'asserts_physical_restoration','malicious_intent_inferred')), f'Nonpersistent scope W{w["window_index"]}')
        selected=p['selected_ml_diagnosis']
        if selected:
            require(selected['last_report_used_s']<=selected['emitted_s']<=p['emitted_s'] and
                    p['window_start_s']<=selected['emitted_s']<=p['window_end_s'], 'Selected ML clock retained')
        projected_physical.append(p);projected_integrity.append(i)

    with np.load(CYBER/'availability.npz',allow_pickle=False) as z:
        at=z['time_s'];missing=z['missing_pmu'];pmus=z['pmus']
    with np.load(HYBRID/'prediction.npz',allow_pickle=False) as z:
        mt=z['time_s'];status=z['status'];source=z['source_label']
    expected_arrays=dict(availability_time_s=at,ml_time_s=mt,missing_pmu=missing,pmus=pmus,
                         ml_status=status,ml_source_label=source)
    with np.load(RUN/'report_status.npz',allow_pickle=False) as z:
        require(set(z.files)==set(expected_arrays),'Exact report-status schema')
        for name,expected in expected_arrays.items():
            require(z[name].dtype==expected.dtype and np.array_equal(z[name],expected), 'Exact array '+name)
    require(len(at)==len(mt)==doc['reports']==161379,'All161379 reports')
    require(np.all(np.diff(at)>0) and np.all(np.diff(mt)>0) and np.all(abs(at-mt)<=1e-7), 'Unique original report-clock alignment')
    require(np.array_equal(missing.any(axis=1),status==0),'Missing and incomplete masks match on this record')
    require(np.all(source[status!=2]==-1),'Unavailable ML sources remain unavailable')
    counts={str(k):int((status==k).sum()) for k in range(4)}
    require(counts==ml['status_counts']=={'0':9200,'1':1800,'2':150379,'3':0},'All ML states preserved')
    require(len(ml['segments'])==5 and ml['prefix_normality_verified'] is False and
            ml['continuous_state_across_gaps'] is False,'Segment limitations retained through verified lineage')
    coverage=np.zeros(len(at),dtype=np.uint8)
    for index,w in enumerate(windows):
        take=(at>=w['window_start_s'])&((at<=w['window_end_s']) if index==179 else (at<w['window_end_s']))
        coverage[take]+=1
        require(bool(np.any(take)) and float(at[take][-1])<=w['emitted_s']+1e-7, f'Observed window support W{index}')
    require(bool(np.all(coverage==1)), 'Report coverage exactly once, including final partial window')

    availability=[];window_stream=[];status_messages=[]
    require(len(messages)==206 and [m['publication_index'] for m in messages]==list(range(206)), 'Unique206 publication indices')
    for number,m in enumerate(messages):
        require(math.isfinite(m['emitted_s']) and math.isfinite(m['last_report_used_s']) and
                0<=m['last_report_used_s']<=m['emitted_s'], f'Causal publication M{number}')
        if number:require(messages[number-1]['emitted_s']<=m['emitted_s'],f'Monotone publication M{number}')
        bare={k:v for k,v in m.items() if k!='publication_index'}
        if m['scope']=='current_report_availability':availability.append(bare)
        elif m['scope']=='observed_interval':window_stream.append(bare)
        elif m['scope']=='current_component_availability':status_messages.append(bare)
        else:raise AssertionError('Unknown scope')
    require(window_stream==windows,'Exactly one message per completed window')
    recovered=[]
    for m in availability:
        require(m['origin']=='CYBER_V2' and m['stream']=='availability' and m['malicious_intent_inferred'] is False,'Availability origin')
        original={k:v for k,v in m.items() if k not in ('scope','origin','stream','malicious_intent_inferred','last_report_used_s')}
        original['last_report_s']=m['last_report_used_s'];recovered.append(original)
    require(recovered==cyber['availability_messages'],'Exact12 availability message projection')
    transitions=np.r_[0,np.flatnonzero(status[1:]!=status[:-1])+1]
    require(len(status_messages)==len(transitions)==14,'All14 status changes')
    for m,k in zip(status_messages,transitions):
        require(m==dict(kind='component_status',component='SEGMENT_INITIALIZED_SIM_ET_SHORT',
                       scope='current_component_availability',report_index=int(k),status_code=int(status[k]),
                       status=ml['status_codes'][str(int(status[k]))],emitted_s=float(max(at[k],mt[k])),
                       last_report_used_s=float(max(at[k],mt[k])),source_component_emitted_s=float(mt[k]),
                       changes_current_availability=False),f'Status transition at row{k}')
    independently_ordered=sorted([(m['emitted_s'],priority,j,m) for priority,stream in
                                enumerate((availability,windows,status_messages)) for j,m in enumerate(stream)])
    require([item[3] for item in independently_ordered]==[{k:v for k,v in m.items() if k!='publication_index'} for m in messages], 'Stable merge and original tie ordering')

    # Independent consumer, not the producer's AvailabilityState implementation.
    current=();episode=None;ml_state=None;cursor=0;wrong_missing=[];wrong_status=[]
    for row,t in enumerate(np.maximum(at,mt)):
        while cursor<len(messages) and messages[cursor]['emitted_s']<=t:
            m=messages[cursor];cursor+=1
            if m['scope']=='current_report_availability':
                if m['kind']=='alarm':
                    require(episode is None,'No duplicate open availability episode');episode=m['episode']
                else:
                    require(m['episode']==episode,'Availability episode identity')
                    if m['kind']=='diagnosis':
                        require(m['family']=='missing','Only missing is current');current=tuple(m['source'])
                    elif m['kind'] in ('restoration','superseded'):current=();episode=None
                    elif m['kind']!='right_censored':raise AssertionError('Unexpected availability transition')
            elif m['scope']=='current_component_availability':ml_state=m['status_code']
            # Interval messages deliberately do not update current state.
        expected=tuple(f'PMU{bus}' for bus,absent in zip(pmus,missing[row]) if absent)
        if current!=expected:wrong_missing.append(row)
        if ml_state!=int(status[row]):wrong_status.append(row)
    require(cursor==len(messages) and not wrong_missing and not wrong_status,'All161379 report states reconstructed exactly')
    require(current==() and episode is None,'Four missing episodes close without window reopening')

    audit=read(RUN/'READ_AUDIT.json')
    allowed={str((ROOT/name).resolve()).lower() for name in plan['input_sha256']}
    allowed.update(str(p.resolve()).lower() for p in (PLAN,ROOT/'runtime/system_replay.py',RUN/'prediction.json',RUN/'report_status.npz'))
    actual={str(Path(p).resolve()).lower() for p in audit['paths']}
    require(actual==allowed and audit['truth_read'] is False and audit['evaluation_read'] is False,'Recorded producer accesses exactly match frozen inputs/code/output paths')
    require(not any('raw0002' in p or 'paper_confirmatory_c01' in p for p in actual),'No forbidden paths in producer access log')

    # Reuse established metrics against targets already in completed reference evaluations.
    physical_reference=read(HYBRID/'PHYSICAL_METADATA_COMPARISON.json')['results']
    physical_records=[dict(truth={tuple(t) for t in r['truth_targets']},native=n,hybrid=p)
                      for r,n,p in zip(physical_reference['rows'],native,projected_physical)]
    physical_score=compare_targets(physical_records)
    for key in ('methods','paired_positive','per_family'):
        require(physical_score[key]==physical_reference[key],'Existing physical metric '+key)
    for p,r in zip(projected_physical,physical_reference['rows']):
        require(predicted_targets(p)=={tuple(t) for t in r['hybrid_targets']},f'Archived physical target set W{p["window_index"]}')
    cyber_reference=read(CYBER/'EVALUATION.json');families=[];sources=[];components={'missing':[],'corrupt':[]}
    for p,r in zip(projected_integrity,cyber_reference['interval_rows']):
        f,s=decode_interval_prediction(p);tf=set(r['truth_families']);ts={tuple(t) for t in r['truth_sources']}
        require(f==set(r['predicted_families']) and s=={tuple(t) for t in r['predicted_sources']},f'Archived integrity target set W{p["window_index"]}')
        families.append((tf,f,p['available'],False));sources.append((ts,s,p['available'],False))
        for kind in components:
            components[kind].append(({v for k,v in ts if k==kind},{v for k,v in s if k==kind},p['available'],False))
    cyber_score=dict(completed_interval_family_sets=set_summary(families),
                     completed_interval_family_source_sets=set_summary(sources),
                     completed_interval_components={k:set_summary(v) for k,v in components.items()})
    for key,value in cyber_score.items():require(value==cyber_reference[key],'Existing cyber metric '+key)
    latency_reference=read(CYBER/'MISSING_LATENCY_COMPARISON.json');notices=[]
    for m in recovered:
        if m['kind']=='diagnosis':
            index=int(np.argmin(abs(at-m['emitted_s'])));canonical=float(at[index])
            require(abs(canonical-m['emitted_s'])<=1e-7,'Missing notice clock')
            notices.append(dict(emitted_s=m['emitted_s'],last_report_used_s=m['last_report_s'],source=m['source'],
                                episode=m['episode'],comparison_time_s=canonical,clock_roundoff_adjustment_s=canonical-m['emitted_s']))
    latency_score=first_notices(latency_reference['observed_intervals'],notices)
    require(latency_score==latency_reference['immediate_availability_v2'],'Existing missing first-notice metric, all rows')
    require({p.relative_to(ROOT).as_posix():sha(p) for p in REFERENCES}==previous,'All prior evaluations unchanged')
    for name,digest in plan['input_sha256'].items():require(sha(ROOT/name)==digest,'Input unchanged after audit '+name)
    for name,digest in seals[RUN.name]['files'].items():require(sha(RUN/name)==digest,'Sealed output unchanged after audit '+name)
    report=dict(status='PASS_EXACT_COMPONENT_EQUIVALENCE',evaluation_kind='Post-seal retrospective equivalence, not a new performance endpoint',
        verifier_sha256=sha(Path(__file__)),plan_sha256=sha(PLAN),runtime_sha256=plan['runtime_sha256'],
        output_seal_sha256=sha(RUN/'PREDICTIONS_SEAL.json'),output_files=seals[RUN.name]['files'],
        checked_assertions=len(CHECKS),checks=CHECKS,windows=180,reports=161379,messages=206,
        message_scopes=dict(Counter(m['scope'] for m in messages)),exact_projected_physical_windows=180,
        exact_projected_integrity_windows=180,exact_projected_availability_messages=12,exact_arrays=list(expected_arrays),
        reconstructed_missing_disagreement_rows=wrong_missing,reconstructed_ml_status_disagreement_rows=wrong_status,
        status_counts=counts,missing_positive_reports=int(missing.any(axis=1).sum()),
        clock_alignment=dict(different_rows=int(np.count_nonzero(at!=mt)),max_absolute_difference_s=float(np.max(abs(at-mt))),
                             matching_tolerance_s=1e-7,original_clocks_preserved=True),
        source_route_counts=dict(Counter(p['source_route'] for p in projected_physical)),
        fallback_counts=dict(Counter(p['fallback_reason'] for p in projected_physical if p['fallback_reason'] is not None)),
        source_changes=sum(p['hybrid_source_changed'] for p in projected_physical),
        existing_physical_metrics={k:v for k,v in physical_score.items() if k!='rows'},existing_interval_integrity_metrics=cyber_score,
        existing_pointwise_availability_metrics=cyber_reference['causal_pointwise_availability'],
        pointwise_metric_status='Inherited unchanged by exact mask/clock equivalence; no new RAW truth read or accuracy estimate',
        existing_missing_latency_metrics={k:v for k,v in latency_score.items() if k!='rows'},
        producer_read_boundary=dict(recorded_paths=len(actual),unexpected_paths=[],exact_frozen_allowlist=True,
            limitation='Repository-scoped Python open-event log and source inspection; not an operating-system sandbox proof'),
        metric_source_sha256={name:sha(ROOT/'evaluation'/name) for name in
            ('compare_missing_latency.py','score_cyber.py','score_continuous.py','score_physical_metadata.py')},
        prior_evaluation_sha256=previous,prior_artifacts_unchanged=True,inference_rerun=False,
        RAW_observations_read=False,reference_evaluation_targets_reused=True,C01_read=False,RAW0002_read=False,
        global_accuracy_created=False,new_independent_performance_claim=False)
    OUT.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],assertions=len(CHECKS),windows=180,reports=161379,messages=206,
                         mismatching_report_states=0,validation=OUT.relative_to(ROOT).as_posix(),sha256=sha(OUT)),indent=2))


if __name__=='__main__':main()
