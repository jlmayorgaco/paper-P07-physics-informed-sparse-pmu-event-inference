# Claims and evidence register

This file governs numerical manuscript wording. Every imported artifact is hashed in `generated/frozen/SOURCE_MANIFEST.csv`; the source branch and commit are recorded in `generated/frozen/SOURCE_SNAPSHOT.txt`.

| Claim | Evidence artifact | Status and allowed wording | Boundary |
| --- | --- | --- | --- |
| Eight voltage/current PMUs support accurate recovery of 31 hidden bus voltages under the tested nominal perturbations. | `e04a_b0_b1_b2_summary.csv`; `e04a_b3_summary.csv` | **Supported.** B0, B1, and B2 may be reported on 100 frozen TEST trajectories. | PowerDynamics IEEE 39-bus pedagogical plant; three-second nominal perturbations only. |
| The causal Kalman estimator modestly improves on snapshot WLS. | `e04a_b0_b1_b2_summary.csv` | **Supported, qualified.** Report the 2.7% relative reduction and overlapping trajectory-bootstrap intervals. | Do not claim broad superiority. |
| The preregistered functional residual predicts bus-level difficulty. | `pd_observability_horizons.csv`; `e04a1_e03_vs_e04.csv` | **Supported as association.** Spearman rho = 0.5625. | Nonzero residual and rank 39/114 prohibit an exact full-state or functional-observability claim. |
| Positive fixed-lag smoothing improves TVE. | `e04a_b3_summary.csv` | **Rejected in tested regime.** Every positive lag is slightly worse than lag zero. | Retain as a negative result. |
| Independent U2 temperature scaling improves nominal marginal calibration. | `e04a3_test_calibration.csv` | **Supported for nominal marginals.** Report NLL and real/imaginary coverage. | It does not whiten innovations or establish shift calibration. |
| Low-rank colored discrepancy improves hidden-state inference. | `e04a3_low_rank_residual.csv`; `e04a4_test_metrics.csv`; `e04a5_test_metrics.csv` | **Rejected for tested placements.** Measurement placement reduces ACF(1) but harms NLL/coverage; process placement is neutral. | Low-rank residual structure alone is not evidence for a useful generative correction. |
| Network and operating-point mismatch dominate the tested physical shifts. | `e06_standard_per_case.parquet`; `e06_standard_summary.csv` | **Supported.** At m=1.5, median TVE ratios are 16.985x and 8.318x. | Stress ranges are engineering tests, not priors or field frequencies. |
| Nominal U2 calibration transfers to physical mismatch. | `e06_standard_per_case.parquet` | **Rejected.** Average 95% coverage falls from 92.9% (U0) to 47.5% (U2) across mismatch cases. | Do not describe U2 as robust calibration. |
| Observed innovations can diagnose harmful model mismatch. | `e06_standard_adequacy.csv` | **Supported as retrospective discrimination.** Report macro AUROC/AUPRC with undefined family AUROCs omitted. | Not family identification, continuous alarm control, or calibrated deployment. |
| Physical recentering/relinearization explains most mismatch error. | `e06_standard_oracle_subset.csv`; `e06e_oracle_closure.csv` | **Supported mechanistically by oracle ablations.** | Oracle state/equilibrium is evaluation-only. |
| The tested causal observed-offset recentering recovers the oracle benefit. | `e06e_summary.csv`; `e06e_oracle_closure.csv`; `report_e06e_online_recentering.md` | **Rejected.** Median closure is 0.4%; nominal-safety passes but recovery fails. | Does not rule out leakage-safe nonlinear AC recentering and Jacobian rebuild. |

## Forbidden upgrades

- Do not call the current paper event detection, event localization, field validation, cross-simulator transfer, real-time deployment, or a full nonlinear Hybrid-DAE demonstration.
- Do not call U2 fully calibrated; it is a nominal marginal correction.
- Do not infer exact breakpoint intervals from prose reports. Figures and ratios use the frozen per-case table directly because earlier breakpoint summaries mixed aggregation definitions.
- Do not turn the oracle result into a deployable-method claim.
