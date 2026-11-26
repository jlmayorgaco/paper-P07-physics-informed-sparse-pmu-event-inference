"""Read-only posthoc diagnostics of sealed predictions, with unchanged matching.

No fit, inference, new event association, or change to the frozen evaluator.
This script requires the local SGSMA prediction archive on the first run.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
SG=ROOT.parent/'SGSMA26-Physics-Informed-AD'
F=ROOT/'generated/frozen/c01_20261029'
OUT=ROOT/'generated/review_diagnostics_20261102'
METHODS=['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE']
NAMES=['Physical bank','Nominal bank','ExtraTrees','ExtraTrees short']

def main():
    OUT.mkdir(exist_ok=True)
    manifest=json.loads((F/'MANIFEST.json').read_text())
    for item in manifest['files']:
        assert hashlib.sha256((F/item['path']).read_bytes()).hexdigest()==item['sha256']
    seal_path=SG/'experiments/PAPER_CONFIRMATORY_C01/run/results/PREDICTIONS_SEAL.json'
    seal=json.loads(seal_path.read_text())
    seals={x['path'].replace('\\','/'):x['sha256'] for x in seal['files']}
    ev=pd.read_csv(F/'EVENTS.csv');rec=pd.read_csv(F/'RECORDS.csv')
    ev=ev[(ev.lane=='continuous') & ev.method.isin(METHODS)]
    cache={};checked={};rows=[]
    for row in ev.to_dict('records'):
        key=(row['record'],row['method'])
        if key not in cache:
            rel=f'experiments/PAPER_CONFIRMATORY_C01/run/data/predictions/{key[0]}/{key[1]}/prediction.json'
            raw=(SG/rel).read_bytes();digest=hashlib.sha256(raw).hexdigest()
            assert digest==seals[rel],rel
            cache[key]=json.loads(raw);checked[rel]=digest
        meta=cache[key];ep=row['episode']
        diagnosis=next((x for x in meta['events'] if x['kind']=='diagnosis' and x['episode']==ep),None)
        available=diagnosis is not None and diagnosis['emitted_s']<row['off_s']
        pred=diagnosis.get('family','unresolved') if available else 'no_timely_diagnosis'
        source=diagnosis.get('source','unresolved') if available else 'no_timely_diagnosis'
        correct=available and pred==row['family'] and source==row['source']
        assert bool(correct)==bool(row['timely']), (key,row['event'])
        rows.append(dict(method=row['method'],record=row['record'],event=row['event'],parent=row['parent'],
                         true_family=row['family'],true_source=row['source'],predicted_family=pred,
                         predicted_source=source,timely_joint=correct))
    d=pd.DataFrame(rows);d.to_csv(OUT/'event_diagnostic_rows.csv',index=False)
    family=[]
    for method in METHODS:
        part=d[d.method==method]
        assert len(part)==648
        m=pd.crosstab(part.true_source,part.predicted_source)
        m.to_csv(OUT/f'source_confusion_{method}.csv')
        for true in ['load','line']:
            for pred in ['load','line','no_timely_diagnosis','unresolved']:
                family.append(dict(method=method,true_family=true,predicted_family=pred,
                                   count=int(((part.true_family==true)&(part.predicted_family==pred)).sum())))
    fd=pd.DataFrame(family);fd.to_csv(OUT/'family_confusion.csv',index=False)
    plt.rcParams.update({'font.size':8,'font.family':'DejaVu Sans','pdf.fonttype':42})
    fig,axes=plt.subplots(2,2,figsize=(7.1,3.65),layout='constrained')
    for ax,method,name in zip(axes.flat,METHODS,NAMES):
        part=fd[fd.method==method]
        matrix=part.pivot(index='true_family',columns='predicted_family',values='count').reindex(index=['load','line'],columns=['load','line','no_timely_diagnosis','unresolved']).to_numpy()
        assert (matrix.sum(axis=1)==324).all()
        ax.imshow(matrix/324,vmin=0,vmax=1,cmap='Blues',aspect='auto')
        for i in range(2):
            for j in range(4):ax.text(j,i,str(matrix[i,j]),ha='center',va='center',color='white' if matrix[i,j]>180 else '#253b49')
        ax.set_xticks(range(4),['Load','Line','No timely\ndiagnosis','Unresolved'])
        ax.set_yticks([0,1],['True load','True line']);ax.set_title(name)
    for ext in ['pdf','png']:fig.savefig(ROOT/f'figures/generated/review_c01_confusion.{ext}',dpi=210,bbox_inches='tight',pad_inches=.04)
    plt.close(fig)
    persistent=rec[(rec.lane=='persistent_line') & rec.method.isin(METHODS)]
    cols=['events','extras','false_restorations','open_eof','tp','fp','fn','monitored_reports']
    persistent.groupby('method')[cols].sum().to_csv(OUT/'persistent_monitoring.csv')
    (OUT/'PROVENANCE.json').write_text(json.dumps(dict(status='POSTHOC_DESCRIPTIVE_NOT_NEW_CONFIRMATORY_METRIC',
        matching='Frozen EVENTS episode association; first diagnosis before physical OFF',
        frozen_evaluator_changed=False,inference_rerun=False,retuned=False,normal_records_in_confusion=False,
        prediction_seal_sha256=hashlib.sha256(seal_path.read_bytes()).hexdigest(),prediction_json_files_verified=len(checked),
        files_verified=checked),indent=2)+'\n')
    print(fd.to_string(index=False))
    print(persistent.groupby('method')[cols].sum().to_string())

if __name__=='__main__':main()
