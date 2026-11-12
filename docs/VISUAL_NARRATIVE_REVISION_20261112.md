# Visual and narrative revision — 12 November 2026

## Editorial diagnosis

The opening repeated the distinction between restoration and recovery, then
repeated scope exclusions in the overview strip, related work and discussion.
The method opened with a list of approaches it does not use. The results figure
devoted space to calibration workflow while omitting the paired uncertainty
from its graphics. Computational cost interrupted the sequence of comparisons.

## Implemented changes

- **Figure 4:** editable TikZ source in `figures/physical_report/main.tex`.
  Conventional electrical symbols, a common switch clock, a continuous state
  trajectory, algebraic feedthrough jumps, and the PMU measurement map replace
  the earlier card layout. The curves are a damped second-order illustrative
  pulse response, not experimental data. Unlike the previous Python drawing,
  the algebraic lane has only one post-OFF curve. The measurement rows contain
  16, 15 and 16 coordinate marks; voltage-site identifiers are distinguished
  from the separately specified current terminals.
- **Figure 1:** retain the recovery example and history comparison; remove the
  redundant scope strip. Shorten the caption and replace “How the bank reasons”
  with “Physical histories.” Shorten the new-event box text to fit its border.
- **Figure 7:** replace cards and repeated method labels with aligned coverage
  and extra-alarm plots, plus a forest panel of paired differences. Every
  number comes from the existing hash-verified C02 result; no TEST rerun or
  new uncertainty calculation is performed. The panels retain the distinction
  between extras on event records and false alarms on normal records.
- **Structure:** add the primary common-budget cohort to the experimental
  population table. Move the computational-cost subsection after the component
  and noise studies, using a separate LaTeX input. Split the discussion's long
  limitation paragraph by transfer, measurement and inference approximation.

## Writing audit and revision examples

| Before | After / reason |
|---|---|
| “We address this gap with three contributions” followed by long numbered descriptions | Connected paragraphs introduce the predictor, its diagnostics and the comparison, with the unresolved mechanism control stated explicitly. |
| “Thus the evaluated method is model-based inference; it does not train a neural network…” | Describe what the conditional predictors and filters compute; remove the unrelated negative comparison. |
| “The graph therefore constrains the prediction without a learned graph embedding” | Explain how branch stamps and terminal operators enter the prediction. |
| “These delays test Prediction 1” | “We compare these delays retrospectively with Prediction 1.” |
| “reports later than the available information requires” | “reports after the nominal signature reference crossing.” |
| “hundreds to millions of nats per second” for deterministic signatures | “large separation energies”; retain the figure reference without equating deterministic energy with full expected log likelihood. |
| “Noise stress with unchanged code” | “Sensitivity to independent PMU noise”; the text still discloses the widened startup bound. |
| “startup contract” and “inherited warmup” | State the intervention-free prefix assumption and 12-s warmup directly. |

The second pass checked that removed scope prose remains supported by the
measurement model and discussion, that parent denominators remain explicit,
and that known negative results are preserved. Scientific terms such as
conditional likelihood and state–severity covariance remain where needed.
The equation-heavy method remains technical; this revision does not claim
that a typography change resolves open scientific questions.

## Verification and limits

The article compiles locally with pdfLaTeX in 19 pages. Figure previews and
the compiled pages were inspected; the protected event-signature image and
IEEE-39 diagram retain their hashes and remain visible. The editorial text
scanner reports no blocked internal terms. The default bundle builder now
regenerates the TikZ figure and C02 figure, as well as their numerical macros.
The distributed supplementary PDFs were stale relative to the existing source.
The supplement was recompiled without source edits (28 pages), and the local
article/supplement review bundle was refreshed (47 pages).

The source data, thresholds, predictions and C02 seal are unchanged. C03 was
not audited in this visual revision, and authenticated Overleaf compilation
remains unverified. This is an editorial revision, not a submission-readiness
certificate or a new literature/citation audit.
