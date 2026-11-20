"""Li–Wang DMD prediction/subtraction and two spectral inputs to CNN-F."""

import numpy as np


def channels(data, baseline=slice(10, 300)):
    v = data["voltage_magnitude"].astype(float) / (345000 / np.sqrt(3))
    i = data["current_magnitude"][:, :7].astype(float)
    angle = np.deg2rad(data["voltage_angle"][:, :7] - data["current_angle"][:, :7])
    # Active-power proxies in common-base units. The omitted current angle is
    # not observable by the paper bank. No signal from the eighth current enters.
    p = v[:, :7] * i * np.cos(angle) / 1000
    x = np.column_stack([v, data["frequency"], p])
    return x - np.nanmean(x[baseline], axis=0)


GROUPS = (slice(0, 8), slice(8, 16), slice(16, 23))


def modes(block):
    x, y = block[:-1].T, block[1:].T
    u, s, vt = np.linalg.svd(x, full_matrices=False)
    if s[0] == 0:
        return np.zeros(0, complex), np.empty((len(x), 0), complex), s[:0]
    rank = 1 + np.searchsorted(s.cumsum(), 0.999 * s.sum())
    rank = min(rank, np.count_nonzero(s > np.finfo(float).eps * max(x.shape) * s[0]))
    u, singular = u[:, :rank], s[:rank]
    a = (u.T @ y @ vt[:rank].T) / singular
    roots, vectors = np.linalg.eig(a)
    return roots, u @ vectors, singular


def features(window):
    eigen = np.zeros((9, 3), np.float32)
    singular = np.zeros((9, 2), np.float32)
    for j, group in enumerate(GROUPS):
        roots, _, values = modes(window[:, group])
        order = np.argsort(-roots.real, kind="stable")
        eigen[: len(roots), j] = roots.real[order]
        if j < 2:
            singular[: len(values), j] = values
    return eigen, singular


def forecast(block, steps, gap):
    """Project the first available state onto DMD modes and extrapolate."""
    roots, vectors, _ = modes(block)
    if not len(roots):
        return np.zeros((steps, block.shape[1]))
    weights = np.linalg.pinv(vectors) @ block[0]
    with np.errstate(over="ignore", invalid="ignore"):
        fitted = ((vectors * weights) @ (roots[:, None] ** np.arange(len(block)))).real.T
        error = np.linalg.norm(fitted - block) / max(np.linalg.norm(block), 1e-15)
        if not np.isfinite(error) or error > 0.5:
            weights[np.abs(np.angle(roots)) * 30 / (2 * np.pi) < 1.0] = 0
        target = np.arange(len(block) + gap, len(block) + gap + steps)
        ok = weights != 0
        pred = ((vectors[:, ok] * weights[ok]) @ (roots[ok, None] ** target)).real.T
    if not np.isfinite(pred).all():
        raise FloatingPointError("Nonfinite DMD extrapolation")
    return pred


def alarm_features(x, previous, alarm, subtract):
    window = x[alarm : alarm + 30].copy()
    if subtract and previous is not None and alarm - 2 - previous >= 3:
        for group in GROUPS:
            window[:, group] -= forecast(x[previous : alarm - 2, group], 30, 2)
    return features(window)
