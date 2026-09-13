# Claims and evidence register

This register governs manuscript wording. Every imported artifact is hashed in `generated/frozen/SOURCE_MANIFEST.csv`; the source branch and commit are recorded in `generated/frozen/SOURCE_SNAPSHOT.txt`.

| Claim | Evidence artifact | Evidence class and allowed wording | Boundary |
| --- | --- | --- | --- |
| The joint state/event/source problem has a projection-dependent information limit under the stated local Gaussian model. | Proposition 1 and Corollary 1 in Section IV. | **Theoretical.** Equal projected signatures imply Bayes error at least one half under equal priors; adding conditionally independent PMUs cannot reduce pairwise information. | Local linearization, stated covariance, hypothesis pair, and nuisance tangent space only. |
| Eight voltage/current PMUs support accurate recovery of 31 hidden bus voltages under the tested nominal perturbations. | `e04a_b0_b1_b2_summary.csv`; `e04a_b3_summary.csv` | **Empirical-primary.** Report B0--B3 on 100 frozen TEST trajectories. | PowerDynamics IEEE 39-bus pedagogical plant; three-second nominal perturbations only. |
| The causal Kalman estimator modestly improves on snapshot WLS. | `e04a_b0_b1_b2_summary.csv` | **Empirical-primary, qualified.** Report the 2.7% relative reduction and overlapping trajectory-bootstrap intervals. | No broad superiority claim. |
| The preregistered functional residual predicts bus-level difficulty. | `pd_observability_horizons.csv`; `e04a1_e03_vs_e04.csv` | **Empirical-secondary association.** Spearman rho = 0.5625. | Nonzero residual and rank 39/114 prohibit exact full-state or functional-observability wording. |
| Positive fixed-lag smoothing improves TVE. | `e04a_b3_summary.csv` | **Rejected.** Every positive lag is slightly worse than lag zero in the tested regime. | Preserve as a negative result. |
| U2 temperature scaling improves nominal marginal calibration. | `e04a3_test_calibration.csv` | **Empirical-secondary, qualified.** Report NLL and real/imaginary marginal coverage. | It does not whiten innovations or establish shift calibration. |
| Low-rank colored discrepancy improves hidden-state inference. | E04A3--E04A5 artifacts | **Rejected.** Measurement placement reduces ACF(1) but harms NLL/coverage; process placement is neutral. | Low-rank structure alone is not evidence for a useful generative correction. |
| Network and operating-point mismatch dominate the tested physical shifts. | `e06_standard_per_case.parquet`; `e06_standard_summary.csv` | **Empirical-secondary.** At m=1.5, median TVE ratios are 16.985x and 8.318x. | Stress ranges are tests, not priors or field frequencies. |
| Nominal U2 calibration transfers to physical mismatch. | `e06_standard_per_case.parquet` | **Rejected.** Average 95% marginal coverage falls from 92.9% to 47.5%. | Do not call U2 robustly calibrated. |
| Observed innovations diagnose harmful mismatch. | `e06_standard_adequacy.csv` | **Empirical-secondary, retrospective.** Report macro AUROC/AUPRC and omit undefined family AUROCs. | Not family identification, online alarm control, or calibrated deployment. |
| Measurement-only physical static MAP recovers hidden voltages under M6 operating-point shift. | E06-H summary, per-case, closure, and manifests | **Empirical-primary for the M6 snapshot contract.** Median TVE falls from 0.1989/0.3883/0.5779% to 0.0053/0.0075/0.0097%, closing 97.4--98.3% of the frozen gap. | One equilibrium snapshot, M6 only; not causal, event-conditioned, or topology-transfer evidence. |
| The M6 nuisance vector is uniquely identifiable. | `e06h_identifiability.csv` | **Rejected.** Observed nuisance Jacobian rank is 25/43, with nullity 18. | Accurate target recovery does not imply nuisance recovery. |
| Hidden voltages are exactly functionally identifiable under M6. | `e06h_identifiability.csv` | **Not established.** Normalized target residual is 0.0419. | Say empirical recovery despite nuisance non-uniqueness. |
| Static-MAP Laplace uncertainty is calibrated. | `e06h_uncertainty_summary.csv` | **Partially rejected.** Marginal coverage is near one, while median NEES-like values rise from 111.6 to 294.2. | Do not equate marginal coverage with joint calibration. |
| The supervised physics-guided event hierarchy performs well when source identities are represented in training. | `legacy_replayed_summary.csv`; `legacy_descriptor_paired_intervals.csv` | **Historical empirical evidence.** Report detection F1 0.989, event macro-F1 0.905, physical-source Top-1 0.592, Top-3 0.719, and integrity-source Top-1 0.974 over 690 trajectories. | Grouped known-source contract; not unseen-source generalization. |
| Electrical descriptors improve physical-source ranking in the legacy hierarchy. | `legacy_descriptor_paired_intervals.csv` | **Historical empirical-secondary.** Top-1 increases by 9.6 percentage points, 95% paired interval 6.9--12.5. | Component result within the same supervised hierarchy. |
| The legacy hierarchy generalizes to unseen physical sources. | `legacy_unseen_sources_recomputed.csv` | **Rejected.** Only 3/303 exact source decisions are correct across 101 held-source parents and three seeds, even with the event family supplied. | Strong evidence of source memorization under this contract. |
| The RAW0001 candidate model is a reliable event alarm. | `legacy_raw0001_transfer_results.csv` | **Rejected.** It recovers 2.7/12 event episodes and 0.3/5 physical episodes on average. | One independent record; preserves a negative transfer result. |
| The proposed joint Bayesian estimator improves source localization or end-to-end state estimation. | None yet. | **Hypothesis, not established.** Present as formulation and required experiment. | Requires a frozen common-contract comparison of ML-only, physics-only, hybrid residual, and full joint methods. |

## Forbidden upgrades

- Do not describe the manuscript as an end-to-end validated joint estimator.
- Do not call the legacy event model zero-shot, source-generalizing, Bayesian, or robust.
- Do not call retrospective inference real-time or continuous unless latency and normal exposure are measured.
- Do not call U2 or the static-MAP Laplace covariance fully calibrated.
- Do not infer topology, PMU loss/join, cross-simulator, field, or HIL performance from nominal/M6 evidence.
- Do not turn oracle recentering into a deployable-method claim.
- Do not claim exact functional identifiability when the projected residual is nonzero.
