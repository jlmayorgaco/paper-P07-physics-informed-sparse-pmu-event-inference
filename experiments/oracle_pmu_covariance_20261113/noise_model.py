"""Known added Gaussian polar noise and its state-space representation."""
import numpy as np
from scipy.linalg import block_diag, cho_factor, cho_solve, solve_discrete_are

WINDOW = 21
KEEP = [np.arange(8)] * 3 + [np.arange(7)] + [np.arange(8)] * 2
FIR = np.linalg.pinv(np.polynomial.polynomial.polyvander(np.arange(-20, 1)/30, 2))
WEIGHTS = np.stack([FIR[1]/360, 2*FIR[2]/360])


def maps(scales, magnitude):
    """Raw standardized noise: current 31-vector plus 20 past voltage angles."""
    direct = np.zeros((47, 31))
    lagged = np.zeros((47, 160))
    direct[:31] = np.diag(np.r_[magnitude[:8], np.full(8, 180/np.pi),
                                magnitude[8:], np.full(7, 180/np.pi)])
    for family, start in enumerate((31, 39)):
        direct[start:start+8, 8:16] = np.eye(8) * (180/np.pi) * WEIGHTS[family, -1]
        for age in range(20):
            lagged[start:start+8, 8*age:8*(age+1)] = (
                np.eye(8) * (180/np.pi) * WEIGHTS[family, -2-age])
    return direct/scales[:, None], lagged/scales[:, None]


def shift():
    transition = np.zeros((160, 160))
    transition[8:, :-8] = np.eye(152)
    injection = np.zeros((160, 31))
    injection[:8, 8:16] = np.eye(8)
    return transition, injection


def add_to_reports(data, fields, magnitude, sigma, seed):
    """Fixed-prefix magnitude reference gives an exactly additive polar law."""
    t = data["time_s"]
    direct, lagged = maps(np.ones(47), magnitude)
    draws = np.random.default_rng(seed).normal(0, sigma, (len(t)+20, 31))
    raw = draws[20:] @ direct.T
    for age in range(20):
        raw += draws[19-age:19-age+len(t), 8:16] @ lagged[:, 8*age:8*(age+1)].T
    out = {key: value.copy() for key, value in data.items()}
    start = 0
    for field, indices in zip(fields, KEEP):
        count = len(indices)
        out[field][:, indices] += raw[:, start:start+count]
        if field.endswith("angle"):
            out[field] = (out[field]+180) % 360 - 180
        start += count
    return out


def verify_maps(scales, magnitude):
    direct, lagged = maps(scales, magnitude)
    rng = np.random.default_rng(203)
    z = rng.standard_normal((64, 31))
    for k in range(20, len(z)):
        direct_eval = direct @ z[k] + lagged @ z[k-20:k, 8:16][::-1].ravel()
        for j, start in enumerate((31,39)):
            expected = WEIGHTS[j] @ z[k-20:k+1, 8:16] * (180/np.pi)
            np.testing.assert_allclose(direct_eval[start:start+8]*scales[start:start+8],
                                       expected, atol=1e-12)


def rebuild(bank, filters, scales, magnitude, white, sigma_by_pmu=None):
    """DARE with Cov(process noise, observation noise) at the same report."""
    t, j, q = bank["T"], bank["J"], bank["Q"]
    n = t.shape[-1]
    cross = np.zeros((n, 47))
    if sigma_by_pmu is not None:
        direct, lagged = maps(scales, magnitude)
        w = block_diag(*[f.W for f in filters])
        wb = block_diag(*[f.B for f in filters])
        # Original ordering: physics, phase memory, observed-noise filter, discrepancy.
        positions = slice(274, n-47)
        assert n == 376 and wb.shape == (55, 47)
        f, g = shift()
        transitions = []
        for matrix in t:
            augmented = block_diag(matrix, f)
            augmented[positions, n:] = wb @ lagged
            transitions.append(augmented)
        t = np.array(transitions)
        j = np.concatenate([j, np.broadcast_to(w @ lagged, (len(j), 47, 160))], axis=2)
        injection = np.zeros((n+160, 31))
        injection[positions] = wb @ direct
        injection[n:] = g
        std = np.tile(sigma_by_pmu, 4)[:31]
        injection *= std
        observed = (w @ direct) * std
        q = np.array([block_diag(x, np.zeros((160,160))) + injection @ injection.T for x in q])
        white = white + observed @ observed.T
        cross = injection @ observed.T
        for key in ("g", "u"):
            bank[key] = np.pad(bank[key], ((0,0),(0,160)))
    ps, gains, inverse, logdets, errors = [], [], [], [], []
    for process in q:
        prior = solve_discrete_are(t[0].T, j[0].T, process, white, s=cross)
        prior = (prior + prior.T)/2
        row_k, row_si, row_ld = [], [], []
        for transition, observation in zip(t, j):
            s = observation @ prior @ observation.T + white
            cf = cho_factor((s+s.T)/2, lower=True)
            k = cho_solve(cf, (transition @ prior @ observation.T + cross).T).T
            row_k.append(k)
            row_si.append(cho_solve(cf, np.eye(47)))
            row_ld.append(2*np.log(np.diag(cf[0])).sum())
        innovation = j[0] @ prior @ j[0].T + white
        reconstructed = t[0] @ prior @ t[0].T + process - row_k[0] @ innovation @ row_k[0].T
        errors.append(float(np.linalg.norm(prior-reconstructed)/np.linalg.norm(prior)))
        ps.append(prior)
        gains.append(row_k)
        inverse.append(row_si)
        logdets.append(row_ld)
    assert max(errors) < 1e-6, errors
    bank.update(T=t, J=j, Q=q, P=np.array(ps), R=np.repeat(white[None], len(q), axis=0),
                K=np.array(gains), Sinv=np.array(inverse), logdet=np.array(logdets))
    return max(errors)
