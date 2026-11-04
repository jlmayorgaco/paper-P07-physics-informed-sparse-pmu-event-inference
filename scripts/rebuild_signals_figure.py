"""Regenerate only the signals figure (revision 2026-11-04): neutral development label.
Does not touch the protected single-line diagram or any other artifact."""
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
    for f in [f for f in manifest['files'] if f['path'].startswith(('observed/','evaluation/')) or f['path']=='assets.json']:  # only inputs of this figure
        raw=(DATA/f['path']).read_bytes()
        ok={hashlib.sha256(raw).hexdigest(),hashlib.sha256(raw.replace(bytes([13,10]),bytes([10]))).hexdigest()}  # git CRLF checkout
        assert f['sha256'] in ok,f['path']
    plt.rcParams.update({'font.size':8,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
    pmus=[2,5,6,10,19,22,29,39]
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
        axes[0,col].set_title(f"{family.title()} at {e['source']} (development record)");axes[3,col].set_xlabel('Time from physical ON (s)')
    fig.legend([Line2D([],[],color=colors[j]) for j in range(8)],[f'PMU {p}' for p in pmus],ncol=8,loc='outside upper center',frameon=False,fontsize=7);save(fig,'narrative_signals')
if __name__=='__main__':main()
