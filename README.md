# P07 — Physics-Based Event Attribution From Sparse PMUs With Recovery Memory

**Figuras protegidas:** la Figura 2 de eventos y el unifilar IEEE-39 deben permanecer
en el artículo. Sus copias de recuperación y controles están documentados en
[PROTECTED_FIGURES.md](docs/PROTECTED_FIGURES.md). La revisión actual usa un unifilar
de una columna y una arquitectura del método organizada en cuatro fases.
Trabajar directamente en `main`, según [AGENTS.md](AGENTS.md).

[Revisión S01 del 31-oct-2026](docs/submission_successor_20261031/STATUS.md):
matemática corregida, comparador físico de estado único, entrenamiento SIM
agrupado y parte de integridad de la hackathon ejecutados. En RAW, el híbrido
solo mejora una ventana de fuente física; no se afirma buen desempeño global.
La salida física y de integridad ya está unificada: conserva las decisiones
selladas y distingue disponibilidad actual de diagnósticos de intervalo.
El [artículo](output/pdf/P07_Event_Attribution_Article.pdf) y el
[suplemento](output/pdf/P07_Event_Attribution_Supplement.pdf) compilan por separado.
El [ZIP de fuentes](output/source/P07_Article_Supplement_Source.zip) también
se compila en una carpeta aislada mediante `scripts/verify_source_package.py`.
C01 y los metadatos editoriales finales siguen pendientes; el paquete es para revisión.

[Resultados E_i en IEEE-39 y reescritura](docs/ei-x02-results.md): nominal, recentrado y firmas condicionadas, con trazabilidad completa. El artículo separa el ensayo de firmas del método causal congelado. La imagen original de eventos y el diagrama aprobado se conservan.

[Corpus científico y continuidad](docs/corpus/README.md): objetivos de la conversación, ecuaciones implementadas, ideas adjudicadas, resultados con fuentes y revisión del nuevo chat compartido. Distingue lo que puede incorporarse al artículo actual de lo que necesita otra validación; no modifica C01.

[Integración del chat de revisión y giro DICE-PMU](docs/SHARED_REVIEW_INTEGRATION_20261030.md): algoritmo por reporte, precedentes, contratos de métricas, normalización del banco auxiliar y candidato separado. La imagen de tipos de eventos permanece intacta.

Revisión actual: [auditoría del artículo principal, 30-oct-2026](docs/MAIN_ARTICLE_AUDIT_20261030.md). El [PDF principal](output/pdf/P07_Event_Attribution_Article.pdf) contiene solo el artículo. C01 todavía está en ejecución; el borrador no anticipa sus resultados ni se declara listo para envío.

**Título de trabajo:** *Physics-Based Event Attribution From Sparse PMUs With Recovery Memory*

**Objetivo:** explicar qué intervención física produce una historia PMU y cuándo puede distinguirse de sus alternativas. El artículo sigue la predicción DAE, la evidencia causal, M/ΔM y la decisión; separa resultados de desarrollo y confirmación.

Ver [guía narrativa en español](NARRATIVA_P07.md), [plan del argumento](PAPER_PLAN.md) y [auditoría de la revisión](docs/narrative-revision-2026-10-30.md). El texto anterior y su PDF se conservan en `archive/narrative_before_20261030/`. C01 sigue ejecutándose sin reajustes; sus resultados se integrarán al completar la evaluación.

El [contraste con Warner y los métodos cercanos](docs/novelty-and-closest-methods.md) define el aporte defendible y sus límites. La [revisión de la línea physics-informed de Barati](docs/barati-physics-informed-options.md) distingue lo incorporado de extensiones futuras. Ninguna cambia el método congelado.

## Repository layout

| Path | Purpose |
| --- | --- |
| `main.tex` | IEEE Access article: recovery-aware attribution, physical prediction, source resolution and frozen operational evaluation |
| `supplement.tex`, `supplement/` | Current causal method, derivations, worked examples, integrity and evaluation contracts |
| `historical_notes.tex` | Preserved earlier theory, state/batch studies, historical qualifications and secondary results |
| `metadata.tex` | Title, author list, affiliations, and running headers |
| `preamble.tex` | Shared packages and mathematical notation |
| `sections/` | One LaTeX source file per manuscript section |
| `references.bib` | Article and supplement bibliographic records; source checks are documented in `docs/` |
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

## Build and document split

The project has **an article and its detailed companion**, plus separately
preserved historical technical notes. `main.tex` produces the compact IEEE
Access article; `supplement.tex` explains its current method step by step.
`historical_notes.tex` preserves the earlier research without making it a
required part of the article's argument. The script builds all three and
creates a combined article/supplement PDF for convenient review:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_manuscript_bundle.ps1
```

| Source / delivery file | Contents |
| --- | --- |
| `main.tex` / [Article](output/pdf/P07_Event_Attribution_Article.pdf) | Problem, physical mechanism, essential equations, causal algorithm, decisive results and limitations |
| `supplement.tex` / [Supplement](output/pdf/P07_Event_Attribution_Supplement.pdf) | Current method step by step; local derivations; examples; scenarios; integrity, metrics and reproduction |
| `historical_notes.tex` / [Historical notes](output/pdf/P07_Historical_Technical_Notes.pdf) | Earlier corrected theory and state/batch studies, kept with their original evidence limits |
| [Combined review](output/pdf/P07_Event_Attribution_Review_Bundle.pdf) | Article followed by the complete supplement, with bookmarks for both documents |

The build uses **pdfLaTeX + BibTeX directly**. It does not need `latexmk` or Perl.
The installed `latexmk` currently fails because Perl is unavailable. The
integrated viewer also reported a MiKTeX log-permission failure; its Tectonic
fallback fails on the IEEE Access class's pdfTeX-specific spot-color commands.
For Overleaf select **pdfLaTeX**, and choose `main.tex` or `supplement.tex` as
Main document. The source files and official class are preserved.

By default the build compiles the versioned evidence already present. It does
not run simulations, re-import results, or regenerate scientific assets.
To explicitly regenerate the existing editorial/theory artifacts, use
`-RefreshArtifacts`; inspect those changes before publishing. Source-results
import remains the separate operation described above.

The manual compilation sequence is:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
bibtex supplement
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
python scripts/verify_supplement_examples.py
python scripts/verify_protected_figures.py --pdf main.pdf
python scripts/publish_manuscript_bundle.py
```

The two long historical PDF filenames remain updated aliases for the separate
article and supplement. The explicitly named `Review_Bundle` is the combined
copy. Recovery details and the content map are recorded in
[the document recovery note](docs/DOCUMENT_RECOVERY_20261031.md).

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

The expanded mathematical supplement is indexed in [`docs/supplement-theory-map-2026-09-15.md`](docs/supplement-theory-map-2026-09-15.md). That map links each proof and estimator block to its interpretation and evidence boundary.

The robust-discrepancy revision is audited in [`docs/robust-discrepancy-routing-2026-09-15.md`](docs/robust-discrepancy-routing-2026-09-15.md). It records the full-likelihood correction to the utility-only design and the incomplete status of the targeted nonlinear-margin campaign.

The phase-1 adversarial review is resolved issue by issue in [`docs/adversarial-audit-response.md`](docs/adversarial-audit-response.md); unresolved experimental items remain submission vetoes rather than prose claims.
