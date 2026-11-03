"""Editorial views of distinct, already executed experiments; no fitting or replay."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
F = ROOT / 'generated/frozen'
OUT = ROOT / 'figures/generated'
HIST = F / 'historical_submission_comparison_20261102'
BLUE, TEAL, ORANGE = '#006a92', '#008f79', '#c46b22'

def main():
    names = ['e04a_b0_b1_b2_summary.csv', 'legacy_feature_group_ablation_summary.csv',
             'likelihood120_physical_validation.csv', 'global137_support_summary.csv']
    manifest = pd.read_csv(F / 'SOURCE_MANIFEST.csv').set_index('imported_name')
    checks = []
    for name in names:
        data = (F / name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == manifest.loc[name, 'sha256'], name
        checks.append(dict(path=f'generated/frozen/{name}', sha256=digest))
    for item in json.loads((HIST / 'MANIFEST.json').read_text())['files']:
        assert hashlib.sha256((HIST / item['path']).read_bytes()).hexdigest() == item['sha256']
        checks.append(dict(path=str((HIST / item['path']).relative_to(ROOT)), sha256=item['sha256']))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,
                         'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    state = pd.read_csv(F / names[0]).set_index('method')
    feat = pd.read_csv(F / names[1])
    feat = feat[feat.split == 'test'].groupby('feature_variant').physical_top1.agg(['mean','min','max','count'])
    response = pd.read_csv(F / names[2])
    response = response[response['T'] == 120]
    grouped = response.groupby('model').whitened_norm.agg(['median','count'])
    assert (grouped['count'] == 32).all()
    fig, axes = plt.subplots(1,3,figsize=(7.1,2.4),layout='constrained')
    vals = state.loc[['B0_NOMINAL','B1_SNAPSHOT_WLS','B2_KALMAN'],'TVE_percent'].to_numpy()
    axes[0].bar(range(3),vals,color=[ORANGE,BLUE,TEAL],width=.6)
    axes[0].set_yscale('log');axes[0].set_ylim(.005,1)
    axes[0].set_xticks(range(3),['Nominal','WLS','Kalman'])
    axes[0].set_ylabel('Hidden-voltage relative error (%)')
    axes[0].set_title('(a) Reconstruct unmeasured buses\n100 nominal trajectories')
    for i,v in enumerate(vals): axes[0].text(i,v*1.1,f'{v:.4f}',ha='center',fontsize=7)
    ids=['base_136','plus_graph_temporal','all_frozen_derived']
    means=feat.loc[ids,'mean'].to_numpy()*100
    axes[1].bar(range(3),means,color=[ORANGE,BLUE,TEAL],width=.6)
    axes[1].errorbar(range(3),means,yerr=np.vstack([means-feat.loc[ids,'min']*100,
                      feat.loc[ids,'max']*100-means]),fmt='none',ecolor='#263b49',capsize=3,lw=.8)
    axes[1].set_ylim(0,75);axes[1].set_xticks(range(3),['Base\n136','+ graph\n184','All\n448'])
    axes[1].set_ylabel('Physical-source Top-1 (%)')
    axes[1].set_title('(b) Enrich learned features\nHistorical typed ExtraTrees')
    for i,v in enumerate(means): axes[1].text(i,feat.loc[ids[i],'max']*100+2,f'{v:.1f}',ha='center',fontsize=7)
    rv=grouped.loc[['D','D_Q','D_Q_Qij'],'median'].to_numpy()
    axes[2].bar(range(3),rv,color=[BLUE,ORANGE,TEAL],width=.6)
    axes[2].set_yscale('log');axes[2].set_ylim(.001,2)
    axes[2].set_xticks(range(3),['$D$','$D+Q_i$','$D+Q_i+Q_{ij}$'])
    axes[2].set_ylabel('Median whitened response error')
    axes[2].set_title('(c) Include source interactions\n32 archived two-load responses')
    for i,v in enumerate(rv): axes[2].text(i,v*1.15,f'{v:.3g}',ha='center',fontsize=7)
    for ax in axes: ax.grid(axis='y',color='#e8e8e8',lw=.5);ax.set_axisbelow(True)
    for ext in ['pdf','png']:fig.savefig(OUT / f'evidence_bridge.{ext}',dpi=210,bbox_inches='tight',pad_inches=.04)
    plt.close(fig)

    summary=pd.read_csv(HIST/'SUMMARY.csv')
    summary=summary[(summary.unit=='windows') & (summary.split=='all')].set_index('method')
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.35),layout='constrained')
    for ax,method,title in zip(axes,['Submitted_ExtraTrees','M02_V3.1'],['Submitted ExtraTrees','Earlier physical estimator']):
        raw=pd.read_csv(HIST / f'confusion_windows_{method}.csv',index_col=0)
        raw.columns=raw.columns.astype(int)
        assert raw.to_numpy().sum()==summary.loc[method,'n']==124
        assert np.trace(raw.to_numpy())==summary.loc[method,'classification_correct']
        m=np.column_stack([raw.loc[[0,2,4],c].to_numpy() for c in [0,2,4]])
        other=raw.loc[[0,2,4]].drop(columns=[0,2,4]).sum(axis=1).to_numpy()
        m=np.column_stack([m,other]);assert np.array_equal(m.sum(axis=1),[28,48,48])
        pct=100*m/m.sum(axis=1)[:,None]
        ax.imshow(pct,vmin=0,vmax=100,cmap='Blues',aspect='auto')
        for i in range(3):
            for j in range(4):ax.text(j,i,f'{m[i,j]}\n{pct[i,j]:.0f}%',ha='center',va='center',fontsize=8,color='white' if pct[i,j]>55 else '#263b49')
        ax.set_xticks(range(4),['Normal','Line','Load','Other'])
        ax.set_yticks(range(3),['Normal (28)','Line (48)','Load (48)'])
        ax.set_xlabel('Predicted family');ax.set_title(title)
    axes[0].set_ylabel('True family')
    for ext in ['pdf','png']:fig.savefig(OUT / f'historical_transfer_confusion.{ext}',dpi=210,bbox_inches='tight',pad_inches=.04)
    plt.close(fig)
    macros={'BridgeNominalError':f'{vals[0]:.4f}','BridgeWLSError':f'{vals[1]:.5f}',
            'BridgeKalmanError':f'{vals[2]:.5f}','BridgeBaseTop':f'{means[0]:.1f}',
            'BridgeGraphTop':f'{means[1]:.1f}','BridgeFullTop':f'{means[2]:.1f}',
            'BridgeDError':f'{rv[0]:.3g}','BridgeQError':f'{rv[1]:.3g}','BridgeMixedError':f'{rv[2]:.3g}'}
    macros.update({name:str(int(summary.loc[method,column])) for name,method,column in [
        ('HistoryWindows','Submitted_ExtraTrees','n'),('HistoryEvents','Submitted_ExtraTrees','events'),
        ('HistoryNormals','Submitted_ExtraTrees','normals'),('HistoryETDetected','Submitted_ExtraTrees','detected_events'),
        ('HistoryETFamily','Submitted_ExtraTrees','event_family_correct'),('HistoryETJoint','Submitted_ExtraTrees','joint_top1'),
        ('HistoryPhysicalJoint','M02_V3.1','joint_top1')]})
    (ROOT/'generated/evidence_bridge_macros.tex').write_text('% Generated from verified archived CSVs.\n'+''.join('\\newcommand{\\'+k+'}{'+v+'}\n' for k,v in macros.items()))
    g=pd.read_csv(F/names[3]).set_index('regime')
    lines=[r'\begin{tabular}{@{}lrr@{}}\toprule',r'Amplitude regime & Replays & Joint support Top-1 \\\midrule']
    for key,label in [('FINITE','Finite / finite'),('MODERATE','Moderate / moderate'),('WEAK_STRONG','Weak / strong'),('WEAK_WEAK','Weak / weak')]:
        lines.append(f'{label} & {int(g.loc[key,"n"]):,} & {100*g.loc[key,"top1"]:.2f}'+r'\% \\')
    lines.append(r'\bottomrule\end{tabular}')
    (ROOT/'tables/generated/archived_support_bridge.tex').write_text('\n'.join(lines)+'\n')
    (ROOT/'generated/EVIDENCE_BRIDGE_PROVENANCE.json').write_text(json.dumps(dict(inputs=checks,reran_methods=False,changed_C01=False,interpretation='Distinct component/development experiments, not pooled or end-to-end ablations'),indent=2)+'\n')
    print('Verified',len(checks),'inputs; generated two evidence figures, macros and support table.')

if __name__ == '__main__':main()
