"""Descriptive artifacts from completed, unchanged experiment ledgers."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from build_reader_figures import verify_manifest,C01
from monitored_exposure import corrected_intervals

ROOT=Path(__file__).resolve().parents[1]
METHODS=['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE']
NAMES=['Physical bank','Nominal bank','ExtraTrees','ExtraTrees short']


def main():
    verify_manifest(C01)
    control=ROOT/'generated/frozen/submission_s01_controls_20261031'
    control_manifest=json.loads((control/'MANIFEST.json').read_text())
    for name,item in control_manifest.items():
        assert hashlib.sha256((control/name).read_bytes()).hexdigest()==item['sha256']
    control_rows=json.loads((control/'single_state_evaluation.json').read_text())['summary']
    macros=(ROOT/'generated/submission_s01_macros.tex').read_text()
    for prefix,method in [('SSSimple','SINGLE_STATE_SHORT_GLR'),('SSNom','R11_NOMINAL_COMMON_CLOCK'),('SSMix','R11_COMMON_CLOCK')]:
        row=next(r for r in control_rows if r['method']==method)
        for suffix,field in [('Timely','timely_joint'),('Total','intended_events'),('Extras','extras')]:
            assert '\\newcommand{\\'+prefix+suffix+'}{'+str(row[field])+'}' in macros
    corrected=corrected_intervals()
    events=pd.read_csv(C01/'EVENTS.csv')
    events=events[(events.lane=='continuous')&events.method.isin(METHODS)]
    assets=json.loads((ROOT/'generated/frozen/narrative_case_20261030/assets.json').read_text())
    loads=[str(a['bus']) for a in assets if a['family']=='load']
    lines=[a['id'].replace('LINE','').replace('-','--') for a in assets if a['family']=='line']
    assert len(loads)==len(lines)==9
    table=r'''\begin{table}[t]\centering\small
\caption{Candidate assets fixed during method development, before the independent schedules. This is a known catalog rather than a representative sample of all network assets.}
\label{tab:source-catalog}
\begin{tabularx}{\columnwidth}{@{}lX@{}}\toprule
Family & Candidate physical sources\\\midrule
'''
    table+='Load buses & '+', '.join(loads)+r'\\'+'\n'
    table+='Lines & '+', '.join(lines)+r'\\'+'\n'+r'\bottomrule\end{tabularx}\end{table}'+'\n'
    (ROOT/'tables/generated/source_catalog.tex').write_text(table)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,
                         'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.55),sharey=True,layout='constrained')
    grid=np.linspace(0,6,181);audit=[]
    for ax,family in zip(axes,['load','line']):
        for method,name,color,style in zip(METHODS,NAMES,['#006a92','#008f79','#666666','#b57943'],['-','--','-.',':']):
            rows=events[(events.method==method)&(events.family==family)]
            assert len(rows)==324
            delay=np.where(rows.joint.to_numpy(bool)&np.isfinite(rows.diagnosis_delay_s),rows.diagnosis_delay_s,np.inf)
            ax.plot(grid,np.mean(delay[:,None]<=grid[None,:],axis=0),label=name,color=color,ls=style,lw=1.4)
            audit.append(dict(method=method,family=family,denominator=len(rows),joint_eventual=int(rows.joint.sum()),timely=int(rows.timely.sum())))
        ax.set_xlim(0,6);ax.set_ylim(0,1.03);ax.set_xlabel('Time since physical ON (s)')
        ax.set_title(family.title(),loc='left');ax.grid(alpha=.14)
    axes[0].set_ylabel('Fraction with correct family and source')
    axes[1].legend(frameon=False,fontsize=7,loc='lower right')
    for extension in ('pdf','png'):fig.savefig(ROOT/f'figures/generated/diagnosis_delay_distribution.{extension}',dpi=190)
    plt.close(fig)
    report={'sources':{name:hashlib.sha256((C01/name).read_bytes()).hexdigest() for name in ['EVENTS.csv','RECORDS.csv','PAIRED_INTERVALS.csv']},
            'plot_scope':'Posthoc descriptive CDF of eventual correct diagnosis delay, normalized by every event. Not a new primary endpoint or before-OFF probability.',
            'groups':audit,'single_state_control_verified':True,'monitored_rate_rows':len(corrected[corrected.metric=='extras_per_event_hour']),
            'new_test_predictions_or_thresholds':False,'event_image_changed':False}
    (ROOT/'generated/scientific_revision_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('REVISION_ARTIFACTS_VERIFIED')


if __name__=='__main__':main()
