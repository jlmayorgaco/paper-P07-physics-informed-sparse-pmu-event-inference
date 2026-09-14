# Disposition of the Claude v2 review

This record treats `11_V2_REVIEWERS.md`, `12_V2_UPGRADE_PLAN.md`, and
`13_V2_CLAIM_DELTA.csv` as external reviewer comments. They do not override the
frozen evidence, the 20-page limit, or the advisers' requirement that the title
contain no colon.

## Corrections incorporated in the manuscript

| Review issue | Disposition | Manuscript change |
| --- | --- | --- |
| Missing theoretical attribution | Accepted | Added and positioned Eriksson (2013), Nyberg (2002), Pasqualetti et al. (2013), Scharf and Friedlander (1994), Zhao et al. (2014), Gillijns and De Moor (2007), and classical outage-inference papers. Section IV-C now states that its projection is a specialization, not a new identity. |
| General theory presented beside a narrower executed model | Accepted | Sections IV-C and V-B now state that the load experiment does not fit initial-state or integrity nuisance directions and does not estimate the nonlinear curvature certificate. |
| Undocumented normal-data generator | Accepted | The paper now declares the Gaussian innovation scales, AR(1) coefficient, fixed cross-channel coupling, disjoint seeds, and the absence of ambient load variation. |
| Undocumented L2 evidence integral | Accepted | The paper now states the 401-point amplitude quadrature, bounds, log-sum-exp normalization, and local grid refinement. |
| ANDES replica ambiguity | Accepted | The event contract now defines the severity grid, operating-scale grid, deterministic source/replica formulas, seed changes, fixed onset, and RAW-calibrated observation noise. |
| Smoother conclusion too strong | Accepted | The result is recast as a model-misspecification diagnostic supported by colored innovations; no general latency conclusion remains. |
| M2--M5 near-unity ratios called tolerance | Accepted | These rows are now described as unexcited 3-s null responses, not robustness. |
| Static-recentering NEES unexplained | Accepted | The Results section identifies the omitted hidden-target image of the PMU-uninformed nuisance nullspace. |
| W0 treated as a baseline | Accepted | W0 is explicitly an unscaled failure diagnostic; a CAL-fitted scaled identity is listed as a missing baseline. |
| Pairwise information compared with pooled 16-way confusion | Accepted | The comparison is now labeled a mismatched test. The required source-by-amplitude prediction is not claimed as executed. |
| Detection-threshold correlation overstated | Accepted | The abstract, Results, Discussion, and claim register now call the $n=16$ association exploratory and disclose threshold discretization and missing inferential uncertainty. |
| Threshold-sensitive observability pseudo-rank | Accepted as an unresolved numerical audit | The paper keeps the failure visible and makes the residual association exploratory pending an SVD/noise-tied recomputation. No corrected numerical result is invented. |
| Internal manuscript labels | Accepted | Replaced `P07 method`, removed the `MANUSCRIPT DRAFT` footer, and rewrote the internal W2/L2 architecture labels in reader-facing terms. |
| RAW0001 missing interval unclear | Accepted | The caption identifies the approximately 30-frame/s source and converts 812 frames to approximately 27.1 s. |

## Evidence gates not converted into prose claims

The following suggestions require new frozen experiments. They remain open
gates rather than manuscript "corrections":

- a 19-load, 10-generation, outage, and fault candidate bank;
- localizer mismatch and recentering repair on M1/M6 plants;
- PMU loss/addition sweeps and a recomputed SVD-based observability audit;
- open-bank events and calibrated abstention;
- ANDES physics-dictionary inference under the same source-holdout contract;
- unknown onset and detection-delay evaluation;
- ambient-load, PMU-noise, and long-normal-exposure sweeps;
- a CAL-fitted scaled-identity covariance baseline;
- source-level psychometric curves and a source--amplitude multi-hypothesis error test;
- numerical curvature bounds and an unknown-input Kalman filter;
- an out-of-family nuisance basis and same-information learned baseline.

Until these gates are run, the paper's empirical claim remains one matched,
known-onset, fixed-topology, closed-bank load family plus separate state and
legacy-event contracts.

## Suggestions not adopted

- The proposed title containing a colon was not used because it conflicts with
  the advisers' explicit title requirement. The current title already reflects
  the narrower executed evidence.
- Expected experimental stories were not written as results. New outcomes will
  enter the manuscript only through hashed frozen artifacts and regenerated
  tables/figures.
