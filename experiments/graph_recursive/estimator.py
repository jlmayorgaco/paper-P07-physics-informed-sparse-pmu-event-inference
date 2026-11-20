"""Recursive physical-mode evidence and conditional rotor-state estimates."""
import numpy as np
from numba import njit
from scipy.linalg import solve_discrete_are, solve_triangular

from physical import measurements


def stationary_gain(a, h, process, ar, noise):
    d = h @ a - ar @ h
    cross = process @ h.T
    direct = noise + h @ cross
    p = solve_discrete_are(a.T, d.T, process, direct, s=cross)
    innovation = d @ p @ d.T + direct
    root = np.linalg.cholesky(innovation)
    white = solve_triangular(root, np.eye(len(root)), lower=True)
    cross_next = a @ p @ d.T + cross
    gain_white = cross_next @ white.T
    posterior = a @ p @ a.T + process - gain_white @ gain_white.T
    if not np.allclose(p, posterior, rtol=2e-5, atol=1e-9):
        raise ArithmeticError("Conditional covariance failed its Riccati identity")
    return white, gain_white, np.log(np.diag(root)).sum()


def prepare(plant, instrument, sigma_torque, onset_rate, end_rate):
    mean, scale, ar, covariance = instrument
    gains, factors, penalties = [], [], []
    for a, h, torque in zip(plant["transition"], plant["output"], plant["torque"]):
        process = sigma_torque**2 * (torque @ torque.T)
        factor, gain, penalty = stationary_gain(a, h, process, ar, covariance)
        gains.append(gain)
        factors.append(factor)
        penalties.append(penalty)
    pairs, group = np.unique([f"{c}/{s}" for c, s in zip(plant["code"], plant["site"])],
                             return_inverse=True)
    labels = [key.split("/", 1) for key in pairs]
    return dict(a=plant["transition"], b=plant["drift"], h=plant["output"], c=plant["center"],
                white=np.array(factors), gain=np.array(gains), penalty=np.array(penalties),
                mean=mean, scale=scale, ar=ar, group=group,
                code=np.array([int(c) for c, _ in labels]), site=np.array([s for _, s in labels]),
                birth=onset_rate * plant["birth_weight"][1:], end=end_rate[plant["code"][1:]],
                field=plant["field"], power=plant["power"], p0=plant["p0"], dp=plant["dp"],
                torque=plant["torque"], bias=plant["bias"], base=plant["base"], gamma=0., polar=plant["polar"])


def physics_arrays(model):
    return tuple(np.ascontiguousarray(model[key]) for key in
                 ("field", "power", "p0", "dp", "torque", "bias", "base", "scale")) + (bool(model.get("polar", False)),)


@njit
def mechanical_prediction(i, x, a, b, physics):
    _, power, p0, dp, torque, _, _, _, _ = physics
    rotation = np.exp(1j * x[:10])
    electric = (rotation * (power[i] @ np.conj(rotation))).real
    correction = p0[i] + dp[i] @ x[:10] - electric
    return a[i] @ x + b[i] + torque[i] @ correction


@njit
def terminal_prediction(i, x, physics):
    field, _, _, _, _, bias, base, scale, polar = physics
    phasors = field[i] @ np.exp(1j * x[:10])
    out = np.empty(31)
    for j in range(8):
        if polar:
            out[j] = np.log(abs(phasors[j]))
            out[8+j] = np.angle(phasors[j])
            out[16+j] = max(0., abs(phasors[8+j]) + bias[j])
            if j < 7:
                out[24+j] = np.angle(phasors[8+j])
            continue
        out[j] = phasors[j].real
        out[8+j] = phasors[j].imag
        raw = phasors[8+j]
        magnitude = abs(raw)
        measured = max(0., magnitude + bias[j])
        if j < 7:
            oriented = (raw / magnitude) * measured if magnitude > 0 else complex(measured, 0.)
            out[16+j] = oriented.real
            out[23+j] = oriented.imag
        else:
            out[30] = measured
    return (out - base) / scale


@njit
def principal(residual, physics):
    if physics[-1]:
        scale = physics[7]
        for j in range(8, 31):
            if j < 16 or j >= 24:
                angle = residual[j] * scale[j]
                residual[j] = ((angle + np.pi) % (2*np.pi) - np.pi) / scale[j]
    return residual


@njit
def advance(y, a, b, h, c, white, gain, penalty, ar, group, log_birth, log_end,
            log_stay, log_quiet, state, error, log_mass, variance=1., physics=None):
    nmode = len(state)
    log_prior = np.empty(nmode)
    log_returns = np.empty(nmode)
    log_returns[0] = log_mass[0] + log_quiet
    log_returns[1:] = log_mass[1:] + log_end
    maximum = np.max(log_returns)
    weights = np.exp(log_returns - maximum)
    log_prior[0] = maximum + np.log(weights.sum())
    weights /= weights.sum()
    mixed_state = np.zeros_like(state)
    mixed_noise = np.zeros_like(error)
    for i in range(nmode):
        mixed_state[0] += weights[i] * state[i]
        mixed_noise[0] += weights[i] * error[i]
    for i in range(1, nmode):
        stay = log_mass[i] + log_stay[i - 1]
        born = log_mass[0] + log_birth[i - 1]
        den = np.logaddexp(stay, born)
        log_prior[i] = den
        # Both parents can have negligible probability in ordinary probability space.
        w = np.exp(stay - den)
        v = np.exp(born - den)
        mixed_state[i] = w * state[i] + v * state[0]
        mixed_noise[i] = w * error[i] + v * error[0]
    for i in range(nmode):
        if physics is None:
            forecast = a[i] @ mixed_state[i] + b[i]
            predicted = h[i] @ forecast + c[i]
        else:
            forecast = mechanical_prediction(i, mixed_state[i], a, b, physics)
            predicted = terminal_prediction(i, forecast, physics)
        residual = y - predicted - ar @ mixed_noise[i]
        if physics is not None:
            residual = principal(residual, physics)
        z = white[i] @ residual
        state[i] = forecast + gain[i] @ z
        if physics is None:
            error[i] = y - c[i] - h[i] @ state[i]
        else:
            error[i] = principal(y - terminal_prediction(i, state[i], physics), physics)
        log_mass[i] = log_prior[i] - penalty[i] - 0.5 * (z @ z) / variance
    maximum = np.max(log_mass)
    log_mass -= maximum + np.log(np.exp(log_mass - maximum).sum())
    by_asset = np.zeros(np.max(group) + 1)
    for i in range(1, nmode):
        by_asset[group[i]] += np.exp(log_mass[i])
    active = by_asset.sum()
    best = np.argmax(by_asset)
    return active, best, by_asset[best] / active if active else 0.0


class Monitor:
    """One instance per trajectory. step returns (event probability, asset index, conditional asset mass)."""

    def __init__(self, model):
        self.model = model
        self.prefix = []
        self.offset = None
        self.variance = 1.
        self.physics = physics_arrays(model)
        self.state = np.zeros(model["a"].shape[:2])
        self.errors = np.zeros(model["c"].shape)
        self.log_mass = np.full(len(self.state), -np.inf)
        self.log_mass[0] = 0.0
        self.operators = tuple(np.ascontiguousarray(model[key]) for key in
                               ("a", "b", "h", "c", "white", "gain", "penalty", "ar", "group"))
        self.transitions = (np.log(model["birth"]), np.log(model["end"]),
                            np.log1p(-model["end"]), np.log1p(-model["birth"].sum()))

    def step(self, frame):
        return self.step_coordinates(measurements(frame, self.physics[-1]))

    def step_coordinates(self, y):
        y = (y - self.model["mean"]) / self.model["scale"]
        if self.offset is None:
            self.prefix.append(y)
            if len(self.prefix) == 30:
                self.offset = np.mean(np.array(self.prefix), axis=0)
                self.errors[:] = y - self.offset
                self.prefix.clear()
            return 0.0, 0, 0.0
        centered = y - self.offset
        scores = advance(centered, *self.operators, *self.transitions,
                         self.state, self.errors, self.log_mass, self.variance, self.physics)
        if not np.isfinite(scores[0]):
            raise ArithmeticError("Nonfinite mode evidence")
        voltage = centered[:16] * self.model["scale"][:16]
        self.variance = 1. + self.model["gamma"] * (voltage @ voltage) / 8
        return scores


def trace(model, record):
    monitor = Monitor(model)
    return np.asarray([monitor.step_coordinates(y) for y in measurements(record, monitor.physics[-1])])


class EpisodeDecision:
    """Separate public detection and diagnosis timestamps for each episode."""
    def __init__(self, model, detect, identify):
        self.model = model
        self.detect = detect
        self.identify = identify
        self.episode = None

    def step(self, k, score):
        active, group, conditional = score
        changes = []
        if self.episode is not None and active < 1 - self.detect:
            self.episode = None
        if self.episode is None and active >= self.detect:
            self.episode = dict(detected=k, published=None, code=None, source=None)
            changes.append(self.episode.copy())
        if (self.episode is not None and self.episode["published"] is None
                and active >= self.detect and conditional >= self.identify):
            self.episode.update(published=k, code=int(self.model["code"][int(group)]),
                                source=str(self.model["site"][int(group)]))
            changes.append(self.episode.copy())
        return changes


def publish(trace_values, model, detect, identify):
    decision = EpisodeDecision(model, detect, identify)
    alarms = {}
    for k, score in enumerate(trace_values):
        for change in decision.step(k, score):
            alarms[change["detected"]] = change
    return list(alarms.values())
