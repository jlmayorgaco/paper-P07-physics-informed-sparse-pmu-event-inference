"""Authorized 3x3 successor: preserve legacy data and all protected assets."""
from pathlib import Path
import hashlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'generated/event_taxonomy_grid_20261113'
OUT=ROOT/'figures/generated'
LEGACY=ROOT/'generated/frozen/legacy_raw_event_figure_values.csv'
PALETTE=['#17608b','#c26821','#47866b']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    protected=json.loads((ROOT/'figures/frozen/PROTECTED_FIGURES.json').read_text())['files']
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    provenance=json.loads((DATA/'PROVENANCE.json').read_text())
    assert all(sha(DATA/p)==h for p,h in provenance['files'].items())
    traces=pd.read_csv(LEGACY)
    manifest=json.loads((ROOT/'generated/frozen/legacy_figure_trace_manifest.json').read_text())
    ends={int(r['event']):r['last_labeled_time_bus2_s']-r['onset_time_bus2_s'] for r in manifest}
    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
                        'font.size':7.5,'axes.labelsize':7.3,'xtick.labelsize':7,'ytick.labelsize':7,
                        'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,axs=plt.subplots(3,3,figsize=(7.16,6.2))
    fig.subplots_adjust(left=.082,right=.958,bottom=.075,top=.89,wspace=.61,hspace=.88)
    titles=['0  Normal operation','1  Fault at bus 39','2  Line outage 23–24',
            '3  Generation at bus 2','4  Load change at bus 7','5  Missing PMU data',
            '6  Missing + physical','7  Corrupted voltage','8  Unknown event']
    for ax,title in zip(axs.flat,titles):
        ax.set_title(title,loc='left',fontsize=8.1,pad=27)
        ax.grid(axis='y',color='.88',lw=.4);ax.tick_params(pad=2,length=3)
    specs={
      1:((-.25,1.5),[(39,'BUS39_VA_MAG','PMU 39'),(5,'BUS5_VA_MAG','PMU 5'),(19,'BUS19_VA_MAG','PMU 19')],r'$|V_A|/V_{A,\mathrm{pre}}$'),
      2:((-1,6),[(22,'BUS22_IA_MAG','PMU 22'),(39,'BUS39_IA_MAG','PMU 39'),(2,'BUS2_IA_MAG','PMU 2')],r'$|I_A|/I_{A,\mathrm{pre}}$'),
      3:((-3,35),[(2,'BUS2_Freq','PMU 2'),(39,'BUS39_Freq','PMU 39')],r'$f-f_{\mathrm{pre}}$ (mHz)'),
      4:((-3,40),[(6,'BUS6_IA_MAG','PMU 6'),(10,'BUS10_IA_MAG','PMU 10'),(5,'BUS5_IA_MAG','PMU 5')],r'$|I_A|/I_{A,\mathrm{pre}}$'),
      5:((-4,32),[(29,'DATA_PRESENT','PMU 29'),(22,'DATA_PRESENT','PMU 22')],'Data available'),
      7:((-.5,2),[(2,'BUS2_VC_MAG','Phase C'),(2,'BUS2_VA_MAG','Phase A'),(2,'BUS2_VB_MAG','Phase B')],r'$|V_\phi|/V_{\phi,\mathrm{pre}}$')}
    checked=[]
    def legend(ax,n):
        ax.legend(loc='lower left',bbox_to_anchor=(-.035,1.01),ncol=n,frameon=False,
                  fontsize=6.3,handlelength=1.05,columnspacing=.55,handletextpad=.3,borderaxespad=0)
    for event,(limits,channels,ylabel) in specs.items():
        ax=axs.flat[event];ax.axvline(0,color='.4',ls=':',lw=.8)
        if event in [5,7]:ax.axvspan(0,ends[event],color='#e7e7e7',alpha=.75,zorder=0)
        for k,(bus,channel,label) in enumerate(channels):
            q=traces[(traces.event==event)&(traces.bus==bus)&(traces.channel==channel)].sort_values('sample_index')
            x,y=q.time_from_label_s.to_numpy(),q.plotted_value.to_numpy()
            if channel=='DATA_PRESENT':line,=ax.step(x,y,where='post',color=PALETTE[k],lw=1,ls='-' if k==0 else '--',label=label)
            else:line,=ax.plot(x,y,color=PALETTE[k],lw=.75 if event in [1,2,7] else .55,label=label)
            assert np.array_equal(line.get_xdata(),x) and np.array_equal(line.get_ydata(),y)
            checked.append({'event':event,'bus':bus,'channel':channel,'points':len(q),'plotted_values_unchanged':True})
        ax.set_xlim(limits);ax.set_ylabel(ylabel,labelpad=1.5);ax.set_xlabel(r'$t-t_0$ (s)',labelpad=2);legend(ax,len(channels))
    ax=axs.flat[1];ax.set_ylim(.15,1.2);ax.set_yticks([.25,.5,.75,1]);ax.set_xticks([0,.5,1,1.5])
    q=traces[(traces.event==1)&(traces.bus==39)];v=q.loc[q.plotted_value.idxmin()]
    ax.annotate(f'{v.plotted_value:.3f} of baseline',xy=(v.time_from_label_s,v.plotted_value),xytext=(.31,.42),
                fontsize=6.5,arrowprops={'arrowstyle':'->','lw':.6,'color':'.35'})
    ax=axs.flat[2];ax.set_ylim(.65,1.84);ax.set_yticks([.7,1,1.4,1.8]);ax.set_xticks([0,2,4,6])
    ax=axs.flat[3];ax.set_ylim(-255,55);ax.set_yticks([-200,-100,0]);ax.set_xticks([0,10,20,30])
    ax=axs.flat[4];ax.set_ylim(.94,1.175);ax.set_yticks([.95,1,1.1,1.15]);ax.set_xticks([0,10,20,30,40])
    ax=axs.flat[5];ax.set_ylim(-.12,1.15);ax.set_yticks([0,1],['No','Yes']);ax.set_xticks([0,10,20,30])
    count=next(r['missing_frames'] for r in manifest if int(r['event'])==5)
    ax.text(.5,.35,f'{count} frames absent',transform=ax.transAxes,ha='center',fontsize=6.5,
            bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':1})
    ax=axs.flat[7];ax.set_ylim(.98,1.13);ax.set_yticks([1,1.05,1.1]);ax.set_xticks([0,.5,1,1.5,2]);ax.text(.55,.8,'Phase C only',transform=ax.transAxes,fontsize=6.5)
    # Label-0 interval, independently checked at all eight PMUs.
    d=pd.read_csv(DATA/'normal_trace.csv');ax=axs.flat[0]
    for k,b in enumerate([2,39]):ax.plot(d.time_s,d[f'pmu{b}_voltage_ratio'],color=PALETTE[k],lw=.6,label=f'PMU {b}')
    ax.set_xlim(0,10);ax.set_ylim(.98,1.02);ax.set_yticks([.98,1,1.02]);ax.set_ylabel(r'$|V_A|/\mathrm{median}(|V_A|)$',labelpad=1.5)
    ax.set_xlabel('Time in normal interval (s)',labelpad=2);legend(ax,2)
    # Full observed loss pulse: grey physical trace, orange binary missing flag.
    d=pd.read_csv(DATA/'composite_trace.csv');ax=axs.flat[6]
    physical,=ax.plot(d.relative_time_s,d.pmu2_frequency_change_mHz,color='#9b9b9b',lw=.6,label='PMU 2: frequency')
    ax.axvline(0,color='.55',ls=':',lw=.7);ax.set_xlim(-45,35);ax.set_xticks([-40,0,30]);ax.set_ylim(-255,55);ax.set_yticks([-200,-100,0])
    ax.set_ylabel(r'$f-f_{\mathrm{pre}}$ (mHz)',labelpad=1.5);ax.set_xlabel(r'Time from generation onset (s)',labelpad=2)
    flag=ax.twinx();flag.set_ylim(-.12,1.15);flag.set_yticks([0,1],['No','Yes']);flag.tick_params(labelsize=6.7,pad=1,length=2)
    flag.set_ylabel('Missing PMU 29',fontsize=6.7,labelpad=2,color=PALETTE[1]);flag.spines['right'].set_visible(True);flag.spines['right'].set_color(PALETTE[1])
    pulse,=flag.step(d.relative_time_s,d.pmu29_missing,where='post',color=PALETTE[1],lw=1.2,label='Missing: 1 / present: 0')
    ax.legend([physical,pulse],['Physical response','Missing-data pulse'],loc='lower left',bbox_to_anchor=(-.035,1.01),
              ncol=1,frameon=False,fontsize=6.3,handlelength=1.5,borderaxespad=0,labelspacing=.15)
    # User correction: clock low/high must coincide with No/Yes (0/1),
    # on availability in panel 5 and missing-data indicator in panel 6.
    clock_levels=[]
    for event in (5,6):
        ax=axs.flat[event];lo,hi=ax.get_xlim()
        clock=ax if event==5 else flag
        t=np.arange(lo,hi+1/30,1/30)
        levels=np.where(np.mod(t-lo,2.0)<1.0,1.0,0.0)
        line,=clock.step(t,levels,where='post',color='#9AA1A9',lw=.65,alpha=.5,zorder=.8)
        assert set(line.get_ydata())=={0.,1.}
        clock_levels.append({'panel':event,'low':0,'high':1,'axis':'availability' if event==5 else 'missing'})
        ax.text(.02,.96,'Clock (illustrative)',transform=ax.transAxes,fontsize=6.0,color='#6B7280')
    # Taxonomy definition, never represented as measured data or a tested output.
    ax=axs.flat[8];ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    for y,h,label,fc in [(.69,.24,'Abnormal observation','#f0f5f7'),(.16,.3,'No clear match\nto classes 1–7','#faf3ec')]:
        ax.add_patch(FancyBboxPatch((.03,y),.94,h,boxstyle='round,pad=.01,rounding_size=.025',edgecolor='#b8c6cd',facecolor=fc,lw=.6))
        ax.text(.5,y+h/2,label,ha='center',va='center',fontsize=7.5)
    ax.annotate('',xy=(.5,.48),xytext=(.5,.68),arrowprops={'arrowstyle':'->','color':'#23343F','lw':.8})
    ax.text(.5,-.14,'Definition only; no measured trace',ha='center',fontsize=6.5)
    pdf=OUT/'event_taxonomy_grid.pdf';fig.savefig(pdf);fig.savefig(OUT/'event_taxonomy_grid.png',dpi=280);plt.close(fig)
    assert all(sha(ROOT/p)==h for p,h in protected.items())
    audit={'authorization':'User requested equal 3x3 panels including normal and explicit missing pulse, 2026-11-13',
           'legacy_trace_sha256':sha(LEGACY),'legacy_curves':checked,'panels':list(range(9)),
           'normal_and_composite_files':provenance['files'],'protected_hashes_verified':len(protected),
           'display_change':'Illustrative clock train spans exact No/Yes levels in panels 5 and 6; measured signals unchanged.',
           'clock_levels':clock_levels,
           'illustrative_clock_panels':[5,6], 'illustrative_clock_period_s':2.0,
           'pdf_sha256':sha(pdf)}
    (DATA/'BUILD_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(f'Built equal 3x3 grid; {len(checked)} legacy curves unchanged; all protected hashes preserved.')

if __name__=='__main__':main()
