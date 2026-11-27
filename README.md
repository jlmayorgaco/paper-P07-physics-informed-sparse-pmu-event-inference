# P07 manuscript

This repository contains the IEEE Access article, its supplement, the bibliography, and the assets needed to compile them. The default branch is `main`.

The [four-family replication counts](tables/generated/restoration_block_counts.csv) give the confusion matrix, exact family-and-asset count, before-clearance count and unmatched alarm count for each streaming method in each of the 15 scenario blocks.
The [window-level counts](tables/generated/restoration_window_counts.csv) report the shared-trigger family decisions and the 24- and 30-second comparisons with the archived forest.

In Overleaf, set the compiler to pdfLaTeX and the main document to `main.tex`. Select `supplement.tex` as the main document to compile the supplement. For a local build, run pdfLaTeX, BibTeX, and two more pdfLaTeX passes for each document.

The fixed figures and their verification files follow the [protected figure instructions](docs/PROTECTED_FIGURES.md). Earlier repository contents remain available in Git history.

Use `src/` for local research code. Git ignores this directory, so its contents stay off Overleaf. Build the manuscript from the tracked LaTeX sources.
