"""Check the common-covariance projection on frozen IEEE-39 mean responses."""

import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import solve_triangular

SOURCE = Path(__file__).resolve().parents[1] / "channel_information_20261112"
sys.path.insert(0, str(SOURCE))
import run_channel_diagnostic as channel


def main():
    provenance = json.loads((SOURCE / "diagnostic_summary.json").read_text())["source"]
    for path, key in [(channel.SNAPSHOT, "snapshot_sha256"), (channel.ASSETS_PATH, "assets_sha256")]:
        if channel.sha256(path) != provenance[key]:
            raise ValueError(f"Frozen input changed: {path.name}")

    bank = channel.load_snapshot()
    assets = channel.read_assets()
    horizon = 30
    channels = channel.CHANNELS["VI"]
    indices = channel.channel_indices(horizon, channels)
    covariance, _ = channel.raw_covariance(bank, horizon)
    factor, scales = channel.stable_factor(covariance[np.ix_(indices, indices)])
    means = channel.event_mean(bank, assets, horizon).reshape(len(assets), -1)[:, indices]
    signals = solve_triangular(factor, means.T / scales[:, None], lower=True)
    directions, singular, _ = np.linalg.svd(signals, full_matrices=False)
    tolerance = max(signals.shape) * np.finfo(float).eps * singular[0]
    basis = directions[:, singular > tolerance]
    reduced = basis.T @ signals

    # Independent reference from the earlier fixed-onset, fixed-severity audit.
    asset_index = {asset["id"]: i for i, asset in enumerate(assets)}
    with (SOURCE / "pairwise_separation.csv").open(newline="") as stream:
        reference = [r for r in csv.DictReader(stream) if int(r["reports"]) == horizon]
    if len(reference) != len(assets) * (len(assets) - 1):
        raise ValueError("Incomplete archived source comparisons")
    errors = []
    for row in reference:
        i, j = asset_index[row["source"]], asset_index[row["competitor"]]
        archived = float(row["D2_VI"])
        difference = reduced[:, i] - reduced[:, j]
        errors.append(abs(difference @ difference - archived) / max(1.0, archived))

    # Whitened observations around null and each mean; include noise orthogonal to the span.
    rng = np.random.default_rng(1731)
    centers = np.column_stack((np.zeros(signals.shape[0]), signals))
    observations = np.repeat(centers, 4, axis=1)
    observations += rng.normal(size=observations.shape)
    full_log_bf = signals.T @ observations - 0.5 * np.sum(signals**2, axis=0)[:, None]
    small_log_bf = reduced.T @ (basis.T @ observations) - 0.5 * np.sum(reduced**2, axis=0)[:, None]
    relative_error = np.abs(small_log_bf - full_log_bf) / np.maximum(1.0, np.abs(full_log_bf))
    if max(errors) > 1e-8 or relative_error.max() > 1e-8:
        raise ArithmeticError("The projected experiment did not reproduce the reference geometry or likelihoods")
    print(f"{signals.shape[0]} V/I coordinates, {len(assets)} fixed alternatives, numerical rank {basis.shape[1]}")
    print(f"{len(errors)} directed comparisons, maximum scaled squared-distance error {max(errors):.3e}")
    print(f"{full_log_bf.size} log likelihood ratios, maximum scaled error {relative_error.max():.3e}")


if __name__ == "__main__":
    main()
