# EXACT-WEAK-REGIME-RESOLUTION-V2

Start HEAD: `871669404ff040ae1b98b3e65d07c299daf22ece`; implementation commits: `6fabb5043162a364f3b351ac03a2278cc328c126`, `47ac8d3a6`.

## Contract
Read-only retrospective audit. No new PowerDynamics TDS, no estimator/prior/covariance/quadrature changes. GH31 is the frozen operational integrator; the previous local-Gaussian prefix replay is not used here.

Physical trajectories used: 2400 (2400 rows); frozen noise realizations used: 2400 (1 per physical path); regimes: WEAK_WEAK and WEAK_STRONG; horizons: (5, 10, 15, 20, 25, 30).

## Exact GH31 prefix replay
T=30 cardinality regression: `PASS`. Prefix posterior summaries: 14400 rows; complete support rows: 1972800.
The support probabilities are stored per case/horizon/support; per-bus inclusion is in gh31_prefix_inclusion.csv.

## Analytic reference
The frozen weak-weak audit reported native analytic-vs-FD relative error 5.46e-6 maximum and cosine 1.0; this audit does not alter that result.

## Conditional support resolvability
| outcome   |    n |   spearman_R |    AUROC |
|:----------|-----:|-------------:|---------:|
| exact     | 3360 |    0.0903951 | 0.550135 |
| top3      | 3360 |    0.102005  | 0.569407 |

Pair-level grouped bootstrap
| outcome   |   pair_count |   spearman_pair |   bootstrap_lo |   bootstrap_hi |   leave_one_out_min |   leave_one_out_max |
|:----------|-------------:|----------------:|---------------:|---------------:|--------------------:|--------------------:|
| exact     |          120 |        0.263774 |      0.0749127 |       0.434242 |            0.245195 |            0.285888 |
| top3      |          120 |        0.400611 |      0.225105  |       0.558912 |            0.386286 |            0.423649 |

## Profiled nonlinear manifold distances
Rows: 9600 (four categories per physical case). The frozen second-order mean was whitened with Sigma0. No additional nuisance subspace exists in the frozen likelihood, so P_N_perp=I; the common-source quotient explicitly removes the shared source direction. 97.656% of profile solves met the optimizer convergence flag; the remaining finite solutions are retained and flagged in the table.
| competitor_class   |   count |   median |     mean |
|:-------------------|--------:|---------:|---------:|
| DISJOINT_DOUBLE    |    2400 |  8.0692  | 36.3983  |
| GLOBAL             |    2400 |  1.35916 |  4.37143 |
| M1                 |    2400 | 23.7885  | 81.7978  |
| SHARED_DOUBLE      |    2400 |  1.36186 |  4.39922 |

## Quotient geometry
Rows: 3360. Shared-source pairs are evaluated after residualizing the common source; the previous zero principal angle is therefore recognized as an intersection artifact, not complete indistinguishability.

## Case-level predictors
| predictor          | outcome   |    n |   spearman |      AUROC |
|:-------------------|:----------|-----:|-----------:|-----------:|
| M1                 | p_M2      | 2400 |   0.818344 | nan        |
| M1                 | exact     | 2400 |   0.724544 |   0.898383 |
| M1                 | top3      | 2400 |   0.588499 |   0.86141  |
| M1                 | entropy   | 2400 |  -0.426146 | nan        |
| SHARED_DOUBLE      | p_M2      | 2400 |   0.819816 | nan        |
| SHARED_DOUBLE      | exact     | 2400 |   0.778271 |   0.93327  |
| SHARED_DOUBLE      | top3      | 2400 |   0.526689 |   0.823451 |
| SHARED_DOUBLE      | entropy   | 2400 |  -0.388072 | nan        |
| DISJOINT_DOUBLE    | p_M2      | 2400 |   0.72668  | nan        |
| DISJOINT_DOUBLE    | exact     | 2400 |   0.68084  |   0.875009 |
| DISJOINT_DOUBLE    | top3      | 2400 |   0.588127 |   0.861181 |
| DISJOINT_DOUBLE    | entropy   | 2400 |  -0.476615 | nan        |
| GLOBAL             | p_M2      | 2400 |   0.823341 | nan        |
| GLOBAL             | exact     | 2400 |   0.780481 |   0.934408 |
| GLOBAL             | top3      | 2400 |   0.528718 |   0.824697 |
| GLOBAL             | entropy   | 2400 |  -0.387301 | nan        |
| weak_severity2_R   | p_M2      | 2400 |   0.612714 | nan        |
| weak_severity2_R   | exact     | 2400 |   0.559888 |   0.801652 |
| weak_severity2_R   | top3      | 2400 |   0.5239   |   0.821738 |
| weak_severity2_R   | entropy   | 2400 |  -0.420726 | nan        |
| support_only_R     | p_M2      | 2400 |   0.175979 | nan        |
| support_only_R     | exact     | 2400 |   0.13966  |   0.577391 |
| support_only_R     | top3      | 2400 |   0.128837 |   0.579122 |
| support_only_R     | entropy   | 2400 |  -0.196754 | nan        |
| conditional_fisher | p_M2      | 2400 |   0.175979 | nan        |
| conditional_fisher | exact     | 2400 |   0.13966  |   0.577391 |
| conditional_fisher | top3      | 2400 |   0.128837 |   0.579122 |
| conditional_fisher | entropy   | 2400 |  -0.196754 | nan        |
Global profiled distance correlates with p(M=2) at Spearman 0.823 and exact-support success at 0.780 case-wise (pair-grouped exact-support correlation 0.842); support-only R is much weaker (0.176/0.140 case-wise).

## Resolvability order
| classification         |   count |
|:-----------------------|--------:|
| FIRST_ORDER_RESOLVABLE |     480 |
Local slopes are descriptive fits of the frozen second-order manifold; all 480 tested directions were first-order resolvable (median p=1.99999), with no curvature-resolvable direction.

## Weak-strong conditional geometry
| anchor_effect   |   count |
|:----------------|--------:|
| IMPROVES        |     240 |
| WORSENS         |     240 |
The strong-anchor conditional ratio has median 1.0000 (range 0.9971–1.0030); its effect is negligible and does not explain the 66.25%/95.83% Top-1/Top-3 gap.

## Exact resolution delay and censoring
|    q | target   |   horizon_frames |    n |   unresolved_fraction |   resolved_fraction |
|-----:|:---------|-----------------:|-----:|----------------------:|--------------------:|
| 0.5  | M        |                5 | 2400 |              0.904167 |          0.0958333  |
| 0.5  | M        |               10 | 2400 |              0.78625  |          0.21375    |
| 0.5  | M        |               15 | 2400 |              0.665833 |          0.334167   |
| 0.5  | M        |               20 | 2400 |              0.598333 |          0.401667   |
| 0.5  | M        |               25 | 2400 |              0.545417 |          0.454583   |
| 0.5  | M        |               30 | 2400 |              0.505417 |          0.494583   |
| 0.5  | S        |                5 | 2400 |              0.984167 |          0.0158333  |
| 0.5  | S        |               10 | 2400 |              0.932917 |          0.0670833  |
| 0.5  | S        |               15 | 2400 |              0.855417 |          0.144583   |
| 0.5  | S        |               20 | 2400 |              0.78875  |          0.21125    |
| 0.5  | S        |               25 | 2400 |              0.74125  |          0.25875    |
| 0.5  | S        |               30 | 2400 |              0.707917 |          0.292083   |
| 0.8  | M        |                5 | 2400 |              0.939583 |          0.0604167  |
| 0.8  | M        |               10 | 2400 |              0.83875  |          0.16125    |
| 0.8  | M        |               15 | 2400 |              0.725833 |          0.274167   |
| 0.8  | M        |               20 | 2400 |              0.649167 |          0.350833   |
| 0.8  | M        |               25 | 2400 |              0.600833 |          0.399167   |
| 0.8  | M        |               30 | 2400 |              0.565417 |          0.434583   |
| 0.8  | S        |                5 | 2400 |              0.992917 |          0.00708333 |
| 0.8  | S        |               10 | 2400 |              0.964167 |          0.0358333  |
| 0.8  | S        |               15 | 2400 |              0.906667 |          0.0933333  |
| 0.8  | S        |               20 | 2400 |              0.849167 |          0.150833   |
| 0.8  | S        |               25 | 2400 |              0.809583 |          0.190417   |
| 0.8  | S        |               30 | 2400 |              0.78625  |          0.21375    |
| 0.9  | M        |                5 | 2400 |              0.95     |          0.05       |
| 0.9  | M        |               10 | 2400 |              0.859583 |          0.140417   |
| 0.9  | M        |               15 | 2400 |              0.7525   |          0.2475     |
| 0.9  | M        |               20 | 2400 |              0.670833 |          0.329167   |
| 0.9  | M        |               25 | 2400 |              0.622917 |          0.377083   |
| 0.9  | M        |               30 | 2400 |              0.58625  |          0.41375    |
| 0.9  | S        |                5 | 2400 |              0.997083 |          0.00291667 |
| 0.9  | S        |               10 | 2400 |              0.97375  |          0.02625    |
| 0.9  | S        |               15 | 2400 |              0.930417 |          0.0695833  |
| 0.9  | S        |               20 | 2400 |              0.885417 |          0.114583   |
| 0.9  | S        |               25 | 2400 |              0.845833 |          0.154167   |
| 0.9  | S        |               30 | 2400 |              0.823333 |          0.176667   |
| 0.95 | M        |                5 | 2400 |              0.955833 |          0.0441667  |
| 0.95 | M        |               10 | 2400 |              0.875    |          0.125      |
| 0.95 | M        |               15 | 2400 |              0.773333 |          0.226667   |
| 0.95 | M        |               20 | 2400 |              0.691667 |          0.308333   |
| 0.95 | M        |               25 | 2400 |              0.641667 |          0.358333   |
| 0.95 | M        |               30 | 2400 |              0.601667 |          0.398333   |
| 0.95 | S        |                5 | 2400 |              0.998333 |          0.00166667 |
| 0.95 | S        |               10 | 2400 |              0.97875  |          0.02125    |
| 0.95 | S        |               15 | 2400 |              0.943333 |          0.0566667  |
| 0.95 | S        |               20 | 2400 |              0.905417 |          0.0945833  |
| 0.95 | S        |               25 | 2400 |              0.8725   |          0.1275     |
| 0.95 | S        |               30 | 2400 |              0.850417 |          0.149583   |

|    q | target   |   n_resolved |   n_total |   censored_fraction |   log_tau_vs_log_severity_slope |   reference_a_minus_2 |   reference_a_minus_4 |
|-----:|:---------|-------------:|----------:|--------------------:|--------------------------------:|----------------------:|----------------------:|
| 0.5  | M        |         1187 |      2400 |            0.505417 |                       -0.489459 |                    -2 |                    -4 |
| 0.5  | S        |          701 |      2400 |            0.707917 |                       -0.437299 |                    -2 |                    -4 |
| 0.8  | M        |         1043 |      2400 |            0.565417 |                       -0.454955 |                    -2 |                    -4 |
| 0.8  | S        |          513 |      2400 |            0.78625  |                       -0.333006 |                    -2 |                    -4 |
| 0.9  | M        |          993 |      2400 |            0.58625  |                       -0.463214 |                    -2 |                    -4 |
| 0.9  | S        |          424 |      2400 |            0.823333 |                       -0.314097 |                    -2 |                    -4 |
| 0.95 | M        |          956 |      2400 |            0.601667 |                       -0.466758 |                    -2 |                    -4 |
| 0.95 | S        |          359 |      2400 |            0.850417 |                       -0.294602 |                    -2 |                    -4 |
Unresolved cases are retained as tau>Tmax; evaluated-prefix crossings retain lower/upper interval bounds.

## Gamma horizon scaling
| quantity       |   n |   power_beta | interpretation                  |
|:---------------|----:|-------------:|:--------------------------------|
| gamma4         |   4 |      0.45873 | descriptive; four horizons only |
| gamma4_squared |   4 |      0.91746 | descriptive; four horizons only |
Gamma4^2 has beta=0.917, consistent with approximately linear information accumulation but based on four horizons only.

## Status block
- EXACT_GH31_PREFIX_REPLAY = PASS
- PROFILED_NONLINEAR_MANIFOLD_DISTANCE = PASS_WITH_FLAGS
- COMMON_SOURCE_QUOTIENT_GEOMETRY = PASS
- CASE_LEVEL_RESOLVABILITY_PREDICTION = PASS
- RESOLVABILITY_ORDER_ATLAS = PASS (FIRST_ORDER_DOMINANT)
- CURVATURE_RESOLUTION_MECHANISM = NOT_SUPPORTED
- WEAK_STRONG_CONDITIONAL_MECHANISM = LITTLE_EFFECT (NOT_EXPLANATORY)
- CENSORING_AWARE_RESOLUTION_DELAY = PASS
- FIRST_ORDER_A_MINUS_2_LAW = NOT_SUPPORTED
- CURVATURE_A_MINUS_4_LAW = NOT_SUPPORTED
- GAMMA_INFORMATION_ACCUMULATION = CONSISTENT_WITH_LINEAR_BUT_UNCERTAIN
- FROZEN_ESTIMATOR_REGRESSION = PASS

## Demonstrated
Exact GH31 posterior prefixes can be replayed on the frozen support space; finite-horizon information increases; shared-source geometry must be quotiented; profiled nonlinear distance explains case-level success better than support-only R; censoring materially changes delay summaries.

## Falsified
The prior local-Gaussian prefix replay is not a valid final resolution-delay law. A zero minimum principal angle is not evidence of complete support indistinguishability for shared-source competitors. The tested directions did not exhibit a curvature-dominated (p≈4) separation regime.

## Remaining hypotheses
A universal a^-2 or a^-4 delay law and global structural left-invertibility remain unproven; gamma scaling is only a four-horizon descriptive fit.

## Recoverability diagnosis
Weak-strong cases with global profiled distance above the within-regime median and early GH31 P(M=2) concentration appear algorithmically recoverable. Weak-weak cases with low global distance or persistent right-censoring remain unresolved; additional horizon may help only where gamma and profiled distance are already favorable.

## One next scientific action
Run the prospective exact-GH31 prefix confirmation on a new physical/noise split, preserving the frozen estimator and using the censoring-aware protocol.
