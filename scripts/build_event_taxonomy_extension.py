"""Append class 6 data and class 8 definition; never rewrite protected panels."""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd
import fitz

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'generated/event_taxonomy_extension_20261113'
OUT = ROOT / 'figures/generated'
BLUE, ORANGE, INK = '#17608b', '#c26821', '#23343F'


def main():
    original = OUT / 'event_signatures.pdf'
    before = hashlib.sha256(original.read_bytes()).hexdigest()
    meta = json.loads((DATA / 'PROVENANCE.json').read_text())
    source = DATA / 'class6_trace.csv'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == meta['trace_sha256']
    d = pd.read_csv(source)
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'DejaVu Serif'],
                         'font.size': 8, 'pdf.fonttype': 42, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.labelsize': 8,
                         'xtick.labelsize': 7, 'ytick.labelsize': 7})
    fig = plt.figure(figsize=(7.16, 2.2))
    ax = fig.add_axes([.08,.32,.43,.48])
    strip = fig.add_axes([.08,.19,.43,.06],sharex=ax)
    fig.text(.04,.94,'(g) Missing data + physical event (class 6)',fontsize=8.2)
    for b,c in [(2,BLUE),(39,ORANGE)]:
        ax.plot(d.relative_time_s,d[f'pmu{b}_frequency_change_mHz'],color=c,lw=.65,label=f'PMU {b}')
    end=meta['last_class6_s']-meta['onset_s']
    ax.axvspan(0,end,color='#edf3f6',zorder=0)
    ax.axvline(0,color='.4',ls=':',lw=.8)
    ax.set_ylabel(r'$f-f_{\mathrm{pre}}$ (mHz)',labelpad=1)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),ncol=2,frameon=False,
              fontsize=7,handlelength=1.3,borderaxespad=0)
    ax.set_xlim(-4,32);ax.set_ylim(-255,55);ax.set_yticks([-200,-100,0])
    ax.tick_params(labelbottom=False);ax.grid(axis='y',color='.87',lw=.4)
    # The strip is observed availability, including missing reports before class 6.
    strip.fill_between(d.relative_time_s,0,1,where=d.pmu29_present.eq(0),step='post',color='#dddddd')
    strip.step(d.relative_time_s,d.pmu29_present,where='post',color=BLUE,lw=1)
    strip.set_ylim(-.1,1.1);strip.set_yticks([]);strip.set_xticks([0,10,20,30])
    strip.set_xlabel(r'Time from generation onset, $t-t_0$ (s)',labelpad=2)
    strip.text(.01,.5,'PMU 29 absent',transform=strip.transAxes,fontsize=6.8,va='center')
    strip.text(.66,.5,'available',transform=strip.transAxes,fontsize=6.8,va='center')
    fig.text(.61,.94,'(h) Unknown event (class 8)',fontsize=8.2)
    flow=fig.add_axes([.60,.22,.37,.62]);flow.set_xlim(0,1);flow.set_ylim(0,1);flow.axis('off')
    for y,h,label,fc in [(.67,.25,'Abnormal observation','#f1f5f7'),
                         (.12,.32,'No clear match to classes 1–7\nUnknown / ambiguous','#faf3ec')]:
        flow.add_patch(FancyBboxPatch((.06,y),.88,h,boxstyle='round,pad=.015,rounding_size=.025',
                                     lw=.65,edgecolor='#becbd2',facecolor=fc))
        flow.text(.5,y+h/2,label,ha='center',va='center',fontsize=8,color=INK,linespacing=1.5)
    flow.annotate('',xy=(.5,.46),xytext=(.5,.65),arrowprops={'arrowstyle':'->','lw':.9,'color':INK})
    fig.text(.785,.12,'Guide definition; schematic, not a measured trace.',ha='center',fontsize=6.8,color='.35')
    extension=OUT/'event_taxonomy_extension.pdf'
    fig.savefig(extension);fig.savefig(OUT/'event_taxonomy_extension.png',dpi=260);plt.close(fig)
    # Preview only: native PDF composition preserves every original vector panel.
    with fitz.open(original) as old, fitz.open(extension) as extra:
        w=old[0].rect.width;h0=old[0].rect.height;h1=extra[0].rect.height*w/extra[0].rect.width
        combined=fitz.open();page=combined.new_page(width=w,height=h0+h1+8)
        page.show_pdf_page(fitz.Rect(0,0,w,h0),old,0)
        page.show_pdf_page(fitz.Rect(0,h0+8,w,h0+h1+8),extra,0)
        combined.save(OUT/'event_taxonomy_complete.pdf')
        page.get_pixmap(matrix=fitz.Matrix(3,3),alpha=False).save(OUT/'event_taxonomy_complete.png')
    assert hashlib.sha256(original.read_bytes()).hexdigest()==before
    print('Added class 6 observation and class 8 schematic; original PDF unchanged.')


if __name__=='__main__':
    main()
