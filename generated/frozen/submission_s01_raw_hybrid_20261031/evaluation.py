"""Metadata-source successor comparison; never alter labels, classes or models."""
from collections import Counter
import argparse
import json
import math
from pathlib import Path
import re

from raw_labels import PHYSICAL,ROOT,REPO,load_raw_labels,sha

FAMILIES={'line':'line_outage','line_outage':'line_outage','load':'load_change','load_change':'load_change',
          'fault':'fault','generation':'generation_change','generation_change':'generation_change'}
SOURCE_BY_FAMILY={'fault':'BUS39','line_outage':'LINE23-24','generation_change':'BUS2','load_change':'BUS7'}


def canonical_source(value):
    if value is None:return None
    if not isinstance(value,str):raise ValueError('Physical source must be a single explicit source label')
    value=value.upper().strip()
    bus=re.fullmatch(r'BUS([1-9][0-9]*)',value)
    if bus:return 'BUS'+str(int(bus[1]))
    line=re.fullmatch(r'LINE([1-9][0-9]*)-([1-9][0-9]*)',value)
    if line:
        i,j=sorted([int(line[1]),int(line[2])])
        if i==j:raise ValueError('A line cannot have the same two endpoints')
        return f'LINE{i}-{j}'
    return value  # Explicit unsupported output remains wrong; never substitute a nearby source.


def first_diagnoses(messages):
    """Deduplicate before family filtering, preserving wrong first diagnoses."""
    groups={}
    for m in messages:
        if m.get('kind')!='diagnosis':continue
        if 'last_report_used_s' not in m and 'last_report_s' not in m:
            raise ValueError('ML diagnosis lacks consumed-report clock provenance')
        time=float(m['emitted_s']);used=float(m.get('last_report_used_s',m.get('last_report_s')))
        if not math.isfinite(time) or not math.isfinite(used) or used>time+1e-7:
            raise ValueError('ML diagnosis uses future or invalid report time')
        key=(m['segment'],m['episode']);groups.setdefault(key,[]).append(dict(m,last_report_used_s=used))
    result=[]
    for key,items in groups.items():
        items.sort(key=lambda x:x['emitted_s']);first_time=items[0]['emitted_s']
        tied=[m for m in items if m['emitted_s']==first_time]
        signatures={(FAMILIES.get(m.get('family'),m.get('family')),canonical_source(m.get('source'))) for m in tied}
        first=dict(tied[0],ambiguous_first=len(signatures)>1,revisions_ignored=len(items)-len(tied))
        first['family']=FAMILIES.get(first.get('family'),first.get('family'))
        result.append(first)
    return sorted(result,key=lambda m:(m['emitted_s'],str(m['segment']),str(m['episode'])))


def select_source_route(native,diagnoses):
    """Selection depends on predicted native class and causal ML evidence only."""
    if not native['available']:return None,'legacy_unavailable'
    code=native['legacy_event'];physical=native['physical_event']
    eligible=code in (2,4) or (code==6 and physical in (2,4))
    if not eligible:return None,'native_class_not_eligible'
    family=PHYSICAL[physical if code==6 else code]
    candidates=[d for d in diagnoses if d.get('segment_available',True) and d['family']==family
                and native['window_start_s']<=d['emitted_s']<=native['emitted_s']
                and d['emitted_s']<=native['window_end_s']]
    if not candidates:return None,'no_causal_matching_first_diagnosis'
    t=min(d['emitted_s'] for d in candidates);earliest=[d for d in candidates if d['emitted_s']==t]
    if any(d['ambiguous_first'] for d in earliest) or len({canonical_source(d['source']) for d in earliest})>1:
        return None,'ambiguous_first_diagnosis'
    return earliest[0],None


def predicted_targets(window):
    if not window['available'] or window.get('physical_event') in (0,None):return set()
    family=PHYSICAL.get(window['physical_event'],'UNSUPPORTED_PHYSICAL_'+str(window['physical_event']))
    return {(family,canonical_source(window.get('physical_source')))}


def compare_targets(records):
    """All positives, including unsupported/missed families, stay in denominator."""
    methods={};paired=Counter();by_family={};rows=[]
    for method in ('native','hybrid'):
        joint=exact=family=source=exact_all=available=fp=fn=0;positive=0
        for r in records:
            truth=set(r['truth']);pred=predicted_targets(r[method]);ok=r[method]['available'];available+=ok
            positive+=bool(truth);joint+=bool(truth & pred);exact+=bool(truth and ok and truth==pred)
            family+=bool({x[0] for x in truth}&{x[0] for x in pred})
            source+=bool({x[1] for x in truth}&{x[1] for x in pred})
            exact_all+=bool(ok and truth==pred);fp+=len(pred-truth);fn+=len(truth-pred)
        methods[method]=dict(windows=len(records),available_windows=available,physical_positive_windows=positive,
                            joint_any=dict(correct=joint,total=positive),exact_set_positive=dict(correct=exact,total=positive),
                            family_any=dict(correct=family,total=positive),source_any_unconditional=dict(correct=source,total=positive),
                            exact_set_all=dict(correct=exact_all,total=len(records)),target_fp=fp,target_fn=fn)
    for r in records:
        truth=set(r['truth']);native=predicted_targets(r['native']);hybrid=predicted_targets(r['hybrid'])
        n=bool(truth & native);h=bool(truth & hybrid)
        change='gain' if h and not n else 'loss' if n and not h else 'both_correct' if n else 'both_incorrect'
        if truth:paired[change]+=1
        for family,source in truth:
            item=by_family.setdefault(family,dict(source=source,positive_windows=0,native_joint=0,hybrid_joint=0,gains=0,losses=0))
            item['positive_windows']+=1;nc=(family,source) in native;hc=(family,source) in hybrid
            item['native_joint']+=nc;item['hybrid_joint']+=hc;item['gains']+=hc and not nc;item['losses']+=nc and not hc
        rows.append(dict(window_index=r['native']['window_index'],truth_targets=[list(t) for t in sorted(truth)],
                         native_targets=[list(t) for t in sorted(native,key=str)],hybrid_targets=[list(t) for t in sorted(hybrid,key=str)],
                         native_joint=n,hybrid_joint=h,paired_change=change if truth else 'no_physical_annotation',
                         native_available=r['native']['available'],hybrid_available=r['hybrid']['available'],
                         source_route=r['hybrid'].get('source_route'),fallback_reason=r['hybrid'].get('fallback_reason'),
                         hybrid_source_changed=r['hybrid'].get('hybrid_source_changed'),
                         selected_ml_diagnosis=r['hybrid'].get('selected_ml_diagnosis')))
    return dict(methods=methods,paired_positive={k:paired[k] for k in ('gain','loss','both_correct','both_incorrect')},
                per_family=by_family,rows=rows)


def audit_routes(native_windows,hybrid_windows,diagnoses):
    """Reconstruct every source substitution before allowing comparative scores."""
    if len(native_windows)!=len(hybrid_windows):raise ValueError('Hybrid window count changed')
    records=[]
    for native,hybrid in zip(native_windows,hybrid_windows):
        for key in ('window_index','window_start_s','window_end_s','emitted_s','last_report_used_s',
                    'available','legacy_event','physical_event'):
            if native.get(key)!=hybrid.get(key):raise ValueError(f'Hybrid changed invariant {key}')
        selected,reason=select_source_route(native,diagnoses)
        expected_source=selected['source'] if selected else native.get('physical_source')
        expected_location=selected['source'] if selected else native.get('legacy_location')
        if canonical_source(hybrid.get('physical_source'))!=canonical_source(expected_source):
            raise ValueError('Hybrid source does not follow the first causal diagnosis rule')
        if canonical_source(hybrid.get('legacy_location'))!=canonical_source(expected_location):
            raise ValueError('Hybrid legacy source differs from expected route')
        claimed=hybrid.get('selected_ml_diagnosis')
        if selected is None and claimed is not None:raise ValueError('Hybrid claims an ineligible ML diagnosis')
        if selected:
            if not claimed:raise ValueError('Hybrid omitted selected diagnosis provenance')
            for key in ('segment','episode','emitted_s'):
                if selected[key]!=claimed.get(key):raise ValueError(f'Selected diagnosis differs: {key}')
            if canonical_source(selected['source'])!=canonical_source(claimed.get('source')):
                raise ValueError('Selected diagnosis source changed')
            if FAMILIES.get(claimed.get('family'),claimed.get('family'))!=selected['family']:
                raise ValueError('Selected diagnosis family changed')
        changed=bool(canonical_source(native.get('physical_source'))!=canonical_source(hybrid.get('physical_source')))
        if bool(hybrid.get('hybrid_source_changed'))!=changed:raise ValueError('Source-change flag differs from actual source')
        records.append(dict(window_index=native['window_index'],selected_diagnosis=selected,
                            expected_fallback_reason=reason,reported_fallback_reason=hybrid.get('fallback_reason'),
                            reported_source_route=hybrid.get('source_route'),source_changed=changed))
    return dict(windows=len(records),class_changes=0,causality_violations=0,source_route_violations=0,
                ML_selected=sum(r['selected_diagnosis'] is not None for r in records),
                actual_source_changes=sum(r['source_changed'] for r in records),
                fallback_counts=dict(Counter(r['reported_fallback_reason'] for r in records if r['selected_diagnosis'] is None)),
                source_route_counts=dict(Counter(r['reported_source_route'] for r in records)),rows=records)


def audit_segmented_output(run,document,label_times):
    """Check full report coverage and all gaps/startups before reading source routes."""
    import numpy as np
    with np.load(run/'prediction.npz',allow_pickle=False) as a:
        times=a['time_s'];status=a['status'];available=a['available'];source=a['source_label']
        raw_source=a['raw_source_label'];complete=a['complete_report'];logical=a['logical_time_s']
    n=len(label_times)
    if any(len(x)!=n for x in (times,status,available,source,raw_source,complete,logical)):
        raise ValueError('Segmented inference dropped reports')
    if not np.allclose(times,label_times,atol=1e-7,rtol=0):raise ValueError('Received clock differs from RAW annotations')
    if not np.isin(status,[0,1,2,3]).all() or not np.array_equal(available,status==2):raise ValueError('Invalid status mask')
    if not (source[~available]==-1).all() or not (raw_source[~available]==-1).all():raise ValueError('Unavailable source silently filled')
    if not np.array_equal(status!=0,complete):raise ValueError('Incomplete report status differs from observed completeness')
    coverage=np.zeros(n,int);segments={};statuses={str(k):int((status==k).sum()) for k in range(4)}
    if document['status_counts']!=statuses or document['reports']!=n:raise ValueError('Status summary differs from full arrays')
    for segment in document['segments']:
        key=segment['segment_id'];left=segment['start_report'];right=segment['end_report_exclusive']
        if key in segments or not 0<=left<right<=n:raise ValueError('Invalid segment scope')
        if segment['reports']!=right-left or not complete[left:right].all():raise ValueError('Invalid complete-run segment')
        if left and complete[left-1] or right<n and complete[right]:raise ValueError('Segment is not maximal')
        if segment.get('prefix_normality_verified') is not False:raise ValueError('Segment claims an uncertified normal prefix')
        startup=min(360,right-left)
        if segment['startup_reports']!=startup or not (status[left:left+startup]==1).all():
            raise ValueError('Segment startup was silently treated as monitored')
        if bool(segment['eligible_length'])!=bool(right-left>=361):raise ValueError('Segment eligibility differs')
        if right-left<361:
            if segment['inference_available']:raise ValueError('Too-short segment claims available inference')
        else:
            success=int(segment['successful_reports']);monitor=max(0,success-360)
            if success not in (0,) and not 361<=success<=right-left:raise ValueError('Invalid successful causal prefix')
            if int((status[left:right]==2).sum())!=monitor or segment['monitoring_reports']!=monitor:
                raise ValueError('Segment monitoring count differs')
            if monitor and not (status[left+360:left+success]==2).all():raise ValueError('Monitoring is not a causal prefix')
            failure_start=left+success if success else left+360
            if failure_start<right and not (status[failure_start:right]==3).all():raise ValueError('Failure interval was removed or reset')
        coverage[left:right]+=1;segments[key]=segment
    if not np.array_equal(coverage,complete.astype(int)):raise ValueError('Complete reports not covered exactly once')
    messages=[];ids=set()
    for raw in document['events']:
        item=dict(raw,segment=raw['segment_id'])
        if item['segment'] not in segments:raise ValueError('Message from unknown segment')
        if item['kind']=='diagnosis':
            if item['diagnosis_id'] in ids:raise ValueError('Duplicate diagnosis ID')
            ids.add(item['diagnosis_id']);i=int(np.argmin(np.abs(times-item['emitted_s'])))
            segment=segments[item['segment']]
            if abs(float(times[i])-item['emitted_s'])>1e-7 or not available[i]:raise ValueError('Diagnosis outside monitored report clock')
            if not segment['start_report']<=i<segment['end_report_exclusive']:raise ValueError('Diagnosis crosses segment')
            item['segment_available']=True
        messages.append(item)
    return first_diagnoses(messages),dict(reports=n,segments=document['segments'],status_counts=statuses,
        unavailable_reports=int((~available).sum()),complete_reports=int(complete.sum()),
        source_unavailable_reports_retained=True,prefix_normality_verified=False,continuous_state_across_gaps=False,
        messages=len(messages),first_diagnoses=len(first_diagnoses(messages)),all_segment_reports_preserved=True)


def main():
    import numpy as np
    parser=argparse.ArgumentParser();parser.add_argument('--ml-run',type=Path,default=ROOT/'run/ml_raw_segmented')
    args=parser.parse_args();run=args.ml_run.resolve()
    if not run.is_relative_to((ROOT/'run').resolve()):raise ValueError('Comparison run must be an S01 successor')
    output=run/'PHYSICAL_METADATA_COMPARISON.json'
    if output.exists():raise FileExistsError('Preserve completed successor comparison')
    seal_path=run/'PREDICTIONS_SEAL.json'
    if not seal_path.exists():raise FileNotFoundError('Hybrid prediction seal is not ready; no partial outputs read')
    protocol_path=ROOT/'evaluation/PHYSICAL_METADATA_COMPARISON_PROTOCOL.json'
    protocol=json.loads(protocol_path.read_text());freeze=json.loads((ROOT/'evaluation/PHYSICAL_METADATA_PROTOCOL_FREEZE.json').read_text())
    if sha(protocol_path)!=freeze['protocol_sha256']:raise ValueError('Evaluation protocol changed after freeze')
    workbook=REPO/protocol['source_provenance']['file']
    if sha(workbook)!=protocol['source_provenance']['sha256']:raise ValueError('Metadata workbook changed')
    for family,source in SOURCE_BY_FAMILY.items():
        if protocol['source_provenance'][family]['source']!=source:raise ValueError('Metadata source contract differs')
    seal=json.loads(seal_path.read_text())
    for name,fingerprint in seal['files'].items():
        p=(run/name).resolve()
        if not p.is_relative_to(run) or sha(p)!=fingerprint:raise ValueError('ML successor seal differs')
    required={'prediction.json','prediction.npz','hybrid_predictions.json'}
    if not required.issubset(seal['files']):raise ValueError('Incomplete sealed ML artifact set')
    native_path=ROOT/'run/legacy_continuous/predictions.json'
    if sha(native_path)!=json.loads(native_path.with_name('PREDICTIONS_SEAL.json').read_text())['sha256']:
        raise ValueError('Native ZIP prediction seal differs')
    preserved=[ROOT/'evaluation/RAW_AUDIT_VALIDATION.json',ROOT/'evaluation/MISSING_LATENCY_VALIDATION.json',
               ROOT/'run/cyber_composition_v2/MISSING_LATENCY_COMPARISON.json']
    preserved += [ROOT/'run'/name/'EVALUATION.json' for name in ('legacy_historical','legacy_continuous','cyber_composition_v2')]
    prior={str(p.relative_to(ROOT)):sha(p) for p in preserved}
    native=json.loads(native_path.read_text());ml=json.loads((run/'prediction.json').read_text());hybrid=json.loads((run/'hybrid_predictions.json').read_text())
    if any(d['truth_read'] is not False for d in (native,ml,hybrid)):raise ValueError('Inference truth boundary not certified')
    if hybrid['zip_prediction_sha256']!=sha(native_path) or hybrid['ml_prediction_sha256']!=sha(run/'prediction.json'):
        raise ValueError('Hybrid lineage differs')
    times,state_ids,states,label_document=load_raw_labels()
    diagnoses,segment_audit=audit_segmented_output(run,ml,times)
    normal_hybrid=[]
    for w in hybrid['windows']:
        row=dict(w)
        if row.get('selected_ml_diagnosis'):
            selected=dict(row['selected_ml_diagnosis']);selected['segment']=selected['segment_id'];row['selected_ml_diagnosis']=selected
        normal_hybrid.append(row)
    native_windows=native['windows']
    if len(native_windows)!=180:raise ValueError('Expected all180 native fixed windows')
    route_audit=audit_routes(native_windows,normal_hybrid,diagnoses)
    coverage=np.zeros(len(times),int);records=[]
    protected=('legacy_event','physical_event','integrity_status','integrity_sources','integrity_diagnoses','legacy_top3','available')
    for index,(old,new) in enumerate(zip(native_windows,normal_hybrid)):
        for key in protected:
            if key in old and old[key]!=new.get(key):raise ValueError('Hybrid modified protected output '+key)
        start,end=old['window_start_s'],old['window_end_s'];mask=(times>=start)&((times<=end) if index==179 else (times<end))
        coverage[mask]+=1;families=set();unknown=False
        for state_id in set(state_ids[mask].tolist()):
            families.update(states[state_id]['physical_families']);unknown |=states[state_id]['physical_family_unknown']
        if unknown:raise ValueError('Unresolved physical-family support requires an explicit uncertainty successor')
        records.append(dict(truth={(f,SOURCE_BY_FAMILY[f]) for f in families},native=old,hybrid=new))
    if not (coverage==1).all():raise ValueError('Window coverage differs from report support')
    if sum(bool(r['truth']) for r in records)!=24:raise ValueError('Expected all24 physical-positive windows')
    comparison=compare_targets(records)
    if comparison['methods']['native']['family_any']!=comparison['methods']['hybrid']['family_any']:
        raise ValueError('Source-only hybrid changed family metrics')
    if any(sha(ROOT/p)!=fingerprint for p,fingerprint in prior.items()):raise ValueError('Prior evaluation modified during comparison')
    report=dict(status='RETROSPECTIVE_METADATA_BASED_PHYSICAL_SOURCE_SUCCESSOR',protocol_sha256=sha(protocol_path),
        protocol_freeze=freeze,source_workbook_sha256=sha(workbook),source_metadata=protocol['source_provenance'],
        source_definition='Metadata source paired with original Event family support; not exact action ON/OFF truth',
        native_prediction_sha256=sha(native_path),hybrid_prediction_seal=seal,
        evaluation_source_sha256={p.name:sha(p) for p in [Path(__file__),ROOT/'evaluation/raw_labels.py']},
        prior_artifact_sha256=prior,prior_artifacts_unchanged=True,segments=segment_audit,routing=route_audit,
        results=comparison,physical_action_delay=None,physical_restoration_score=None,
        inference_reexecuted=False,model_or_routing_changed_by_evaluation=False,C01_read=False,RAW0002_read=False,
        limitations=['All24 physical-positive windows are included, including generation outside the ML source catalog.',
            'Original Event spans are annotation support; exact physical actions, ON/OFF, magnitudes and reversals remain unresolved.',
            'Source identity uses archived metadata; original device PMU IDs must not be mixed with project bus-indexed aliases.',
            'Segment startup prefixes are not verified normal and physical state is not preserved across gaps.',
            'One retrospective record already exposed during prior development; no independent or official-score claim.'])
    output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps({'methods':comparison['methods'],'paired_positive':comparison['paired_positive'],
                      'per_family':comparison['per_family'],'routing':{k:v for k,v in route_audit.items() if k!='rows'},
                      'status_counts':segment_audit['status_counts']},indent=2))


if __name__=='__main__':main()
