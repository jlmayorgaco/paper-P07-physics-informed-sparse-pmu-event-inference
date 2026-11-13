# Descriptor bridge: integration and verification

13 November 2026. Scope: supplied Kirchhoff-to-estimator derivation, actual
frozen F01 operator extraction, and finite-event open-loop validation.
Scientific details, failure ledger and reproduction are in
[the experiment README](../experiments/descriptor_bridge_20261113/README.md).

## Integration

- Main method adds one construction-validation sentence; no abstract,
  detection result, protected diagram or novelty claim is changed.
- Appendix T derives mass normalization and observation maps, reports all
  five physical events plus the normal control, and explains local accuracy
  versus finite-rotation error. Table 28 and Figure 17 come from sealed data.
- The current architecture already connects network operators and conditional
  Bayesian inference. No untested Hamiltonian prior or online parameter
  adaptation is inserted into that algorithm.
- C03 is neither read nor changed by this work. Earlier C03 status dates remain
  explicit; this diagnostic is not a campaign-progress check.

## Verification completed

- Six successful nonlinear solves, derivative gates, independent Schur
  reconstruction and terminal-current checks; all outputs retained.
- The initial new extractor's failed B/D check is preserved with its cause
  and separately frozen corrected successor. No threshold was relaxed.
- Saved analysis covers 47 physical report coordinates separately by units,
  observation map and event/recovery window; no unscaled aggregate score.
- Main article: 19 pages. Supplement: 37 pages. No unresolved citations,
  cross-references or multiply-defined labels in either build.
- Reader-vocabulary scan: zero hits after replacing internal archive wording.
- Protected figures: 16 hashes pass; event figure and IEEE39 topology remain
  visible on main pages 5 and 6. Event-original verifier passes.
- Compared with the previous committed article, only page 6 changes in text
  or rendered pixels. Inspected that final page and supplement pages 35-37;
  the new plot's long axis label was shortened to remove overlap before final
  export. Final plot and table remain readable at paper size.
- Source ZIP contains 702 inputs. It compiles independently to matching text
  and pagination for both documents. Its standalone descriptor figure/table
  builder also passes all 114 sealed hashes in the extracted directory.
- Source ZIP stays local/ignored; the Git size gate checks the actual tracked
  files before publication. Compiling in the authenticated Overleaf service
  was not observed; the user requests Git-based synchronization.

The article remains a scientific review draft. This study verifies derivation
and records approximation limits; C03's controlled mechanism/transfer evidence,
remaining methodological closure gates and author approvals still determine
submission readiness.
