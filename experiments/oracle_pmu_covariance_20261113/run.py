"""Retrospective B01 replays. Archived artifacts and C03 are read-only."""
import os
for key in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[key] = "1"

from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np
from scipy.linalg import solve_discrete_lyapunov
from scipy.stats import chi2
from sklearn.covariance import LedoitWolf
from scipy.sparse import csr_matrix

from noise_model import KEEP, add_to_reports, rebuild, verify_maps

HERE = Path(__file__).resolve().parent
SCI = HERE.parents[2] / "SGSMA26-Physics-Informed-AD" / "experiments"
ARCHIVE = Path(r"\\WallaMediaNAS\home\academic\SGSMA26-Physics-Informed-AD\experiments\PAPER_CALIBRATION_B01\run")
RUNTIME = SCI/"PAPER_NOISE_STRESS_N01/runtime_relaxed"
OBSERVER = SCI/"E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/observer"
PUBLICATION = SCI/"PAPER_RECOVERY_C02/runtime/frozen_S01"
METRICS = SCI/"PAPER_RECOVERY_C02/protocol"
sys.path[:0] = [str(x) for x in (RUNTIME, OBSERVER, PUBLICATION, METRICS)]
from core_v6 import StreamTensor
from static_rx import Particle
from continuous_bank import ContinuousBank
from instrument_parent import FIELDS
from publication import EvidenceClock, logodds
from frozen_metrics import alarms, match, bootstrap_difference

CFG = json.loads((HERE/"protocol.json").read_text())
OUT = HERE.parents[1]/"build/oracle_pmu_covariance_20261113"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")
    temp.replace(path)


def job(task):
    split, kind, record, pct, arm = task
    output = OUT/split/f"{record}_{pct:g}_{arm}.json"
    if output.exists():
        return
    folder = ARCHIVE/"particles"/record/"nominal"
    ready = json.loads((folder/"READY.json").read_text())
    source = ARCHIVE/"data/observed"/f"{record}.npz"
    assert digest(source) == ready["observation_sha256"]
    assert digest(folder/"bank.npz") == ready["bank_sha256"]
    with np.load(source, allow_pickle=False) as z:
        data = {key: z[key] for key in ("time_s", *FIELDS)}
    model = StreamTensor(RUNTIME)
    with np.load(folder/"bank.npz", allow_pickle=False) as z:
        model.bank = {key: z[key] for key in z.files}
    scales = np.repeat(model.obs.scales, [8,8,8,7,8,8])
    fit = json.loads((folder/"fit.json").read_text())
    baseline = np.array(fit["baseline"])
    magnitude = np.r_[baseline[:8], baseline[16:24]]
    assert np.all(magnitude > 0)
    verify_maps(scales, magnitude)
    sigma = pct/100
    seed = np.random.SeedSequence([CFG["seed"], int(record[1:])])
    data = add_to_reports(data, FIELDS, magnitude, sigma, seed)
    times = data["time_s"]
    n_prefix = CFG["prefix_reports"]
    parts = []
    for field, indices in zip(FIELDS, KEEP):
        x = data[field][:n_prefix, indices].copy()
        if field.endswith("angle"):
            x = np.rad2deg(np.unwrap(np.deg2rad(
                x-times[:n_prefix,None]*model.obs.cfg["common_phase_slope_deg_s"]), axis=0))
        parts.append(x)
    combined = np.concatenate(parts, axis=1)
    baseline = np.nanmean(combined, axis=0)
    offset = 0
    for j, indices in enumerate(KEEP):
        end = offset+len(indices)
        model.obs.base[j] = baseline[offset:end] - model.obs.centers[j]
        offset = end
    # A disposable observation filter ensures the same initial state in all arms.
    import copy
    prefix_filter = copy.deepcopy(model.obs)
    z = np.array([prefix_filter.process(float(t), {f:data[f][k] for f in FIELDS})
                  for k,t in enumerate(times[:n_prefix])])[60:]
    variances = np.concatenate([np.full(len(i), np.mean(np.var(z[:,s:s+len(i)],axis=0)))
                                for i,s in zip(KEEP,[0,8,16,24,31,39])])
    white = np.eye(47)
    estimated = None
    if arm == "family":
        white = np.diag(np.maximum(variances, 1e-6))
    elif arm == "shrinkage":
        # Fit correlation with normalized marginals, then restore their units.
        sd = np.maximum(z.std(axis=0), 1e-3)
        white = LedoitWolf().fit(z/sd).covariance_ * np.outer(sd, sd)
    elif arm == "structured":
        f = model.obs.filters[1]
        stationary = solve_discrete_lyapunov(f.F, f.Q)
        ac0 = f.H @ stationary @ f.H.T
        ac1 = f.H @ f.F @ stationary @ f.H.T
        base = 2*np.diag(ac0-ac1)*model.obs.scales[1]**2
        observed = np.var(np.diff(parts[1][20:],axis=0), axis=0)
        estimated = np.sqrt(np.maximum(observed-base, 1e-12)/2)*np.pi/180
    elif arm == "oracle":
        estimated = np.full(8, sigma)
    else:
        raise ValueError(arm)
    err = rebuild(model.bank, model.obs.filters, scales, magnitude, white, estimated)
    model.n = model.bank["P"].shape[-1]
    model.sparseT = [csr_matrix(x) for x in model.bank["T"]]
    model.m0 = np.zeros(model.n)
    model.clear_histories()
    # Freeze the boundary proposal noise rule across arms. The continuous
    # recovery proposal and conditional likelihood use the rebuilt gains.
    model.boundary.configure_noise(fit["noise_std_factors"])
    model.boundary.configure_physical(model.bank["step_signatures"])
    model.__class__ = Particle
    model.attach(ContinuousBank(model, "dense"))
    if split == "CAL":
        thresholds = CFG["thresholds"]
    else:
        chosen = json.loads((OUT/"CAL_LOCK.json").read_text())[f"{pct:g}_{arm}"]["threshold"]
        thresholds = [] if chosen is None else [chosen]
    clocks = [EvidenceClock(model.assets, threshold=h) for h in thresholds]
    starts = time.perf_counter()
    for k, t in enumerate(times):
        row = model.process(float(t), {field:data[field][k] for field in FIELDS})
        if clocks:
            on = logodds(row["M"])
            off = logodds(row["M_cause"]*row["restoration_probability"])
            for clock in clocks:
                clock.process(k, on, off)
    for clock in clocks:
        clock.finalize(float(times[-1]))
    save(output, dict(record=record, arm=arm, split=split, kind=kind, sigma_percent=pct,
                      elapsed_s=time.perf_counter()-starts, reports=len(times),
                      riccati_residual=err, bank_sha256=ready["bank_sha256"],
                      observation_sha256=ready["observation_sha256"],
                      fit_sha256=digest(folder/"fit.json"),
                      structured_sigma=estimated.tolist() if estimated is not None else None,
                      thresholds=[dict(threshold=clock.threshold, events=clock.events) for clock in clocks]))
    print("COMPLETE", record, pct, arm, split, flush=True)


def collect(split):
    p = SCI/"PAPER_CALIBRATION_B01/execution_request/truth_private/by_split"/f"{split}.json"
    truth = {r["id"]:r for r in json.loads(p.read_text())}
    results = {}
    for pct in CFG["sigma_percent"]:
        for arm in CFG["arms"]:
            by_threshold = {}
            for kind, records in CFG["split"][split].items():
                for record in records:
                    prediction = json.loads((OUT/split/f"{record}_{pct:g}_{arm}.json").read_text())
                    case = truth[record]
                    for pred in prediction["thresholds"]:
                        aa = alarms(pred)
                        hits, extras = match(case["events"], aa, case["duration_s"])
                        row = dict(record=record, kind=kind, parent=case["parent_id"],
                                   alarms=len(aa), extras=len(extras),
                                   load_hits=sum(x["family"]=="load" and x["timely"] for x in hits),
                                   line_hits=sum(x["family"]=="line" and x["timely"] for x in hits),
                                   loads=sum(x["family"]=="load" for x in hits),
                                   lines=sum(x["family"]=="line" for x in hits),
                                   hours=(case["duration_s"]-CFG["warmup_s"])/3600)
                        by_threshold.setdefault(pred["threshold"], []).append(row)
            scores = []
            for threshold, rows in by_threshold.items():
                assert len(rows) == sum(map(len, CFG["split"][split].values()))
                totals = {k:sum(r[k] for r in rows if r["kind"]=="event")
                          for k in ("load_hits","line_hits","loads","lines","extras")}
                count = sum(r["alarms"] for r in rows if r["kind"]=="normal")
                hours = sum(r["hours"] for r in rows if r["kind"]=="normal")
                scores.append(dict(threshold=threshold, **totals, normal_count=count, normal_hours=hours,
                                   far=count/hours, far_upper95=chi2.ppf(.95,2*(count+1))/(2*hours),
                                   parents=rows))
            key = f"{pct:g}_{arm}"
            if split == "CAL":
                feasible = [s for s in scores if s["far"]<=CFG["budget_per_hour"]]
                best = min(feasible, key=lambda s:(-s["load_hits"]-s["line_hits"],s["extras"],s["threshold"]),
                           default={"threshold":None})
                results[key] = dict(**best, grid=scores)
            else:
                results[key] = scores[0] if scores else {"threshold":None}
    return results


def main(stage):
    if stage == "evaluate":
        results = collect("TEST")
        comparisons = {}
        for pct in CFG["sigma_percent"]:
            ref = results[f"{pct:g}_family"].get("parents")
            if ref is None:
                continue
            ref = [r for r in ref if r["kind"]=="event"]
            for arm in CFG["arms"][1:]:
                key = f"{pct:g}_{arm}"
                rows = results[key].get("parents")
                if rows is None:
                    continue
                rows = [r for r in rows if r["kind"]=="event"]
                assert [r["parent"] for r in rows] == [r["parent"] for r in ref]
                comparisons[key] = bootstrap_difference(
                    [(r["load_hits"], r["loads"]) for r in rows],
                    [(r["load_hits"], r["loads"]) for r in ref], "ratio",
                    np.random.default_rng(CFG["bootstrap_seed"]), CFG["bootstrap_repetitions"])
        save(OUT/"TEST_RESULTS.json", dict(arms=results, paired_load_difference=comparisons))
        return
    split = stage
    if split == "TEST" and not (OUT/"CAL_LOCK.json").exists():
        raise FileNotFoundError("Complete and lock CAL before TEST")
    jobs = [(split,kind,r,p,a) for p in CFG["sigma_percent"] for kind,records in CFG["split"][split].items()
            for r in records for a in CFG["arms"]]
    with ProcessPoolExecutor(max_workers=3) as pool:
        for _ in pool.map(job,jobs):
            pass
    if split == "CAL":
        save(OUT/"CAL_LOCK.json", collect("CAL"))
    else:
        main("evaluate")


if __name__ == "__main__":
    if sys.argv[1] == "smoke":
        job(("CAL","event","C025",.05,"oracle"))
    else:
        main(sys.argv[1])
