# Historical Technical Notes: visual verification

Date: 2026-11-03. Scope: historical document only; active main paper and supplement were not edited during this pass.

## Inspection and changes

The initial 46-page build was inspected through all eight contact sheets (pages 1–46), with full-page inspection of pages 1, 5, 28, 29, 40 and 45. Two displayed equations extended beyond their column, and the float/output state caused stretched text on page 40 and a two-page bibliography with an almost empty final page.

- In `historical_notes.tex`, the frequency/ROCOF mean and covariance now use a two-line gathered display. This removes the 17.1151-pt body overflow without changing the equation.
- In the historical-only `supplement/appendix_narrative_support.tex`, the four local-amplitude identities now occupy two aligned lines. This removes the 27.03127-pt body overflow without changing any expression.
- `raggedbottom` is enabled immediately after the title. A page flush after the historical narrative-support float block restores the full text-column height for the archived source-resolution discussion. A page flush before the bibliography starts the references with a clean output state.
- All numerical values, tables and figures were preserved. The prior version of the narrative-support source was saved under `before/supplement/`.

## Rebuild and final verification

Only `historical_notes.tex` was rebuilt, using three `pdflatex -interaction=nonstopmode -halt-on-error` passes with BibTeX between the first and second. The command output is in `tmp/pdfs/revision_20261103/historical_visual_rebuild.log`.

The final `historical_notes.pdf` has **45 pages**. All 45 pages and the contact sheets were re-rendered to `tmp/pdfs/revision_20261103/historical_notes_*.png`. The old page 46 image was retained as `historical_notes_previous_46.png` so it is not mistaken for a current page.

The corrected equations were inspected at full-page size on pages 5 and 36. Page 40 was inspected again after the float flush: the column discontinuity is gone and the archived normalizer qualification remains visible. The bibliography is wholly contained on page 45. Updated contact sheets covering pages 37–45 were inspected after the final rebuild; no text/figure clipping was observed. Sparse historical float pages remain, including the short integrity table on page 44; these are retained archival tables, not missing content.

The final log has no unresolved references, multiply defined labels or cross-reference rerun request. The two title/template warnings at line 48 (9.2679 pt) and repeated class-output warnings remain; the identified body-equation overflows are absent. No change was made to the protected illustrations, scientific outputs, active supplement or main paper.

The parent integration step owns publication/package refresh. This pass did not publish, commit or push.
