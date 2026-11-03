# P07 pre-A01 review package

This directory contains a reviewed editorial candidate and derived, aggregated evidence for technical review. The article and supplement PDFs are explicitly **PRE-A01**. A01 is still running; the package contains no partial A01 outcomes and is not a final post-A01 manuscript or a submission package.

## Review PDFs

- `review_outputs/P07_Article_PRE_A01_Review.pdf`
- `review_outputs/P07_Supplement_PRE_A01_Review.pdf`
- `review_outputs/P07_Coauthor_Review_PRE_A01.pdf`

`PRE_A01_PACKAGE_MANIFEST.json` records their SHA-256 hashes, page counts, the staged source hashes and the visual QA render hashes. `FINAL_READINESS.md` records the pending A01 boundary.

## Contents and exclusions

The ZIP contains this closure package, the manuscript-source staging candidate, scripts, aggregated summaries, and the three review PDFs. It excludes `staging/inputs/`, raw or record-level experiment results, A01 partial outputs, local build caches, process logs, private author decisions, and the separate science repository. The editable scientific sources in the P07 repository remain untouched until the A01 completion gate passes.

## Reproduction and handoff

- `scripts/verify_a01_gate_and_apply_staging.ps1` is an explicit, guarded post-A01 command. Its default mode checks completion artifacts; `-Apply` applies the editorial allowlist only after its completion, parity, seal, denominator and import checks pass. It is not a watcher and never compiles or publishes.
- `staging/scripts/prepare_preview.py` verifies the prepared isolated preview sources without modifying them. The recorded manifest requires exactly one inclusion of the closure-results section.
- `staging/scripts/build_closure_evidence.py` reads the already-tracked frozen C01 package in this repository and writes aggregated restoration summaries. The timing/domain-profile generators use the frozen experiment files in the sibling `SGSMA26-Physics-Informed-AD` repository; those inputs are not bundled.
- No Python or TeX packages were installed for this review candidate.

The current A01 progress and all pre-A01 artifact hashes are in `STATUS.json` and `PRE_A01_PACKAGE_MANIFEST.json`. After A01 finishes, verify the seal and automatic import, compare the active manuscript with this staging, then compile and review the final PDFs before declaring P4/P7 complete.
