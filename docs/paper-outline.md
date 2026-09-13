# Evidence-driven paper outline

## Five-sentence research map

1. **Problem:** Sparse PMUs leave the voltage field incomplete and may not distinguish physical source assets, especially when measurement failures coexist with grid events.
2. **Gap:** Existing state estimators, partial-observation reconstruction methods, and sparse-PMU localizers solve overlapping subsets, but the exact source-disjoint joint state/physical-event/integrity contract remains insufficiently tested.
3. **Insight:** Treat each physical event as a counterfactual DAE intervention, keep measurement integrity separate, and project candidate signatures away from uncertain initial-state directions before ranking sources.
4. **Test:** Compare learned-only, physics-only, physics-plus-discrepancy, and diagnosability-aware inference on common source-disjoint parents under PMU loss/join and physical shift.
5. **Consequence:** A successful system could reconstruct the hidden network while declaring when the available PMUs support a source decision; the current evidence establishes the state component and the known-source baseline but not this end-to-end result.

## Section logic

| Section | Scientific role |
| --- | --- |
| I. Introduction | Exact joint problem, defensible gap, contributions, and evidence boundary. |
| II. Related Work | State estimation, sparse-PMU localization, partial-observation reconstruction, and capability matrix. |
| III. Problem Formulation | Hybrid DAE, AC/terminal-current model, sparse PMUs, eight event labels, separate physical/integrity sources. |
| IV. Observability and Diagnosability | Functional target recovery, nuisance projection, pairwise information, and indistinguishability limit. |
| V. Estimation | Proposed joint objective; validated B0--B3, calibration, adequacy, and static-MAP components. |
| VI. Protocol | Audited PowerDynamics state campaign and separate ANDES event campaign. |
| VII. State Results | Nominal reconstruction and theory-to-error evidence. |
| VIII. Mismatch and Event Results | Calibration/mismatch/adaptation plus known-source event baseline and source-transfer failure. |
| IX. Discussion | Mechanisms, competing explanations, limitations, and next frozen common-contract campaign. |
| X. Conclusion | Established component evidence and explicit end-to-end completion gate. |

## Title gate

The working title states the program's central problem. If the end-to-end joint campaign is not complete at submission, narrow the title to reflect a formulation plus component-evidence paper.
