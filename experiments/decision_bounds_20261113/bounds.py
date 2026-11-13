"""Conditional bounds for Gaussian scores; no error estimator or bank integration.

Inputs must bound error relative to the approximate covariance, not raw units.
An empirical coarse/fine discrepancy is NOT automatically such a bound.
"""
import numpy as np
from scipy.special import logsumexp


def gaussian_score_radius(residual_norm, mean_error_bound, covariance_error_bound, dimension):
    """Bound |log N(y;mu,S)-log N(y;mu_t,S_t)|.

    W S_t W.T=I, r=||W(y-mu_t)||, eps>=||W(mu-mu_t)||,
    eta>=||W S W.T-I||_2. For eta>=1 return infinity: uncertified.
    Same dimension and finite SPD covariances required by the caller.
    """
    r, eps, eta = map(float, (residual_norm, mean_error_bound, covariance_error_bound))
    if not all(np.isfinite(v) and v >= 0 for v in (r, eps, eta)):
        raise ValueError('Bounds and residual norm must be finite and nonnegative')
    if not isinstance(dimension, (int, np.integer)) or dimension < 1:
        raise ValueError('dimension must be a positive integer')
    if eta >= 1:
        return float('inf')
    return .5 * (-dimension*np.log1p(-eta) +
                 (eta*r*r + 2*r*eps + eps*eps)/(1-eta))


def score_intervals(scores, radii):
    scores, radii = np.asarray(scores, float), np.asarray(radii, float)
    if scores.ndim != 1 or scores.shape != radii.shape or len(scores) < 2:
        raise ValueError('At least two matching score/radius entries are required')
    if not np.all(np.isfinite(scores)) or np.any(np.isnan(radii)) or np.any(radii < 0):
        raise ValueError('Invalid scores or radii')
    return scores-radii, scores+radii


def certified_winner(scores, radii):
    lower, upper = score_intervals(scores, radii)
    winner = int(np.argmax(scores))
    return winner if lower[winner] > np.max(np.delete(upper, winner)) else None


def group_mass_interval(scores, radii, membership):
    """Conservative normalized mass bounds for a FIXED finite candidate set.

    Scores include prior. Pruned candidates require separate mass bounds.
    Infinite radii return [0,1]; no claim about temporal confirmation rules.
    """
    lower, upper = score_intervals(scores, radii)
    mask = np.asarray(membership, bool)
    if mask.shape != lower.shape:
        raise ValueError('Membership must match scores')
    if not np.any(mask): return 0., 0.
    if np.all(mask): return 1., 1.
    if np.any(~np.isfinite(lower)) or np.any(~np.isfinite(upper)): return 0., 1.
    lo_a, hi_a = logsumexp(lower[mask]), logsumexp(upper[mask])
    lo_b, hi_b = logsumexp(lower[~mask]), logsumexp(upper[~mask])
    return float(np.exp(lo_a-np.logaddexp(lo_a, hi_b))), float(np.exp(hi_a-np.logaddexp(hi_a, lo_b)))


def quadrature_log_interval(log_likelihoods, radii, weights):
    """Bounds the SAME positive-weight quadrature, not its integration error."""
    lower, upper = score_intervals(log_likelihoods, radii)
    weights = np.asarray(weights, float)
    if weights.shape != lower.shape or not np.all(np.isfinite(weights)) or np.any(weights <= 0):
        raise ValueError('Positive matching quadrature weights required')
    return float(logsumexp(np.log(weights)+lower)), float(logsumexp(np.log(weights)+upper))
