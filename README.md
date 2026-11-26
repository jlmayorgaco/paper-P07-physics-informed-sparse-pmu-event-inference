# P07 manuscript

This repository contains the IEEE Access article, its supplement, the bibliography, and the assets needed to compile them. The default branch is `main`.

In Overleaf, set the compiler to pdfLaTeX and the main document to `main.tex`. Select `supplement.tex` as the main document to compile the supplement. For a local build, run pdfLaTeX, BibTeX, and two more pdfLaTeX passes for each document.

The fixed figures and their verification files follow the [protected figure instructions](docs/PROTECTED_FIGURES.md). Earlier repository contents remain available in Git history.

Use `src/` for local research code. Git ignores this directory, so its contents stay off Overleaf. Build the manuscript from the tracked LaTeX sources.
