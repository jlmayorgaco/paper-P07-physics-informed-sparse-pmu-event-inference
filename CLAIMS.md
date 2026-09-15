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
- A fresh prospective bank evaluates all 137 hypotheses, comprising no event, 16 single sources, and all 120 two-source supports. It contains 3,488 successful nonlinear physical trajectories and 10,564 noise realizations with no identifier overlap against 1,816 historical records.
- Exact two-source support Top-1 is 24.4% for weak--weak, 66.3% for weak--strong, 98.8% for moderate, and 100% for finite pairs. Weak--weak cardinality accuracy is 37.4% and Top-3 is 59.8%; global two-source recovery is therefore partial.
- In the prospective bank, event detection AUROC/AUPRC is 0.9897/0.9999 and per-bus source-inclusion AUROC/ECE is 0.9497/0.0289. The no-event population contains only 100 records, so zero observed false positives is not an operational false-alarm result.
- A retrospective 2,400-case weak-regime audit associates global profiled manifold distance with exact-support success (Spearman rho 0.780), while the support-only quantity is much weaker (rho 0.140). All tested directions are first-order resolvable; a curvature-dominated explanation is not supported.
- The T120 diagnostic has a positive frozen equilibrium four-source margin and no zero-distance pair at numerical tolerance, but near-unit signature coherence shows poor conditioning. This is a local-model diagnostic, not a universal no-ambiguity result.
- At T120, median whitened model error is 0.2053 for D, 0.4690 for D+Q, and 0.00307 for D+Q+Qij. Cross interaction is therefore essential for the tested simultaneous load responses. The validation bank has only 32 nominal-operating-point paths and remains limited.

## Supported theory and design claims

- The paper defines physical interventions and measurement-integrity states as separate, composable latent variables.
- When the requested functional is estimable in the finite-horizon local model, its generalized least-squares map is the best linear unbiased estimator and its target covariance is explicit.
- Under the stated local linear-Gaussian assumptions, intersecting candidate--nuisance manifolds admit indistinguishable parameter pairs; no classifier can distinguish them uniformly over the declared nuisance set.
- Adding a conditionally independent, correctly modeled PMU block cannot decrease the nuisance-profiled separation margin. The margins are not generally additive, and the result is not a guarantee for an arbitrary learned classifier.
- A K-sparse persistent-event vector is uniquely determined over a finite horizon exactly when the event operator kernel contains no nonzero 2K-sparse vector. Nonsingularity establishes uniqueness; the smallest support-Gramian eigenvalue governs conditioning.
- With a fixed nuisance domain and prefix-consistent whitening, profiled separation cannot decrease as samples are appended. A nonzero profiled steady signature implies linear information growth; an equal steady signature can leave a transient-only, saturating separation.
- A zero projected event tangent is not, by itself, a universal nonlinear impossibility statement because relative curvature may retain higher-order separation. This possibility is stated as a boundary, not claimed as the mechanism: all tested load directions are first-order resolvable and the curvature-dominated delay explanation is not supported.
- For a whitened low-rank discrepancy covariance, principal angles give the exact worst retained fraction of protected event information. The complete expected Gaussian score gives a finite fixed-basis variance; the result is a design theorem, not evidence that a learned correction improves the IEEE 39-bus estimator.

## Not established

The paper does **not** yet establish an executed multi-family joint state/event/source estimator, multi-family source generalization, calibrated candidate sets, causal nonlinear adaptation, topology transfer, optimal PMU placement, field or HIL validity, cross-simulator superiority, continuous false-alarm control, or real-time deployment. The T120 contract also lacks independent operating-point validation and a reconciled absolute separation scale. State, load-source, and ANDES metrics come from distinct frozen contracts and must never be pooled.

See `docs/claims-and-evidence.md` for the artifact-level register.
