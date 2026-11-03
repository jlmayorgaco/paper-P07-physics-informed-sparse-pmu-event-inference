# P07 — Recovery-Aware Physical Attribution of Load and Line Events From Sparse PMUs

Scientific audit revision (3 November): the article has eight sections and a narrower recovery-consistency claim. See the [audit response, implemented corrections and remaining scientific gaps](docs/SCIENTIFIC_AUDIT_RESPONSE_20261103.md). This is a coauthor-review draft, not a submission-ready manuscript.

C01 completed without retuning: 171 physical trajectories and all 342 observed records. See the [results and failure ledger](docs/c01-confirmatory-results.md). Scientific coauthor review remains open.

The article preserves the protected event-types image and IEEE-39 single-line diagram. Their hashes and validation procedure are documented in [PROTECTED_FIGURES.md](docs/PROTECTED_FIGURES.md). Project-specific editing constraints are in [AGENTS.md](AGENTS.md).

The active validation work is described in [P07 validation actions](docs/P07_VALIDATION_ACTIONS.md): B01 calibration is running; the independent, all-source C02 comparison is being implemented.

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
