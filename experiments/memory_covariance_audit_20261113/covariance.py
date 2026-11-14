"""Prefix covariance under controlled Gaussian innovations in nominal channel units."""
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.linalg import cholesky, solve_triangular
from scipy.signal import lfilter
from sklearn.covariance import LedoitWolf

HERE = Path(__file__).resolve().parent
SNAPSHOT = HERE.parent / "channel_information_20261112/input_snapshot.npz"


def run(config):
    assert hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest() == config["snapshot"]
    with np.load(SNAPSHOT) as archive:
        cov = archive["S"]
    cov = (cov + cov.T) / 2
    units = np.sqrt(np.diag(cov))
    nominal = cov / units[:, None] / units[None, :]
    rng = np.random.default_rng(config["seed"])
    rows = []
    for diagonal in config["local_variance"]:
        truth = nominal + diagonal * np.eye(len(nominal))
        factor = cholesky(truth, lower=True)
        oracle_logdet = 2 * np.log(np.diag(factor)).sum()
        for rho in config["ar"]:
            for n in config["prefix"]:
                scores = {key: [] for key in ("scaled_nominal", "sample", "shrinkage")}
                for _ in range(config["replicates"]):
                    draws = rng.standard_normal((n, len(cov)))
                    draws[1:] *= np.sqrt(1-rho*rho)
                    prefix = lfilter([1], [1, -rho], draws, axis=0) @ factor.T
                    sample = np.cov(prefix, rowvar=False, bias=True)
                    scaled = nominal * np.trace(sample)/np.trace(nominal)
                    shrunk = LedoitWolf().fit(prefix).covariance_
                    for key, estimate in zip(scores, (scaled, sample, shrunk)):
                        left = solve_triangular(factor, estimate, lower=True)
                        relative = solve_triangular(factor, left.T, lower=True).T
                        eig = np.linalg.eigvalsh(relative)
                        assert eig.min() > 0
                        # Exact expected excess negative log-density under truth.
                        kl = .5 * np.sum(1/eig - 1 + np.log(eig))
                        assert kl > -1e-10
                        inverse_error = np.max(np.abs(1/eig - 1))
                        whitened_error = np.max(np.abs(eig - 1))
                        if whitened_error < 1:
                            assert inverse_error <= whitened_error/(1-whitened_error)+1e-10
                        scores[key].append((kl, inverse_error))
                rows.append(dict(local_variance=diagonal, ar=rho, prefix=n,
                                 oracle_logdet=float(oracle_logdet),
                                 arms={key: dict(zip(("median_kl", "median_inverse_error"),
                                                     np.median(values, axis=0).tolist()))
                                       for key, values in scores.items()}))
    return rows


if __name__ == "__main__":
    config = json.loads((HERE/"protocol.json").read_text())
    lock = json.loads((HERE/"EXECUTION_FREEZE.json").read_text())
    for name, digest in lock.items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest
    rows = run(config)
    (HERE/"covariance_results.json").write_text(json.dumps(rows,indent=2)+"\n")
    print(json.dumps(rows,indent=2))
