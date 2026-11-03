"""Mandatory supplement tables, generated from the unchanged sealed outputs."""
from pathlib import Path
import hashlib,json
import pandas as pd
from c01_main_tables import write_tables
from monitored_exposure import corrected_intervals
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'generated/frozen/c01_20261029'
LABEL={'R11':'Physical bank','R11_NOMINAL':'Nominal bank','ET_REFERENCE':'ExtraTrees','ET_CANDIDATE':'ExtraTrees short','CHEN2016':'Chen'}
COND={'MATCH':'Matched','RX_IN_SUPPORT':'In-bank','RX_OUT_SUPPORT':'Out-of-bank'}

def table(name,caption,spec,header,rows,wide=True):
    env='table*' if wide else 'table'
    lines=[f'\\begin{{{env}}}[t]\\centering\\small',r'\caption{'+caption+'}',r'\label{tab:'+name+'}',
           r'\begin{tabular}{'+spec+r'}\toprule',header+r'\\\midrule',*rows,r'\bottomrule\end{tabular}',f'\\end{{{env}}}']
    (ROOT/'tables/generated'/f'{name}.tex').write_text('\n'.join(lines)+'\n')

def main():
    for folder in [F,ROOT/'generated/frozen/submission_s01_system_20261031']:
        manifest=json.loads((folder/'MANIFEST.json').read_text())
        items=manifest['files'] if 'files' in manifest else [dict(path=k,**v) for k,v in manifest.items()]
        for item in items:
            assert hashlib.sha256((folder/item['path']).read_bytes()).hexdigest()==item['sha256']
    s=pd.read_csv(F/'SUMMARY.csv');r=pd.read_csv(F/'RECORDS.csv');e=pd.read_csv(F/'EVENTS.csv')
    write_tables(ROOT,s)
    methods=list(LABEL)[:4];c=s[s.lane=='continuous'];rows=[]
    for (cond,noise),g in c.groupby(['condition','noise']):
        d=g.set_index('method')
        rows.append(COND[cond]+f' & {noise:g} & '+' & '.join(f'{int(d.loc[m,"timely"])}/{int(d.loc[m,"events"])}; {int(d.loc[m,"event_extras"])}' for m in methods)+r'\\')
    table('review_continuous','Continuous outcomes by network and noise stratum. Each cell is timely family/source decisions / intended events; unmatched event-stream alarms. Replays share physical parents.','llrrrr',r'Network & Noise & Physical bank & Nominal bank & ExtraTrees & ET short',rows)
    a=r[(r.lane=='persistent_line')&r.method.isin(methods)].groupby('method')[['events','extras','false_restorations','open_eof','fn','tp']].sum();rows=[]
    for m in methods:
        z=a.loc[m];rows.append(LABEL[m]+f' & {int(z.events)} & {int(z.extras)} & {int(z.false_restorations)} & {int(z.open_eof)} & {int(z.fn)}'+r'\\')
    table('review_persistence','Descriptive persistence audit after first detection on sustained line openings. All four procedures first identify 162/162 lines. Extras are later unmatched alarms; unmatched OFF counts only restoration messages on unmatched episodes. Open-at-end messages are expected for sustained events and are not automatically errors. False-negative reports include detection delay and later inactive labels. Chen is a first-stop method and is excluded from this recurrent-monitoring diagnostic.','lrrrrr',r'Method & Openings & Extras & Unmatched OFF & Open at end & FN reports',rows)
    rows=[]
    for (fam,source),g in e[(e.lane=='continuous')&e.method.isin(methods)].groupby(['family','source']):
        d=g.groupby('method').agg(n=('event','size'),timely=('timely','sum'))
        rows.append(f'{fam.title()} / {source} & '+' & '.join(f'{int(d.loc[m,"timely"])}/{int(d.loc[m,"n"])}' for m in methods)+r'\\')
    table('review_sources','Timely decisions by source in the continuous test. These are correlated realizations of the registered physical schedules, not source-excluded generalization.','lrrrr',r'Family / asset & Physical bank & Nominal bank & ExtraTrees & ET short',rows)
    p=corrected_intervals();rows=[]
    for (cond,noise,m,ref),g in p[p.lane=='continuous'].groupby(['condition','noise','method','reference']):
        z=g.set_index('metric');cells=[]
        for metric,factor in [('timely_fraction',100),('extras_per_event_hour',1)]:
            q=z.loc[metric];cells.append(f'{q.difference*factor:.2f} [{q.lower95*factor:.2f}, {q.upper95*factor:.2f}]')
        rows.append(f'{COND[cond]} & {noise:g} & {LABEL[m]} & {LABEL[ref]} & '+' & '.join(cells)+r'\\')
    table('review_paired','Paired physical-bank minus learned-comparator differences. Timely attribution is in percentage points; extras are per monitored event-record hour, excluding 12 s of startup from each 120-s record. The registered rate differences and 95-percent parent-bootstrap bounds are exactly rescaled by 120/108; original counts, matches and intervals remain archived.','ll ll rr',r'Network & Noise & Method & Reference & Timely difference & Extra-rate difference',rows)
    cyber=json.loads((ROOT/'generated/frozen/submission_s01_system_20261031/validation.json').read_text())
    rows=[]
    for kind,z in cyber['existing_interval_integrity_metrics']['completed_interval_components'].items():
        hit=z['any_target_hit_over_all_positive'];rows.append(kind.title()+f' & {hit["correct"]}/{hit["total"]} & {z["identifiable_target_fp"]} & {z["identifiable_target_fn"]}'+r'\\')
    table('review_integrity','Retrospective measurement-integrity components over 180 windows. Hits require family and PMU identity. Missingness is observed availability; corrupted-data identification is inherited from the window classifier. These are not counts of attributed cyberattacks.','lrrr',r'Component & Positive-window hits & FP & FN',rows)
    macros={'PersistETExtras':int(a.loc['ET_REFERENCE','extras']),'PersistShortExtras':int(a.loc['ET_CANDIDATE','extras']),
            'PersistPhysicalExtras':int(a.loc['R11','extras'])}
    (ROOT/'generated/review_audit_macros.tex').write_text(''.join('\\newcommand{\\'+k+'}{'+str(v)+'}\n' for k,v in macros.items()))
    audit=json.loads((F/'EVALUATION_AUDIT.json').read_text())
    assert not audit['physical_rejections'] and not audit['inference_failures']
    print('Complete frozen tables generated; zero solver/inference failures verified. No predictions or metrics changed.')

if __name__=='__main__':main()
