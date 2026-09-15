# Robust-discrepancy and nonlinear-margin routing on 2026-09-15

## Scientific disposition

| Incoming block | Disposition | Reason |
| --- | --- | --- |
| Binary, beta-min, contact-order, and Fano limits | Already integrated; no duplicate prose | These results and their independent checks are already in Section IV and Supplementary Appendix D. |
| Exact low-rank discrepancy retention | Main consequence plus full supplementary theorem | The projector inverse and principal-angle information loss directly constrain a candidate-residual learner. |
| Utility-only discrepancy optimization for `q=1` | Corrected, not adopted as a Bayesian tuning theorem | Maximizing only the reduction in quadratic mismatch penalty omits `log det(C)` and the base-noise trace. Its infinite-variance optimum is therefore an artifact of an incomplete score. |
| General `q>1` SDP and moment/SOS hierarchy | Deferred to an optimization/theory paper | It is an offline global-design route, not an executed IEEE 39-bus method, and would dilute the present state/event evidence chain. |
| Master causal theory synthesis | Used as an audit map | Its subspace-versus-cone, simple-Gaussian, proper-prior, prefix-consistency, and pseudoinverse warnings agree with the current claim boundaries. |
| Targeted nonlinear margin closure directive | Protocol provenance only | Embedded branch and execution instructions belong to the source campaign, not to this paper-editing task. Results enter the manuscript only after frozen analysis and classification artifacts exist. |

## Mathematical correction integrated

For a frozen discrepancy basis, the paper now retains the exact information fraction

`rho = 1 - [s/(1+s)] sigma_max^2(Q_U^T Q_D)`.

It also evaluates the complete expected Gaussian score under residual covariance `I + C_m`:

`Delta L(s) = q log(1+s) - [s/(1+s)] (q + E_D)`.

The finite unconstrained optimum is `s = E_D/q`; a requested information-retention floor clips it at the exact geometric variance cap. This replaces the utility-only conclusion that infinite discrepancy variance is optimal. Under strict no-loss protection, safe projected PCA is the top-`q` eigenspace of the mismatch covariance restricted to the orthogonal complement of the protected event directions.

`scripts/verify_discrepancy_design.py` independently checks the covariance inverse, principal-angle retention, variance cap, finite likelihood optimum, projected-PCA solution, and protected-distance floor. These are controlled algebraic checks, not power-system validation.

## Targeted nonlinear campaign status

The source campaign is on branch `research/pmu-hybrid-dae-bayes-v1` at `155b686a260e1a331dec4b1b98fca6c961aac38b`. Its preregistration selects 48 targets over three operating points. All 48 Stage-A trajectory entries currently report `EXECUTED_SUCCESS` and have SHA-256 values in the execution manifest. However, the source tree contains no analysis implementation, classification table, report, or figure for the campaign, and no Stage-B decision has been frozen. These trajectories are therefore not imported as paper evidence in this revision.

The gate for later inclusion is a committed, reproducible package containing center-error certificates, activated Stage-B stencils, nonlinear profiled margins, frozen rule classifications, failure accounting, and an explicit comparison between predicted hard pairs and physical-estimator errors.

## Paper boundary

The main article receives one mechanism equation because it prevents a learned correction from absorbing event directions. The supplementary material receives the proof and deterministic checks. The paper still does not claim that a learned discrepancy layer improves state or source inference, and it does not claim that the targeted nonlinear campaign has closed the IEEE 39-bus first-order margin law.
