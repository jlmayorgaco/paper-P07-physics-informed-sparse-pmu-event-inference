# HBG reproduction and audit — 2026-11-12

## Provenance and containment

Input archive: `C:/Users/walla/Downloads/HBG_DAE_Derivacion_y_Verificacion.zip` (SHA-256 `a433c305788a527a1cc025bef478a77a2d863a43e713883fc615c2ae93169a4e`). Inspection found exactly two root-level members, with no absolute paths, parent traversal, or nested paths:

| Member | Size | SHA-256 |
|---|---:|---|
| `verify_hamiltonian_graph_bayes.py` | 4059 | `bd50e57217fb122ac8495189e4e659463c2462bc824eaa985917ac91e65850ca` |
| `DERIVACION_HAMILTONIANA_BAYES_GRAFOS.md` | 20131 | `68689a2552e2a3d963d9aaf337720ccf114dc5d4b1f4853964804d3b69d92a69` |

Both members were extracted to this new experiment directory and retained unchanged. The separately supplied `DERIVACION_HAMILTONIANA_BAYES_GRAFOS (1).md` is 20131 bytes and has matching content to the ZIP document. No historical scripts, paper text, data, or protected figures were edited.

## Original script audit

The script is a compact toy demonstration, not an IEEE-39 implementation. It integrates a four-node, five-edge reduced swing model with a power pulse and one edge removal, then constructs a separate discrete linear Gaussian example. It depends on NumPy and SciPy.

Checks present in the original:

- Segment energy balance from auxiliary accumulated work and dissipation states.
- Potential-energy jump at line removal.
- A rank-one Laplacian update at zero angle (the script checks the DC Laplacian; it does not test the nonlinear Hessian at a nonzero operating angle).
- Analytic rank-one Gaussian log Bayes factor compared against SciPy's multivariate-normal log densities for the same constructed covariance and observations.

The Gaussian density comparison is a sound numerical identity check but is not an independent data/model validation. All original gates use Python `assert`, which is disabled under `python -O`; run with ordinary Python. The energy residual tests numerical integration of the stipulated reduced model only. The source itself correctly reports these results as illustrative and not DAE, IEEE-39, SGSMA, or localization-performance results.

## Reproduction

Run on Python 3.13 with one BLAS thread:

```text
MODELO: 4 buses, 5 branches (illustrative, not IEEE-39)
ENERGY_MAX_BALANCE_RESIDUAL=3.517e-13
ENERGY_SWITCH_JUMP=-1.359727180e-04
EDGE_HESSIAN_RANK_ONE_RESIDUAL=1.570e-16
BAYES_FACTOR_C1=114.993064323
BAYES_FACTOR_C2=44.067872847
BAYES_MAX_IDENTITY_RESIDUAL=1.037e-12
```

The minor differences from the supplied document's last digits are floating-point/platform variation. `verify_extended.py` adds explicit, non-assert gates and independently checks:

1. Rank-one Gaussian BF against normalized multivariate-normal densities and direct numerical integration over the Gaussian amplitude prior.
2. Truncated Gaussian normalization and mean against quadrature.
3. Recovery covariance Woodbury/Schur MAP against the full joint normal-equation solve for state and event amplitude.
4. Profiled Mahalanobis separation monotonicity from a voltage-only observation to correlated voltage/current observations, exact decomposition into a V marginal plus I|V conditional residual at one shared fitted amplitude, and non-additivity versus the sum of independently profiled V and I marginal distances.
5. Energy balance and switching-potential bookkeeping for a small reduced lossless swing network, integrating power from the dense trajectory, plus the nonlinear Hessian rank-one edge-removal update at a nonzero angle.

Captured stdout and gates are in `../experiments/hbg_verification_20261112/original_run_20261112.txt` and `../experiments/hbg_verification_20261112/gates_20261112.json`. The extended gates include direct truncated-prior evidence integration against the posterior/prior truncation-normalizer ratio, nonzero-angle Hessian rank-one update, and an explicit solver-success gate. A failing condition exits with status 1; the gates are not Python asserts. `../experiments/hbg_verification_20261112/manifest_20261112.json` records hashes for source inputs, scripts, and captured outputs. The calculations are deterministic and resource-light.

## Scope and interpretation

The energy identity verified here is for the reduced lossless swing model with damping and external input. It does not establish energy balance for a full power-system DAE with algebraic network states, controllers, exciters, governors, or resistive losses. The added scripts do not load PMU data, the Sauer–Pai DAE, P07 baselines, or the IEEE-39 network. No estimator accuracy, event attribution, generalization, or paper claim is established by these checks.
