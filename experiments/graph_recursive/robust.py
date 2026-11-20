"""Scale-mixture successor. Keeps the frozen Gaussian observer as a paired control."""
import sys
import numpy as np
from numba import njit
from scipy.optimize import minimize_scalar
from scipy.special import gammaln

from estimator import Monitor, mechanical_prediction, physics_arrays, publish, terminal_prediction
from physical import measurements
from study import (FREEZE, HERE, STORE, digest, evaluate, labels, read, sequences, verify_freeze,
                   write_json)

SELECTION = HERE / "robust_freeze.json"
ROBUST_SEAL = HERE / "robust_seal.json"


@njit
def advance_student(y, a, b, h, c, white, gain, penalty, ar, group, log_birth, log_end,
                    log_stay, log_quiet, state, error, log_mass, variance, physics, degrees):
    n = len(state)
    old = log_mass.copy()
    returns = old.copy()
    returns[0] += log_quiet
    returns[1:] += log_end
    peak = np.max(returns)
    weights = np.exp(returns - peak)
    quiet_prior = peak + np.log(weights.sum())
    weights /= weights.sum()
    quiet_x, quiet_noise = state[0].copy(), error[0].copy()
    merged_x, merged_noise = weights @ state, weights @ error
    for j in range(n):
        if j == 0:
            x, noise, prior = merged_x, merged_noise, quiet_prior
        else:
            stay, born = old[j] + log_stay[j-1], old[0] + log_birth[j-1]
            prior = np.logaddexp(stay, born)
            ws, wb = np.exp(stay - prior), np.exp(born - prior)
            x, noise = ws * state[j] + wb * quiet_x, ws * error[j] + wb * quiet_noise
        forecast = mechanical_prediction(j, x, a, b, physics)
        residual = y - terminal_prediction(j, forecast, physics) - ar @ noise
        innovation = white[j] @ residual
        state[j] = forecast + gain[j] @ innovation
        error[j] = y - terminal_prediction(j, state[j], physics)
        log_mass[j] = prior - penalty[j] - .5 * (degrees + len(y)) * np.log1p(
            (innovation @ innovation) / (degrees * variance))
    peak = np.max(log_mass)
    log_mass -= peak + np.log(np.exp(log_mass - peak).sum())
    assets = np.zeros(np.max(group) + 1)
    for j in range(1, n):
        assets[group[j]] += np.exp(log_mass[j])
    active = assets.sum()
    best = np.argmax(assets)
    return active, best, assets[best] / active if active else 0.


class StudentMonitor(Monitor):
    def step_coordinates(self, y):
        if self.offset is None:
            return super().step_coordinates(y)
        centered = (y - self.model["mean"]) / self.model["scale"] - self.offset
        score = advance_student(centered, *self.operators, *self.transitions, self.state, self.errors,
                                self.log_mass, self.variance, self.physics, self.model["degrees"])
        if not np.isfinite(score[0]):
            raise ArithmeticError("Nonfinite Student mode evidence")
        voltage = centered[:16] * self.model["scale"][:16]
        self.variance = 1. + self.model["gamma"] * (voltage @ voltage) / 8
        return score


def trace_student(model, record):
    monitor = StudentMonitor(model)
    return [monitor.step_coordinates(y) for y in measurements(record)]


def calibration_innovations(model, plant, observations, truth):
    physics = physics_arrays(model)
    energy, lag_voltage = [], []
    for record, events in zip(observations, truth):
        y = (measurements(record) - model["mean"]) / model["scale"]
        y -= y[:30].mean(axis=0)
        path = np.zeros(len(y), int)
        for e in events:
            ids = np.flatnonzero((plant["code"] == e["code"]) & (plant["site"] == e["source"]))
            j = ids[np.argmin(abs(plant["strength"][ids] - e["strength"]))]
            path[e["onset"]:e["end"]] = j
        x, noise, previous = np.zeros(30), y[29], 0.
        for k in range(30, len(y)):
            j = path[k]
            pred = mechanical_prediction(j, x, model["a"], model["b"], physics)
            e = model["white"][j] @ (y[k]-terminal_prediction(j, pred, physics)-model["ar"] @ noise)
            x = pred + model["gain"][j] @ e
            noise = y[k] - terminal_prediction(j, x, physics)
            energy.append(e @ e)
            lag_voltage.append(previous)
            v = y[k, :16] * model["scale"][:16]
            previous = v @ v / 8
    return np.array(energy), np.array(lag_voltage)


def fit_student(energy, lag_voltage):
    dimension = 31
    options = []
    for nu in (3., 5., 10., 30.):
        constant = gammaln(nu/2) - gammaln((nu+dimension)/2) + dimension/2*np.log(nu*np.pi)
        def loss(log_gamma):
            variance = 1. + np.expm1(log_gamma)*lag_voltage
            return constant + .5*np.mean(dimension*np.log(variance) +
                         (nu+dimension)*np.log1p(energy/(nu*variance)))
        upper = np.log1p(1e12)
        fit = minimize_scalar(loss, bounds=(0., upper), method="bounded")
        best = min((0., fit.x, upper), key=loss)
        options.append((float(loss(best)), nu, float(np.expm1(best))))
    return min(options)


def load():
    with np.load(HERE / "model.npz") as archive:
        return dict(archive)


def fit():
    if (STORE / "test").exists() or SELECTION.exists():
        raise FileExistsError("Robust selection must precede test generation")
    from physical import Generator, build_plant
    verify_freeze()
    observations, truth = sequences("dev", True)
    model = load()
    plant = build_plant(Generator(), model["scale"])
    loss, degrees, gamma = fit_student(*calibration_innovations(model, plant, observations, truth))
    model.update(degrees=degrees, gamma=gamma)
    traces = [trace_student(model, x) for x in observations]
    choices = []
    for gate in (.9, .99, .999):
        for identify in (.5, .8, .95):
            result = evaluate(truth, [publish(z, model, gate, identify) for z in traces])
            loss_count = result["events"] - result["joint"] + result["event_record_extras"]
            choices.append(((result["quiet_extras"], loss_count, -result["joint"], -gate, -identify),
                            gate, identify, result))
    _, gate, identify, result = min(choices, key=lambda item:item[0])
    gaussian = read(FREEZE)["dev"]
    def risk(r):
        return (r["quiet_extras"], r["events"] - r["joint"] + r["event_record_extras"], -r["joint"])
    primary = "student" if risk(result) < risk(gaussian) else "graph"
    write_json(SELECTION, dict(degrees=degrees, gamma=gamma, conditional_loss_without_fixed_logdet=loss,
                               gate=gate, identify=identify, dev=result, primary=primary,
                               source=digest(HERE / "robust.py"), gaussian=digest(FREEZE)))
    print("robust calibration", degrees, gamma, primary, result, flush=True)


def predict():
    verify_freeze()
    selection = read(SELECTION)
    if selection["source"] != digest(HERE / "robust.py") or selection["gaussian"] != digest(FREEZE):
        raise ValueError("Robust development freeze changed")
    model = load()
    model.update(degrees=selection["degrees"], gamma=selection["gamma"])
    alarms = [publish(trace_student(model, x), model, selection["gate"], selection["identify"])
              for x in sequences("test")]
    path = HERE / "robust_predictions.json"
    write_json(path, alarms)
    write_json(ROBUST_SEAL, dict(predictions=digest(path), freeze=digest(SELECTION),
                                 manifest=digest(HERE / "test_manifest.json")))


def score():
    path = HERE / "robust_predictions.json"
    expected = dict(predictions=digest(path), freeze=digest(SELECTION), manifest=digest(HERE / "test_manifest.json"))
    if expected != read(ROBUST_SEAL):
        raise ValueError("Robust predictions differ from seal")
    result = evaluate(labels("test"), read(path), bootstrap=True)
    write_json(HERE / "robust_scores.json", result)
    print(result, flush=True)


if __name__ == "__main__":
    {"fit":fit, "predict":predict, "score":score}[sys.argv[1]]()
