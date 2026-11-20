"""Independent dense conditioning, path enumeration and nonlinear plant checks."""
import itertools

import numpy as np
from scipy.linalg import block_diag, solve_discrete_are
from scipy.special import logsumexp
from scipy.stats import multivariate_t

from estimator import advance, mechanical_prediction, stationary_gain, terminal_prediction
from evaluate import evaluate
from physical import Generator, measurements, mode_operators


def check_conditioning():
    a = np.array([[.94, .13], [0., .83]])
    h = np.array([[1.1, -.3], [.4, .75]])
    ar = np.array([[.28, .12], [-.07, .51]])
    q = np.diag([.04, .09])
    r = np.array([[.13, .02], [.02, .05]])
    white, gain, _ = stationary_gain(a, h, q, ar, r)
    d = h @ a - ar @ h
    p = solve_discrete_are(a.T, d.T, q, r + h @ q @ h.T, s=q @ h.T)
    # Independent calculation: condition (previous state error, process shock)
    # in information form and then map the conditional Gaussian to the current state.
    prior = block_diag(p, q)
    design = np.hstack((d, h))
    forward = np.hstack((a, np.eye(len(q))))
    post = np.linalg.inv(np.linalg.inv(prior) + design.T @ np.linalg.solve(r, design))
    dense_gain = forward @ post @ np.linalg.solve(r, design).T
    np.testing.assert_allclose(gain @ white, dense_gain, atol=1e-11)
    np.testing.assert_allclose(forward @ post @ forward.T, p, atol=1e-11)


def check_modes():
    transition = np.array([[.8, .07, .13], [.25, .75, 0.], [.15, 0., .85]])
    centers = np.array([[0.], [.6], [-.8]])
    scales = np.array([1., .9, 1.3])
    zero = np.zeros((3, 1, 1))
    state, error = np.zeros((3, 1)), np.zeros((3, 1))
    mass = np.array([0., -np.inf, -np.inf])
    history = [0.4, -0.7, 0.35, 0.9]
    for k, y in enumerate(history, start=1):
        advance(np.array([y]), zero, state * 0., zero, centers, (1/scales)[:, None, None].copy(),
                zero, np.log(scales), np.zeros((1, 1)), np.arange(3),
                np.log(transition[0, 1:]), np.log(transition[1:, 0]),
                np.log(transition.diagonal()[1:]), np.log(transition[0, 0]), state, error, mass)
        exact = np.zeros(3)
        for path in itertools.product(range(3), repeat=k):
            w, prev = 1., 0
            for t, j in enumerate(path):
                w *= transition[prev, j] * np.exp(-.5*((history[t]-centers[j, 0])/scales[j])**2) / scales[j]
                prev = j
            exact[path[-1]] += w
        np.testing.assert_allclose(np.exp(mass), exact / exact.sum(), atol=1e-13)


def check_plant():
    sim = Generator()
    _, _, _, _, base = mode_operators(sim, 0, "", 1.)
    for code in range(1, 5):
        source = sorted(sim.catalog[code])[0]
        a, drift, torque, h, center, field, power, p0, dp = mode_operators(sim, code, source, 1., nonlinear=True)
        e = dict(code=code, source=source, onset=60, end=82, strength=1., sensors=[2, 5])
        obs = measurements(sim.simulate([e], np.random.default_rng(51), nominal=True)).astype(float)
        observed = obs[60] - obs[59]
        predicted = center - base + h @ drift
        # Separate voltage and ampere scales. Tolerance includes finite-step local linearization.
        np.testing.assert_allclose(predicted[:16], observed[:16], atol=4e-4, rtol=.01)
        np.testing.assert_allclose(predicted[16:], observed[16:], atol=1.5, rtol=.02)
        physics = (field[None], power[None], p0[None], dp[None], torque[None], sim.exp.mag.center,
                   base, np.ones(31), False)
        state = np.zeros(30)
        single_a, single_b = a[None], drift[None]
        for frame in range(60, 66):
            state = mechanical_prediction(0, state, single_a, single_b, physics)
            report = terminal_prediction(0, state, physics)
            np.testing.assert_allclose(report[:16], obs[frame, :16] - obs[59, :16], atol=.001, rtol=.02)
            np.testing.assert_allclose(report[16:], obs[frame, 16:] - obs[59, 16:], atol=2., rtol=.025)
        shifted = state.copy()
        shifted[:10] += .7
        delta = mechanical_prediction(0, shifted, single_a, single_b, physics) - state
        original = mechanical_prediction(0, state, single_a, single_b, physics) - state
        np.testing.assert_allclose(delta - original, np.r_[np.full(10, .7), np.zeros(20)], atol=1e-8)


def check_score():
    truth = [[dict(onset=65, code=1, source="BUS3"), dict(onset=235, code=4, source="BUS4")], []]
    alarms = [[dict(detected=65, published=111, code=1, source="BUS3"),
               dict(detected=237, published=238, code=4, source="BUS4")],
              [dict(detected=56, published=None, code=None, source=None)]]
    result = evaluate(truth, alarms)
    assert (result["detected"], result["joint"], result["quiet_extras"]) == (2, 1, 1)


def check_selected():
    from estimator import physics_arrays, principal
    from phasors import MODEL
    from robust import StudentMonitor
    with np.load(MODEL) as archive:
        m = dict(archive)
    physics = physics_arrays(m)
    for j in (0, 1, len(m["a"])//2, len(m["a"])-1):
        eye = 1e-6*np.eye(30)
        numerical = np.column_stack([principal(terminal_prediction(j, d, physics)
                      - terminal_prediction(j, -d, physics), physics) / 2e-6 for d in eye])
        np.testing.assert_allclose(numerical, m["h"][j], rtol=2e-6, atol=1e-4)
    # Check the entire first posterior against normalized Student densities,
    # with the scale matrix in the measurement coordinates passed directly to SciPy.
    monitor = StudentMonitor(m)
    for _ in range(30):
        monitor.step_coordinates(m["mean"])
    y = np.linspace(-.9, .9, 31)
    monitor.step_coordinates(m["mean"] + m["scale"]*y)
    prior = np.r_[1-m["birth"].sum(), m["birth"]]
    direct = []
    for j, w in enumerate(prior):
        pred = mechanical_prediction(j, np.zeros(30), m["a"], m["b"], physics)
        e = principal(y-terminal_prediction(j, pred, physics), physics)
        root = np.linalg.inv(m["white"][j])
        direct.append(np.log(w) + multivariate_t.logpdf(e, shape=root @ root.T, df=float(m["degrees"])))
    direct = np.array(direct) - logsumexp(direct)
    np.testing.assert_allclose(monitor.log_mass, direct, atol=1e-7, rtol=5e-10)


if __name__ == "__main__":
    check_conditioning()
    check_modes()
    check_plant()
    check_score()
    check_selected()
    print("Gaussian conditioning, enumerated modes, four nonlinear operators, deadline scoring, polar Jacobians and Student posterior passed.")
