# Evidence-driven paper outline

## Five-sentence research map

1. **Problem:** Sparse PMU deployments leave most bus voltages unmeasured, and a nominal estimator can become unreliable when its physical model is stale.
2. **Gap:** Dynamic estimation, functional observability, uncertainty calibration, and model-mismatch studies are rarely joined in one audited nonlinear benchmark with disjoint splits and physically rebuilt plants.
3. **Insight:** Hidden-voltage recovery should be treated as a target-specific functional-output problem, and failure under shift should be decomposed into information loss versus stale centering and linearization.
4. **Test:** Compare equilibrium, snapshot, causal, and smoothed local estimators; preregister the structural diagnostic; rebuild seven mismatch families; then contrast frozen, oracle, and causal recentering.
5. **Consequence:** The evidence identifies when sparse-PMU reconstruction is credible, when nominal uncertainty is misleading, and which physical adaptation must precede learned residuals or event inference.

## Section logic

| Section | Scientific role |
| --- | --- |
| I. Introduction | Exact problem, evidence-backed gap, four contributions, headline boundary. |
| II. Related Work | Dynamic estimation, functional observability, uncertainty/adaptation, benchmark validity. |
| III. Problem Formulation | Hybrid DAE, PMU operator, observed/hidden sets, target and metrics. |
| IV. Functional Observability | Finite-horizon condition, projector residual, preregistered theory-to-evidence link. |
| V. Estimation and Diagnostics | B0-B3, U2, discrepancy placements, adequacy statistic, R1/R2-A. |
| VI. Benchmark and Protocol | Validation ladder, splits, denominators, rebuilt plants, anti-leakage rules. |
| VII. Nominal Results | B0/B1/B2/B3 and structural-error relation. |
| VIII. Mismatch and Adaptation | Calibration, discrepancy negatives, mismatch families, adequacy, oracle/causal adaptation. |
| IX. Discussion | Mechanism, competing explanations, deployment boundary, next falsifiable step. |
| X. Conclusion | Only established evidence and its narrow implication. |

The Results sections should remain among the largest sections. Additional event-inference material belongs in a separate manuscript or a later revision only after its own frozen evidence is available.
