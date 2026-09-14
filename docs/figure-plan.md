# Figure and table map

## Shared visual grammar

Figures 1, 5, and 6 are the visual reference for the manuscript. New and revised graphics use the same color-blind-safe blue/orange/green/purple palette, left-aligned panel headings, comparable type size at final two-column width, restrained grids, direct annotations of only the decisive values, and vector output. Multi-panel figures are ordered as a scientific argument---mechanism or stressor, observed evidence, and claim boundary---rather than as a collection of available metrics. Continuous color maps are reserved for fields or matrices and are paired with printed values when exact reading matters.

Every empirical panel is generated from a frozen artifact. Conceptual drawings are TikZ/vector graphics; they contain no empirical values.

| Asset | Scientific function | Evidence/source | Status |
| --- | --- | --- | --- |
| Fig. 1 | Separate the evaluated state and load-source lanes from the unvalidated joint candidate path. | Joint formulation in Sections III--V. | TikZ three-lane evidence diagram, integrated. |
| Fig. 2 | Show how state/input, event/source, and observability/sensor-value developments converge on the unresolved combined contract. | Verified literature through 2026. | TikZ convergence timeline, integrated. |
| Fig. 3 | Tell the observability-claim story: the pseudo-rank contradiction, improved conditioning without a certificate, and the boundary between structural and empirical evidence. | `pd_observability_horizons.csv`, `e04a_b0_b1_b2_summary.csv`, `e04a1_e03_vs_e04.csv`. | Full-width generated vector PDF/PNG, integrated. |
| Fig. 4 | Distinguish first-order source separation from shared-tangent, second-order relative curvature. | Propositions 2--3 and Corollary 2. | TikZ, integrated. |
| Fig. 5 | Define six representative event signatures and distinguish missing PMU packets from continued reference time. | Frozen RAW0001 trace values and trace manifest. | Programmatically regenerated vector PDF/PNG, integrated. |
| Fig. 6 | Compare B0--B2, relate the preregistered residual to bus-level difficulty, and show paired B2--B1 differences. | E04A frozen summaries and per-case results. | Generated vector PDF/PNG, integrated. |
| Fig. 7 | Test lag, marginal calibration, and low-rank discrepancy placement. | E04A3--E04A5 artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 8 | Show the mismatch atlas and observed-only adequacy discrimination. | E06 per-case, calibration, and adequacy artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 9 | Compare frozen and regularized physical-recentering M6 errors, oracle-gap closure, and covariance failure. | E06-H summary, closure, uncertainty, and identifiability artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 10 | Connect load-response curvature, normal whitening, weak-event detection, source resolution, EVI prediction, and finite-amplitude calibration. | LOAD-TANGENT-V2 and LOAD-BAYES-FD-V2 frozen artifacts. | Six-panel generated vector PDF/PNG, integrated. |
| Main tables | Fix literature capabilities, event semantics/operators, experimental contracts, state-estimation results, uncertainty, mismatch, recentering, weak-load inference, and legacy event evidence. | Manuscript definitions and frozen artifacts. | Integrated. |

The generated eight-PMU topology/estimator panel remains a reserve asset (`figures/generated/system_architecture.pdf`); it is not numbered in the current manuscript because Fig. 1 states the inference flow more directly.

Still prospective: calibrated candidate sets versus profiled pairwise separation; PMU loss/join and placement sweeps; topology-outage maps; and the common-contract multi-family joint estimator. These assets enter the paper only after their manifests, selection rules, and test results are frozen.

Production rules:

- `scripts/generate_paper_artifacts.py` produces numerical plots and tables; no numerical result is transcribed by hand.
- Vector PDF is the manuscript source; PNG is a review companion.
- Color is redundant with marker, hatch, or brightness and remains interpretable in grayscale.
- Captions state the split, denominator, independent unit, and interpretation boundary.
