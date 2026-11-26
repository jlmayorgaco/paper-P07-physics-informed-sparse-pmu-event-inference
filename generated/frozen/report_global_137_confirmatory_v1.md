# GLOBAL-137-CONFIRMATORY-V1

Starting HEAD: `9c3bbeb83df055663c1eee0d0c2c3f0578f71f17`; final HEAD: `5189fa16a1e39e31595ed5786f2ccc4487db24d3`; branch `research/pmu-hybrid-dae-bayes-v1`.

## Frozen contract
D, Q, Qij, Sigma0, W2, PMU map, priors, event onset and GH31 were read-only frozen. GK2D is a reference integrator only. OLD31 is not used. ANALYTIC_DAE_TANGENT remains PENDING.

## Fresh data and no-overlap
Physical rows: 3488 (3488 successful); unique trajectories: 3488. Noise realizations: 10564 (H0=100, events=10464). All case IDs use the isolated GLOBAL-137 namespace and frozen manifests were hashed before inference. Historical manifest IDs checked: 1816; overlap: 0.

## Prospective cardinality and support
| regime      |    n |       top1 |       top3 |   cardinality_accuracy |   mean_p_M2 |
|:------------|-----:|-----------:|-----------:|-----------------------:|------------:|
| H0          |  100 | nan        | nan        |               1        | 0.000105618 |
| SINGLE      |  384 | nan        | nan        |               0.9375   | 0.0509195   |
| WEAK_WEAK   | 5760 |   0.24375  |   0.598437 |               0.373611 | 0.426776    |
| WEAK_STRONG | 1440 |   0.6625   |   0.958333 |               0.776389 | 0.807865    |
| MODERATE    | 1440 |   0.988194 |   1        |               0.996528 | 0.995968    |
| FINITE      | 1440 |   1        |   1        |               1        | 1           |

Support accuracy
| regime      |    n |     top1 |     top3 |     top5 |    top10 |   median_rank |   mean_p_true |
|:------------|-----:|---------:|---------:|---------:|---------:|--------------:|--------------:|
| FINITE      | 1440 | 1        | 1        | 1        | 1        |             1 |      1        |
| MODERATE    | 1440 | 0.988194 | 1        | 1        | 1        |             1 |      0.98038  |
| WEAK_STRONG | 1440 | 0.6625   | 0.958333 | 0.985417 | 0.997917 |             1 |      0.625133 |
| WEAK_WEAK   | 5760 | 0.24375  | 0.598437 | 0.716146 | 0.835938 |             2 |      0.218156 |

Event metrics
|     n |   event_prevalence |    AUROC |    AUPRC |   FPR |   FPR_lo |    FPR_hi |       FNR |
|------:|-------------------:|---------:|---------:|------:|---------:|----------:|----------:|
| 10564 |           0.990534 | 0.989664 | 0.999901 |     0 |        0 | 0.0362167 | 0.0728211 |

Source inclusion
|      n |    AUROC |   AUPRC |     Brier |       ECE |   precision |   recall |
|-------:|---------:|--------:|----------:|----------:|------------:|---------:|
| 169024 | 0.949711 | 0.84301 | 0.0427741 | 0.0288932 |    0.907801 | 0.644616 |

True-support amplitude control
| regime      |     n |   coverage95 |         bias |        RMSE |
|:------------|------:|-------------:|-------------:|------------:|
| FINITE      |  2880 |     0.951736 |  1.6151e-06  | 0.000180719 |
| MODERATE    |  2880 |     0.953819 | -3.23911e-06 | 0.000179026 |
| WEAK_STRONG |  2880 |     0.941319 | -1.38098e-07 | 0.000197378 |
| WEAK_WEAK   | 11520 |     0.955295 |  9.78434e-07 | 0.000177649 |

## GK2D reference
| case_id                            | regime      | support   | status   |   logZ_GH31 |   logZ_GK2D |   abs_delta_logZ |    mean_i_GH |    mean_i_GK |    mean_j_GH |    mean_j_GK |
|:-----------------------------------|:------------|:----------|:---------|------------:|------------:|-----------------:|-------------:|-------------:|-------------:|-------------:|
| PAIR_7_12_AIm0p00014_AJm0p00033_R1 | WEAK_WEAK   | (7, 12)   | PASS     |    -1367.25 |    -1367.25 |      7.50333e-12 | -0.000296507 | -0.000296507 | -0.000468163 | -0.000468163 |
| PAIR_7_12_AIm0p00073_AJm0p00255_R1 | WEAK_STRONG | (7, 12)   | PASS     |    -1361.56 |    -1361.56 |      7.7307e-12  | -0.000826641 | -0.000826641 | -0.00272301  | -0.00272301  |
| PAIR_7_12_AIm0p0026_AJm0p0054_R1   | MODERATE    | (7, 12)   | PASS     |    -1381.36 |    -1381.36 |      7.50333e-12 | -0.00262212  | -0.00262212  | -0.00539837  | -0.00539837  |
| PAIR_7_12_AIm0p0113_AJm0p0217_R1   | FINITE      | (7, 12)   | PASS     |    -1371.35 |    -1371.35 |      7.7307e-12  | -0.0112255   | -0.0112255   | -0.0213786   | -0.0213786   |

## Multiplicity decomposition
| regime      |   best_support_term |   multiplicity_term |   support_volume_term |   cardinality_prior_term |   posterior_log_odds_M2_vs_M1 |
|:------------|--------------------:|--------------------:|----------------------:|-------------------------:|------------------------------:|
| FINITE      |          9023.69    |             -2.0149 |          -0.000260956 |                -0.510826 |                    9021.17    |
| H0          |            -2.30542 |             -2.0149 |           0.914831    |                -0.510826 |                      -3.91632 |
| MODERATE    |           494.015   |             -2.0149 |           0.0101601   |                -0.510826 |                     491.5     |
| SINGLE      |            -1.98066 |             -2.0149 |           1.35043     |                -0.510826 |                      -3.15596 |
| WEAK_STRONG |            43.9383  |             -2.0149 |           0.355078    |                -0.510826 |                      41.7676  |
| WEAK_WEAK   |             9.11552 |             -2.0149 |           0.841615    |                -0.510826 |                       7.4314  |

## Historical comparison
| metric                 |   retrospective_value |   confirmatory_value |   difference |
|:-----------------------|----------------------:|---------------------:|-------------:|
| event_AUROC            |              0.994788 |             0.989664 | -0.00512439  |
| event_AUPRC            |              0.999898 |             0.999901 |  2.52651e-06 |
| weak_weak_top1         |              0.1667   |             0.24375  |  0.07705     |
| weak_strong_top1       |              0.6675   |             0.6625   | -0.005       |
| moderate_top1          |              0.9525   |             0.988194 |  0.0356944   |
| finite_top1            |              1        |             1        |  0           |
| source_inclusion_AUROC |              0.970289 |             0.949711 | -0.0205781   |

Model-averaged amplitudes retain an explicit zero atom and are reported as PARTIAL pending interval calibration; weak-weak remains the limiting regime. Noise replays are not counted as independent physical systems.

## Exact statuses
- FRESH_FULL_137_DATA = PASS
- CONFIRMATORY_GH31_GK2D = PASS
- EVENT_DETECTION_CONFIRMATORY = PASS
- CARDINALITY_CONFIRMATORY = PASS
- GLOBAL_DOUBLE_SUPPORT_CONFIRMATORY = PARTIAL
- SOURCE_INCLUSION_CONFIRMATORY = PASS
- TRUE_SUPPORT_AMPLITUDE_CALIBRATION = PASS
- MODEL_AVERAGED_AMPLITUDE_CALIBRATION = PARTIAL
- WEAK_WEAK_IDENTIFIABILITY = LIMITED
- SUPPORT_SPACE_MULTIPLICITY = MODERATE
- CONDITIONAL_FISHER_INCREMENTAL_VALUE = INCONCLUSIVE
- NESTED_SINGLE_MANIFOLD_DISTANCE = INCONCLUSIVE
- PAIR_MANIFOLD_DISTANCE = INCONCLUSIVE
- GLOBAL_SUPPORT_RECOVERY = PARTIAL
- ANALYTIC_DAE_TANGENT = PENDING

## Scope and next action
This is the first fresh full 137-hypothesis confirmation. No model component was retuned and no end-to-end estimator, sequential event model, ML/GNN, or analytic DAE tangent was started.

One next scientific action: if the global result is at least partial with valid weak-weak uncertainty, integrate the frozen single-event contract into IEEE39 end-to-end state/event estimation; do not change this likelihood in this run.