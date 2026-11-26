# RAWSIM39 V1.2 — Identifiability and Restricted RAW0001 Posterior

Generated: 2026-08-30T18:01:35.230863+00:00

## Executive conclusion

The requested identifiability stage is complete. All **56/56** controlled ANDES runs passed TDS completion and frozen-hash checks. The full 18-parameter candidate family must not be estimated jointly: only 10 candidates passed the individual sensitivity/linearity/information screen, and that 10-column Jacobian is numerically ill-conditioned (`κ=722.9`). Rank-revealing selection produced eight stable local directions (`rank=8`, `κ=7.83`).

One of those eight, `fault_reactance_pu`, demanded a robust MAP displacement of **6.15 prior standard deviations**. It was therefore rejected rather than extrapolated or rescued by widening its prior. The released posterior contains exactly **seven parameters**. Its mean was rerun through four new nonlinear ANDES event simulations and passed every predeclared forward-validation gate.

This is a **restricted local Laplace pseudo-posterior**, not proof that all plant, event, and PMU parameters are known. It improves Generation and Load, but it does not solve Fault or Line. `RAW0002` remained untouched, angles and ROCOF were excluded from the physical likelihood, the measurement covariance was not estimated, and no SIM0002–SIM9999 bank was generated.

## Gate ledger

| Gate | Result | Evidence |
| --- | --- | --- |
| Controlled sensitivity executions | PASS | 4 nominal + 52 perturbation runs; zero failures |
| Frozen artifacts | PASS | hashes unchanged after all sensitivity and forward runs |
| RAW0002 isolation | PASS | not read or used by this campaign |
| Full eligible Jacobian | REJECT JOINT | rank 10/10, condition 722.9 |
| Rank-revealing subset | PASS | rank 8/8, condition 7.83 |
| Prior-domain gate | PARTIAL | fault reactance rejected at 6.15σ; seven parameters remain within ±2σ |
| Linear calibration / holdout | PASS | 15.1% / 20.3% robust-objective improvement |
| Nonlinear calibration / holdout | PASS | 12.6% / 17.5% robust-objective improvement |
| Linearization consistency | PASS | discrepancy ratio 0.134 ≤ 1.0 |
| Posterior runtime contract | PASS | 5,000 finite samples, SHA-256 verified, `PosteriorArtifact` instantiation and deterministic draw |

## Released posterior

The table reports the actual bounded sample distribution delivered in `RAW_TWIN_POSTERIOR_V1_SAMPLES.parquet`; the Laplace mean/SD before ±2σ truncation are retained for audit.

| name | layer | nominal | released_sample_mean | released_sample_sd | released_q025 | released_q50 | released_q975 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| generation_delta_p_pu | EVENT_OPERATOR | 3.4 | 2.711 | 0.1377 | 2.452 | 2.709 | 2.981 |
| generation_amplitude | EVENT_OPERATOR | 1.1 | 0.7378 | 0.0865 | 0.6089 | 0.7276 | 0.9344 |
| load_delta_p_fraction | EVENT_OPERATOR | 0.25 | 0.3612 | 0.02112 | 0.3186 | 0.3616 | 0.401 |
| generation_peak_s | EVENT_OPERATOR | 1.25 | 1.31 | 0.1073 | 1.099 | 1.309 | 1.523 |
| generation_delta_q_pu | EVENT_OPERATOR | 1.75 | 1.715 | 0.1682 | 1.383 | 1.716 | 2.046 |
| plant_inertia_scale | PLANT_DIAGNOSTIC | 0.85 | 0.7672 | 0.08038 | 0.6272 | 0.7618 | 0.9355 |
| plant_governor_droop_scale | PLANT_DIAGNOSTIC | 1.5 | 1.664 | 0.1963 | 1.267 | 1.666 | 2.027 |

The two global plant parameters remain global in forward validation: they were applied to every event, not silently switched by event family. The other five parameters belong to their declared Generation or Load operators.

## Nonlinear event-level outcome

| event | calibration_improvement_% | holdout_improvement_% |
| --- | --- | --- |
| fault | -5.063 | -6.409 |
| generation | 46.19 | 38.56 |
| line | -1.936 | -4.486 |
| load | 28.67 | 33.72 |

Generation improves by about 46.2% on calibration horizons and 38.6% on held-out horizons; Load improves by 28.7% and 33.7%. Fault degrades by 5.1% and 6.4%, and Line by 1.9% and 4.5%, because the accepted global plant changes also act on those events. These degradations remain inside the predeclared 10% per-event holdout gate, but they are real and must not be described as improvements.

## Rejected or deferred parameters

| name | layer | final_status | final_reason |
| --- | --- | --- | --- |
| plant_damping | PLANT_DIAGNOSTIC | REJECTED_PRESELECTION | individual_posterior_sd_z>0.9; insufficient sensitivity in at least one declared support event |
| plant_governor_lag_scale | PLANT_DIAGNOSTIC | REJECTED_PRESELECTION | sensitivity_rms<0.005; individual_posterior_sd_z>0.9; insufficient sensitivity in at least one declared support event |
| plant_turbine_time_scale | PLANT_DIAGNOSTIC | REJECTED_PRESELECTION | individual_posterior_sd_z>0.9 |
| plant_avr_gain_scale | PLANT_DIAGNOSTIC | REJECTED_PRESELECTION | individual_posterior_sd_z>0.9; insufficient sensitivity in at least one declared support event |
| plant_avr_time_scale | PLANT_DIAGNOSTIC | REJECTED_PRESELECTION | individual_posterior_sd_z>0.9; insufficient sensitivity in at least one declared support event |
| plant_subtransient_x_scale | PLANT_DIAGNOSTIC | REJECTED_PRESELECTION | individual_posterior_sd_z>0.9 |
| fault_reactance_pu | EVENT_OPERATOR | REJECTED_PRIOR_DOMAIN | unconstrained robust MAP exceeds local/prior domain |z|<=2 |
| fault_duration_s | EVENT_OPERATOR | REJECTED_PRESELECTION | curvature_ratio>0.5 |
| line_duration_s | EVENT_OPERATOR | REJECTED_PRESELECTION | curvature_ratio>0.5 |
| generation_tau_s | EVENT_OPERATOR | REJECTED_JOINT_IDENTIFIABILITY | orthogonal_fraction<0.15; condition_number>50 |
| generation_residual | EVENT_OPERATOR | REJECTED_JOINT_IDENTIFIABILITY | orthogonal_fraction<0.15; condition_number>50 |

Important interpretations:

- fault duration and line duration were highly sensitive but failed the local-curvature gate; sensitivity alone is not identifiability;
- generation residual and recovery time were redundant with stronger Generation directions;
- damping, governor lag, turbine time, AVR gain/time, and subtransient reactance carried insufficient individual information under the conservative likelihood;
- common angle offset and fixed frequency bias were structurally removed by invariant/event-centered features;
- ROCOF artifacts, stochastic covariance, and per-PMU drift remain deferred measurement-layer work.

## Statistical contract

The likelihood uses RAW0001 feature residuals for `VA_MAG`, `IA_MAG`, and `Freq`; each event × signal × horizon × statistic block has total weight one to prevent eight PMUs from masquerading as eight independent experiments. A Huber pseudo-likelihood (`σ=0.25` normalized feature units, `δ=1.5`) controls the extreme mismatch rows. Independent standard-normal priors operate in prior-scaled coordinates. Calibration horizons are 0.25, 1, and 3 seconds; every other available horizon is a temporal holdout.

The posterior covariance is a robust Laplace approximation. It does not include model-form uncertainty, event-label uncertainty, measurement covariance uncertainty, or external-record uncertainty. Therefore the 95% intervals are conditional local intervals, not universal bounds for every future RAW record.

## Figures

1. `IDENTIFIABILITY_SINGULAR_SPECTRUM.png` — unstable full eligible family versus stable selected subset.
2. `CANDIDATE_IDENTIFIABILITY_MAP.png` — sensitivity, curvature, and final disposition of all 18 candidates.
3. `RELEASED_SUBSET_JACOBIAN_COSINE.png` — collinearity structure of the released seven parameters.
4. `RESTRICTED_POSTERIOR_FOREST.png` — posterior means and uncertainties in prior-scaled coordinates.
5. `NONLINEAR_FORWARD_VALIDATION.png` — actual event-level nonlinear improvements and degradations.

## Reproduction

```powershell
python -m experiments.rawsim39_v12_identifiability.campaign
python -m experiments.rawsim39_v12_identifiability.identify
python -m experiments.rawsim39_v12_identifiability.posterior --forward
python -m experiments.rawsim39_v12_identifiability.finalize
```

The sensitivity campaign reuses passing per-run feature/audit caches. The review package contains every compact feature vector and run audit, but intentionally excludes source RAW files. The scientifically correct next step is independent review of this checkpoint, followed—only if accepted—by posterior-predictive validation on the reserved RAW0002 record before generating a large synthetic bank.
