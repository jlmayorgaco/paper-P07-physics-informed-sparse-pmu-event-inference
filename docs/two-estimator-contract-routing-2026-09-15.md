# Two-estimator contract routing

## Canonical taxonomy

The paper evaluates two event-estimator proposals, not a growing list of solvers.

1. $\mathcal E_{\mathrm B}$ is the implemented batch physical-manifold Bayesian estimator. It receives a centered 32-channel PMU window and fixes the operating point, onset, and load family. It compares 137 supports of cardinality zero, one, or two through the frozen quadratic response manifold and W2 covariance. Event amplitudes are integrated by GH31 rather than replaced by point estimates.
2. $\mathcal E_{\mathrm J}$ is the proposed joint Hybrid-DAE Bayesian estimator. It places state, operating nuisance, family, onset, support, amplitude, and integrity in one candidate-conditioned posterior. It has not yet produced the paper's empirical results.

The B0--B3 state hierarchy remains an independently evaluated reconstruction component. A filter, smoother, moving-horizon optimizer, generalized EM loop, or sequential likelihood implementation is a numerical realization, not a new scientific estimator.

## Required consistency checks

- A sequential implementation of $\mathcal E_{\mathrm B}$ must reproduce the batch posterior at every prefix when it uses the same AR(1) model and initial density.
- Under restriction $\mathcal R_0$, $\mathcal E_{\mathrm J}$ must use the same operating point, onset, load family, 137-support bank, quadratic surrogate, W2 covariance, and priors as $\mathcal E_{\mathrm B}$. Its restricted posterior must then equal the batch posterior to numerical tolerance.
- Failure of either equality indicates an implementation error or a changed statistical contract. It cannot be explained away as a different solver.

## Evidence boundary

Only $\mathcal E_{\mathrm B}$ currently supports event/source claims. Candidate-conditioned virtual currents, powers, frequency quantities, integrity inference, and state/event model averaging belong to $\mathcal E_{\mathrm J}$ and remain proposed. Hidden-voltage reconstruction is supported separately by B0--B3 and the physical recentering campaign.
