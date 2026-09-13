# Current manuscript claim boundary

## Supported component claims

- On the audited PowerDynamics IEEE 39-bus benchmark, eight voltage/current PMUs support accurate nominal reconstruction of 31 hidden bus voltages. A preregistered functional residual is associated with bus-level difficulty.
- Network and operating-point mismatch dominate the tested estimator shifts. A held-out, measurement-only regularized physical recentering closes 97.4--98.3% of the frozen M6 operating-point error gap, although the nuisance information matrix has rank 25 of 43.
- On a separate 690-trajectory ANDES bank, the 448-feature hierarchy with availability handling reaches detection F1 0.989, event macro-F1 0.905, physical Top-1 0.592, and physical Top-3 0.719 for sources represented during training.
- Expanding the event representation improves physical Top-1 by 9.6 percentage points over the 136-feature hierarchy (paired 95% interval 6.9--12.5 points).
- Complete source holdout rejects a zero-shot-source claim for the legacy baseline: 3 of 303 exact decisions are correct across 101 held-source cases and three fitted seeds.

## Supported theory and design claims

- The paper defines physical interventions and measurement-integrity states as separate, composable latent variables.
- Under the stated local linear-Gaussian assumptions, intersecting candidate--nuisance manifolds admit indistinguishable parameter pairs; no classifier can distinguish them uniformly over the declared nuisance set.
- Adding a conditionally independent, correctly modeled PMU block cannot decrease the nuisance-profiled separation margin. The margins are not generally additive, and the result is not a guarantee for an arbitrary learned classifier.

## Not established

The paper does **not** yet establish an executed end-to-end joint state/event/source estimator, calibrated event posteriors, source-generalizable physical inference, diagnosability-to-posterior prediction, causal nonlinear adaptation, topology transfer, optimal PMU placement, field or HIL validity, cross-simulator superiority, continuous false-alarm control, or real-time deployment. State and event metrics come from different frozen campaigns and must never be pooled.

See `docs/claims-and-evidence.md` for the artifact-level register.
