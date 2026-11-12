# Figures 1, 4 and 7: visual revision

## Figure 1

Replaced the two independently laid-out Python panels with one editable TikZ
composition (`figures/recovery_overview/main.tex`). Pulse edges, onset and
restoration markers, and the response now share exact coordinates. The
illustrative response includes both ON and OFF through a damped second-order
pulse response; the former curve did not include OFF in its calculation.
The A-only continuation and A-followed-by-B response diverge at the same onset.
This illustrative construction is not an additional experiment or a claim that
the implemented switched bank assumes linear superposition of events.

The method panel routes the observed report into two separate innovation
calculations. Downward arrows join at weight updating, not at a physical-state
merge. Predictors, innovations and active/cause weights have distinct positions.
Event guides stop around the legend so they cannot run through its labels.

## Figure 4

Rebuilt the TikZ composition around conventional bus/load and open-branch
symbols, a shared switch clock, and a measurement panel. The dynamic-state
marker is continuous at OFF; open/filled algebraic markers show its jump.
The measurement panel includes a phasor glyph, causal phase history and an
explicit coordinate table: voltage 8+8, current 8+7, frequency/ROCOF 8+8.
This replaces the unexplained barcode-like marks. Voltage sites and current
terminals remain distinct; BUS39 current angle remains excluded.

## Figure 7

Four aligned statistical panels now show absolute coverage and extras, then
paired differences for both coverage and extra-alarm rate. Method colors and
circle/square/triangle symbols remain consistent across panels. Numerical
annotations occupy fixed positions above their rows; a white backing prevents
grid/reference lines from crossing the text. Additional export padding keeps
the complete font bounds of the panel headings within the PDF page.

The new alarm-rate intervals already exist in the sealed C02 result. The
generator verifies its hash and checks that each paired point equals the
difference of the archived arm totals. No predictions, thresholds, raw
observations or bootstrap calculations were rerun. Negative differences in
extras/h favor the bank; positive coverage differences favor the bank.

## Inspection and verification

- Inspected each original image, the redesigned vector previews, and rendered
  article pages 2, 7 and 13. A second visual pass corrected upward-entering
  normalization arrows, event-guide/legend intersections and numeric labels
  intersected by plot reference lines.
- All three exported PDFs have one page, zero raster images and zero extracted
  words outside the page bounds. This is a bounds check, not an automated proof
  that every possible graphical overlap is absent.
- Main article: two successful pdfLaTeX passes, 19 pages, no unresolved
  references or duplicate labels. Existing template warnings remain.
- Protected event and IEEE-39 figures: all 16 hashes pass; present on pages 5
  and 6. The final editorial scanner reports zero blocked terms.

The old overview assets and generator remain available for recovery, but the
article and default build now use the combined TikZ overview. This revision
does not certify Overleaf compilation or scientific submission readiness.
