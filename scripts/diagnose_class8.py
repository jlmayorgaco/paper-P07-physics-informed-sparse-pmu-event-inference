"""Paired class-8 diagnostic using the same physical trajectory and sensor noise."""

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from pmu_source_readout import sufficient_statistics, profile_scores
from competition_response_bank import BUSES

ARMS = ("clean_known", "composite_known", "unknown_strength", "unknown_onset_strength")


def measurement_view(pmus):
    frames = {}
    for bus, frame in pmus.items():
        fields = ["TIMESTAMP", "DATA_PRESENT", bus + "_Freq", bus + "_ROCOF"]
        fields += [
            f"{bus}_{q}{p}_{a}" for q in "VI" for p in "ABC" for a in ("MAG", "ANG")
        ]
        frames[int(bus[3:])] = frame.loc[frame.TIMESTAMP < 90, fields].copy()
    return frames


def evaluate(archive, out):
    sys.path.insert(0, str(archive / "V5"))
    from src.simulation.m9.generator import (
        get_template,
        extract_reference_statistics,
        generate_physical_truth,
        build_observed_pmu_frames,
        apply_cyber_events,
    )

    meta = archive / "data/metadata"
    raw = meta / "IEEE_39_Bus_Power_System.raw"
    ref = extract_reference_statistics(archive / "data/RAW0001")
    bank = dict(np.load("experiments/pmu_source_readout/bank.npz"))
    sites = bank["sites8"]
    rng = np.random.default_rng(610463)
    cases = [(s, c) for s in sites for c in ("isolated", "consecutive")]
    rng.shuffle(cases)
    rows = []
    for i, (site, context) in enumerate(cases):
        seed = int(rng.integers(1, 2**30))
        u = int(rng.integers(32, 152))
        onset = round(60 + u / 30, 3)
        strength = float(rng.uniform(0.8, 1.2))
        spec = get_template("EVENT8_UNKNOWN_COMPOSITE")
        for event in spec["physical_events"] + spec["cyber_events"]:
            event["start_time_s"] = round(event["start_time_s"] + onset - 4, 3)
            event["end_time_s"] = round(event["end_time_s"] + onset - 4, 3)
        spec["physical_events"][0]["target_bus"] = str(site)
        spec["physical_events"][0]["severity"] *= strength
        instruments = rng.choice(BUSES, 2, replace=False)
        for event, b in zip(spec["cyber_events"], instruments):
            event["target_pmus"] = [f"BUS{b}"]
        if context == "consecutive":
            prev = get_template("EVENT1_FAULT")["physical_events"][0]
            prev.update(target_bus="BUS4", start_time_s=59.28, end_time_s=59.5)
            spec["physical_events"].insert(0, prev)
        state = generate_physical_truth(
            raw, meta / "PMUbus_ Location.txt", spec, seed=seed, duration_s=90
        )
        pmus = build_observed_pmu_frames(state, raw, ref, seed=seed)
        clean = measurement_view(pmus)
        composite = measurement_view(
            apply_cyber_events(
                pmus, spec["cyber_events"], state.event_by_frame, seed=seed
            )
        )
        assert all(clean[b].iloc[:1800].equals(composite[b].iloc[:1800]) for b in BUSES)

        def known(frames):
            inner, energy = sufficient_statistics(frames, 8, bank)
            return inner, energy, strength * inner[u] - 0.5 * strength**2 * energy[u]

        _, _, s1 = known(clean)
        inner, energy, s2 = known(composite)
        a = np.clip(inner[u] / np.maximum(energy[u], 1e-12), 0, 2)
        scores = (
            s1,
            s2,
            a * inner[u] - 0.5 * a * a * energy[u],
            0.5 * profile_scores(composite, 8, inner, energy),
        )
        j = np.flatnonzero(sites == site).item()
        for arm, s in zip(ARMS, scores):
            order = np.argsort(-s, kind="stable")
            rival = order[0] if order[0] != j else order[1]
            rows.append(
                dict(
                    case=i,
                    context=context,
                    truth=site,
                    arm=arm,
                    predicted=sites[order[0]],
                    rank=int(np.flatnonzero(order == j)[0]) + 1,
                    margin=float(s[j] - s[rival]),
                    seed=seed,
                    onset=onset,
                    severity=strength,
                    angle_pmu=int(instruments[0]),
                    gain_pmu=int(instruments[1]),
                    max_known_score_change=float(np.max(abs(s1 - s2))),
                )
            )
    df = pd.DataFrame(rows)
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "diagnostic.csv", index=False)
    summary = {}
    prev = None
    for arm in ARMS:
        sub = df[df.arm == arm].sort_values("case")
        hit = sub["rank"].to_numpy() == 1
        summary[arm] = dict(
            n=len(hit),
            hits=int(hit.sum()),
            top3=int((sub["rank"] <= 3).sum()),
            median_rank=float(sub["rank"].median()),
            median_margin=float(sub.margin.median()),
            gained=None if prev is None else int((hit & ~prev).sum()),
            lost=None if prev is None else int((~hit & prev).sum()),
        )
        prev = hit
    s = summary[ARMS[0]]
    p = binomtest(s["hits"], s["n"], 1 / 39, alternative="greater").pvalue
    summary["gate"] = dict(p=p, opened=bool(p < 0.05 or s["median_rank"] <= 39 / 4))
    summary["max_known_score_change"] = float(df.max_known_score_change.max())
    (out / "diagnostic.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(summary)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for k in ("archive", "out"):
        p.add_argument(k, type=Path)
    a = p.parse_args()
    evaluate(a.archive.resolve(), a.out)
