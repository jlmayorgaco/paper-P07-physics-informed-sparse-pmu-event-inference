"""Fit and apply an instrument-level contrast for the weak composite pulse."""

from pathlib import Path
import argparse
import sys

import numpy as np
from sklearn.covariance import LedoitWolf
from competition_response_bank import BUSES


def features(frames, on, off):
    width = off - on
    if width < 12 or on - width < 0 or off + width >= len(frames[BUSES[0]]):
        return None
    vec = []
    # Exclude the immediate edges and interpolate the baseline across the pulse.
    before = slice(on - width, on - 2)
    after = slice(off + 2, off + width)
    inside = slice(on + 2, off - 2)
    for bus in BUSES:
        df = frames[bus]
        for q in ("V", "I"):
            mag = df[[f"BUS{bus}_{q}{p}_MAG" for p in "ABC"]].to_numpy()
            ang = df[[f"BUS{bus}_{q}{p}_ANG" for p in "ABC"]].to_numpy()
            z = mag * np.exp(1j * np.deg2rad(ang))
            z[df.DATA_PRESENT.to_numpy() != 1] = np.nan
            ref = (np.nanmean(z[before], axis=0) + np.nanmean(z[after], axis=0)) / 2
            step = np.nanmean(z[inside], axis=0) / ref
            if q == "V":
                vec.append(np.nanmean(abs(step) - 1))
            vec.append(np.nanmean(np.angle(step)))
    return np.array(vec)


def build(archive, out):
    sys.path.insert(0, str(archive / "V5"))
    from src.simulation.m9.generator import (
        get_template,
        extract_reference_statistics,
        generate_physical_truth,
        build_observed_pmu_frames,
    )

    raw = archive / "data/metadata/IEEE_39_Bus_Power_System.raw"
    pmus = archive / "data/metadata/PMUbus_ Location.txt"
    stats = extract_reference_statistics(archive / "data/RAW0001")
    rng = np.random.default_rng(481009)
    rows = []
    for bus in range(1, 40):
        spec = get_template("EVENT0_NORMAL")
        windows = []
        for j in range(20):
            start = 8 + j * 12 + rng.uniform(0, 1)
            duration = rng.uniform(1.7, 2.3)
            if j % 2:
                prior = get_template("EVENT1_FAULT")["physical_events"][0]
                prior["end_time_s"] = start - rng.uniform(1.5, 5.5)
                prior["start_time_s"] = prior["end_time_s"] - prior["duration_s"]
                prior["target_bus"] = "BUS4"
                spec["physical_events"].append(prior)
            event = get_template("EVENT8_UNKNOWN_COMPOSITE")["physical_events"][0]
            event.update(
                start_time_s=start,
                end_time_s=start + duration,
                duration_s=duration,
                target_bus=f"BUS{bus}",
            )
            event["severity"] *= rng.uniform(0.8, 1.2)
            spec["physical_events"].append(event)
            windows.append(
                (int(round(30 * start)), int(round(30 * (start + duration))))
            )
        seed = int(rng.integers(1, 2**30))
        state = generate_physical_truth(raw, pmus, spec, seed=seed, duration_s=250)
        frames = {
            int(k[3:]): v
            for k, v in build_observed_pmu_frames(state, raw, stats, seed=seed).items()
        }
        rows.append([features(frames, on, off) for on, off in windows])
    x = np.array(rows)
    mu = x.mean(axis=1)
    residual = (x - mu[:, None, :]).reshape(-1, x.shape[2])
    scale = np.maximum(residual.std(axis=0), 1e-9)
    cov = LedoitWolf().fit(residual / scale).covariance_
    np.savez_compressed(out / "pulse.npz", means=mu / scale, scale=scale, cov=cov)


def location(frames, pulse, model):
    if not pulse:
        return None
    start, end, _ = pulse
    # The current-gain marker overlaps the weak physical step in this M9 template.
    x = features(frames, start - 12, end - 6)
    if x is None:
        return None
    valid = np.isfinite(x)
    if valid.sum() < 12:
        return None
    z = x[valid] / model["scale"][valid]
    mu = model["means"][:, valid]
    cov = model["cov"][np.ix_(valid, valid)]
    proj = np.linalg.solve(cov, mu.T).T
    inner = proj @ z
    energy = (mu * proj).sum(axis=1)
    scale = np.clip(inner / np.maximum(energy, 1e-12), 0.6, 1.4)
    return f"BUS{1+np.argmax(2*scale*inner-scale**2*energy)}"


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    build(a.archive.resolve(), a.out)
