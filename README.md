# P07 — Recovery-Aware Physical Attribution of Load and Line Events From Sparse PMUs

This repository contains the LaTeX sources for the main article, supplementary material, and historical technical notes. The entry points are [`main.tex`](main.tex), [`supplement.tex`](supplement.tex), and [`historical_notes.tex`](historical_notes.tex). Overleaf should compile `main.tex` with pdfLaTeX.

## Build

On Windows with MiKTeX (pdfLaTeX and BibTeX) and Python:

```powershell
.\scripts\build_manuscript_bundle.ps1
```

The script produces `main.pdf`, `supplement.pdf`, and `historical_notes.pdf` locally and verifies the [protected figures](docs/PROTECTED_FIGURES.md). Overleaf builds the PDF from the same sources. Compiled PDFs and simulation runs are excluded from GitHub sync to keep the project within Overleaf's file limit.

The tracked `experiments/` files are limited to the six TeX or PDF assets cited by the manuscripts. Historical simulations and publication bundles remain recoverable from Git commit `2df2c7f`. For example, `git restore --source=2df2c7f -- experiments/NAME` restores an earlier directory when needed. The removal does not revise the reported scientific results.

The protected event figure and IEEE-39 single-line diagram remain in the main article. Do not alter their frozen recovery copies or hashes; see [`docs/PROTECTED_FIGURES.md`](docs/PROTECTED_FIGURES.md).
