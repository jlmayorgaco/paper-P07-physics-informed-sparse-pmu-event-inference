# Mathematical supplement map on 2026-09-15

## Purpose

The supplementary material now carries the full mathematical chain behind the compact claims in the main paper. It separates statements proved under a local statistical model from mechanisms observed in frozen experiments and from joint-estimator components that remain to be executed.

## Appendix D proof inventory

| Block | Mathematical result | Interpretation | Evidence boundary |
| --- | --- | --- | --- |
| Consistency jump and event-map sensitivities | Local algebraic right-limit expansion, direct PMU signature, reduced dynamic forcing, sampled-map variations, and homogeneous propagation of second-order mismatch | Differential states remain continuous while algebraic variables re-equilibrate; direct and dynamic visibility are distinct | The physical contract is proved locally, but callback/right-limit logging and derivative convergence remain open; topology jumps require their declared simulator reset |
| Functional reconstruction | Kernel/factorization equivalence and minimum-covariance linear unbiased estimator | Full state observability is unnecessary when the requested voltage function is estimable | Nonlinear TEST accuracy remains empirical |
| Efficient Fisher information | Projection/Schur-complement formula after deterministic nuisance profiling; proper-prior marginal form | Detectability is the event tangent energy outside the observable nuisance span | Current sourcewise Fisher association is exploratory, not a validated universal predictor |
| Pairwise and onset geometry | Profiled pairwise separation, conditional support Fisher matrix, and onset-amplitude Schur complement | Source separation and onset estimation are distinct from detection | Unknown onset is not evaluated by the frozen known-onset load bank |
| Sparse injectivity | Necessary and sufficient local uniqueness on the admissible difference set plus a restricted stability margin | Sparse PMUs can identify a sparse event without reconstructing every internal state | Applies to the fixed dictionary/noise-free local model; empirical errors still require the frozen tests |
| Added measurements | Conditional Gaussian information decomposition and a discrepancy-robust lower bound | A valid new PMU or frame cannot reduce ideal information; model error can erase the nominal margin | Changing-PMU and cross-simulator campaigns remain pending |
| Temporal information | Exact AR(1) innovation separation, monotonicity, persistent-event linear rate, transient ceiling, and shared-source bottleneck | More frames help only when they add nonredundant candidate separation | T120 is diagnostic and still lacks an independent operating-point block |
| First- and higher-order contact | Profiled coefficient $\gamma_1$, relative curvature after nuisance projection, and local detection-rate consequence | Positive $\gamma_1$ gives first-order separation; zero first-order Fisher information need not imply nonlinear impossibility | The $\Delta^2(a)/a^2$ convergence test is pending; all audited load directions are first-order and curvature-dominated scaling is a boundary result only |
| Multi-event signed support geometry | Support-to-support projection, exclusive-source quotient, conditional matrix, enrichment monotonicity, nested-support degeneracy, and conditional principal angles | Exact support depends on the true-exclusive response outside the competitor span; full-support angles contain trivial zeros when supports overlap | Deterministic identities pass, but the analytic IEEE 39-bus tangent/nuisance dictionary has not been validated |
| Physical tangent-cone geometry | Local cone-distance law, nuisance quotient, cone--span relation, NNLS/KKT conditions, directed cone separation, and one-sided corrections to shared-source and sparse-recovery claims | Sign information can restore separation hidden by a span relaxation; cardinality still requires integrated evidence | Deterministic cone checks pass; no IEEE 39-bus fault/outage/trip cone has been evaluated |

## Appendix E estimator inventory

The executed path is written in the order used to obtain results:

1. Bayesian prediction/correction and the B0--B3 hierarchy.
2. Constrained physical recentering and its feasible tangent-space covariance.
3. The quadratic 16-load event dictionary, frozen W2 likelihood, priors, and known-onset window.
4. Closed-form signed and one-sided single-source evidence where conjugacy applies.
5. GH31 quadrature and log-sum-exp normalization for the 137-support nonlinear bank.
6. Cardinality, support, inclusion, amplitude, entropy, effective multiplicity, and credible-set outputs.
7. A 12-step table marking which operations produced the frozen results.

The joint path is a design specification, not a result. It adds candidate-conditioned constrained state solving, integrity variables, learned discrepancy, cone--Laplace evidence with determinant and physical-boundary terms, Schur arrival-prior updates, sequential stopping, and model-averaged hidden-voltage uncertainty. Its 10-step table records the present implementation status of every component. The singular quartic counterexample explains why genuine rank loss cannot be repaired by inserting a pseudoinverse into regular Laplace theory.

## Submission claim boundary

- The local linear-Gaussian recursion is exactly Bayesian under its stated model.
- The frozen W2/L2 load bank computes normalized Bayesian evidence for zero-, one-, and two-source supports.
- Physical recentering is a regularized constrained estimator with separately assessed uncertainty; it is not relabeled as a complete nonlinear posterior.
- The common state--event--integrity posterior, changing-PMU operation, unknown-onset inference, learned discrepancy, and sequential stopping remain unexecuted.
- No theorem is used to replace a missing experiment, and no diagnostic association is promoted to an operational guarantee.
