# P07 State Reconstruction and Event-Source Diagnosability From Sparse PMUs

**Working paper title:** *Physics-Based State Reconstruction and Event-Source Diagnosability With Sparse PMU Measurements*

**Target venue:** IEEE Access

This repository develops an evidence-backed IEEE Access manuscript on hidden-state recoverability and event-source diagnosability from eight PMUs. It consolidates three frozen contracts: (i) PowerDynamics reconstruction of 31 hidden IEEE 39-bus voltages, including model mismatch and regularized physical recentering; (ii) physics-based Bayesian inference over 16 load-source candidates with weak-event and finite-amplitude tests; and (iii) an ANDES event-diagnosis baseline spanning eight abnormal labels plus normal operation. The draft derives functional-observability and source-diagnosability limits, regenerates the measured event-signature figure from frozen trace values, and preserves negative results. The full multi-family joint posterior remains unexecuted and is not presented as a completed result.

## Repository layout

| Path | Purpose |
| --- | --- |
| `main.tex` | IEEE Access root manuscript |
| `metadata.tex` | Title, author list, affiliations, and running headers |
| `preamble.tex` | Shared packages and mathematical notation |
| `sections/` | One LaTeX source file per manuscript section |
| `references.bib` | Verified, cited bibliography entries only |
| `figures/` | Source figures and the figure roadmap |
| `tables/` | Evidence-backed modular manuscript tables |
| `docs/` | Scope, claims, experiment, and editorial records, including the binding paper contract |
| `scripts/` | Reproducible experiment and artifact-generation scripts |
| `generated/frozen/` | Hashed snapshot of the result artifacts used by the paper |
| `generated/results_macros.tex` | Generated numerical prose values; do not edit manually |
| `figures/generated/`, `tables/generated/` | Regenerated empirical assets |

## Reproduce paper artifacts

The source-results import is an explicit operation because it snapshots another local research repository. Its default location can be overridden with `-SourceRepository`.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/import_frozen_results.ps1
python scripts/generate_paper_artifacts.py
```

`SOURCE_MANIFEST.csv` records a SHA-256 hash and source-relative path for every imported state or event artifact. `SOURCE_SNAPSHOT.txt` records the source branch and commit. The generator asserts the principal denominators before writing LaTeX macros, tables, and vector figures.

## Build

The root manuscript uses the official `ieeeaccess.cls` supplied with the repository. The current MiKTeX installation has no Perl engine, so use the fallback sequence:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

When `latexmk` and Perl are available, the equivalent command is:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The resulting local build is `main.pdf`; it is intentionally ignored. Run the artifact generator before compiling whenever the frozen snapshot changes.

## GitHub and Overleaf workflow

1. Pull before beginning local work.
2. Edit and build locally.
3. Commit and push a coherent change.
4. Pull GitHub changes into Overleaf before faculty review.
5. Faculty review and edit in Overleaf.
6. Push Overleaf changes back to GitHub.
7. Pull locally before continuing.

Avoid editing the same LaTeX lines locally and in Overleaf at the same time. Resolve one coherent version first, then synchronize it before the next review pass.

## Evidence policy

Do not add numerical results or performance claims without a traceable experiment contract. [`CLAIMS.md`](CLAIMS.md) is the concise submission boundary; [`docs/claims-and-evidence.md`](docs/claims-and-evidence.md) maps each main claim to its artifact. [`TODO_PENDING.md`](TODO_PENDING.md) separates the next research gates from completed manuscript work. The earlier event-inference system remains useful prior development, but its numerical claims must not be merged into this reconstruction paper without a compatible, frozen protocol.

The full-project scientific compendium is routed through [`docs/compendium-estimator-integration-map.md`](docs/compendium-estimator-integration-map.md). That map separates validated estimator results, the audited historical diagnosis baseline, and the still-proposed common-contract joint experiment.

The September 13 master dossier is routed through [`docs/master-dossier-integration-map.md`](docs/master-dossier-integration-map.md), which records what fits in the 20-page paper, what remains compact, and what is deferred until an experiment is complete.

The phase-1 adversarial review is resolved issue by issue in [`docs/adversarial-audit-response.md`](docs/adversarial-audit-response.md); unresolved experimental items remain submission vetoes rather than prose claims.
