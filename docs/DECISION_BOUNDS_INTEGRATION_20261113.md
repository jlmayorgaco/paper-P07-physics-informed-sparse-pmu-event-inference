# Verification record: conditional refinement bounds

The second-wave attachment audit is in `IDEAS_SECOND_WAVE_AUDIT_20261113.md`.
It distinguishes mathematical identities, implementation checks, and future
inference experiments. The new results are not C03 results or a replacement
for the previously sealed open-loop trajectory comparison.

## Reproducibility

- `experiments/decision_bounds_20261113/RESULTS_SEAL.json` seals twelve files,
  including four unchanged native-operator inputs from the descriptor study.
- The complete prior descriptor result seal was checked again: no mismatches.
- Initial JSON serialization failure is preserved and explained; the v2
  numerical checks and thresholds are unchanged.
- The final source package has 805 inputs, SHA-256
  `746ea1e968481166bbc24dc239d5803eb7b6bd6e2f0bdefd8750a4d6386ae8a4`.
- Extracted-source compilation passed for article (19 pages) and supplement
  (39 pages), with matching PDF text and pagination. The new checker also
  passed in that isolated copy, including its input hashes.

## Editorial and visual verification

Appendix U adds conditional Gaussian score bounds, a proof outline, and
separate winner and event-mass conditions. It states that prediction-error
certificates are not available from the open-loop RMSE experiment, and that
quadrature approximation and omitted hypotheses need separate bounds.
No new numerical claim was manually inserted into LaTeX. The article and
existing figures are unchanged. Supplement pages 38 and 39 were rendered
and inspected: equations, columns, caption and references remain legible.
The editorial scan returned zero hits; references resolved. Existing class
and font warnings remain; this is not a warning-free-build claim.
All sixteen protected hashes passed, and both protected figures remain
visible in article pages 5 and 6.

## C03 and submission

At 17:00 Bogotá on 13 November, PID 32480 was active and the campaign log
reported `INFERENCE F01 TEST 60 72 C03_51820f4e5615`. Final results and
evaluation lock were absent. Only operational progress was inspected;
no TEST truth, predictions or outcome metrics were opened. C03 was not
modified or restarted. Submission status remains scientific-review draft.
Git publication supports the user's Overleaf synchronization workflow;
authenticated remote Overleaf compilation was not observed.
