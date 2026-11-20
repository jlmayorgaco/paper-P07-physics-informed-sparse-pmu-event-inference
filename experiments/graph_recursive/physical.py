"""Local switched IEEE-39 model in rotor coordinates and oriented PMU outputs."""
from pathlib import Path
import sys

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/supervised_stream"))
from plant import FS, Generator


def measurements(frames):
    """Real/imaginary relative voltage, real/imaginary terminal current and terminal 39 magnitude."""
    frames = np.asarray(frames, dtype=float)
    if frames.shape[-2:] != (8, 5) or not np.isfinite(frames).all() or not (frames[..., 4] == 1).all():
        raise ValueError("Expected eight available, finite PMU reports with five fields each")
    voltage = np.exp(frames[..., 0] + 1j * frames[..., 1])
    current = frames[..., 2] * np.exp(1j * np.deg2rad(frames[..., 3]))
    return np.concatenate((voltage.real, voltage.imag, current.real[..., :7],
                           current.imag[..., :7], frames[..., 7:8, 2]), axis=-1)


def fit_instrument(records):
    # The archived generator guarantees at least 60 quiet reports. No labels are read.
    quiet = measurements(records[:256, :55])
    mean = quiet.mean(axis=(0, 1))
    scale = quiet.std(axis=(0, 1))
    if np.any(scale <= 0):
        raise ValueError("Degenerate training measurement")
    standardized = (quiet - mean) / scale
    prev = standardized[:, :-1].reshape(-1, len(scale))
    curr = standardized[:, 1:].reshape(-1, len(scale))
    ar = np.linalg.lstsq(prev, curr, rcond=None)[0].T
    if max(abs(np.linalg.eigvals(ar))) >= 1:
        raise ValueError("Unstable fitted quiet instrument model")
    innovations = curr - prev @ ar.T
    covariance = innovations.T @ innovations / len(curr)
    np.linalg.cholesky(covariance)
    return mean, scale, ar, covariance


def mode_operators(sim, code, source, strength, nonlinear=False):
    plant = sim.plant
    y = plant.Y0 + plant.Yg
    torque = np.zeros(10)
    connected = np.ones(8)
    if code in (1, 4):
        bus = int(source[3:])
        demand = 4.0 if code == 1 else 0.1 * plant.base_load[bus]
        y[bus - 1, bus - 1] += np.conj(strength * demand) / plant.net.vbase[bus]**2
    elif code == 2:
        line = sim.lines[source]
        idx = [line.from_bus - 1, line.to_bus - 1]
        series = 1 / complex(line.r, line.x)
        tap = line.tap * np.exp(1j * np.deg2rad(line.shift_deg))
        diag = series + 0.5j * line.b
        y[np.ix_(idx, idx)] -= [[diag / abs(tap)**2, -series / tap.conjugate()],
                                 [-series / tap, diag]]
        for k, terminal in enumerate(sim.exp.mapping.itertuples()):
            if {terminal.src, terminal.dst} == {line.from_bus, line.to_bus}:
                connected[k] = 0.0
    elif code == 3:
        torque[sim.dynamics.GEN.index(int(source[3:]))] = 0.1 * strength
    transfer = np.linalg.solve(y, np.eye(39)[:, plant.gi])
    equilibrium = plant.init_state()

    def dynamics(x):
        dx, _ = plant._f(x, transfer)
        dx[10:20] += torque / (2 * plant.H)
        return dx

    def observation(x):
        v = transfer @ (plant.yg * plant.mag * np.exp(1j * x[:10]))
        vr = v[plant.pm] / sim.exp.v0[plant.pm]
        i = (sim.exp.b @ v) * sim.exp.factor * connected
        amplitude = np.maximum(0.0, abs(i) + sim.exp.mag.center)
        ir = amplitude * np.exp(1j * np.angle(i / sim.exp.i0))
        return np.r_[vr.real, vr.imag, ir.real[:7], ir.imag[:7], amplitude[7]]

    def jacobian(fn, coordinates):
        delta = 1e-5 * np.eye(len(equilibrium))
        return np.column_stack([(fn(equilibrium + d) - fn(equilibrium - d)) / 2e-5
                                for d in delta[:coordinates]])

    # Integrate the affine drift and the injection of constant random torque through one report.
    block = np.zeros((41, 41))
    block[:30, :30] = jacobian(dynamics, 30)
    block[:30, 30] = dynamics(equilibrium)
    block[10:20, 31:] = np.diag(1 / (2 * plant.H))
    discrete = expm(block / FS)
    output = np.zeros((31, 30))
    output[:, :10] = jacobian(observation, 10)
    result = (discrete[:30, :30], discrete[:30, 30], discrete[:30, 31:], output, observation(equilibrium))
    if not nonlinear:
        return result
    field = transfer * (plant.yg * plant.E0)
    v_map = field[plant.pm] / sim.exp.v0[plant.pm, None]
    i_map = (sim.exp.b @ field) * (sim.exp.factor * connected * np.exp(-1j*np.angle(sim.exp.i0)))[:, None]
    # P_e(g) = Re(sum_j power[g,j] exp(i*(delta_g-delta_j)))).
    power = -plant.E0[:, None] * np.conj(plant.yg[:, None] * field[plant.gi])
    power[np.diag_indices(10)] += plant.E0 * np.conj(plant.yg * plant.E0)
    base_power = power.real.sum(axis=1)
    dp = power.imag.copy()
    dp[np.diag_indices(10)] -= power.imag.sum(axis=1)
    return (*result, np.vstack((v_map, i_map)), power, base_power, dp)


def build_plant(sim, scale):
    nodes, weights = np.polynomial.legendre.leggauss(3)
    modes = [(0, "", 1.0, 1.0)]
    for code in range(1, 5):
        sites = sorted(sim.catalog[code])
        quadrature = [(1.0, 1.0)] if code == 2 else zip(1 + 0.3 * nodes, weights / 2)
        for strength, weight in quadrature:
            for source in sites:
                modes.append((code, source, float(strength), float(weight / (4 * len(sites)))))
    operators = [mode_operators(sim, *mode[:3], nonlinear=True) for mode in modes]
    transition, drift, torque, output, center, field, power, p0, dp = map(np.stack, zip(*operators))
    return dict(transition=transition, drift=drift, torque=torque, output=output / scale[None, :, None],
                center=(center - center[0]) / scale, code=np.array([m[0] for m in modes]),
                site=np.array([m[1] for m in modes]), strength=np.array([m[2] for m in modes]),
                birth_weight=np.array([m[3] for m in modes]), field=field, power=power, p0=p0, dp=dp,
                bias=sim.exp.mag.center, base=center[0])
