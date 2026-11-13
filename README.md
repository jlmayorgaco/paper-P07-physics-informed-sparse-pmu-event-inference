# P07 — Recovery-Aware Physical Attribution of Load and Line Events From Sparse PMUs

**Current status, 13 November 2026:** scientific review draft; C03 has frozen
its CAL selection and is running F01 TEST. Both-plant results are not yet sealed.
The [technical/editorial review](docs/P07_REVIEW_20261113.md) corrects reset-gain
wording and N01 noise units, and records the remaining gates.
The [autonomous closure plan](docs/P07_AUTONOMOUS_CLOSURE_PLAN.md)
sets the remaining evidence and submission gates. The new supplementary analysis
distinguishes predictive state sufficiency, distributional compression and
historical attribution. Its finite examples can be checked with
`python scripts/verify_recovery_distribution.py`. Earlier dated notes below are
historical; the [current closure record](docs/P07_CLOSURE_CURRENT.md) takes precedence.

The [corrected covariance/noise diagnostics](experiments/adaptive_innovation_20261113_corrected/README.md)
replace the earlier auxiliary study, which used the wrong OFF operator. The
old run remains archived and marked withdrawn. Corrected covariance ranking
is 279/360 versus 343/360; noise learning yields 20/72 in all arms and two arms
exceed the TEST alarm target. No adaptive attribution gain is established.

The [rotor-energy and graph-port study](experiments/hamiltonian_f01_20261113/README.md)
adds four new nonlinear F01 consistency trajectories, an exact mechanical
subsystem derivation and an equivalence comparison using 18 nominal sources.
Energy coordinates do not add information; the absolute numerical likelihood
gate remains failed and no detector improvement is claimed. The architecture
now shows graph structure, rotor storage and Bayesian evidence. Article: 19
pages; supplement: 35 pages. C03 remains unchanged.

Overleaf sync excludes `output/source/*.zip`: the source delivery archive
exceeded its 50 MB per-file limit. It is still generated and retained locally.
Check tracked sizes before push with `python scripts/check_overleaf_file_sizes.py`.

The [terminal-current diagnostic](docs/CHANNEL_INFORMATION_20261112.md) now
compares voltage and current information with the actual nominal predictor,
retaining temporal and cross-channel covariance. It is a fixed-mean diagnostic,
not a detector accuracy claim. The article includes its scoped result and the
supplement contains its derivation and figure. A separate
[successor of the external prototype](docs/TERMINAL_SUCCESSOR_20261112.md)
corrects terminal orientation without changing the frozen measurement map.
The [unifying research question](docs/P07_UNIFIED_RESEARCH_QUESTION_20261112.md)
states which interaction between recovery uncertainty and current information
still needs an independent experiment.

The [HBG idea audit and integration](docs/HBG_INTEGRATION_DECISIONS_20261112.md)
adds bounded rival-severity profiling to that diagnostic. Currents retain a
median 1.53-fold nominal separation gain after the rival load magnitude is
fitted, while some source ambiguities become much stronger. The supplement
connects this geometry to recovery uncertainty without adding a second copy
of the state covariance or claiming a new Hamiltonian detector. The current
article and supplement at that revision had 19 and 31 pages.

**Revision 4 November 2026.** Repositioned as switched-DAE change detection and isolation, with a new physics-derived detectability section (Willsky--Jones signature information, minimum detectable change, cost of forgetting the state), a noise-stress test with unchanged code (N01) and a measured real-time rate for the nominal bank. See the [verified audit and plan](docs/review_chatgpt_20261104/PLAN_SUBMIT_READY.md) and the [response matrix](docs/review_chatgpt_20261104/RESPONSE_MATRIX.md). Pre-revision sources are kept in `archive/pre_revision_20261104/`.


Scientific audit revision (3 November): the article has eight sections and a narrower recovery-consistency claim. See the [audit response, implemented corrections and remaining scientific gaps](docs/SCIENTIFIC_AUDIT_RESPONSE_20261103.md). This is a coauthor-review draft, not a submission-ready manuscript.

The [latest executed review](docs/revision_execution_20261103/RESPONSE_AND_STATUS.md) adds explicit affine/state–amplitude equations, portable numerical checks, verified comparator lineage and a focused supplement containing complete C01/A01 outcomes. The second supplied Gemini attachment duplicates the first; the revision addresses that review and the independent repository audit.

C01 completed without retuning: 171 physical trajectories and all 342 observed records. See the [results and failure ledger](docs/c01-confirmatory-results.md). Scientific coauthor review remains open.

The article preserves the protected event-types image and IEEE-39 single-line diagram. Their hashes and validation procedure are documented in [PROTECTED_FIGURES.md](docs/PROTECTED_FIGURES.md). Project-specific editing constraints are in [AGENTS.md](AGENTS.md).

The [current closure record](docs/P07_CLOSURE_CURRENT.md) supersedes older dated readiness notes. The article includes C02 from its sealed result; the successor mechanism and plant-transfer campaign is separate.

The central half-page method figure and physical/report figure are editable
TikZ diagrams, built by `scripts/build_paper_method_figure.py` and
`scripts/build_physics_measurement_chain.py`. The earlier recovery overview
is preserved with its original builder, `scripts/build_recovery_overview.py`.
The method includes numbered per-report pseudocode. C03 is running TEST;
no C03 test results have been added. See the closure record for the dated status.

## Manuscript and results

- [Main article PDF](output/pdf/P07_Event_Attribution_Article.pdf)
- [Supplement PDF](output/pdf/P07_Event_Attribution_Supplement.pdf)
- [Historical technical notes PDF](output/pdf/P07_Historical_Technical_Notes.pdf)
- [Coauthor brief](docs/P07_COAUTHOR_BRIEF.md)
- [Coauthor closure and decision points](docs/P07_CLOSURE_FOR_COAUTHORS.md)
- [Evidence and claims boundary](CLAIMS.md)
- [C01 confirmatory results](docs/c01-confirmatory-results.md)
- [E_i results](docs/ei-x02-results.md)
- [Recovery results](docs/recovery-x04-results.md)

## Repository layout

| Path | Purpose |
| --- | --- |
| `main.tex` | IEEE Access article |
| `supplement.tex`, `supplement/` | Method, derivations, examples and evaluation contracts |
| `historical_notes.tex` | Earlier theory and state/batch studies with their original evidence limits |
| `sections/` | Article source sections |
| `references.bib` | Scientific bibliography |
| `figures/`, `tables/` | Protected and generated manuscript assets |
| `generated/frozen/` | Frozen result artifacts used by the paper |
| `docs/editorial_closure/` | Current editorial status and handoff index |
| `scripts/` | Reproducible checks, artifact generation and build scripts |

## Build

The default build uses the checked-in evidence and does not run simulations or re-import results. Run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_manuscript_bundle.ps1
```

The build compiles the article, supplement and historical notes, verifies the protected figures, and creates the combined review bundle. `-RefreshArtifacts` explicitly regenerates deterministic editorial/theory artifacts and should be reviewed separately.

The default build also verifies the local mathematical identities (NumPy/SciPy required) and regenerates comparator lineage from bundled source/metadata snapshots. These checks do not require the research checkout or rerun empirical campaigns. `python scripts/verify_source_package.py` checks an isolated rebuild of the article and supplement source ZIP.
