"""Qualified archive figure and X01 implementation-audit artifacts.

Never uses unfinished C01 results. The protected event-types image is untouched.
"""
from pathlib import Path
import csv,hashlib,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from verify_protected_event_figure import verify

ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'generated/frozen'
X01=DATA/'shared_review_x01_20261030';FIG=ROOT/'figures/generated';TAB=ROOT/'tables/generated'
BLUE='#0072b2';ORANGE='#d55e00';GREEN='#009e73';GRAY='#737d83'

def save(fig,name):
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight')
    fig.savefig(FIG/(name+'.png'),dpi=200,bbox_inches='tight');plt.close(fig)

def main():
    verify();manifest=json.loads((X01/'MANIFEST.json').read_text())
    for f in manifest['files']:
        assert hashlib.sha256((X01/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
    proof_dir=DATA/'shared_review_x01_normalization_20261030'
    proof_manifest=json.loads((proof_dir/'MANIFEST.json').read_text())
    for f in proof_manifest['files']:
        assert hashlib.sha256((proof_dir/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
    proof=json.loads((proof_dir/'run/NORMALIZATION_ANALYTIC_CHECK.json').read_text())
    assert proof['passed'] and proof['supports']==136 and not proof['physical_replay']
    with (DATA/'SOURCE_MANIFEST.csv').open(encoding='utf-8-sig',newline='') as f:
        imported={r['imported_name']:r['sha256'] for r in csv.DictReader(f)}
    names=['global137_support_summary.csv','global137_cardinality_summary.csv']
    for name in names:assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==imported[name]
    s=pd.read_csv(DATA/names[0]).set_index('regime');c=pd.read_csv(DATA/names[1]).set_index('regime')
    regimes=['WEAK_WEAK','WEAK_STRONG','MODERATE','FINITE'];x=np.arange(4)
    plt.rcParams.update({'font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.1),layout='constrained')
    ax=axes[0];ax.bar(x-.17,[100*c.loc[g,'accuracy'] for g in regimes],width=.34,color=BLUE,label='Correct cardinality')
    ax.bar(x+.17,[100*s.loc[g,'top1'] for g in regimes],width=.34,color=ORANGE,label='Joint exact support')
    labels=['Weak + weak','Weak + strong','Moderate','Finite']
    ax.set_xticks(x,[label+'\n'+str(int(c.loc[g,'physical_trajectories']))+' parents' for label,g in zip(labels,regimes)],fontsize=6.8)
    ax.set_ylim(0,118);ax.set_ylabel('Correct decisions (%)');ax.set_title('(a) Frozen joint decisions',loc='left',fontsize=9)
    ax.legend(frameon=False,fontsize=6.8,loc='upper left');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    for k,g in enumerate(regimes):ax.text(k+.17,100*s.loc[g,'top1']+2,f"{100*s.loc[g,'top1']:.1f}",ha='center',fontsize=7)
    ax=axes[1];values=[100*s.loc[g,'top3'] for g in regimes]
    ax.plot(x,values,color=GREEN,marker='D',lw=1.5,label='Conditional pair Top-3')
    for k,value in enumerate(values):ax.annotate(f'{value:.1f}',(k,value),xytext=(0,7),textcoords='offset points',ha='center',fontsize=7)
    ax.set_xticks(x,labels,fontsize=6.8);ax.set_ylim(0,118);ax.set_ylabel('True pair within first three (%)')
    ax.set_title('(b) Pair ranking, K = 2 supplied',loc='left',fontsize=9);ax.grid(axis='y',alpha=.15)
    ax.legend(frameon=False,fontsize=6.8,loc='lower right')
    save(fig,'narrative_resolution')
    report=json.loads((X01/'run/RESULTS.json').read_text());norm=report['normalization']
    header=[r'\begin{table}[t]\centering\small',r'\caption{Uninformative-response control on the archived numerical functions. The isolated successor restores the declared prior. This is an algebra/code check, not a new physical-event test.}',r'\label{tab:review-normalization}',r'\begin{tabular}{lrrr}\toprule',r'Cardinality & Declared & Legacy & Successor\\\midrule']
    for k,(expected,old,new) in enumerate(zip(norm['declared_prior'],norm['legacy_null_masses'],norm['corrected_null_masses'])):
        header.append(f'$K={k}$ & {expected:.3f} & {old:.3f} & {new:.3f}'+r'\\')
    (TAB/'review_normalization.tex').write_text('\n'.join(header+[r'\bottomrule\end{tabular}\end{table}'])+'\n')
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.9),layout='constrained')
    kernel_labels=['Support-wise\nGram','Shared\nprojection','Batched\nGH31'];colors=[GRAY,BLUE,GREEN]
    ax=axes[0]
    for k,row in enumerate(report['timings']):
        ax.plot([k]*3,[row['p50_ms'],row['p95_ms'],row['p99_ms']],color=colors[k],lw=2)
        ax.scatter([k],[row['p50_ms']],marker='o',color=colors[k]);ax.scatter([k],[row['p99_ms']],marker='^',color=colors[k])
    ax.axhline(1000/30,color=ORANGE,ls=':',lw=1,label='30-fps period (reference)')
    ax.set_xticks(range(3),kernel_labels,fontsize=7);ax.set_ylabel('Kernel time (ms)');ax.set_title('(a) Synthetic kernel only: median to p99',loc='left',fontsize=9)
    ax.legend(frameon=False,fontsize=6.5);ax.grid(axis='y',alpha=.15)
    ax=axes[1];width=.24
    for offset,key,label,color in [(-width,'declared_prior','Declared prior',GRAY),(0,'legacy_null_masses','Legacy null control',ORANGE),(width,'corrected_null_masses','Corrected null control',GREEN)]:
        ax.bar(np.arange(3)+offset,norm[key],width=width,color=color,label=label)
    ax.set_xticks(range(3),['K = 0','K = 1','K = 2']);ax.set_ylim(0,.66);ax.set_ylabel('Cardinality mass')
    ax.set_title('(b) Same likelihood must recover the prior',loc='left',fontsize=9);ax.legend(frameon=False,fontsize=6.3);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    save(fig,'review_kernel_audit')
    audit=dict(source_review=manifest['source_review'],archived_inputs_sha256={n:imported[n] for n in names},legacy_results_changed=False,C01_outcomes_used=False,Top3_conditioned_on_two_sources=True,legacy_normalization_qualified=True,weak_transition_curve_excluded='Source repeats global Top-1 across severities',synthetic_not_physical_kernel_check=True,event_types_figure_unchanged=True)
    (ROOT/'generated/shared_review_evidence_audit.json').write_text(json.dumps(audit,indent=2)+'\n');verify()
    print('SHARED_REVIEW_EVIDENCE_GENERATED')

if __name__=='__main__':main()
