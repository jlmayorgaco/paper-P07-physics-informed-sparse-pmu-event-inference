"""Copy the simulated integrity-stress outcomes into the paper and derive macro values.

Read-only source: the science repository's integrity-stress run (EVENTS.csv,
UNMATCHED_ALARMS.csv, SCHEDULE.json).  Output:
generated/revision_20261104/integrity_stress.json (+ copies of the tables).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT.parent / "SGSMA26-Physics-Informed-AD/experiments/PAPER_INTEGRITY_N02/run"
REV = ROOT / "generated/revision_20261104"


def main() -> None:
    for f in ("EVENTS.csv", "UNMATCHED_ALARMS.csv", "SCHEDULE.json", "SUMMARY.json", "CORRUPTION_RESPONSES.csv"):
        shutil.copy2(RUN / f, REV / f"integrity_stress_{f}")
    ev = pd.read_csv(RUN / "EVENTS.csv")
    al = pd.read_csv(RUN / "UNMATCHED_ALARMS.csv")
    sch = json.loads((RUN / "SCHEDULE.json").read_text())
    n_corr = sum(len(s["schedule"]["corruptions"]) for s in sch)
    c = ev[ev.scenario == "C"]
    m = ev[ev.scenario == "M"].copy()
    win = {s["record"]: s["schedule"]["dropouts"][0] for s in sch if s["kind"] == "event"}
    m["phase"] = [("inside" if w["start_s"] <= o < w["start_s"] + w["dur_s"] else
                   "before" if o < w["start_s"] else "after") for o, w in zip(m.onset_s, (win[r] for r in m.record))]
    corr_alarm = al[(al.scenario == "C") & (al.cause == "corruption")]
    normal_c = al[(al.scenario == "C") & (al.kind == "normal")]
    normal_m = al[(al.scenario == "M") & (al.kind == "normal")]
    out = dict(
        IntSimCorr=n_corr,
        IntSimCorrAlarm="None" if len(corr_alarm) == 0 else len(corr_alarm),
        IntSimCorrLoad=int(c[c.family == "load"].timely.sum()), IntSimCorrLine=int(c[c.family == "line"].timely.sum()),
        IntSimCorrNormalAlarms=len(normal_c),
        IntSimMissInside=int((m.phase == "inside").sum()),
        IntSimMissInsideTimely=int(m[m.phase == "inside"].timely.sum()),
        IntSimMissBefore=int((m.phase == "before").sum()),
        IntSimMissBeforeTimely=int(m[m.phase == "before"].timely.sum()),
        IntSimMissAfter=int((m.phase == "after").sum()),
        IntSimMissAfterTimely=int(m[m.phase == "after"].timely.sum()),
        IntSimMissExtras=int(((al.scenario == "M") & (al.cause == "dropout") & (al.kind == "event")).sum()),
        IntSimMissNormalAlarms=len(normal_m),
    )
    out["IntSimMissText"] = (
        f"Attribution did not recover after the PMU returned: {out['IntSimMissAfterTimely']} of the "
        f"{out['IntSimMissAfter']} later interventions in these records were attributed in time, against "
        f"{out['IntSimMissBeforeTimely']} of {out['IntSimMissBefore']} before the dropout. On the completed normal "
        f"record the two held intervals produced {out['IntSimMissNormalAlarms']} alarms (the second normal record of "
        f"this scenario was not run). A held value is a measurement that "
        f"contradicts the network response, not an absent one; the bank therefore needs the deletion of "
        f"Proposition~\\ref{{prop:integrity}}, an availability-switched observation operator, rather than imputation.")
    (REV / "integrity_stress.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
