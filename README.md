# P07 --- Functional Voltage Reconstruction From Sparse PMUs

**Working paper title:** *Functional Observability and Physics-Based Reconstruction of Unobserved Power-System Voltages From Sparse PMUs Under Model Mismatch*

**Target venue:** IEEE Access

This repository develops an evidence-backed IEEE Access manuscript on reconstructing 31 unobserved IEEE 39-bus voltages from eight voltage/current PMUs. The paper connects functional observability, local physics-based estimation, nominal uncertainty diagnostics, physically rebuilt mismatch plants, model-adequacy detection, and a deliberately retained negative causal-adaptation result. Event detection and source localization remain later research stages rather than claims of this manuscript.

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

`SOURCE_MANIFEST.csv` records a SHA-256 hash and source-relative path for every imported artifact. `SOURCE_SNAPSHOT.txt` records the source branch and commit. The generator asserts the principal denominators before writing LaTeX macros, tables, and vector figures.

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

Do not add numerical results or performance claims without a traceable experiment contract. [`CLAIMS.md`](CLAIMS.md) is the concise submission boundary; [`docs/claims-and-evidence.md`](docs/claims-and-evidence.md) maps each main claim to its artifact. [`TODO_PENDING.md`](TODO_PENDING.md) separates the next research gates from completed manuscript work. The earlier event-inference and competition-derived system remains useful prior development, but its numerical claims must not be merged into this reconstruction paper without a compatible, frozen protocol.
