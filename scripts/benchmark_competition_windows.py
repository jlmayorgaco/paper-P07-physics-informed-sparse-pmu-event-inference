"""Synthetic nine-class window benchmark. Run prepare, predict, score in separate processes.

Arguments: stage, experiment directory, scientific archive, extracted original ZIP.
Use a new directory for each cohort. Predict reads only opaque observation folders.
Score one 30-s window per record following 60 s of normal startup. Localization
is exact target equality across all true nonnormal windows (also report joint hits).
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import sys

from replay_competition_router import route


def save(path, obj):
    with path.open("x", encoding="utf8") as out:
        json.dump(obj, out, indent=2)


def prepare(root, archive, *, seed=202611190731, repetitions=3, move_integrity=False,
            asset_catalog=None, normal_only=False, vary_physical=False):
    sys.path.insert(0, str(archive / "V5"))
    from src.simulation.m9.generator import (get_template, list_templates,
        extract_reference_statistics, generate_physical_truth, build_observed_pmu_frames,
        apply_cyber_events)
    rng = random.Random(seed)
    meta = archive / "data/metadata"
    network = meta / "IEEE_39_Bus_Power_System.raw"
    stats = extract_reference_statistics(archive / "data/RAW0001")
    truth = {}
    for template in sorted(n for n in list_templates() if n.startswith("TEMPLATE_EVENT")):
        code = int(re.search(r"EVENT(\d)", template)[1])
        if normal_only and code != 0:
            continue
        assets = list(asset_catalog.get(code, ())) if asset_catalog else []
        schedule = [assets[i % len(assets)] for i in range(repetitions)] if assets else []
        if vary_physical:
            rng.shuffle(schedule)
        for repetition in range(repetitions):
            spec = get_template(template)
            delay = rng.uniform(60.1, 66)
            case = f"{rng.getrandbits(64):016x}"
            seed = rng.randrange(1, 2**31)
            folder = root / "observations" / case
            folder.mkdir(parents=True)
            physical, quality = spec["physical_events"], spec["cyber_events"]
            if asset_catalog and physical and code in asset_catalog:
                event = physical[0]
                target = schedule[repetition]
                if event.get("target_line"):
                    event["target_line"] = target
                else:
                    event["target_bus"] = target
            if move_integrity and code in (5, 6, 7):
                original = quality[0]["target_pmus"][0]
                # Rotate through sites excluded from this template in development.
                candidates = [f"BUS{b}" for b in (2,5,6,10,19,22,29,39) if f"BUS{b}" != original]
                for event in quality:
                    event["target_pmus"] = [candidates[repetition % len(candidates)]]
            if move_integrity and asset_catalog and code == 8:
                sites = ("BUS2","BUS5","BUS6","BUS10","BUS19","BUS22","BUS29","BUS39")
                for j,event in enumerate(quality):
                    event["target_pmus"] = [sites[(repetition + 3*j) % len(sites)]]
            for event in physical + quality:
                event["start_time_s"] += delay
                event["end_time_s"] += delay
            if vary_physical:
                for event in physical:
                    event["severity"] *= rng.uniform(.8, 1.2)
                    event["duration_s"] *= rng.uniform(.85, 1.15)
                    event["end_time_s"] = event["start_time_s"] + event["duration_s"]
            state = generate_physical_truth(network, meta / "PMUbus_ Location.txt",
                                            spec, seed=seed, duration_s=90)
            pmus = build_observed_pmu_frames(state, network, stats, seed=seed)
            pmus = apply_cyber_events(pmus, quality, state.event_by_frame, seed=seed)
            for bus, df in pmus.items():
                meas = df.loc[df.TIMESTAMP < 90].drop(columns="Event")
                allowed = {"TIMESTAMP", "DATA_PRESENT", bus+"_Freq", bus+"_ROCOF"}
                allowed.update(f"{bus}_{q}{p}_{a}" for q in "VI" for p in "ABC" for a in ("MAG","ANG"))
                assert set(meas) == allowed
                meas.to_csv(folder / f"Bus{bus[3:]}_Competition_Data_nanmask.csv", index=False)
            source = "none"
            if physical:
                line = physical[0].get("target_line")
                source = physical[0]["target_bus"] if not line else "LINE" + "-".join(
                    map(str, sorted(map(int, re.findall(r"\d+", line)))))
            elif quality:
                source = quality[0]["target_pmus"][0].replace("BUS", "PMU")
            truth[case] = dict(code=code, source=source, seed=seed)
            if asset_catalog and physical:
                truth[case]["onset_s"] = physical[0]["start_time_s"]
    save(root / "truth.json", truth)


def predict(root, archive, submitted):
    sys.path.insert(0, str(submitted))
    sys.path.insert(0, str(archive / "experiments/PAPER_ALLEVENTS_V1/frozen_v2"))
    import raw_io, integrity, attribute_v2
    from src.models.hybrid_submission import run_hybrid_submission_prediction
    expert = attribute_v2.Attributor()
    records = {}
    for folder in sorted((root / "observations").iterdir()):
        out = root / "native" / folder.name / "predictions.csv"
        _, diag = run_hybrid_submission_prediction(folder, out, ml_model_dir=submitted / "models")
        win = diag["window_predictions"][-1]
        assert diag["route"] == "ml_windowed" and 59.9 <= win["start_time_s"] <= 60.1
        code, source = int(win["predicted_event"]), str(win["predicted_location"])
        obs = raw_io.load(folder)
        flags = integrity.flags(obs, expert.net)
        _, episodes = expert.run(folder, flags)
        in_window = obs["t"] >= 60
        missing = (~obs["present"][in_window]).sum(axis=0)
        corrupt = flags[in_window].sum(axis=0)
        phys = [e for e in episodes if 60 <= e["onset_s"] < 90 and e.get("cls") in (1,2,3,4)]
        # Each expert sees the entire prefix up to the common decision time.
        end = float(obs["t"][-1])
        evidence = [dict(available=True, family_code=e["cls"], source=e["location"],
                         emitted_s=end, last_report_used_s=end) for e in phys if e.get("location") not in (None,"none")]
        physical = (phys[0]["cls"], phys[0]["location"]) if phys else (0, "none")
        if missing.max():
            physical = (6, physical[1]) if phys else (5, f"PMU{raw_io.PMUS[missing.argmax()]}")
        elif corrupt.max():
            physical = (7, f"PMU{raw_io.PMUS[corrupt.argmax()]}")
        status = "missing" if code in (5,6) else "corrupt" if code == 7 else "nominal"
        frontend = dict(legacy_event=code, available=True, emitted_s=end, last_report_used_s=end,
                        window_start_s=60, window_end_s=90, window_index=2, integrity_status=status,
                        integrity_sources=[], physical_event=code, physical_source=source)
        hybrid = route(frontend, evidence)
        records[folder.name] = dict(original=[code, source], physical=physical,
            hybrid=[hybrid["event_code"], hybrid["physical_source"]], route=hybrid["source_route"])
    save(root / "predictions.json", records)
    save(root / "seal.json", hashlib.sha256((root / "predictions.json").read_bytes()).hexdigest())


def score(root):
    from sklearn.metrics import confusion_matrix, f1_score
    predictions = (root / "predictions.json").read_bytes()
    assert hashlib.sha256(predictions).hexdigest() == json.loads((root / "seal.json").read_text())
    rows = json.loads(predictions)
    truth = json.loads((root / "truth.json").read_text())
    assert rows.keys() == truth.keys()
    ids = sorted(rows)
    codes = [truth[i]["code"] for i in ids]
    assert Counter(codes) == {i: 3 for i in range(9)}
    positive = [i for i in ids if truth[i]["code"]]
    results = {}
    for name in ("original", "physical", "hybrid"):
        pred = [rows[i][name][0] for i in ids]
        results[name] = dict(macro_f1=f1_score(codes,pred,labels=list(range(9)),average="macro",zero_division=0),
            exact=sum(rows[i][name][1] == truth[i]["source"] for i in positive),
            joint=sum(rows[i][name] == [truth[i]["code"],truth[i]["source"]] for i in positive),
            positive_windows=len(positive), confusion=confusion_matrix(codes,pred,labels=list(range(9))).tolist())
    results["source_routes"] = dict(Counter(r["route"] for r in rows.values()))
    save(root / "results.json", results)
    print(json.dumps(results))


def check_dynamic_startup(root, archive):
    """Apply the main paper's frozen admission test to the same initial PMU reports."""
    import numpy as np
    import pandas as pd
    deps = archive / "experiments/PAPER_RECOVERY_C03/run/dependencies"
    sys.path.insert(0, str(deps / "frozen_R11/physics"))
    from conditional_prefix import prefix_statistics
    times = np.arange(300) / 30
    buses = (2, 5, 6, 10, 19, 22, 29, 39)
    fields = dict(voltage_magnitude="VA_MAG", voltage_angle="VA_ANG",
                  current_magnitude="IA_MAG", current_angle="IA_ANG",
                  frequency="Freq", rocof="ROCOF")
    admission = {}
    for folder in sorted((root / "observations").iterdir()):
        frames = [pd.read_csv(folder / f"Bus{b}_Competition_Data_nanmask.csv", nrows=300)
                  for b in buses]
        assert all(np.allclose(f.TIMESTAMP, times, atol=.00051) for f in frames)
        data = {k: np.column_stack([f[f"BUS{b}_{v}"].where(f.DATA_PRESENT == 1)
                                    for b, f in zip(buses, frames)]) for k, v in fields.items()}
        try:
            prefix_statistics(deps / "runtime", times, data)
            admission[folder.name] = "admitted"
        except ValueError as exc:
            admission[folder.name] = str(exc)
    save(root / "dynamic_admission.json", admission)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("stage", choices=["prepare","predict","score","startup"])
    p.add_argument("directory", type=Path)
    p.add_argument("archive", type=Path)
    p.add_argument("submitted", type=Path)
    a = p.parse_args()
    if a.stage == "prepare":
        prepare(a.directory, a.archive.resolve())
    elif a.stage == "predict":
        predict(a.directory, a.archive.resolve(), a.submitted.resolve())
    elif a.stage == "startup":
        check_dynamic_startup(a.directory, a.archive.resolve())
    else:
        score(a.directory)
