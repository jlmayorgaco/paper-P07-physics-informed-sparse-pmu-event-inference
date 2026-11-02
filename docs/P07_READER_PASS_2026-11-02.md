# P07: reader pass, 2 November 2026

The main article now takes the reader through four questions in order.

| Reader question | Where answered | Evidence boundary |
|---|---|---|
| What is the problem? | Introduction and revised Fig. 1 distinguish recovery, a later intervention, and network error. | Only load and line are executed in the causal study. |
| What does the algorithm do? | Fig. 1 gives the report loop; Algorithm 1 lists initialization, prediction, onset proposal/replay, evidence update and publication. The DAE and terminal-current equations remain in the method. | Local switched predictors, shared approximate covariances and pruning; no optimal-filter claim. |
| How does it compare? | Related-work contract table and Fig. 7 show the tested comparators and tradeoff. | Warner is discussed, not numerically compared; ExtraTrees is two frozen implementations; Chen has a separate persistent-line contract. |
| What are the results? | Fig. 7 shows per-family timely attribution and extras under R/X; Fig. 8 shows physical-parent intervals. | Physical bank: 322/324 loads and 322/324 lines; ExtraTrees reference: 15/324 and 315/324. Out-of-bank R/X: 68 versus 10 extras. These counts are paired realizations, not independent events. |

The main article is 11 pages. The repeated drafting footnotes were removed;
the explicit OpenAI Codex acknowledgment and bibliographic disclosure remain.
No methods, C01 records, thresholds, baselines, protected event image or
IEEE-39 single-line diagram were changed. The figures and results remain
traceable to frozen manifests. The source package was rebuilt from the
actual LaTeX inputs.

Three biographies now use monochrome portraits from attributable public
institutional pages: Masoud Barati, Payman Dehghanian and David Felipe
Celeita Rodríguez. Sources and edited variants are listed in
`figures/author_photos/PROVENANCE.md`. Jorge Luis Mayorga Taborda and
Yessica Africano Rodriguez remain without photos until author-supplied
portraits are available. The coauthors should approve all selected
likenesses and confirm image reuse rights before submission.

The paper is suitable for coauthor scientific review. Submission still
requires author approval of novelty wording, photo rights and the frozen
method comparison, including the larger alarm burden under R/X mismatch.

The subsequent method pass adds a direct table with all four C01 methods,
load and line hits, and extra alarms. It identifies the hackathon submission
as a 30-s, nine-label historical model with engineered features; the two
ExtraTrees models run in C01 are distinct 30-report/s causal successors.
`docs/HACKATHON_TO_C01_METHOD_TRACE.md` records the source files and the
non-comparability of the historical score. The interpretation now states
that generator and physical predictor share the F01 model family and PMU
map, a material limit on transfer. The article remains 11 pages, the
one-page coauthor brief was regenerated, and the source smoke test passed.
