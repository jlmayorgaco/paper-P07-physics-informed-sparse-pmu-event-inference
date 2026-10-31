# IEEE-39 single-line figure review — 2026-10-31

Updated by the subsequent user request: the active figure is now compact and
single-column. The approved wide original and the compact successor are both
frozen independently. See [the layout review](FIGURE_LAYOUT_REVIEW_20261031.md)
and [the mandatory retention contract](PROTECTED_FIGURES.md).

The current article uses an original, native TikZ electrical single-line diagram,
following the conventional arrangement in the three visual references supplied
for this task. All connections are orthogonal. There are no wire crossings,
shared branch segments, or opaque masks over bus labels.

- [Compiled article — Figure 3, page 5](../output/pdf/P07_Event_Attribution_Article.pdf)
- [Vector figure](../figures/generated/narrative_topology.pdf)
- [PNG preview](../figures/generated/narrative_topology.png)
- [Editable TikZ](../figures/ieee39_single_line.tex)
- [Standalone LaTeX document](../figures/ieee39/main.tex)
- [Geometry and PDF audit](../generated/single_line_topology_audit.json)
- [Clean compilation audit](../generated/ieee39_article_build_audit.json)

## Electrical meaning

The source inventory is frozen: 39 buses, 46 branches, 12 transformers,
10 generators and 19 connected loads. Blue busbars and P badges identify the
eight voltage PMU buses: **2, 5, 6, 10, 19, 22, 29, 39**. Orange branches and
load arrows retain the existing article's nine line and nine load intervention
candidates. Schematic lengths do not represent distance or impedance.

The voltage PMU markers do not imply that all current channels are measured at
the same buses. The copied terminal map preserves the provisional F01 BUS5
5–6 assignment and the existing BUS39 limitation. No simulation, operating
parameter, terminal assignment or detector result was changed.

The source records and SHA-256 provenance are in
[`figures/source/ieee39_single_line/`](../figures/source/ieee39_single_line/).
They are read-only inputs to the diagram builder. Nominal bus data are used only
for device presence; they do not replace the effective frozen operating point.

## Rebuild

The existing paper already uses TikZ. No external drawing library or image
generation service is needed. The standalone document requires pdfLaTeX,
PGF/TikZ, `standalone`, `fontenc` and `helvet`. The builder uses Python's standard
library plus PyMuPDF for rendered-PDF checks and the preview.

```powershell
python scripts/build_ieee39_tikz.py
powershell -ExecutionPolicy Bypass -File scripts/build_ieee39_review.ps1
```

For direct LaTeX editing, open `figures/ieee39/main.tex`, edit
`figures/ieee39_single_line.tex`, and compile from the `figures/ieee39/` directory.
To make layout changes persist through regeneration, edit the named coordinates
and routes in `scripts/build_ieee39_tikz.py`. The builder regenerates the TikZ
source, vector PDF, PNG and audit. The prior generator's `render(root)` entry point
delegates to this builder so a later narrative rebuild retains the new drawing.

## Verification

The build compares every branch against the frozen CSV, checks all 46 endpoints
and orthogonal routes, and rejects crossings, overlaps and accidental bus
contacts. It verifies generator/load inventory and the eight PMU locations from
independent input records. After compilation it verifies all 39 numeric labels
and eight badge positions against wire and device envelopes, using the actual
PDF glyph bounds with a 0.30 pt label margin in the compact version (0.75 pt in
the preserved wide original). The compact drawing uses 7 pt nominal bus labels.
The figure contains no raster images.

Visual review covered the standalone figure and its placement in the 15-page
IEEE Access article, including the full page and a complete article contact sheet.
Both documents were rebuilt from a clean export of the staged Git inputs. Every
page rendered identically at 72 dpi; no unpublished local dependency was required.
The article's existing class/font/line-breaking warnings are outside this figure
change; compilation finishes with resolved citations and references.

## Scope of the review commit

The local manuscript already contained an unpublished revision before this task.
Its active LaTeX inputs and generated result figures are included so the committed
article matches the supplied PDF. Those scientific statements are preserved,
not newly validated by this figure task. Unrelated working files, campaign data,
archives, and pending research changes are excluded. The legacy topology source
and old manuscript section remain unchanged.
