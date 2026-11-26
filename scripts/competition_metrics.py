"""Competition-guide metrics for the independent evaluation (continuous lane, all conditions).

Reads the stored independent-evaluation result tables (read-only) and writes a
LaTeX table in the metric vocabulary of the SGSMA 2026 competition guide:
report-level detection precision/recall/F1, false alarms per minute of normal
operation, median detection delay, Top-1/Top-3 localization (family and source
jointly) and run time per minute of PMU data.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT.parent / "SGSMA26-Physics-Informed-AD/experiments/PAPER_CONFIRMATORY_C01/run/results"
OUT_T = ROOT / "tables/generated/competition_metrics.tex"
OUT_J = ROOT / "generated/revision_20261104/competition_metrics.json"
METHODS = [("R11", "Physical bank, five R/X models"), ("R11_NOMINAL", "Physical bank, nominal model"),
           ("ET_REFERENCE", "Submitted ExtraTrees"), ("ET_CANDIDATE", "Retrained short-window ExtraTrees")]


def main() -> None:
    s = pd.read_csv(RES / "SUMMARY.csv"); s = s[s.lane == "continuous"]
    r = pd.read_csv(RES / "RECORDS.csv"); r = r[r.lane == "continuous"]
    e = pd.read_csv(RES / "EVENTS.csv"); e = e[e.lane == "continuous"]
    lat = json.loads((ROOT / "generated/revision_20261104/latency.json").read_text())
    rows = []
    for m, name in METHODS:
        rr = r[r.method == m][["tp", "fp", "fn"]].sum()
        p = rr.tp / (rr.tp + rr.fp); rc = rr.tp / (rr.tp + rr.fn)
        ss = s[s.method == m]; ee = e[e.method == m]
        normal_min = ss.normal_available_s.sum() / 60
        rows.append(dict(method=m, name=name, precision=p, recall=rc, f1=2 * p * rc / (p + rc),
                         fa_per_min=ss.normal_FA.sum() / normal_min, normal_min=normal_min,
                         delay_s=float(ee[ee.detected].delay_s.median()),
                         top1=ee.joint.mean(), top3=ee.top3.mean(), events=len(ee),
                         extras=int(ss.event_extras.sum())))
    df = pd.DataFrame(rows)
    rt = {"R11": 99.6 * 1.8, "R11_NOMINAL": float(lat["NomMsReport"]) * 1.8}
    lines = [r"\begin{table*}[t]\centering\small",
             r"\caption{Independent evaluation in the metric vocabulary of the competition guide (648 interventions, "
             r"%.0f\,min of normal records, three R/X conditions pooled). Detection is scored per report; "
             r"Top-$k$ requires the correct family and source among the first $k$ candidates. Run time is per minute of "
             r"PMU data on one CPU thread.}" % df.normal_min.iloc[0],
             r"\label{tab:competition-metrics}",
             r"\begin{tabular}{@{}lrrrrrrrr@{}}\toprule",
             r"Method & Precision & Recall & F1 & FA/min & Delay (s) & Top-1 & Top-3 & Run time (s/min)\\\midrule"]
    for _, x in df.iterrows():
        run = f"{rt[x.method]:.0f}" if x.method in rt else "--"
        lines.append(f"{x['name']} & {x.precision:.3f} & {x.recall:.3f} & {x.f1:.3f} & {x.fa_per_min:.0f} & "
                     f"{x.delay_s:.2f} & {x.top1:.3f} & {x.top3:.3f} & {run}\\\\")
    lines += [r"\bottomrule\end{tabular}\end{table*}"]
    OUT_T.write_text("\n".join(lines) + "\n", encoding="utf-8")
    OUT_J.write_text(df.to_json(orient="records", indent=2))
    print(df.round(3).to_string())


if __name__ == "__main__":
    main()
