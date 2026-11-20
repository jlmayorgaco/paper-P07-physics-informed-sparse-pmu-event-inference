"""Secondary class-8 posterior using a physically site-dependent current-angle term."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from scipy.special import logsumexp
from competition_response_bank import frames_from, BUSES
from joint_class8 import marker_evidence
from pmu_source_readout import sufficient_statistics


def contrasts(frames):
    # All fully observed two-second pulses at trial onsets, in the same feature
    # order as pmu_source_pulse.features. Missing support omits this extra term.
    onset = np.arange(1800, 2580)
    off = onset + 60
    cols = []
    for bus in BUSES:
        df = frames[bus]
        for quantity in ("V", "I"):
            m = df[[f"BUS{bus}_{quantity}{p}_MAG" for p in "ABC"]].to_numpy()
            ang = df[[f"BUS{bus}_{quantity}{p}_ANG" for p in "ABC"]].to_numpy()
            z = m * np.exp(1j * np.deg2rad(ang))
            valid = np.isfinite(z) & (df.DATA_PRESENT.to_numpy()[:, None] == 1)
            cs = np.vstack([np.zeros(3), np.cumsum(np.where(valid, z, 0), axis=0)])
            ns = np.vstack([np.zeros(3), np.cumsum(valid, axis=0)])

            def avg(a, b):
                n = ns[b] - ns[a]
                return np.divide(
                    cs[b] - cs[a],
                    n,
                    out=np.full(n.shape, np.nan, dtype=complex),
                    where=n > 0,
                )

            ratio = avg(onset + 2, off - 2) / (
                (avg(onset - 60, onset - 2) + avg(off + 2, off + 60)) / 2
            )
            if quantity == "V":
                cols.append(np.nanmean(abs(ratio) - 1, axis=1))
            cols.append(np.nanmean(np.angle(ratio), axis=1))
    return np.column_stack(cols)


def physical_current_posterior(frames, bank, model):
    stats = sufficient_statistics(frames, 8, bank)
    if stats is None:
        return None
    inner, energy = stats
    z = contrasts(frames) / model["scale"]
    current = np.arange(2, 24, 3)
    voltage = np.setdiff1d(np.arange(24), current)
    cov = model["cov"]
    block = cov[np.ix_(voltage, current)]
    regression = np.linalg.solve(cov[np.ix_(voltage, voltage)], block)
    conditional = cov[np.ix_(current, current)] - block.T @ regression
    index = [int(s[3:]) - 1 for s in bank["sites8"]]
    means = model["means"][index]
    mu = means[:, current] - means[:, voltage] @ regression
    proj = np.linalg.solve(conditional, mu.T).T
    valid = np.flatnonzero(np.isfinite(z).all(axis=1))
    inner[valid] += (z[valid][:, current] - z[valid][:, voltage] @ regression) @ proj.T
    energy[valid] += (mu * proj).sum(axis=1)
    log_time = marker_evidence(frames)
    score = np.full_like(inner, -np.inf)
    for a in 0.5 + (np.arange(48) + 0.5) / 48:
        score = np.logaddexp(score, a * inner - 0.5 * a * a * energy)
    logp = logsumexp(score + (log_time - logsumexp(log_time))[:, None], axis=0)
    return np.exp(logp - logsumexp(logp))


def predict(root, out):
    raw = (root / "predictions.json").read_bytes()
    assert sha256(raw).hexdigest() == json.loads((root / "seal.json").read_text())
    base = Path("experiments/pmu_source_readout")
    bank = dict(np.load(base / "bank.npz"))
    model = dict(np.load(base / "pulse.npz"))
    rows = {}
    for key, r in json.loads(raw).items():
        family, site = r["joint"]
        if family == 8:
            p = physical_current_posterior(
                frames_from(root / "observations" / key), bank, model
            )
            if p is not None:
                site = str(bank["sites8"][np.argmax(p)])
        rows[key] = [family, site]
    out.mkdir(parents=True, exist_ok=True)
    path = out / "current_predictions.json"
    path.write_text(json.dumps(rows, indent=2) + "\n")
    (out / "current_seal.json").write_text(
        json.dumps(sha256(path.read_bytes()).hexdigest()) + "\n"
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for k in ("root", "out"):
        p.add_argument(k, type=Path)
    a = p.parse_args()
    predict(a.root, a.out)
