"""Physical-template likelihood for a second switch after a reported restoration."""
from dataclasses import dataclass

import numpy as np
from scipy.special import logsumexp
from sklearn.covariance import LedoitWolf

WINDOW = 30


def frequency(modes_hz):
    modes = np.sort(np.asarray(modes_hz, dtype=float))
    observable = modes[(modes >= 0.2) & (modes <= 3)]
    if not len(observable):
        raise ValueError("No in-band oscillatory mode")
    return np.median(observable[: (len(observable) + 1) // 2])


def basis(modes_hz, arm):
    dc = np.ones(WINDOW) / np.sqrt(WINDOW)
    if arm == "mean":
        return dc[:, None]
    time = np.arange(WINDOW) / WINDOW
    if arm == "modal":
        phase = 2 * np.pi * frequency(modes_hz) * time
        vectors = (dc, np.cos(phase), np.sin(phase))
    elif arm == "quadratic":
        vectors = (dc, time, time**2)
    else:
        raise ValueError(arm)
    q, r = np.linalg.qr(np.column_stack(vectors))
    return q * np.sign(np.diag(r))


def windows(y, clearance, temporal):
    y = np.asarray(y, dtype=float)
    if y.ndim != 2 or y.shape[1] != 16 or not np.isfinite(y).all():
        raise ValueError("Expected eight finite voltage and current magnitudes per report")
    if not 0 <= clearance <= len(y) - 2 * WINDOW:
        raise ValueError("Insufficient reports after the restoration")
    contrast = y[clearance + WINDOW:] - y[clearance:-WINDOW]
    frames = np.lib.stride_tricks.sliding_window_view(contrast, WINDOW, axis=0)
    projected = np.einsum("nct,tk->nkc", frames, temporal)
    reports = np.arange(clearance + 2 * WINDOW - 1, len(y))
    return reports, projected.reshape(len(frames), -1)


@dataclass
class Estimator:
    temporal: np.ndarray
    center: np.ndarray
    scale: np.ndarray
    matched: np.ndarray
    cost: np.ndarray
    names: np.ndarray
    families: np.ndarray
    templates_by_asset: tuple

    def scan(self, y, clearance):
        reports, z = windows(y, clearance, self.temporal)
        log_ratio = ((z - self.center) / self.scale) @ self.matched.T - self.cost
        # Uniform priors over sizes within each asset, assets within each family, and families.
        asset_mass = np.column_stack([logsumexp(log_ratio[:, ix], axis=1) - np.log(len(ix))
                                      for ix in self.templates_by_asset])
        labels = np.unique(self.families)
        family_mass = np.column_stack([logsumexp(asset_mass[:, self.families == f], axis=1)
                                       - np.log(sum(self.families == f)) for f in labels])
        family = labels[family_mass.argmax(axis=1)]
        source = self.names[np.where(self.families[None, :] == family[:, None], asset_mass, -np.inf).argmax(axis=1)]
        return reports, logsumexp(family_mass, axis=1) - np.log(len(labels)), family, source


def fit(templates, records, arm):
    temporal = basis(templates["modes_hz"], arm)
    z = np.concatenate([windows(y, clearance, temporal)[1] for y, clearance in records])
    center = z.mean(axis=0)
    scale = z.std(axis=0)
    if np.any(scale <= 0):
        raise ValueError("Unobservable contrast in fit recoveries")
    covariance = LedoitWolf(assume_centered=True).fit((z-center)/scale).covariance_
    # A predicted switch shifts the recovery mean by its isolated physical response.
    response = np.einsum("ntc,tk->nkc", templates["signatures"], temporal)
    shift = response.reshape(len(response), -1) / scale
    matched = np.linalg.solve(covariance, shift.T).T
    cost = 0.5 * np.einsum("ij,ij->i", shift, matched)
    ids = np.asarray(templates["ids"], dtype=str)
    names = np.unique(ids)
    groups = tuple(np.flatnonzero(ids == name) for name in names)
    tags = np.asarray(templates["families"], dtype=str)
    families = []
    for ix in groups:
        if len(np.unique(tags[ix])) != 1:
            raise ValueError("Asset belongs to multiple families")
        families.append(tags[ix[0]])
    return Estimator(temporal, center, scale, matched, cost, names, np.array(families), groups)
