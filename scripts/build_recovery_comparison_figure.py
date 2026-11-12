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
    "ink": "#20282E",
    "muted": "#5C6971",
    "rule": "#CDD6DA",
    "teal": "#087F78",
    "orange": "#D55E00",
    "blue": "#0077A8",
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
    # The panel of paired differences uses archived intervals, never new TEST fits.
    fig, axes = plt.subplots(1, 3, figsize=(7.15, 2.45),
                             gridspec_kw={'width_ratios': [1.1, 1.0, 1.45]})
    fig.subplots_adjust(left=.15, right=.98, top=.86, bottom=.27, wspace=.32)
    for ax in axes:
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.spines['bottom'].set_color(C['rule'])
        ax.tick_params(length=0, labelsize=6.5, colors=C['muted'])
        ax.set_axisbelow(True)
        ax.grid(axis='x', color=C['rule'], lw=.45)
    for idx, (key, name, color) in enumerate(METHODS):
        arm=report['arms'][key]; y=2-idx
        pct=100*arm['timely_joint']/arm['events']
        axes[0].hlines(y, 0, pct, color=color, lw=2)
        axes[0].plot(pct,y,'o',color=color,ms=4)
        axes[0].text(pct, y+.22, f"{pct:.1f}% ({arm['timely_joint']}/{arm['events']})",
                     ha='right', fontsize=6, color=color)
        count=arm['event_extras']
        axes[1].hlines(y, 0, count, color=color, lw=2)
        axes[1].plot(count,y,'o',color=color,ms=4, clip_on=False)
        axes[1].text(0, y+.22, f"{count} alarms ({arm['event_extras_per_h']:.1f}/h)",
                     fontsize=6, color=color)
    axes[0].set_yticks([2,1,0], [x[1] for x in METHODS])
    axes[0].set_xlim(-2,105); axes[0].set_xticks([0,50,100])
    axes[1].set_xlim(-2,90); axes[1].set_xticks([0,40,80]); axes[1].set_yticks([])
    for ax in axes[:2]: ax.set_ylim(-.45,2.65)
    axes[0].set_title('(a) Timely attribution', loc='left', fontsize=8, pad=13)
    axes[1].set_title('(b) Extra alarms', loc='left', fontsize=8, pad=13)
    axes[0].set_xlabel('Correct before OFF (%)', fontsize=6.5)
    axes[1].set_xlabel('Count on event records', fontsize=6.5)
    ax=axes[2]
    ax.set_title('(c) Paired coverage gain',loc='left',fontsize=8,pad=13)
    for y,(label,key) in zip([1.6,.15],[('Bank minus GLR','PHYSICAL_CONTINUOUS_GLR'),('Bank minus ExtraTrees','EXTRATREES_ALL_SOURCES')]):
        d=report['paired_intervals']['PHYSICAL_HISTORY-minus-'+key]['coverage_difference']
        v,lo,hi=[100*d[k] for k in ['point','lower95','upper95']]
        ax.errorbar(v,y,xerr=[[v-lo],[hi-v]],fmt='o',color=C['teal'],capsize=3,lw=1.3,ms=4)
        ax.text(2,y+.47,label,fontsize=6.5,color=C['ink'])
        ax.text(2,y-.40,f'{v:+.1f} pp  [{lo:.2f}, {hi:.2f}]',fontsize=6.2,color=C['muted'])
    ax.axvline(0, color=C['muted'], lw=.65, ls='--')
    ax.set_xlim(-5,100); ax.set_ylim(-.55,2.65); ax.set_xticks([0,25,50,75,100]); ax.set_yticks([])
    ax.set_xlabel('Percentage points (95% interval)',fontsize=6.5)
    test=report['arms']['PHYSICAL_HISTORY']
    fig.text(.02,.09, f"Normal records: 0 alarms / {test['normal_monitored_s']/3600:.2f} h per method; Poisson upper 95% limit {test['normal_Poisson_upper95_per_h']:.2f}/h.",fontsize=6.5,color=C['muted'])
    fig.text(.02,.025,'Paired intervals: 10,000 resamples of 18 event parents. Thresholds selected on separate calibration data.',fontsize=6.5,color=C['muted'])
    return fig


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    fig = draw(read_sealed_result())
    fig.savefig(OUT / "recovery_comparison_c02.pdf", bbox_inches="tight",
                pad_inches=0.03)
    fig.savefig(OUT / "recovery_comparison_c02.png", dpi=260,
                bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)
    print("Built C02 figure from the sealed TEST evaluation.")
