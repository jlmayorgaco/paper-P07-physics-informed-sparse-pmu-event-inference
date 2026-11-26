"""Compare fixed and bounded-profile channel separation from audited CSVs."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'experiments/channel_profile_20261112'


def main():
    report=json.loads((DATA/'summary.json').read_text())
    for name,expected in report['outputs'].items():
        if hashlib.sha256((DATA/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('Changed output: '+name)
    d=pd.read_csv(DATA/'nearest.csv')
    d=d[d.reports==30].set_index(['source','channels'])
    assets=json.loads((ROOT/'experiments/channel_information_20261112/r11_assets.json').read_text())
    plt.rcParams.update({'font.family':'STIXGeneral','font.size':8,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.5),sharex=True,sharey=True)
    palette={'load':'#2276A0','line':'#C46B2C'}
    for ax,field,title in zip(axes,['D2_fixed','D2_profile'],
        ['(a) Fixed rival load amplitude','(b) Fitted rival load amplitude']):
        for i,a in enumerate(assets):
            y=17-i; c=palette[a['family']]
            if i%2==0: ax.axhspan(y-.4,y+.4,color='#F3F6F7',zorder=0)
            v=d.loc[(a['id'],'V'),field]/2; vi=d.loc[(a['id'],'VI'),field]/2
            ax.plot([v,vi],[y,y],color=c,lw=1.1)
            ax.plot(v,y,'o',ms=3.5,mfc='white',mec=c,mew=.9)
            ax.plot(vi,y,'o',ms=3.5,color=c)
        ax.set_xscale('log'); ax.set_ylim(-.7,17.7)
        ax.spines[['top','right']].set_visible(False)
        ax.spines[['bottom','left']].set_color('#CDD6DA')
        ax.tick_params(colors='#4C5D67',labelsize=7,length=2)
        ax.grid(axis='x',color='#E7ECEE',lw=.5); ax.set_axisbelow(True)
        ax.set_title(title,loc='left',fontsize=8.5,fontweight='bold')
        ax.set_xlabel('Minimum pairwise separation Q (nats)')
        ax.plot([],[],'o',mfc='white',mec='#23343F',ms=3.5,label='V')
        ax.plot([],[],'o',color='#23343F',ms=3.5,label='V + I')
        ax.legend(loc='lower left',frameon=True,facecolor='white',edgecolor='none',fontsize=7)
    axes[0].set_yticks(range(18),[a['id'].replace('BUS','Bus ').replace('LINE','Line ') for a in assets[::-1]])
    axes[1].tick_params(labelleft=True)
    fig.tight_layout(w_pad=1.8)
    for ext in ['pdf','png']:
        fig.savefig(ROOT/f'figures/generated/channel_profile_information.{ext}',bbox_inches='tight',pad_inches=.05,dpi=220)
    plt.close(fig)
    ratios=report['results']['nearest_profile_VI_over_V']
    numbers={'GainMin':f'{ratios["min"]:.2f}','GainMedian':f'{ratios["median"]:.2f}','GainMax':f'{ratios["max"]:.2f}',
        'NearestChanges':str(report['results']['nearest_changes_fixed_vs_profile_VI']),
        'BusThirtyOneRetained':f'{100*d.loc[("BUS31","VI"),"D2_profile"]/d.loc[("BUS31","VI"),"D2_fixed"]:.1f}'}
    (ROOT/'generated/channel_profile_macros.tex').write_text('% Generated from bounded rival severity diagnostic.\n'+
        ''.join('\\newcommand{\\ProfileChannel'+k+'}{'+v+'}\n' for k,v in numbers.items()),encoding='utf-8')
    print(json.dumps(numbers,indent=2))


if __name__=='__main__': main()
