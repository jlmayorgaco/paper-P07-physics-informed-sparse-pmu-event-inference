# Narrative revision on 2026-09-15

## Diagnosis

The previous draft contained strong evidence but asked the reader to infer the argument from many equations, tables, and campaign names. Numerical results were individually traceable, yet several appeared before the question, denominator, and decision consequence were clear. The revision therefore changes the information architecture rather than adding more results.

## Main-paper sequence

1. State the operational problem as two distinct inverse questions: recovery of a requested hidden-voltage function and separation of candidate physical sources.
2. Define the physical model, PMU set, source bank, integrity variables, correctness populations, and causal boundary.
3. Establish what the measurements can determine before introducing an estimator: functional reconstruction, profiled candidate separation, and sparse-support injectivity.
4. Present the two evaluated inference paths in executable order and mark the unexecuted joint posterior explicitly.
5. Freeze four research questions and their independent experimental units.
6. Answer RQ1 and RQ2 as a state-estimation story: measurement conditioning, the smaller temporal contribution, model failure under shift, and physical recentering.
7. Answer RQ3 and RQ4 as an event-inference story: cardinality, exact support, weak-case geometry, observation time, and source-holdout failure.
8. Interpret mechanisms and limits without introducing new results.

## What moved to the supplement

The paper-by-paper literature matrix, full AC and terminal-current conventions, detailed event operators, metric definitions, complete proofs, full estimator and likelihood equations, all campaign contracts, calibration ablations, weak single-source development results, and the historical known-source benchmark now appear in `supplement.tex`. The main paper retains only the evidence needed to change the reader's scientific conclusion.
