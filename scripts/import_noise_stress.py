"""Import the N01 noise-stress evaluation into generated/revision_20261104.

Copies EVENTS/EXTRAS/NORMALS produced by
SGSMA26-Physics-Informed-AD/experiments/PAPER_NOISE_STRESS_N01/stress.py evaluate,
and derives amortized processing rates of the nominal bank from the job logs.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
N01 = ROOT.parent / "SGSMA26-Physics-Informed-AD/experiments/PAPER_NOISE_STRESS_N01/run"
REV = ROOT / "generated/revision_20261104"


def main() -> None:
    for src, dst in [("EVENTS.csv", "noise_stress_events.csv"), ("EXTRAS.csv", "noise_stress_extras.csv"),
                     ("NORMALS.csv", "noise_stress_normals.csv"), ("SUMMARY.csv", "noise_stress_summary.csv")]:
        shutil.copyfile(N01 / src, REV / dst)
    rates = []
    for done in sorted((N01 / "jobs").glob("*__U1/COMPLETE.json")):
        info = json.loads(done.read_text())
        pred = next(done.parent.glob("prediction/R11/prediction.json"))
        reports = json.loads(pred.read_text())["reports"]
        rates.append(dict(job=done.parent.name, reports=reports, infer_s=info["infer_s"],
                          ms_per_report=1000 * info["infer_s"] / reports))
    ms = np.array([r["ms_per_report"] for r in rates])
    out = dict(NomMsReport=f"{np.median(ms):.1f}", NomMsReportMax=f"{ms.max():.1f}", NomRecords=str(len(ms)),
               detail=rates)
    (REV / "latency.json").write_text(json.dumps(out, indent=2))
    manifest = json.loads((N01 / "OBSERVED_MANIFEST.json").read_text())
    (REV / "noise_stress_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "detail"}, indent=2))


if __name__ == "__main__":
    main()
