# Figure and table map

Every empirical panel is generated from a frozen artifact. Conceptual drawings are TikZ/vector graphics; they contain no empirical values.

| Asset | Scientific function | Evidence/source | Status |
| --- | --- | --- | --- |
| Fig. 1 | Separate evaluated state/event components from the unvalidated joint candidate path. | Joint formulation in Sections III--V. | TikZ lane diagram, integrated. |
| Fig. 2 | Map state/input, event/source, and observability/sensor-value developments on separate lanes. | Verified literature through 2026. | TikZ three-lane timeline, integrated. |
| Fig. 3 | Expose numerical horizon sensitivity in the prescribed eight-PMU observability audit. | `pd_observability_horizons.csv`. | Generated vector PDF/PNG, integrated. |
| Fig. 4 | Show affine candidate separation and the nonlinear remainder that can erase it. | Propositions 2--3 and Corollary 2. | TikZ, integrated. |
| Fig. 5 | Define six representative event signatures without smoothing or hand-drawn values. | Frozen legacy RAW0001 trace artifact. | Imported vector PDF/PNG, integrated. |
| Fig. 6 | Compare B0--B2, relate the preregistered residual to bus-level difficulty, and show paired B2--B1 differences. | E04A frozen summaries and per-case results. | Generated vector PDF/PNG, integrated. |
| Fig. 7 | Test lag, marginal calibration, and low-rank discrepancy placement. | E04A3--E04A5 artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 8 | Show the mismatch atlas and observed-only adequacy discrimination. | E06 per-case, calibration, and adequacy artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 9 | Compare frozen and regularized physical-recentering M6 errors, oracle-gap closure, and covariance failure. | E06-H summary, closure, uncertainty, and identifiability artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 10 | Separate known-source event performance from held-source collapse and RAW transfer. | Frozen legacy event summaries. | Generated vector PDF/PNG, integrated. |
| Main tables | Fix literature capabilities, event semantics/operators, experimental contracts, state-estimation results, uncertainty, mismatch, recentering results, and legacy event evidence. | Manuscript definitions and frozen artifacts. | Integrated. |

The generated eight-PMU topology/estimator panel remains a reserve asset (`figures/generated/system_architecture.pdf`); it is not numbered in the current manuscript because Fig. 1 states the inference flow more directly.

Still prospective: calibrated uncertainty versus profiled separation; PMU loss/join and placement sweeps; topology-outage maps; and the common-contract end-to-end joint estimator. These assets enter the paper only after their manifests, selection rules, and test results are frozen.

Production rules:

- `scripts/generate_paper_artifacts.py` produces numerical plots and tables; no numerical result is transcribed by hand.
- Vector PDF is the manuscript source; PNG is a review companion.
- Color is redundant with marker, hatch, or brightness and remains interpretable in grayscale.
- Captions state the split, denominator, independent unit, and interpretation boundary.
