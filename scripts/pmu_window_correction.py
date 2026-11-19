"""Recovery-window corrections from frequency persistence, phase balance and spatial voltage decay."""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse.csgraph import shortest_path

import competition_electrical_localizer as electrical

BUSES = electrical.prior.bank.BUSES


def distance_signatures(data):
    lines = pd.read_csv(data / "topology/ieee39/branches_physical.csv")
    graph = np.zeros((39, 39))
    for line in lines.itertuples():
        a, b = line.from_bus - 1, line.to_bus - 1
        graph[a, b] = graph[b, a] = abs(complex(line.r, line.x))
    dist = shortest_path(graph, directed=False)
    assert np.isfinite(dist).all()
    to_bus = dist[np.array(BUSES) - 1]
    signatures = electrical.network_signatures(data)
    result = {}
    for family, sites in signatures.items():
        if family == 2:
            ends = np.array([s.removeprefix("LINE").split("-") for s in sites], int) - 1
            distances = np.minimum(to_bus[:, ends[:, 0]], to_bus[:, ends[:, 1]])
        else:
            idx = [int(s.removeprefix("BUS")) - 1 for s in sites]
            distances = to_bus[:, idx]
        result[family] = (list(sites), distances.T)
    return result


def physical_evidence(frames):
    voltages, frequency, asymmetry = [], [], []
    for bus in BUSES:
        df = frames[bus]
        valid = df.DATA_PRESENT.to_numpy() == 1
        mags = df[[f"BUS{bus}_V{p}_MAG" for p in "ABC"]].to_numpy(copy=True)
        mags[~valid] = np.nan
        volts = np.median(mags / np.nanmedian(mags[:900], axis=0), axis=1) - 1
        voltages.append(volts)
        freq = df[f"BUS{bus}_Freq"].where(valid)
        ref = freq.iloc[:900]
        frequency.append(freq.iloc[-300:].median() - ref.median())
        # Balanced three-phase changes cancel in interphase angle differences.
        angles = df[[f"BUS{bus}_V{p}_ANG" for p in "ABC"]].to_numpy(copy=True)
        angles[~valid] = np.nan
        difference = angles - np.roll(angles, 1, axis=1)
        ref = np.rad2deg(
            np.angle(np.nanmean(np.exp(1j * np.deg2rad(difference[:900])), axis=0))
        )
        residual = (difference - ref + 180) % 360 - 180
        scaled = residual / np.maximum(np.nanstd(residual[:900], axis=0), 1e-5)
        score = pd.DataFrame(scaled[1800:]).rolling(12).mean().abs().max().max()
        asymmetry.append(score)
    return np.array(voltages).T, np.array(frequency), np.array(asymmetry)


def spatial_estimate(volts, family, dictionary, length):
    # A short dip is measured at its nadir; sustained steps use their late displacement.
    if family == 1:
        smooth = (
            pd.DataFrame(volts[1800:]).rolling(3, min_periods=3).median().to_numpy()
        )
        k = np.nanargmin(np.nanmedian(smooth, axis=1))
        displacement = -smooth[k]
    else:
        displacement = np.abs(np.nanmedian(volts[-300:], axis=0))
    sites, distances = dictionary[family]
    mask = np.isfinite(displacement)
    if mask.sum() < 5:
        return None
    y = displacement[mask]
    y -= y.mean()
    atoms = np.exp(-distances[:, mask] / length)
    atoms -= atoms.mean(axis=1, keepdims=True)
    gain = np.maximum(atoms @ y, 0) ** 2 / np.maximum(
        (atoms * atoms).sum(axis=1), 1e-12
    )
    if np.ptp(gain) == 0:
        return None
    return sites[np.argmax(gain)]


def corrected(frames, baseline, dictionary, selected):
    volts, frequency, asymmetry = physical_evidence(frames)
    family, source = baseline
    if family in (0, 1, 7) and np.isfinite(asymmetry).all():
        order = np.argsort(asymmetry)
        top, second = order[-1], order[-2]
        if asymmetry[top] >= 1.8 and asymmetry[top] >= 1.5 * asymmetry[second]:
            return [7, f"PMU{BUSES[top]}"]
    if family in (3, 4) and np.isfinite(frequency).sum() >= 5:
        if np.count_nonzero(frequency < -0.015) >= 5:
            family = 3
        elif np.count_nonzero(abs(frequency) < 0.008) >= 5:
            family = 4
        if family != baseline[0]:
            source = electrical.rank_source(
                frames, [family, "none"], electrical.signatures
            )[1]
    if str(family) in selected:
        estimate = spatial_estimate(volts, family, dictionary, selected[str(family)])
        if estimate is not None:
            source = estimate
    return [family, source]
