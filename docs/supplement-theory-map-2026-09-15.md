# Mathematical supplement map on 2026-09-15

## Purpose

The supplementary material now carries the full mathematical chain behind the compact claims in the main paper. It separates statements proved under a local statistical model from mechanisms observed in frozen experiments and from joint-estimator components that remain to be executed.

## Appendix D proof inventory

| Block | Mathematical result | Interpretation | Evidence boundary |
| --- | --- | --- | --- |
| Event-map sensitivities | First and second variations of the simulator-consistent DAE event map; homogeneous propagation of second-order model mismatch | The physical dictionary must differentiate the actual callback--solve--sample map | Local smooth fixed-mode result; topology jumps require their declared simulator reset |
| Functional reconstruction | Kernel/factorization equivalence and minimum-covariance linear unbiased estimator | Full state observability is unnecessary when the requested voltage function is estimable | Nonlinear TEST accuracy remains empirical |
| Efficient Fisher information | Projection/Schur-complement formula after deterministic nuisance profiling; proper-prior marginal form | Detectability is the event tangent energy outside the observable nuisance span | Current sourcewise Fisher association is exploratory, not a validated universal predictor |
| Pairwise and onset geometry | Profiled pairwise separation, conditional support Fisher matrix, and onset-amplitude Schur complement | Source separation and onset estimation are distinct from detection | Unknown onset is not evaluated by the frozen known-onset load bank |
| Sparse injectivity | Necessary and sufficient local uniqueness on the admissible difference set plus a restricted stability margin | Sparse PMUs can identify a sparse event without reconstructing every internal state | Applies to the fixed dictionary/noise-free local model; empirical errors still require the frozen tests |
| Added measurements | Conditional Gaussian information decomposition and a discrepancy-robust lower bound | A valid new PMU or frame cannot reduce ideal information; model error can erase the nominal margin | Changing-PMU and cross-simulator campaigns remain pending |
| Temporal information | Exact AR(1) innovation separation, monotonicity, persistent-event linear rate, transient ceiling, and shared-source bottleneck | More frames help only when they add nonredundant candidate separation | T120 is diagnostic and still lacks an independent operating-point block |
| Higher-order contact | Relative curvature after nuisance projection and local detection-rate consequence | Zero first-order Fisher information need not imply nonlinear impossibility | All audited load directions are first-order; curvature-dominated scaling is a boundary result only |

## Appendix E estimator inventory

The executed path is written in the order used to obtain results:

1. Bayesian prediction/correction and the B0--B3 hierarchy.
2. Constrained physical recentering and its feasible tangent-space covariance.
3. The quadratic 16-load event dictionary, frozen W2 likelihood, priors, and known-onset window.
4. Closed-form single-source evidence where conjugacy applies.
5. GH31 quadrature and log-sum-exp normalization for the 137-support nonlinear bank.
6. Cardinality, support, inclusion, amplitude, entropy, effective multiplicity, and credible-set outputs.
7. A 12-step table marking which operations produced the frozen results.

The joint path is a design specification, not a result. It adds candidate-conditioned constrained state solving, integrity variables, learned discrepancy, Laplace evidence with its determinant term, Schur arrival-prior updates, sequential stopping, and model-averaged hidden-voltage uncertainty. Its 10-step table records the present implementation status of every component.

## Submission claim boundary

- The local linear-Gaussian recursion is exactly Bayesian under its stated model.
- The frozen W2/L2 load bank computes normalized Bayesian evidence for zero-, one-, and two-source supports.
- Physical recentering is a regularized constrained estimator with separately assessed uncertainty; it is not relabeled as a complete nonlinear posterior.
- The common state--event--integrity posterior, changing-PMU operation, unknown-onset inference, learned discrepancy, and sequential stopping remain unexecuted.
- No theorem is used to replace a missing experiment, and no diagnostic association is promoted to an operational guarantee.
