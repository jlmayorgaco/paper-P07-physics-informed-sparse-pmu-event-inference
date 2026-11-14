"""Read-only development probes of frozen IEEE-39 operators and a Gaussian null."""
import os
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"

import csv
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from scipy.linalg import expm, solve_triangular
from scipy.optimize import least_squares
from scipy.sparse import csr_matrix
from scipy.special import logsumexp
from scipy.stats import binomtest

HERE = Path(__file__).resolve().parent
CHANNEL = HERE.parent / "channel_information_20261112"
NATIVE = HERE.parent / "descriptor_bridge_20261113" / "run_v2/operators"
sys.path.insert(0, str(CHANNEL))
import run_channel_diagnostic as base


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recovery_geometry(config):
    bank, assets = base.load_snapshot(), base.read_assets()
    h = config["horizon_reports"]
    d = config["previous_load_duration_reports"]
    gaps = config["recovery_gaps_reports"]
    raw, _ = base.raw_covariance(bank, h)
    chol, scale = base.stable_factor(raw)

    def whiten(values):
        return solve_triangular(chol, (values / scale).T, lower=True).T

    offsets, slopes = [], []
    for cell in range(len(assets)):
        state = np.zeros((bank["T"].shape[1], 2))
        output = []
        for report in range(h):
            op = base.operator_index(cell, "on0" if report == 0 else "stay")
            group = bank["group"][op]
            output.append(bank["J"][group] @ state + (bank["j"][op] - bank["j"][0])[:, None]
                          + bank["v"][op, :, None] * [0., 1.])
            state = (bank["T"][group] @ state + bank["g"][op, :, None]
                     + bank["u"][op, :, None] * [0., 1.])
        pair = whiten(np.array(output).reshape(h * 47, 2).T)
        offsets.append(pair[0])
        slopes.append(pair[1] - pair[0])
    offsets, slopes = np.array(offsets), np.array(slopes)
    loads = [i for i, asset in enumerate(assets) if asset["family"] == "load"]
    cells = np.array(loads)
    tmat = csr_matrix(bank["T"][0])
    jmat = bank["J"][0]
    state = np.zeros((tmat.shape[0], len(loads)))
    recovery = []
    for report in range(d + max(gaps) + h):
        op = (2 + 5*cells if report == 0 else 1 + 5*cells if report < d else
              3 + 5*cells if report == d else np.zeros_like(cells))
        assert np.all(bank["group"][op] == 0) and np.all(bank["g"][op] == 0)
        recovery.append((jmat @ state + bank["v"][op].T).T)
        state = tmat @ state + bank["u"][op].T
    recovery = np.array(recovery)
    rows = []
    lo, hi = config["rival_amplitude_limits"]
    max_identity_error = 0.
    for gap in gaps:
        trajectories = recovery[d+gap:d+gap+h].transpose(1, 0, 2).reshape(len(loads), -1)
        for prev, direction in zip(loads, whiten(trajectories)):
            for sigma in config["previous_amplitude_sd"]:
                u = sigma * direction
                norm2 = u @ u
                denominator = 1 + norm2

                def distances(diff, nuisance):
                    ds = diff @ u
                    ss = slopes @ u
                    dd = np.einsum("ij,ij->i", diff, diff) - nuisance * ds**2/denominator
                    aa = np.einsum("ij,ij->i", slopes, slopes) - nuisance * ss**2/denominator
                    da = np.einsum("ij,ij->i", diff, slopes) - nuisance * ds*ss/denominator
                    fit = np.clip(np.divide(da, aa, out=np.zeros_like(da), where=aa>0), lo, hi)
                    return dd - 2*da*fit + aa*fit**2, fit

                for source in loads:
                    for a in config["new_load_amplitudes"]:
                        event = a * slopes[source]
                        difference = offsets[source] + event - offsets
                        fixed, _ = distances(difference, 0)
                        uncertain, fit = distances(difference, 1)
                        assert np.all(uncertain <= fixed + 1e-8*np.maximum(1., fixed))
                        assert uncertain.min() >= -1e-8*np.maximum(1., fixed.max())
                        fixed[source] = uncertain[source] = np.inf
                        i, j = int(fixed.argmin()), int(uncertain.argmin())
                        # Independent square-root action on the fitted residual.
                        residual = difference[j] - slopes[j]*fit[j]
                        transformed = residual + ((1/np.sqrt(denominator)-1)
                                       * (u @ residual)/max(norm2, 1e-300))*u
                        err = abs(transformed @ transformed - uncertain[j])
                        max_identity_error = max(max_identity_error, err/max(1., uncertain[j]))
                        known = event @ event
                        marginal = known - (event @ u)**2/denominator
                        rows.append(dict(gap_reports=gap, previous=assets[prev]["id"],
                                         source=assets[source]["id"], severity=a, previous_sd=sigma,
                                         null_retention=marginal/known, separation_known=fixed[i],
                                         separation_uncertain=uncertain[j], retention=uncertain[j]/fixed[i],
                                         rival_known=assets[i]["id"], rival_uncertain=assets[j]["id"]))
    assert len(rows) == len(gaps)*len(loads)**2*len(config["previous_amplitude_sd"])*len(config["new_load_amplitudes"])
    assert max_identity_error < 1e-8
    groups = []
    for gap in gaps:
        for sigma in config["previous_amplitude_sd"]:
            records = [r for r in rows if r["gap_reports"]==gap and r["previous_sd"]==sigma]
            ratio = np.array([r["retention"] for r in records])
            groups.append(dict(gap_reports=gap, previous_sd=sigma, count=len(records),
                               median=float(np.median(ratio)), minimum=float(ratio.min()),
                               p10=float(np.quantile(ratio,.1)),
                               changed=sum(r["rival_known"]!=r["rival_uncertain"] for r in records)))
    with (HERE/"geometry.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return dict(groups=groups, rows=len(rows), max_identity_error=max_identity_error,
                worst=min(rows, key=lambda r:r["retention"]))


def switching_time(config):
    # Affine mode flows of the saved physical descriptor reduction.
    matrices, outputs, offsets = [], [], []
    for mode in ("normal", "line"):
        def read(name):
            return np.loadtxt(NATIVE/mode/(name+".csv"), delimiter=",", skiprows=1)
        a = read("A")
        matrices.append(np.block([[a, read("force")[:,None]], [np.zeros((1,len(a)+1))]]))
        pmus = [2,5,6,10,19,22,29,39]
        idx = [2*(b-1)+j for b in pmus for j in (0,1)]
        outputs.append(np.column_stack((read("C")[idx], np.zeros(len(idx)))))
        offsets.append(read("voltage")[idx])
    normal, active = matrices
    anchor = np.r_[np.zeros(len(normal)-1), 1.]
    base_on, base_off = np.array(config["switch_reports"])/30
    times = np.array([base_on+1/30, base_off-1/30, base_off+1/30, base_off+.2])

    def evaluate(switch):
        on, off = switch
        x_on = expm(normal*on) @ anchor
        x_off = expm(active*(off-on)) @ x_on
        d_on = (normal-active) @ x_on
        off_on = expm(active*(off-on)) @ d_on
        d_off = (active-normal) @ x_off
        values, jac = [], []
        for t in times:
            if t < off:
                step = expm(active*(t-on))
                values.append(offsets[1]+outputs[1] @ step @ x_on)
                jac.append(np.column_stack((outputs[1] @ step @ d_on, np.zeros(len(offsets[1])))))
            else:
                step = expm(normal*(t-off))
                values.append(offsets[0]+outputs[0] @ step @ x_off)
                jac.append(outputs[0] @ step @ np.column_stack((off_on,d_off)))
        return np.concatenate(values), np.vstack(jac)

    low, high = np.array([base_on,base_off])+1e-5, np.array([base_on,base_off])+1/30-1e-5
    midpoint = (low+high)/2
    cases = []
    for on_fraction, off_fraction in zip(config["timing_fractions"], reversed(config["timing_fractions"])):
        truth = np.array([base_on+on_fraction/30, base_off+off_fraction/30])
        observed, jac = evaluate(truth)
        errors = []
        for step in config["timing_fd_seconds"]:
            fd = np.column_stack([(evaluate(truth+delta)[0]-evaluate(truth-delta)[0])/(2*step)
                                  for delta in step*np.eye(2)])
            errors.append(float(np.linalg.norm(fd-jac)/np.linalg.norm(jac)))
        result = least_squares(lambda s: evaluate(s)[0]-observed, midpoint,
                               jac=lambda s: evaluate(s)[1], bounds=(low,high), gtol=1e-14)
        cases.append(dict(true_s=truth.tolist(), estimated_s=result.x.tolist(),
                          midpoint_max_ms=float(1000*abs(midpoint-truth).max()),
                          fitted_max_ms=float(1000*abs(result.x-truth).max()),
                          finite_difference_errors=errors, success=bool(result.success)))
    assert all(r["success"] and max(r["finite_difference_errors"])<1e-5 and r["fitted_max_ms"]<.01 for r in cases)
    return cases


def sequential(config):
    # Same standard normals in both arms. Denominator N(0,1), numerator N(.5,1).
    noise = np.random.default_rng(config["sequential_seed"]).normal(
        size=(config["sequential_records"],config["sequential_reports"]))
    results = []
    for mean in (0., .35):
        score = np.cumsum(.5*(noise+mean)-.125, axis=1)
        n = int(np.sum(np.max(score,axis=1)>=-np.log(config["sequential_alpha"])))
        total = len(noise)
        ci = binomtest(n,total).proportion_ci()
        results.append(dict(actual_null_mean=mean, crossings=n, records=total,
                            fraction=n/total, exact_95_interval=[ci.low,ci.high]))
    return results


def main():
    lock = json.loads((HERE/"EXECUTION_FREEZE.json").read_text())
    for name, expected in lock.items():
        if digest(HERE/name)!=expected:
            raise ValueError(f"Changed input: {name}")
    config = json.loads((HERE/"protocol.json").read_text())
    results = dict(geometry=recovery_geometry(config), switching=switching_time(config),
                   sequential=sequential(config))
    (HERE/"RESULTS.json").write_text(json.dumps(results, indent=2)+"\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
