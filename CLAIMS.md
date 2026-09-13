# Current manuscript claim boundary

## Supported component claims

- On the audited PowerDynamics IEEE 39-bus benchmark, eight voltage/current PMUs support accurate nominal reconstruction of 31 hidden bus voltages. A preregistered functional residual is associated with bus-level difficulty.
- Network and operating-point mismatch dominate the tested estimator shifts. A held-out, measurement-only regularized physical recentering closes 97.4--98.3% of the frozen M6 operating-point error gap, although the nuisance information matrix has rank 25 of 43.
- On a separate 690-trajectory ANDES bank, the 448-feature hierarchy with availability handling reaches detection F1 0.989, event macro-F1 0.905, physical Top-1 0.592, and physical Top-3 0.719 for sources represented during training.
- Expanding the event representation improves physical Top-1 by 9.6 percentage points over the 136-feature hierarchy (paired 95% interval 6.9--12.5 points).
- Complete source holdout rejects a zero-shot-source claim for the legacy baseline: 3 of 303 exact decisions are correct across 101 held-source cases and three fitted seeds.
- A centered nonlinear-simulation derivative supplies a numerical physical dictionary for 16 candidate load buses. Its largest central-versus-one-sided discrepancy is 0.235%; this is not an analytic descriptor-DAE tangent.
- In the frozen V2 load-source contract, W2 normalizes the residual covariance (NIS/frame 0.998, ACF(1) -0.0026, Ljung--Box p = 0.598) and DEV selects the second-order-mean L2 likelihood.
- The load-intervention remainder has fitted order 2.00 (bootstrap 95% interval 1.79--2.24). L2 finite-amplitude 95% coverage ranges from 92.9% to 96.0% across the tested signed amplitudes.
- Event-visible information predicts the source-wise empirical 90%-detection amplitude (Spearman rho = -0.794). The projected pairwise information does not convincingly predict source confusion (rho = 0.361; inconclusive).
- Weak-event detection and source resolution separate sharply: sign-pooled source Top-1 is 13.0% at 0.01% load change and 100% at 0.4%, over 9,600 frozen event tests and 800 no-event tests.

## Supported theory and design claims

- The paper defines physical interventions and measurement-integrity states as separate, composable latent variables.
- When the requested functional is estimable in the finite-horizon local model, its generalized least-squares map is the best linear unbiased estimator and its target covariance is explicit.
- Under the stated local linear-Gaussian assumptions, intersecting candidate--nuisance manifolds admit indistinguishable parameter pairs; no classifier can distinguish them uniformly over the declared nuisance set.
- Adding a conditionally independent, correctly modeled PMU block cannot decrease the nuisance-profiled separation margin. The margins are not generally additive, and the result is not a guarantee for an arbitrary learned classifier.
- A bounded second-order DAE remainder gives a sufficient local condition for an affine source-separation margin to survive nonlinear curvature. The load-intervention remainder is measured, but the full multi-family state/integrity curvature certificate is not evaluated.

## Not established

The paper does **not** yet establish an executed multi-family joint state/event/source estimator, multi-family source generalization, calibrated candidate sets, causal nonlinear adaptation, topology transfer, optimal PMU placement, field or HIL validity, cross-simulator superiority, continuous false-alarm control, or real-time deployment. State, load-source, and ANDES metrics come from distinct frozen contracts and must never be pooled.

See `docs/claims-and-evidence.md` for the artifact-level register.
