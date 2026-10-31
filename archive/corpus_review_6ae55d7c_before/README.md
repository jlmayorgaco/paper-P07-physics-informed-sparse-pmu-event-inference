# P07 — Recovery-Aware Physical Event Attribution From Sparse PMUs

[Integración del chat de revisión y giro DICE-PMU](docs/SHARED_REVIEW_INTEGRATION_20261030.md): algoritmo por reporte, precedentes, contratos de métricas, normalización del banco auxiliar y candidato separado. La imagen de tipos de eventos permanece intacta.

Revisión actual: [auditoría del artículo principal, 30-oct-2026](docs/MAIN_ARTICLE_AUDIT_20261030.md). El [PDF principal](output/pdf/P07_Event_Attribution_Article.pdf) contiene solo el artículo. C01 todavía está en ejecución; el borrador no anticipa sus resultados ni se declara listo para envío.

**Título de trabajo:** *Recovery-Aware Physical Event Attribution From Sparse PMUs*

**Objetivo:** explicar qué intervención física produce una historia PMU y cuándo puede distinguirse de sus alternativas. El artículo sigue la predicción DAE, la evidencia causal, M/ΔM y la decisión; separa resultados de desarrollo y confirmación.

Ver [guía narrativa en español](NARRATIVA_P07.md), [plan del argumento](PAPER_PLAN.md) y [auditoría de la revisión](docs/narrative-revision-2026-10-30.md). El texto anterior y su PDF se conservan en `archive/narrative_before_20261030/`. C01 sigue ejecutándose sin reajustes; sus resultados se integrarán al completar la evaluación.

El [contraste con Warner y los métodos cercanos](docs/novelty-and-closest-methods.md) define el aporte defendible y sus límites. La [revisión de la línea physics-informed de Barati](docs/barati-physics-informed-options.md) distingue lo incorporado de extensiones futuras. Ninguna cambia el método congelado.

## Repository layout

| Path | Purpose |
| --- | --- |
| `main.tex` | IEEE Access article: recovery-aware attribution, physical prediction, source resolution and frozen operational evaluation |
| `supplement.tex`, `supplement/` | Detailed proofs, Fisher-information analysis, stepwise Bayesian estimators, frozen contracts, and secondary results |
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

The root manuscript uses the official `ieeeaccess.cls` supplied with the repository. The normal build compiles the standalone supplement first and then compiles `main.tex`, which appends every supplementary page after the principal article. Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_manuscript_bundle.ps1
```

The current MiKTeX installation has no Perl engine. The equivalent manual sequence is:

```powershell
python scripts/verify_theory_identities.py
python scripts/verify_cone_bayes_identities.py
python scripts/verify_information_limits.py
python scripts/verify_discrepancy_design.py
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
bibtex supplement
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
Copy-Item supplement.pdf output/pdf/P07_Physics_Informed_State_Reconstruction_Event_Source_Inference_Supplement.pdf -Force
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The resulting `main.pdf` contains the principal article followed by the complete supplement, while `supplement.pdf` remains available as a standalone companion. Both review copies under `output/pdf/` are tracked for direct delivery. The principal article retains the scientific argument and decisive evidence; the supplement contains the paper-by-paper literature matrix, electrical conventions, complete proofs, nuisance-profiled Fisher information, sparse and temporal identifiability results, the executed 137-hypothesis Bayesian algorithm, the candidate-conditioned joint-estimator design, frozen contracts, and secondary diagnostics. Run the artifact generator before compiling whenever the frozen snapshot changes.

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
