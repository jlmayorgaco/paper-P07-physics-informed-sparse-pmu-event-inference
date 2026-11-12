"""Plot the sealed C02 comparison without rerunning or reopening TEST."""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "generated/frozen/recovery_c02_20261105"
OUT = ROOT / "figures/generated"
EXPECTED = "4f19cb72a2cf1929b5e68805c41fb00703fa88bdc365b726ed408fd57423349a"

C = {
    "ink": "#23343F",
    "muted": "#4C5D67",
    "rule": "#CDD6DA",
    "teal": "#087F78",
    "orange": "#C46B2C",
    "blue": "#2276A0",
    "green": "#4B7F52",
    "pale_teal": "#F0F7F6",
    "pale_blue": "#F2F7F9",
    "pale_orange": "#FBF5EF",
    "pale_gray": "#F6F8F8",
    "white": "#FFFFFF",
}

METHODS = [
    ("PHYSICAL_HISTORY", "History bank", C["teal"]),
    ("PHYSICAL_CONTINUOUS_GLR", "Continuous GLR", C["orange"]),
    ("EXTRATREES_ALL_SOURCES", "ExtraTrees", C["blue"]),
]

plt.rcParams.update({
    "font.family": "STIXGeneral",
    "font.size": 6.3,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def read_sealed_result():
    data = (SNAPSHOT / "TEST_EVALUATION.json").read_bytes()
    lock = json.loads((SNAPSHOT / "TEST_EVALUATION_LOCK.json").read_bytes())
    seal = json.loads((SNAPSHOT / "RESULTS_SEAL.json").read_bytes())
    digest = hashlib.sha256(data).hexdigest()
    if (digest != EXPECTED or lock.get("result_sha256") != EXPECTED
            or lock.get("status") != "COMPLETE_SINGLE_USE"
            or seal.get("files", {}).get("run/TEST_EVALUATION.json") != EXPECTED):
        raise ValueError("C02 result seal mismatch; refusing to draw the figure")
    report = json.loads(data)
    arms = report["arms"]
    bank = arms["PHYSICAL_HISTORY"]
    for key, _, _ in METHODS:
        arm = arms[key]
        if (arm["events"] != bank["events"]
                or arm["event_parents"] != bank["event_parents"]
                or arm["normal_monitored_s"] != bank["normal_monitored_s"]):
            raise ValueError("C02 arms do not share the sealed evaluation denominator")
    return report


def draw(report):
    # Absolute outcomes and paired contrasts retain their different denominators.
    # All intervals come from the sealed report, not a new bootstrap of TEST.
    fig = plt.figure(figsize=(7.15, 3.55))
    axes = [fig.add_axes(bounds) for bounds in
            [(.18,.62,.31,.27),(.62,.62,.35,.27),
             (.18,.22,.31,.22),(.62,.22,.35,.22)]]
    for ax in axes:
        ax.set_axisbelow(True)
        ax.spines[['top','right','left']].set_visible(False)
        ax.spines['bottom'].set_color(C['rule'])
        ax.tick_params(axis='both',length=0,labelsize=7.5,pad=4,colors=C['muted'])
        ax.grid(axis='x',color=C['rule'],lw=.45)
    markers=['o','s','^']
    for i, (key,label,color) in enumerate(METHODS):
        arm=report['arms'][key]; y=2-i
        coverage=100*arm['coverage']; extras=arm['event_extras']
        for ax,value in zip(axes[:2],[coverage,extras]):
            ax.axhspan(y-.16,y+.16,color='#F2F5F6',zorder=0)
            ax.hlines(y,0,value,color=color,lw=1.6,zorder=2)
            ax.plot(value,y,marker=markers[i],ms=4.5,color=color,zorder=3,clip_on=False)
        axes[0].text(100,y+.23,f"{coverage:.1f}%   {arm['timely_joint']}/{arm['events']}",
                     ha='right',fontsize=7.5,color=C['ink'],
                     bbox=dict(facecolor='white',edgecolor='none',pad=.7))
        axes[1].text(100,y+.23,f"{extras} alarms   {arm['event_extras_per_h']:.1f}/h",
                     ha='right',fontsize=7.5,color=C['ink'],
                     bbox=dict(facecolor='white',edgecolor='none',pad=.7))
    axes[0].set_yticks([2,1,0],[m[1] for m in METHODS])
    axes[1].set_yticks([])
    for ax in axes[:2]:
        ax.set_ylim(-.45,2.65); ax.set_xlim(-2,102); ax.set_xticks([0,25,50,75,100])
    bank=report['arms']['PHYSICAL_HISTORY']
    axes[0].set_xlabel('Correct family and source before OFF (%)',fontsize=7.5,labelpad=5)
    axes[1].set_xlabel(f"Unmatched alarms over {bank['event_monitored_s']/3600:.2f} event-hours",fontsize=7.5,labelpad=5)
    for i,(key,_,color) in enumerate(METHODS[1:]):
        y=1-i; arm=report['arms'][key]
        pair=report['paired_intervals']['PHYSICAL_HISTORY-minus-'+key]
        metrics=[('coverage_difference',100,bank['coverage']-arm['coverage']),
                 ('event_extras_difference_per_h',1,bank['event_extras_per_h']-arm['event_extras_per_h'])]
        for ax,(metric,scale,expected) in zip(axes[2:],metrics):
            d=pair[metric]
            if abs(d['point']-expected)>1e-9 or not d['lower95']<=d['point']<=d['upper95']:
                raise ValueError('Paired interval inconsistent with sealed arm totals')
            v,lo,hi=[scale*d[k] for k in ['point','lower95','upper95']]
            ax.errorbar(v,y,xerr=[[v-lo],[hi-v]],fmt=markers[i+1],color=color,
                        ms=4.5,capsize=3,elinewidth=1.3,zorder=3)
            ax.text(.99,y+.25,f'{v:+.1f}  [{lo:.2f}, {hi:.2f}]',
                    transform=ax.get_yaxis_transform(),ha='right',fontsize=7.5,color=C['ink'],
                     bbox=dict(facecolor='white',edgecolor='none',pad=.7))
    axes[2].set_yticks([1,0],['Bank minus GLR','Bank minus ExtraTrees'])
    axes[3].set_yticks([])
    for ax in axes[2:]:
        ax.set_ylim(-.43,1.65)
        ax.axvline(0,color=C['muted'],lw=.7,ls=(0,(3,3)),zorder=2)
    axes[2].set_xlim(-5,102);axes[2].set_xticks([0,25,50,75,100])
    axes[3].set_xlim(-200,50);axes[3].set_xticks([-200,-150,-100,-50,0,50])
    axes[2].set_xlabel('Percentage points; positive favors the bank',fontsize=7.5,labelpad=5)
    axes[3].set_xlabel('Extras/h; negative favors the bank',fontsize=7.5,labelpad=5)
    titles=['(a) Timely attribution','(b) Extra alarms',
            '(c) Paired coverage difference','(d) Paired extra-alarm difference']
    for ax,title in zip(axes,titles):
        ax.set_title(title,loc='left',fontsize=9.2,fontweight='bold',pad=12,color=C['ink'])
    fig.text(.02,.055,
             f"Normal records: 0 alarms in {bank['normal_monitored_s']/3600:.2f} h per method; one-sided 95% Poisson upper bound {bank['normal_Poisson_upper95_per_h']:.2f}/h.",
             fontsize=7.5,color=C['muted'])
    fig.text(.02,.012,
             'Paired 95% intervals: 10,000 resamples of 18 event parents. Each method meets the calibration alarm budget.',
             fontsize=7.5,color=C['muted'])
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw(read_sealed_result())
    fig.savefig(OUT / "recovery_comparison_c02.pdf", bbox_inches="tight",
                pad_inches=0.08)
    fig.savefig(OUT / "recovery_comparison_c02.png", dpi=260,
                bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)
    print("Built C02 figure from the sealed TEST evaluation.")
