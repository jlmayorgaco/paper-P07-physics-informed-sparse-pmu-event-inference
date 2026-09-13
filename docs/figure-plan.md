# Figure and table map

Every empirical panel is generated from a frozen artifact. Conceptual drawings are TikZ/vector graphics; they contain no empirical values.

| Asset | Scientific function | Evidence/source | Status |
| --- | --- | --- | --- |
| Fig. 1 | Expose the joint inference contract: sparse measurements, physical hypotheses, integrity variables, hidden state, source posterior, and abstention. | Joint formulation in Sections III--V. | TikZ, integrated. |
| Fig. 2 | Make the projected-signature information limit geometrically interpretable. | Proposition 1 and Corollary 1. | TikZ, integrated. |
| Fig. 3 | Define six representative event signatures without smoothing or hand-drawn values. | Frozen legacy RAW0001 trace artifact. | Imported vector PDF/PNG, integrated. |
| Fig. 4 | Compare B0--B2, relate the preregistered residual to bus-level difficulty, and show paired B2--B1 differences. | E04A frozen summaries and per-case results. | Generated vector PDF/PNG, integrated. |
| Fig. 5 | Test lag, marginal calibration, and low-rank discrepancy placement. | E04A3--E04A5 artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 6 | Show the mismatch atlas and observed-only adequacy discrimination. | E06 per-case, calibration, and adequacy artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 7 | Compare frozen and physical static-MAP M6 errors, oracle-gap closure, and covariance failure. | E06-H summary, closure, uncertainty, and identifiability artifacts. | Generated vector PDF/PNG, integrated. |
| Fig. 8 | Separate known-source event performance from held-source collapse and RAW transfer. | Frozen legacy event summaries. | Generated vector PDF/PNG, integrated. |
| Tables I--VIII | Fix literature capabilities, event semantics, experimental contracts, state-estimation results, uncertainty, mismatch, static-MAP results, and legacy event evidence. | Manuscript definitions and frozen artifacts. | Integrated. |

The generated eight-PMU topology/estimator panel remains a reserve asset (`figures/generated/system_architecture.pdf`); it is not numbered in the current manuscript because Fig. 1 states the inference flow more directly.

Still prospective: posterior ambiguity versus projected information; PMU loss/join and placement sweeps; topology-outage maps; and the common-contract end-to-end joint estimator. These assets enter the paper only after their manifests, selection rules, and test results are frozen.

Production rules:

- `scripts/generate_paper_artifacts.py` produces numerical plots and tables; no numerical result is transcribed by hand.
- Vector PDF is the manuscript source; PNG is a review companion.
- Color is redundant with marker, hatch, or brightness and remains interpretable in grayscale.
- Captions state the split, denominator, independent unit, and interpretation boundary.
