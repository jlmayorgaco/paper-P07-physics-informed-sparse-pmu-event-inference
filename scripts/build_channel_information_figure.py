"""Draw the audited nominal channel diagnostic; never read campaign outcomes."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'experiments/channel_information_20261112'
OUT = ROOT / 'figures/generated'


def main():
    report = json.loads((DATA/'diagnostic_summary.json').read_text(encoding='utf-8'))
    for name, expected in report['outputs'].items():
        if hashlib.sha256((DATA/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Diagnostic output changed: '+name)
    pairs = pd.read_csv(DATA/'pairwise_separation.csv')
    nearest = pd.read_csv(DATA/'nearest_competitor.csv')
    assets = json.loads((DATA/'r11_assets.json').read_text())
    names = [a['id'] for a in assets]
    one = nearest[nearest.reports == 30].set_index(['source', 'channels'])
    pair = pairs[pairs.reports == 30].set_index(['source', 'competitor'])
    palette = {'load': '#2276A0', 'line': '#C46B2C'}
    ink, muted, rule = '#23343F', '#4C5D67', '#CDD6DA'
    plt.rcParams.update({'font.family':'STIXGeneral','font.size':8,'pdf.fonttype':42})
    fig, axes = plt.subplots(1,2,figsize=(7.1,3.5),gridspec_kw={'width_ratios':[1.18,1]})
    shares, gains = [], []
    for ax in axes:
        ax.spines[['top','right']].set_visible(False)
        ax.spines[['bottom','left']].set_color(rule)
        ax.tick_params(colors=muted, labelsize=7, length=2)
        ax.grid(axis='x',color='#E7ECEE',lw=.5)
        ax.set_axisbelow(True)
    for i,a in enumerate(assets):
        name=a['id']; color=palette[a['family']]; y=len(names)-1-i
        v=float(one.loc[(name,'V'),'nearest_D2'])/2
        vi=float(one.loc[(name,'VI'),'nearest_D2'])/2
        if v<=0 or vi<=0: raise ValueError('Nonpositive plotted separation')
        gains.append(vi/v)
        competitor=one.loc[(name,'VI'),'nearest_competitor']
        row=pair.loc[(name,competitor)]
        share=100*(row.D2_VI-row.D2_V)/row.D2_VI
        shares.append(share)
        for ax in axes:
            if i%2==0: ax.axhspan(y-.4,y+.4,color='#F3F6F7',zorder=0)
        axes[0].plot([v,vi],[y,y],color=color,lw=1.1)
        axes[0].plot(v,y,'o',ms=3.5,mfc='white',mec=color,mew=.9)
        axes[0].plot(vi,y,'o',ms=3.5,color=color)
        axes[1].plot(share,y,'o',ms=3.5,color=color)
    axes[0].set_xscale('log')
    axes[0].set_yticks(range(len(names)),[s.replace('BUS','Bus ').replace('LINE','Line ') for s in names[::-1]])
    axes[1].set_yticks(range(len(names)),[s.replace('BUS','Bus ').replace('LINE','Line ') for s in names[::-1]])
    for ax in axes: ax.set_ylim(-.7,len(names)-.3)
    axes[0].plot([],[],'o',mfc='white',mec=ink,ms=3.5,label='V')
    axes[0].plot([],[],'o',color=ink,ms=3.5,label='V + I')
    axes[0].legend(loc='best',frameon=True,facecolor='white',edgecolor='none',fontsize=7)
    axes[0].set_title('(a) Separation from the nearest source',loc='left',fontsize=8.5,fontweight='bold')
    axes[0].set_xlabel('Minimum pairwise separation Q (nats)')
    axes[1].set_title('(b) Contribution of currents given voltage',loc='left',fontsize=8.5,fontweight='bold')
    axes[1].set_xlim(-2,102)
    axes[1].set_xticks([0,25,50,75,100])
    axes[1].set_xlabel('Conditional current term / joint separation (%)')
    fig.tight_layout(w_pad=1.8)
    OUT.mkdir(exist_ok=True,parents=True)
    for ext in ['pdf','png']:
        fig.savefig(OUT/f'channel_information.{ext}',bbox_inches='tight',pad_inches=.05,dpi=220)
    plt.close(fig)
    numbers={'GainMin':f'{min(gains):.2f}', 'GainMedian':f'{np.median(gains):.2f}',
             'GainMax':f'{max(gains):.2f}', 'CurrentShareMin':f'{min(shares):.1f}',
             'CurrentShareMedian':f'{np.median(shares):.1f}', 'CurrentShareMax':f'{max(shares):.1f}'}
    (ROOT/'generated/channel_information_macros.tex').write_text(
        '% Generated from audited deterministic channel diagnostics.\n'+
        ''.join('\\newcommand{\\Channel'+k+'}{'+v+'}\n' for k,v in numbers.items()),encoding='utf-8')
    print(json.dumps(numbers,indent=2))


if __name__=='__main__': main()
