"""Fit, freeze, predict and score the paired PMU recovery experiment."""
import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import sys

for name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[name] = "1"

import joblib
import numpy as np
from scipy.stats import beta, binomtest, chi2
import sklearn

import estimator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/second_family"))
from shared import RUN

TMP = ROOT / "tmp/modal_recovery"
RESULT = HERE / "results"
ARMS = ("mean", "modal", "quadratic")


def digest(path):
    value = path.read_bytes()
    if path.suffix in {".py", ".md", ".json"}:
        value = value.replace(b"\r\n", b"\n")
    return sha256(value).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf8") as out:
        json.dump(value, out, indent=2, allow_nan=False)
        out.write("\n")


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def unpack(path):
    with np.load(path, allow_pickle=False) as z:
        return z["y"], int(z["clearance"])


def quiet(plant, split, models, thresholds=None):
    manifest_path = RUN / f"OBSERVATIONS_{plant}_{split}.json"
    manifest = read(manifest_path)
    cases = [r for r in manifest if r["reports"] == 18001]
    assert len(cases) == 36
    summaries = {}
    for row in cases:
        key = row["id"]
        path = RUN / "observations" / plant / split / (key + "_nominal.npz")
        if digest(path) != row["files"]["nominal"]:
            raise ValueError(f"Quiet observation checksum mismatch for {key}")
        with np.load(path, allow_pickle=False) as z:
            y = np.column_stack((z["voltage_magnitude"] * (np.sqrt(3) / 345000), z["current_magnitude"]))
        result = {}
        for arm, model in models.items():
            # Chunk with both sides of each candidate cut intact. Each publication occurs once.
            pieces = []
            for start in range(360, len(y) - 59, 1800):
                stop = min(start + 1800 + 59, len(y))
                reports, scores, _, _ = model.scan(y[start:stop], 0)
                assert np.array_equal(reports, np.arange(59, stop - start))
                pieces.append(scores)
            scores = np.concatenate(pieces)
            assert len(scores) == len(y) - 360 - 59 and np.isfinite(scores).all()
            out = {"max": float(scores.max()), "scored_reports": len(scores)}
            if thresholds is not None:
                above = scores > thresholds[arm]
                out["episodes"] = int(np.count_nonzero(above & ~np.r_[False, above[:-1]]))
            result[arm] = out
        summaries[key] = result
    return summaries


def fit():
    target = RESULT / "freeze.json"
    if target.exists():
        raise FileExistsError(target)
    with np.load(TMP / "templates.npz", allow_pickle=False) as z:
        templates = dict(z)
    train = [unpack(p) for p in sorted((TMP / "fit").glob("*.npz"))]
    cal_paths = sorted((TMP / "cal").glob("*.npz"))
    assert len(train) == 48 and len(cal_paths) == 80
    from freeze import verify as verify_science_inputs
    verify_science_inputs()
    models = {arm: estimator.fit(templates, train, arm) for arm in ARMS}
    calibration = {p.stem: {k: float(m.scan(*unpack(p))[1].max()) for k, m in models.items()} for p in cal_paths}
    normal = quiet("F01", "CAL", models)
    fit_paths = {}
    thresholds = {}
    order = math.ceil((len(cal_paths) + 1) * .95)
    RESULT.mkdir(parents=True, exist_ok=True)
    for arm, m in models.items():
        path = RESULT / (arm + ".joblib")
        joblib.dump(m, path, compress=3)
        fit_paths[path.name] = digest(path)
        recovery_bound = sorted(row[arm] for row in calibration.values())[order - 1]
        quiet_bound = max(row[arm]["max"] for row in normal.values())
        thresholds[arm] = dict(recovery=recovery_bound, quiet=quiet_bound, value=max(recovery_bound, quiet_bound))
    save(RESULT / "calibration.json", dict(recovery=calibration, quiet=normal))
    files = ["data.py", "estimator.py", "study.py", "PROTOCOL.md", "results/calibration.json"]
    save(target, dict(models=fit_paths, files={k: digest(HERE / k) for k in files},
                      thresholds=thresholds, mode_hz=float(estimator.frequency(templates["modes_hz"])),
                      modes_hz=templates["modes_hz"].tolist(), template_sha=digest(TMP / "templates.npz"),
                      fit_cal_inputs={p.relative_to(TMP).as_posix(): digest(p) for split in ("fit", "cal")
                                      for p in sorted((TMP / split).glob("*.npz"))},
                      numpy=np.__version__, sklearn=sklearn.__version__, archive=str(RUN),
                      upstream_sha=digest(ROOT / "experiments/second_family/results/freeze.json")))
    print("Frozen", thresholds, flush=True)


def verify():
    f = read(RESULT / "freeze.json")
    for folder, items in ((HERE, f["files"]), (RESULT, f["models"])):
        for name, expected in items.items():
            if digest(folder / name) != expected:
                raise ValueError(f"Source or model changed: {name}")
    return f


def predict():
    f = verify()
    models = {arm: joblib.load(RESULT / (arm + ".joblib")) for arm in ARMS}
    thresholds = {k: v["value"] for k, v in f["thresholds"].items()}
    paths = sorted((TMP / "test").glob("*.npz"))
    assert len(paths) == 192 and not (RESULT / "predictions.json").exists()
    calls = {}
    for p in paths:
        y, clear = unpack(p)
        row = {}
        for arm, m in models.items():
            reports, scores, families, sources = m.scan(y, clear)
            hits = np.flatnonzero(scores > thresholds[arm])
            row[arm] = None
            if hits.size:
                i = hits[0]
                row[arm] = dict(report=int(reports[i]), family=str(families[i]), source=str(sources[i]))
        calls[p.stem] = dict(arms=row, observation_sha=digest(p))
    normal = quiet("P2", "TEST", models, thresholds)
    save(RESULT / "predictions.json", dict(freeze_sha=digest(RESULT / "freeze.json"), calls=calls, quiet=normal,
                                          target_sha=(TMP / "test_truth.sha256").read_text(encoding="ascii")))
    print("Predictions saved before unblinding", digest(RESULT / "predictions.json"), flush=True)


def exact_interval(success, total):
    return [float(beta.ppf(.025, success, total-success+1)) if success else 0.,
            float(beta.ppf(.975, success+1, total-success)) if success < total else 1.]


def score():
    pred_path = RESULT / "predictions.json"
    pred = read(pred_path)
    assert pred["freeze_sha"] == digest(RESULT / "freeze.json")
    target_path = TMP / "test_truth.json"
    assert sha256(target_path.read_bytes()).hexdigest() == pred["target_sha"]
    truth = read(target_path)
    assert set(pred["calls"]) == set(truth)
    outcomes = {}
    measures = ("timely", "family", "site", "recovery_false_alarm", "early_positive_alarm")
    for key, t in truth.items():
        row = {}
        for arm, a in pred["calls"][key]["arms"].items():
            event = t["family"] != "none"
            time = a["report"] / 30 if a else math.inf
            timely = event and t["on"] <= time < t["off"]
            row[arm] = dict(timely=timely, family=bool(timely and a["family"] == t["family"]),
                            site=bool(timely and a["source"] == t["source"]),
                            recovery_false_alarm=not event and a is not None,
                            early_positive_alarm=event and time < t["on"])
        outcomes[key] = row
    pos = [k for k,t in truth.items() if t["family"] != "none"]
    neg = [k for k,t in truth.items() if t["family"] == "none"]
    assert len(pos) == len(neg) == 96
    assert sorted(truth[k]["parent"] for k in pos) == sorted(truth[k]["parent"] for k in neg)
    assert len({truth[k]["parent"] for k in pos}) == 96
    results = {}
    for metric in measures:
        group = neg if metric == "recovery_false_alarm" else pos
        baseline = np.array([outcomes[k]["mean"][metric] for k in group], dtype=int)
        modal = np.array([outcomes[k]["modal"][metric] for k in group], dtype=int)
        polynomial = np.array([outcomes[k]["quadratic"][metric] for k in group], dtype=int)
        plus, minus = int(sum(modal > baseline)), int(sum(modal < baseline))
        plus_poly, minus_poly = int(sum(modal > polynomial)), int(sum(modal < polynomial))
        results[metric] = dict(n=len(group), mean=int(baseline.sum()), modal=int(modal.sum()),
                               quadratic=int(polynomial.sum()), modal_more_than_quad=plus_poly,
                               quad_more_than_modal=minus_poly, exact_p_vs_quad=(
                                   float(binomtest(plus_poly, plus_poly+minus_poly).pvalue) if plus_poly+minus_poly else 1.
                               ),
                               modal_more=plus, mean_more=minus,
                               exact_p=float(binomtest(plus, plus+minus).pvalue) if plus+minus else 1.,
                               modal_ci95=exact_interval(int(modal.sum()),len(group)))
    by_family = {family:{arm:sum(outcomes[k][arm]["family"] for k in pos if truth[k]["family"]==family)
                         for arm in ARMS} for family in ("load", "line")}
    quiet_results = {}
    for arm in ARMS:
        rows=[r[arm] for r in pred["quiet"].values()]
        n=sum(r["episodes"] for r in rows)
        hours=sum(r["scored_reports"] for r in rows)/30/3600
        quiet_results[arm]=dict(alarms=n,hours=hours,poisson_upper95_h=float(chi2.ppf(.95, 2*(n+1))/2/hours))
    save(RESULT / "truth.json", truth)
    value=dict(prediction_sha=digest(pred_path), truth_sha=digest(RESULT / "truth.json"),
               outcomes=results, family_counts=by_family, quiet=quiet_results)
    save(RESULT / "scores.json", value)
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("fit", "predict", "score"))
    stage = parser.parse_args().stage
    {"fit": fit, "predict": predict, "score": score}[stage]()
