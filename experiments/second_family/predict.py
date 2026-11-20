"""PMU-only predictions. No event schedules or labels are imported in this process."""

import argparse
import copy
import hashlib
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from shared import FIELDS, RESULT, RUN, TMP, archive_imports, digest, read, save
from spectral import alarm_features, channels

THRESHOLD = float(np.log(999.0))


def init():
    global worker, loader, clock_type, logodds, prefix_sha, cnn
    archive_imports()
    import worker
    from publication import EvidenceClock, logodds
    from prefix_contract import prefix_sha256
    from classifier import Predict

    loader = worker.load("second_family_frozen_runner", worker.OBSERVER / "run.py")
    clock_type, prefix_sha, cnn = EvidenceClock, prefix_sha256, Predict()


def estimate(model, previous, alarm):
    # An intervention that started before the previous diagnostic alarm
    # cannot be the new episode. Allow it to have ended by publication.
    eligible = (model.on > previous) & (model.on <= alarm) & (model.off > alarm)
    families = np.array([a["family"] == "line" for a in model.assets])
    label = families[model.cell[eligible]].astype(int)
    masses = np.bincount(label, weights=np.exp(model.logw[eligible]), minlength=2)
    return ("load", "line")[int(masses.argmax())] if masses.sum() > 0 else None


def record(task):
    pid, path, folder, obs_sha, expected_original_sha = task
    if digest(path) != obs_sha:
        raise ValueError("Observation changed")
    with np.load(path, allow_pickle=False) as z:
        t = z["time_s"]
        data = {k: z[k] for k in FIELDS}
    model, fit, ready = loader.load_particle(worker.RUNTIME, folder)
    prefix = prefix_sha(t, data)
    if not (
        ready["observation_sha256"] == expected_original_sha
        and ready["prefix_sha256"] == fit["prefix_sha256"] == prefix
        and fit["used_reports"] == 300
    ):
        raise ValueError("Frozen initialization has a different PMU prefix")
    clock = clock_type(model.assets, threshold=THRESHOLD)
    controls = {}
    pending = {}
    alarms = []
    x = channels(data)
    for k, tt in enumerate(t):
        pmu = {f: data[f][k] for f in FIELDS}
        row = model.process(float(tt), pmu)
        for control in controls.values():
            control.process(float(tt), pmu)
        action = clock.process(
            k, logodds(row["M"]), logodds(row["M_cause"] * row["restoration_probability"])
        )
        if action and action["kind"] == "off":
            if not controls:
                controls = {arm: copy.deepcopy(model) for arm in ("carry", "reset")}
            for name, control in controls.items():
                worker.collapse(control, name == "reset")
        if action and action["kind"] == "on":
            family = model.assets[action["cell"]]["family"]
            a = dict(report=k, prior=alarms[-1]["report"] if alarms else None, original=family)
            alarms.append(a)
            pending[k + 29] = a
        if k in pending:
            a = pending.pop(k)
            prev = a["prior"] if a["prior"] is not None else -1
            a["readout"] = k
            for name, arm in (
                ("lag", model),
                ("carry", controls.get("carry", model)),
                ("reset", controls.get("reset", model)),
            ):
                a[name] = estimate(arm, prev, a["report"])
            for name, sp in (("cnn", True), ("cnn_no_sub", False)):
                a[name] = cnn(alarm_features(x, a["prior"], a["report"], sp))
    return pid, alarms


def historical(plant, split):
    """Sealed original calls identify the shared clock and the quiet exposure."""
    receipt = RUN / (f"TEST_{plant}_SEAL.json" if split == "TEST" else "CAL_PREDICTIONS_SEAL.json")
    hashes = read(receipt)["predictions"]
    manifest = read(RUN / f"OBSERVATIONS_{plant}_{split}.json")
    quiet = []
    for row in manifest:
        if row["reports"] != 18001:
            continue
        pid = row["id"]
        file = (
            RUN
            / "work"
            / plant
            / split
            / (pid + "_nominal")
            / "predictions/history"
            / (format(THRESHOLD, ".16g") + ".json")
        )
        expected = hashes[str(file.relative_to(RUN)).replace("/", "\\")]
        if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
            raise ValueError("Archive prediction seal mismatch")
        prediction = read(file)
        assert prediction["observation_sha256"] == row["files"]["nominal"] and prediction["available"]
        quiet.append(
            dict(
                id=pid,
                reports=prediction["reports"],
                alarms=sum(a["kind"] == "alarm" for a in prediction["events"]),
            )
        )
    assert len(quiet) == 36
    return quiet


def run(workers):
    from freeze import verify

    verify()
    if (RESULT / "prediction_seal.json").exists():
        raise FileExistsError("Predictions sealed")
    observations = read(RESULT / "observations.json")["records"]
    original = {r["id"]: r["files"]["nominal"] for r in read(RUN / "OBSERVATIONS_P2_TEST.json")}
    tasks = [
        (
            r["id"],
            TMP / "pmu" / (r["id"] + ".npz"),
            RUN / "work/P2/TEST" / (r["id"] + "_nominal") / "nominal",
            r["observation_sha"],
            original[r["id"]],
        )
        for r in observations
    ]
    out = {}
    with ProcessPoolExecutor(workers, initializer=init) as pool:
        futures = [pool.submit(record, t) for t in tasks]
        for f in as_completed(futures):
            pid, a = f.result()
            out[pid] = a
            if len(out) % 6 == 0:
                print("completed", len(out), "/", len(tasks), flush=True)
    normal = {
        name: historical(plant, split)
        for name, plant, split in (("cal", "F01", "CAL"), ("test", "P2", "TEST"))
    }
    save(RESULT / "predictions.json", dict(events=dict(sorted(out.items())), normal=normal))
    save(
        RESULT / "prediction_seal.json",
        {k: digest(RESULT / (k + ".json")) for k in ("freeze", "observations", "predictions")},
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=5)
    run(parser.parse_args().workers)
