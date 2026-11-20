"""Bayesian class-8 site readout with a latent instrument marker and shared onset."""

import numpy as np
from scipy.special import logsumexp, log_ndtr
from pmu_source_readout import sufficient_statistics, BUSES


def marker_evidence(frames):
    scores = []
    for bus in BUSES:
        frame = frames[bus]
        current = frame[[f"BUS{bus}_I{p}_MAG" for p in "ABC"]].to_numpy(copy=True)
        current[frame.DATA_PRESENT.to_numpy() != 1] = np.nan
        reference = np.nanmedian(current[:1440], axis=0)
        z = np.nanmedian(current / reference - 1, axis=1)
        spread = max(
            0.02, 1.4826 * np.nanmedian(abs(z[:1440] - np.nanmedian(z[:1440])))
        )
        # Downweight temporal dependence using one average per three reports.
        measured = z[1800:]
        valid = np.isfinite(measured)

        def sums(x):
            total = np.r_[0, np.cumsum(x)]
            idx = np.arange(len(x))
            return total[np.minimum(idx + 54, len(x))] - total[idx]

        inner = sums(np.where(valid, measured, 0)) / (3 * spread**2)
        energy = sums(valid.astype(float)) / (3 * spread**2)
        tau = 0.25
        precision = energy + 1 / tau**2
        log_bf = (
            0.5 * inner**2 / precision
            - 0.5 * np.log1p(tau**2 * energy)
            + np.log(2)
            + log_ndtr(inner / np.sqrt(precision))
        )
        scores.append(log_bf)
    # Uniform prior on eight instruments and lags of 0--24 reports.
    # A marker starting outside the buffer contributes a neutral likelihood.
    site_mix = logsumexp(np.array(scores), axis=0) - np.log(len(BUSES))
    padded = np.pad(site_mix, (0, 24))
    return logsumexp(
        np.lib.stride_tricks.sliding_window_view(padded, 25), axis=1
    ) - np.log(25)


def posterior(frames, bank):
    stats = sufficient_statistics(frames, 8, bank)
    if stats is None:
        return None
    inner, energy = stats
    log_time = marker_evidence(frames)
    obs_prior = log_time - logsumexp(log_time)
    # Midpoint quadrature for the uniform relative-strength prior [0.5,1.5].
    scores = np.full(inner.shape, -np.inf)
    for a in 0.5 + (np.arange(48) + 0.5) / 48:
        scores = np.logaddexp(scores, a * inner - 0.5 * a * a * energy)
    log_site = logsumexp(scores + obs_prior[:, None], axis=0)
    return np.exp(log_site - logsumexp(log_site))
