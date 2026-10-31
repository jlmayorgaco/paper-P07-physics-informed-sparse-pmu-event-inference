"""Executable evidence -> a small set of figures that explain the argument."""
from pathlib import Path
import hashlib,json,re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1];DATA=ROOT/'generated/frozen/narrative_case_20261030';OUT=ROOT/'figures/generated';TAB=ROOT/'tables/generated'
BLUE='#0072b2';GREEN='#009e73';ORANGE='#d55e00';GRAY='#777777'
def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight');fig.savefig(OUT/(name+'.png'),dpi=190,bbox_inches='tight');plt.close(fig)
def main():
    manifest=json.loads((DATA/'MANIFEST.json').read_text())
    for f in manifest['files']:assert hashlib.sha256((DATA/f['path']).read_bytes()).hexdigest()==f['sha256'],f['path']
    plt.rcParams.update({'font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    assets=json.loads((DATA/'assets.json').read_text());b=pd.read_csv(DATA/'branch.csv');pmus=[2,5,6,10,19,22,29,39]
    text=(ROOT/'figures/ieee39_pmu_topology.tex').read_text();pos={int(i):(float(x),float(y)) for i,x,y in re.findall(r'\\coordinate \(b(\d+)c\) at \(([-\d.]+),([-\d.]+)\)',text)};assert len(pos)==39 and len(b)==46
    fig,ax=plt.subplots(figsize=(7.1,3.9),layout='constrained');linepairs={frozenset([a['i'],a['j']]) for a in assets if a['family']=='line'};loads={a['bus'] for a in assets if a['family']=='load'}
    for r in b.itertuples():
        i,j=int(r.src_bus),int(r.dst_bus);active=frozenset([i,j]) in linepairs;ax.plot([pos[i][0],pos[j][0]],[pos[i][1],pos[j][1]],color=ORANGE if active else '#bbbbbb',lw=2.3 if active else .7,zorder=1)
    for i,(x,y) in pos.items():
        ax.scatter(x,y,s=180 if i in pmus else 115,marker='s' if i in loads else 'o',facecolor='#d8edf8' if i in pmus else '#fff0dd' if i in loads else 'white',edgecolor=BLUE if i in pmus else ORANGE if i in loads else '#666',linewidth=1.6 if i in pmus else .8,zorder=3);ax.text(x,y,str(i),ha='center',va='center',fontsize=6.4,zorder=4)
    ax.set_axis_off();ax.legend(handles=[Line2D([],[],marker='o',color=BLUE,ls='',markerfacecolor='#d8edf8',label='8 measured buses'),Line2D([],[],marker='s',color=ORANGE,ls='',label='9 load candidates'),Line2D([],[],color=ORANGE,lw=2.3,label='9 line candidates')],loc='upper left',ncol=3,fontsize=8,frameon=False,bbox_to_anchor=(0,1.1));save(fig,'narrative_topology')
    source={}
    for p in (DATA/'evaluation').glob('*.json'):
        e=json.loads(p.read_text());rid=e['record']['id'];source[e['case']['condition']]=(rid,e['case'])
    rid,c=source['MATCH']
    with np.load(DATA/'observed'/(rid+'.npz')) as z:obs={k:z[k].copy() for k in z.files}
    fig,axes=plt.subplots(4,2,figsize=(7.1,5.3),sharex='col',layout='constrained');colors=plt.cm.tab10(np.linspace(0,1,8))
    for col,family in enumerate(['load','line']):
        e=next(e for e in c['events'] if e['family']==family);t=obs['time_s'];window=(t>=e['onset_s']-.7)&(t<=e['off_s']+1.4);baseline=(t>=e['onset_s']-.6)&(t<e['onset_s']-.1)
        for row,(field,ylabel,scale) in enumerate([('voltage_magnitude',r'$\Delta |V|$ (%)',100),('current_magnitude',r'$\Delta |I|$ (%)',100),('frequency',r'$\Delta f$ (mHz)',1000),('rocof',r'ROCOF (Hz/s)',1)]):
            y=obs[field].copy();center=np.nanmedian(y[baseline],axis=0)
            if row<2:y=(y/center-1)*scale
            elif row==2:y=(y-center)*scale
            ax=axes[row,col]
            for j in range(8):ax.plot(t[window]-e['onset_s'],y[window,j],color=colors[j],lw=.7,alpha=.9)
            ax.axvspan(0,e['off_s']-e['onset_s'],color='#cccccc',alpha=.24);ax.axvline(0,color='#555',ls=':',lw=.8);ax.axvline(e['off_s']-e['onset_s'],color='#555',ls=':',lw=.8);ax.grid(alpha=.12);ax.set_ylabel(ylabel)
        axes[0,col].set_title(f"{family.title()} at {e['source']} (H04 development)");axes[3,col].set_xlabel('Time from physical ON (s)')
    fig.legend([Line2D([],[],color=colors[j]) for j in range(8)],[f'PMU {p}' for p in pmus],ncol=8,loc='outside upper center',frameon=False,fontsize=7);save(fig,'narrative_signals')
    fig,axes=plt.subplots(4,1,figsize=(7.1,7.7),layout='constrained',gridspec_kw={'height_ratios':[.5,2.,2.,1.1]});ax=axes[0]
    for k,e in enumerate(c['events']):
        ax.broken_barh([(e['onset_s'],e['off_s']-e['onset_s'])],(0,.7),facecolors=BLUE if e['family']=='load' else ORANGE);ax.text(e['onset_s'],.8,e['source'].replace('LINE','L'),fontsize=7,rotation=30)
    ax.set_ylim(-.1,1.5);ax.set_yticks([]);ax.set_title('Physical interventions: evaluation truth only');ax.set_xlim(12,65)
    states={}
    for ax,condition in zip(axes[1:3],['MATCH','OUT_SUPPORT']):
        rr,cc=source[condition]
        with np.load(DATA/'prediction'/(rr+'_compact.npz')) as z:a={k:z[k].copy() for k in z.files}
        states[condition]=a;mass=np.nan_to_num(a['M']);ix=(a['time_s']>=12)&(a['time_s']<=65);im=ax.imshow(mass[ix].T,aspect='auto',origin='lower',extent=[a['time_s'][ix][0],a['time_s'][ix][-1],-.5,17.5],cmap='Blues',vmin=0,vmax=1,interpolation='nearest');ax.set_yticks(range(18),[v['id'].replace('LINE','L') for v in assets],fontsize=6.5);ax.set_title('Active source mass M: '+condition.replace('_',' '),fontsize=9)
        for e in cc['events']:ax.axvline(e['off_s'],color=ORANGE,ls=':',lw=.6,alpha=.8)
    fig.colorbar(im,ax=list(axes[1:3]),shrink=.7,label='Approximate active mass')
    a=states['OUT_SUPPORT'];j=next(i for i,v in enumerate(assets) if v['id']=='BUS31');t=a['time_s'];d1=np.cumsum(np.nan_to_num(a['delta_M_conditional'][:,j]));d2=np.cumsum(np.nan_to_num(a['delta_M_parameter'][:,j]));err=float(np.max(abs(d1+d2-np.nan_to_num(a['M'][:,j]))));assert err<1e-8,err
    ix=(t>=34)&(t<=44);ax=axes[3];origin=np.flatnonzero(ix)[0];ax.plot(t[ix],a['M'][ix,j]-a['M'][origin,j],color='black',label='M BUS31 change');ax.plot(t[ix],d1[ix]-d1[origin],color=BLUE,ls='--',label='Cumulative conditional evidence');ax.plot(t[ix],d2[ix]-d2[origin],color=ORANGE,ls=':',label='Cumulative model reweighting');event=next(e for e in source['OUT_SUPPORT'][1]['events'] if e['source']=='BUS31');ax.axvspan(event['onset_s'],event['off_s'],color=BLUE,alpha=.1)
    meta=json.loads((DATA/'prediction'/(source['OUT_SUPPORT'][0]+'.json')).read_text());diagnosis=next(e for e in meta['events'] if e['kind']=='diagnosis' and e['source']=='BUS31');ax.axvline(diagnosis['emitted_s'],color=ORANGE,lw=1);ax.set_title('A visible failure: BUS31 diagnosis is late under out-of-bank R/X');ax.set_xlabel('Time (s)');ax.set_ylabel('Mass / increment sum');ax.legend(loc='upper left',fontsize=6.4,ncol=1);ax.grid(alpha=.15);save(fig,'narrative_rolling')
    h=ROOT/'generated/frozen/continuous_20261029/H04';ed=pd.read_csv(h/'EVENTS.csv');sd=pd.read_csv(h/'SUMMARY.csv');arms=['R11','R11_NOMINAL','ET_REFERENCE','ET_CANDIDATE','R12'];names=['Physical bank (5 models)','Physical bank (nominal)','ExtraTrees reference','ExtraTrees short','Onset-witness ablation'];rows=[]
    for arm,name in zip(arms,names):
        e=ed[ed.method==arm];s=sd[sd.method==arm];v=dict(method=arm,name=name,detected=int(e.detected.sum()),joint=int(e.joint_top1.sum()),timely=int(e.diagnosis_before_off.sum()),events=len(e),load_timely=int(e[e.family=='load'].diagnosis_before_off.sum()),load_total=int((e.family=='load').sum()),line_timely=int(e[e.family=='line'].diagnosis_before_off.sum()),line_total=int((e.family=='line').sum()),extras=int(s.extras.sum()),normal_fa=int(s.normal_FA.sum()),normal_s=float(s.normal_available_s.sum()));rows.append(v)
    df=pd.DataFrame(rows);df.to_csv(TAB/'narrative_results.csv',index=False)
    macros=[]
    for v,prefix in zip(rows,['NarMix','NarNom','NarET','NarETS','NarWitness']):
        for key,suffix in [('detected','Detected'),('joint','Joint'),('timely','Timely'),('events','Events'),('load_timely','LoadTimely'),('load_total','LoadTotal'),('line_timely','LineTimely'),('line_total','LineTotal'),('extras','Extras')]:macros.append('\\newcommand{\\'+prefix+suffix+'}{'+str(v[key])+'}')
    (ROOT/'generated/narrative_macros.tex').write_text('\n'.join(macros)+'\n')
    table=[r'\begin{table}[t]\centering\small',r'\caption{What the causal component actually resolves in H04 development. Load and line columns require the correct family and source emitted before OFF. The 54 realizations repeat 18 interventions across three R/X conditions; they are not 54 independent trials. Normal exposure is only 204 s per method.}',r'\label{tab:narrative-results}',r'\setlength{\tabcolsep}{3pt}\begin{tabular}{lrrrr}\toprule',r'Method & \shortstack{Load\\timely} & \shortstack{Line\\timely} & Extras & \shortstack{Normal\\alarms}\\\midrule']
    for v,name in zip(rows,['Physical (5 models)','Physical nominal','ExtraTrees ref.','ET short','Onset witness']):table.append(f"{name} & {v['load_timely']}/{v['load_total']} & {v['line_timely']}/{v['line_total']} & {v['extras']} & {v['normal_fa']}"+r'\\')
    table += [r'\bottomrule\end{tabular}\end{table}'];(TAB/'narrative_results.tex').write_text('\n'.join(table)+'\n')
    fig,ax=plt.subplots(figsize=(3.4,2.8),layout='constrained');markers=['o','s','^','v','X'];cs=[BLUE,GREEN,GRAY,'#aaaaaa',ORANGE]
    for i,v in enumerate(rows):
        ax.scatter(v['extras'],v['timely'],s=65,marker=markers[i],color=cs[i]);offset=(8,4) if i!=3 else (8,-13);ax.annotate(f"{['5-model','Nominal','ExtraTrees','ET short','Onset witness'][i]}\n{v['timely']}/{v['events']}",(v['extras'],v['timely']),xytext=offset,textcoords='offset points',fontsize=6.2)
    ax.set_xlim(-.5,12);ax.set_ylim(23,58);ax.set_xlabel('Unmatched event-stream alarms');ax.set_ylabel('Timely family + source / 54');ax.grid(alpha=.15);save(fig,'narrative_tradeoff')
    a=pd.read_csv(ROOT/'generated/frozen/global137_support_summary.csv').set_index('regime');k=pd.read_csv(ROOT/'generated/frozen/global137_cardinality_summary.csv').set_index('regime');regimes=['WEAK_WEAK','WEAK_STRONG','MODERATE','FINITE'];x=np.arange(4);fig,ax=plt.subplots(figsize=(7.1,2.7),layout='constrained');ax.bar(x-.17,[k.loc[r,'accuracy']*100 for r in regimes],width=.34,color=BLUE,label='Correct number of sources');ax.bar(x+.17,[a.loc[r,'top1']*100 for r in regimes],width=.34,color=ORANGE,label='Exact source support');ax.set_xticks(x,['Weak + weak','Weak + strong','Moderate pair','Finite pair']);ax.set_ylim(0,115);ax.set_ylabel('Correct decisions (%)');ax.legend(frameon=False,ncol=2,loc='upper left');ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
    for i,r in enumerate(regimes):ax.text(i+.17,a.loc[r,'top1']*100+2,f"{a.loc[r,'top1']*100:.1f}",ha='center',fontsize=8)
    save(fig,'narrative_resolution')
    (ROOT/'generated/narrative_audit.json').write_text(json.dumps(dict(case='H04 H002 paired MATCH/OUT',C01_outcomes_used=False,import_hashes_verified=True,delta_identity_max_error=err,rows=rows,figures=['narrative_topology','narrative_signals','narrative_rolling','narrative_tradeoff','narrative_resolution']),indent=2));print(df.to_string(index=False))
if __name__=='__main__':main()
