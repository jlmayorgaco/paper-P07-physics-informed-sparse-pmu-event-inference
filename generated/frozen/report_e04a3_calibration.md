# E04-A3 uncertainty calibration

The B2 posterior mean, A/C/Q/R/P0, PMU mapping, hidden-output map, and the 100
TEST trajectories were frozen. No RTS/B3, events, ML, or benchmark regeneration
was performed.

## CAL split

`CAL_NOMINAL_V1` contains 30 new nonlinear trajectories × 91 frames. Seeds are
disjoint from DEV/TEST and the manifest was written before fitting.

## NIS audit

For m=32, `NIS_raw = nu' S^-1 nu` and `NIS_norm = NIS_raw/32`. The reported
0.245 is the **raw** NIS (not normalized); normalized NIS is 0.00765 on the
frozen TEST. Under the ideal model raw NIS would have mean 32, but these
residuals are much smaller than the frozen R.
Quantiles and chi-square(32) references are in `e04a3_nis_audit.csv`.

## Temperature fits

U0 NLL on CAL: -13.4715; U1 scalar tau: **0.038548**
(empirical squared-error tau=0.038548), CAL NLL=-15.7659; U2 scales:
tau_Re=0.0135162, tau_Im=0.064707, CAL NLL=-16.0547. U2 is selected because its
componentwise scales give a reproducible NLL improvement and restore balanced
Re/Im variance.

On frozen TEST, U0/U1/U2 NLL are respectively
-13.4766/-15.8981/-16.184.
Selected U2 TEST coverage is Re/Im=0.9392/0.9424
(90%=0.9077/0.8880,
50%=0.7110/0.6193); standardized variances are
0.8673/0.8680.

## Colored discrepancy

CAL innovation norm ACF at lags 1/2/3/5/10 is
[0.635216, 0.307398, 0.275654, 0.237113, 0.171312]; Ljung-Box-style Q(10)=62.83.
The diagnostic AR(1) coefficient is rho1=0.635216. PCA cumulative variance
at ranks 1/2/4/8/16 is [0.767594, 0.956734, 0.992203, 0.99991, 1.0]; this supports a
low-rank Gauss-Markov discrepancy diagnostic, not an integrated model yet.

For selected U2, worst calibration buses by Re coverage error are
[{'hidden_bus': 37, 'coverage_re': 0.5108791208791209, 'coverage_im': 1.0}, {'hidden_bus': 25, 'coverage_re': 0.6125274725274725, 'coverage_im': 1.0}, {'hidden_bus': 38, 'coverage_re': 0.6712087912087912, 'coverage_im': 0.9516483516483516}, {'hidden_bus': 21, 'coverage_re': 0.8392307692307692, 'coverage_im': 0.813076923076923}, {'hidden_bus': 35, 'coverage_re': 0.8434065934065934, 'coverage_im': 0.8142857142857143}].
Spearman(E03 functional residual, |coverage-0.95|) = **0.254456**.

## Runtime accounting correction

The prior B3 value is labelled `smoother_overhead` (0.087 ms/frame), not a
complete estimator runtime. The complete B2 `filter_runtime` reference is
1.078 ms/frame; a fair B3 total is `filter_runtime + smoother_overhead`, about
1.165 ms/frame, versus 33.333 ms/frame.

## Status

- E04-A-RECONSTRUCTION = **PASS**
- MARGINAL_VARIANCE_CALIBRATION = **PASS** (U2 frozen from CAL)
- INNOVATION_WHITENESS = **FAIL** (residual remains colored)
- E04-A-PROBABILISTIC = **MARGINAL_CALIBRATED_BUT_COLORED**

The next extension should be a physics-only colored/model-discrepancy state,
not additional covariance-temperature tuning.
