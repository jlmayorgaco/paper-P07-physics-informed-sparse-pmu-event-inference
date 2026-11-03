# Pre-A01 readiness checkpoint

## Completed preparation

- The article, supplement, and coauthor brief were prepared as isolated pre-A01 review PDFs and retained under `review_outputs/`. Their page counts and SHA-256 hashes are in `PRE_A01_REVIEW_OUTPUTS.json`.
- The pre-A01 review covered the staged method, C01 closure table, restoration audit, and source package. The staged source hashes were checked for consistency before packaging.
- Protected figures were verified in the review copy: all 16 frozen hashes passed; the event-types figure and IEEE-39 single-line diagram remained visible.
- C01 remains complete at 171 trajectories and 342 observed records. Its frozen data and failure/denominator ledger are preserved in the active repository.

## A01 gate pending

A01 remains active at inference task 61/72, record S321, PROFILE_MEMORY. No completion marker or final post-A01 import is present; no partial outcomes have been used to change manuscript claims or thresholds. The staged candidate is not the final post-A01 manuscript.

The next action is to wait for A01 completion, run `scripts/verify_a01_gate_and_apply_staging.ps1` without `-Apply`, verify its completion, seal, parity and import checks, and inspect the exact editorial allowlist. Only then apply the staged changes and rebuild/inspect the final article and supplement.

No author message or journal submission has been made. Author declarations and permissions remain open.
