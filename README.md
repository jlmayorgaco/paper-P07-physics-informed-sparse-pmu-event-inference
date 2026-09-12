# P07 --- Physics-Informed Sparse PMU Estimation

**Working paper title:** *Physics-Informed Bayesian Event Inference and Localization from Sparse PMU Measurements*

**Target venue:** IEEE Access

This repository develops a defensible research manuscript on physical-event inference from sparse, dynamically changing phasor measurement unit (PMU) observations. The draft separates proposed methodology, historical motivation, and unvalidated experimental claims so that reproducible simulations can be added without rewriting the scientific contract.

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
| `generated/` | Small, intentional generated artifacts; never LaTeX build products |

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

The resulting local build is `main.pdf`; it is intentionally ignored and is not a repository artifact.

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

Do not add numerical results, reference simulations, or performance claims without a traceable experiment contract. [`docs/PAPER_GUIDELINES.md`](docs/PAPER_GUIDELINES.md) defines the hybrid physics/ML scope, required comparisons, literature standard, and submission gates; [`docs/claims-and-evidence.md`](docs/claims-and-evidence.md) records what can be said now and what must wait for a frozen campaign.
