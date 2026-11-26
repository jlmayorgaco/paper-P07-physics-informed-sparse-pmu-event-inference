"""Hash-checked evidence -> macros, tables and scientific figure. No hand-transcribed scores."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'generated/frozen/continuous_20261029'
def main():
    for f in json.loads((DATA/'MANIFEST.json').read_text())['files']:
        assert hashlib.sha256((DATA/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
    h3=pd.read_csv(DATA/'H03/SUMMARY.csv');h4=pd.read_csv(DATA/'H04/SUMMARY.csv');events=pd.read_csv(DATA/'H04/EVENTS.csv')
    keep=['R11','R11_NOMINAL','R12','ET_REFERENCE','ET_CANDIDATE'];names={'R11':'R11 mixture','R11_NOMINAL':'R11 nominal','R12':'Admission ablation','ET_REFERENCE':'ExtraTrees reference','ET_CANDIDATE':'ExtraTrees short'}
    rows=[]
    for m in keep:
        d=h4[h4.method==m];out=d[d.condition=='OUT_SUPPORT'].iloc[0];assert len(d)==3
        rows.append(dict(method=m,label=names[m],timely=int(d.before_off.sum()),total=int(d.events.sum()),extras=int(d.extras.sum()),false_restorations=int(d.false_restorations.sum()),out_timely=int(out.before_off),out_total=int(out.events),out_extras=int(out.extras),out_f1=float(out.detection_f1),out_bus31_timely=int(events[(events.method==m)&(events.condition=='OUT_SUPPORT')&(events.source=='BUS31')].diagnosis_before_off.sum())))
    df=pd.DataFrame(rows);(ROOT/'tables/generated').mkdir(parents=True,exist_ok=True);df.to_csv(ROOT/'tables/generated/continuous_h04.csv',index=False)
    table=[r'\begin{table}[t]',r'\centering\small',r'\caption{Executed continuous-stream development evidence (H04). Timely means correct family/source emitted before physical restoration; extras are unmatched alarms. OUT denotes out-of-bank R/X; F1 is report-level detection F1. These are paired realizations of 18 events from three event parents, not 54 independent events.}',r'\label{tab:continuous-h04}',r'\resizebox{\columnwidth}{!}{%',r'\begin{tabular}{lrrrr}',r'\toprule',r'Method & Timely & Extras & OUT timely & OUT F1\\',r'\midrule']
    for r in rows:table.append(f"{r['label']} & {r['timely']}/{r['total']} & {r['extras']} & {r['out_timely']}/{r['out_total']} & {r['out_f1']:.3f}"+r'\\')
    table += [r'\bottomrule',r'\end{tabular}}',r'\end{table}'];(ROOT/'tables/generated/continuous_h04.tex').write_text('\n'.join(table)+'\n')
    macros=[]
    for m,prefix in [('R11','ContMix'),('R11_NOMINAL','ContNom'),('R12','ContAdmission'),('ET_REFERENCE','ContET')]:
        r=next(r for r in rows if r['method']==m)
        for k,suffix in [('timely','Timely'),('total','Total'),('extras','Extras'),('out_timely','OutTimely'),('out_bus31_timely','BusTimely')]:macros.append('\\newcommand{\\'+prefix+suffix+'}{'+str(r[k])+'}')
    d=h3[h3.method=='R11'];macros += ['\\newcommand{\\ContPriorTimely}{'+str(int(d.before_off.sum()))+'}','\\newcommand{\\ContPriorExtras}{'+str(int(d.extras.sum()))+'}']
    matched=pd.read_csv(DATA/'C01/comparator/MATCHED_SUMMARY.csv');changed=matched[matched.source!='normal'];normal=matched[matched.source=='normal'].iloc[0]
    macros += ['\\newcommand{\\ChenMatchedCorrect}{'+str(int(changed.correct_after_change.sum()))+'}','\\newcommand{\\ChenMatchedTotal}{'+str(int(changed.trials.sum()))+'}','\\newcommand{\\ChenMatchedEarly}{'+str(int(changed.prechange_alarms.sum()))+'}','\\newcommand{\\ChenNormalExposure}{'+f'{int(normal.exposure):,}'+'}']
    (ROOT/'generated/continuous_macros.tex').write_text('\n'.join(macros)+'\n')
    plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.8),layout='constrained');colors=['#0072b2','#009e73','#d55e00','#777777','#aaaaaa'];labels=['R11\nmixture','R11\nnominal','Admission\nablation','ET\nreference','ET\nshort'];x=np.arange(5)
    for ax,col,title in zip(axes,['out_timely','out_extras'],['Correct family/source before OFF','Unmatched alarms']):
        values=df[col].to_numpy();ax.bar(x,values,color=colors,width=.7);ax.set_xticks(x,labels);ax.set_title(title);ax.set_ylabel('Events / 18' if col=='out_timely' else 'Alarms');ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
        for xx,v in zip(x,values):ax.text(xx,v+.3,str(v),ha='center',va='bottom',fontsize=9)
        ax.set_ylim(0,20 if col=='out_timely' else max(values)+2);ax.set_yticks([0,6,12,18] if col=='out_timely' else [0,2,4,6])
    fig.suptitle('Out-of-bank R/X: development evidence, paired H04 records',fontsize=10)
    folder=ROOT/'figures/generated';folder.mkdir(parents=True,exist_ok=True)
    fig.savefig(folder/'continuous_tradeoff.pdf');fig.savefig(folder/'continuous_tradeoff.png',dpi=200);plt.close(fig)
    summary=dict(status='GENERATED_FROM_VERIFIED_FROZEN_OUTPUTS',rows=rows,primary_paper_estimator_unchanged=True,confirmatory_C01_executed=False)
    (ROOT/'generated/continuous_evidence_audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(df.to_string(index=False))
if __name__=='__main__':main()
