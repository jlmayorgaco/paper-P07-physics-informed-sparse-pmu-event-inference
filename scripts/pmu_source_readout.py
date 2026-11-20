"""Match a calibrated space-time voltage response to a frozen family decision."""

import numpy as np
from scipy.signal import fftconvolve
from competition_response_bank import BUSES
from competition_held_locations import residual_pulse


def voltage_residuals(frames, freq):
    t = frames[BUSES[0]].TIMESTAMP.to_numpy()
    if len(t) != 2700 or not np.allclose(t, np.arange(2700) / 30, atol=0.00051):
        return None
    baseline = t < 48
    planes = np.full((2, len(t), len(BUSES)), np.nan)
    sigma = np.full((2, len(BUSES)), np.inf)
    for b, bus in enumerate(BUSES):
        df = frames[bus]
        present = df.DATA_PRESENT.to_numpy() == 1
        for q, suffix in enumerate(("MAG", "ANG")):
            x = df[[f"BUS{bus}_V{p}_{suffix}" for p in "ABC"]].to_numpy(copy=True)
            x[~present] = np.nan
            if q == 0:
                x = x / np.nanmedian(x[baseline], axis=0) - 1
            else:
                z = np.exp(1j * np.deg2rad(x))
                x = np.angle(z * np.nanmean(z[baseline], axis=0).conj())
            phase_var = np.nanmedian(abs(np.diff(x[baseline], axis=0)), axis=0) ** 2
            precision = 1 / np.maximum(phase_var, 1e-12)
            total = np.sum(np.where(np.isfinite(x), precision, 0), axis=1)
            obs = np.divide(
                np.nansum(x * precision, axis=1),
                total,
                out=np.full(len(t), np.nan),
                where=total > 0,
            )
            f = freq[q, b]
            harmonics = 2 * np.pi * t[:, None] * f
            basis = np.column_stack(
                [np.ones(len(t)), np.sin(harmonics), np.cos(harmonics)]
            )
            use = baseline & np.isfinite(obs)
            if use.sum() < 300:
                continue
            fit = basis @ np.linalg.lstsq(basis[use], obs[use], rcond=None)[0]
            y = obs - fit
            if q == 0:
                y /= 1 + fit
            planes[q, :, b] = y
            sigma[q, b] = max(1e-6, 1.4826 * np.median(abs(y[use] - np.median(y[use]))))
    return planes, sigma


def subtract_recovery(planes, wave):
    # If a coherent sag began just before this decision window, fit its tail
    # from prefix reports only. Keep each sensor amplitude free.
    start = 1800
    trace = np.nanmedian(planes[0, start - 240 : start], axis=1)
    crossing = np.flatnonzero(trace < -0.025)
    if not len(crossing):
        return
    onset = start - 240 + int(crossing[0])
    for q in range(2):
        h = wave[q, 0]
        pre = h[: start - onset, None]
        y = planes[q, onset:start]
        energy = np.sum(np.isfinite(y) * pre**2, axis=0)
        amplitude = np.nansum(y * pre, axis=0) / np.maximum(energy, 1e-9)
        tail = h[start - onset :]
        planes[q, start : start + len(tail)] -= tail[:, None] * amplitude


def correlations(x, h):
    return fftconvolve(x, h[::-1, None], axes=0, mode="full")[len(h) - 1 :]


def sufficient_statistics(frames, family, bank):
    observed = voltage_residuals(frames, bank["freq"])
    if observed is None:
        return None
    planes, sigma = observed
    subtract_recovery(planes, bank["wave1"])
    wave, weight = bank[f"wave{family}"], bank[f"weight{family}"]
    sites = bank[f"sites{family}"]
    inner = np.zeros((900, len(sites)))
    energy = np.zeros_like(inner)
    for q in range(2):
        y = planes[q, 1800:] / sigma[q]
        valid = np.isfinite(y)
        obs = np.where(valid, y, 0)
        mask = valid.astype(float)
        scaled = weight[q] / sigma[q]
        for r, h in enumerate(wave[q]):
            if not h.any():
                continue
            inner += correlations(obs, h) @ scaled[r].T
            for k in range(r + 1):
                multiplier = 1 if r == k else 2
                energy += (
                    multiplier
                    * correlations(mask, h * wave[q, k])
                    @ (scaled[k] * scaled[r]).T
                )
    return inner, energy


def profile_scores(frames, family, inner, energy):
    # Positive severity is a nuisance shared across all PMUs. Extreme fits
    # from a single noisy report cannot use an unbounded severity.
    amplitude = np.clip(inner / np.maximum(energy, 1e-12), 0, 2)
    gain = 2 * amplitude * inner - amplitude**2 * energy
    if family == 8:
        pulse = residual_pulse(frames)
        if pulse is not None:
            first = max(0, pulse[0] - 1800 - 20)
            last = min(900, pulse[0] - 1800)
            if first < last:
                gain = gain[first:last]
    return gain.max(axis=0)


def localize(frames, decision, bank):
    family, previous = decision
    if f"sites{family}" not in bank:
        return previous
    stats = sufficient_statistics(frames, family, bank)
    if stats is None:
        return previous
    per_site = profile_scores(frames, family, *stats)
    sites = bank[f"sites{family}"]
    if not np.all(np.isfinite(per_site)) or per_site.max() <= 0:
        return previous
    tied = np.flatnonzero(np.isclose(per_site, per_site.max(), rtol=1e-10, atol=1e-10))
    return previous if previous in sites[tied] else str(sites[tied[0]])
