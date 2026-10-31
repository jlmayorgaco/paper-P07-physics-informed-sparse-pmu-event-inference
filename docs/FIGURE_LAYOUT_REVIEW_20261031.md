# Compact topology, protected figures, and phased method diagram

This revision implements the user's request directly on `main`.

## IEEE-39 in one column

The topology now uses a single-column `figure`, at `\columnwidth`. Its physical
coordinates are compacted independently of its fonts: nominal bus labels remain
7 pt rather than being reduced to roughly 5 pt. Transformer and generator
symbols, label positions, PMU badges and the legend were retuned for that scale.
The standalone drawing is about 8.9 by 8.7 cm, versus 15.6 by 16.8 cm before.
It retains 39 buses, 46 orthogonal branches, 12 transformers, 10 generators,
all connected loads, nine load candidates and nine line candidates, and the eight original PMUs.
The compact layout has no detected wire crossings, overlaps or label contacts.

Both the approved wide original and the compact successor are preserved as
independently compilable TikZ projects under `figures/frozen/`. Their compiled
output was compared with the corresponding frozen PDF and reproduced exactly
when rasterized. The source figure of events is unchanged byte for byte.

`AGENTS.md` and `docs/PROTECTED_FIGURES.md` prohibit deleting either protected
figure or removing it from the paper. A build guard verifies 16 immutable asset
hashes, source reachability, actual figure inclusion, and the compiled captions
and drawing content. Six regression tests cover intact inputs, corruption,
removed floats, commented figures, removed sections, and substituted assets.
The event figure remains Figure 2.

## Four phases of the implemented method

The new architecture contains 19 processing blocks in four phases:

1. **Physical model preparation:** oriented network measurement map, five fixed
   R/X hypotheses, reduced/discrete switched predictors and augmented memory.
2. **Startup context:** the 300-report prefix, model-specific operating context,
   frozen observation correction and retained state initialization.
3. **Causal update:** eight numbered steps from the incoming report to history
   prediction, onset screening, suffix replay, conditional evidence, state/model
   updates and continuity through OFF. A feedback path retains memory.
4. **Publication:** active/cause masses and delta mass, fixed alarm/OFF rules,
   and time-stamped outputs. Evaluation with reserved truth is downstream.

The earlier multi-lane figure provided visual precedent, but its unexecuted
joint-estimation and integrity stages were not reintroduced into the R11 method.
The new blocks follow `sections/article_method.tex`: predictive model density
is saved before proposals, state correction follows scoring, and suffix replay
replaces old likelihood contributions. Colors distinguish measurements,
physical state, histories, conditional evidence and decisions.

The architecture builder checks 19 block envelopes, orthogonal connectors,
connector/text intersections and connectors entering unrelated blocks. Its
source is `figures/narrative_architecture.tex`; a standalone LaTeX project and
vector PDF/PNG are also included.

## Targeted title and label review

The title changed from **Recovery-Aware Physical Event Attribution From Sparse
PMUs** to **Physics-Based Event Attribution From Sparse PMUs With Recovery
Memory**. The revision identifies the physical modeling basis and the retained
recovery state more explicitly. It does not add a neural-network, learned
discrepancy, calibrated-probability or real-time claim. The article, supplement,
PDF metadata, running header, README and paper plan use the same wording.

Block headings use short verbs and established method terms. Line breaks and
labels were inspected in the rendered diagram and in the actual journal page.
This was a targeted presentation review; scientific results were not re-estimated.

## Validation and delivery

- Main article: 15 pages; method architecture on page 2, events on page 4,
  compact IEEE-39 on page 5.
- Supplement: 29 pages; title synchronized with the main article.
- Visual review: title page, architecture, protected figure pages, and full
  main-article contact sheet.
- Geometric/PDF audits and protected-figure regression tests pass.
- Rebuild: `powershell -ExecutionPolicy Bypass -File scripts/build_ieee39_review.ps1`.
  The full manuscript bundle also invokes the protection guard and architecture build.
