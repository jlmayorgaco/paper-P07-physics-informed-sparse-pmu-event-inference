# Revisión visual de la figura problema–método

**Fecha:** 11 de noviembre de 2026

**Estado:** incorporada en el borrador compilado; C03 todavía no aporta resultados.

## Cambios

La introducción abre con dos diagramas vectoriales, generados por `scripts/build_problem_method_diagrams.py` y compuestos como una figura de dos paneles:

- **(a) Problema.** Muestra los intervalos activos de A y B en una línea de tiempo; el trazo PMU ilustra que la recuperación de A continúa al comenzar B. Dos notas breves explican el riesgo de reiniciar o esperar a que la señal se asiente.
- **(b) Método.** Ordena el flujo en una sola dirección: ocho PMU, reporte, cinco modelos R/X, dos historias que compiten, puntuación DAE, actualización y publicación. Los conectores ya no cruzan tarjetas ni pasan sobre etiquetas.

El azul para las PMU y el naranja para las intervenciones siguen la paleta del unifilar IEEE-39 protegido. Verde identifica las decisiones publicadas; turquesa identifica la memoria dinámica conservada. Se acortaron rótulos que excedían sus tarjetas, se separó la leyenda de la señal y se redibujó la respuesta de B para que empiece sin un salto artificial. La nueva figura sustituye al resumen arquitectónico más denso de la introducción; el detalle ejecutable del método permanece en la sección de método y el suplemento.

## Verificación visual y de compilación

- Los dos paneles se revisaron a tamaño final en la página 2 del artículo; sus textos, flechas y leyendas caben dentro de cada panel.
- Tras la revisión, se acortaron los rótulos inferiores, se separaron los hitos de la línea de tiempo del título del gráfico y se alinearon las conexiones del método en rutas rectas sin cruces.
- El artículo tiene 17 páginas y el suplemento, 27.
- `scripts/verify_protected_figures.py --pdf main.pdf` pasa: las 16 huellas protegidas coinciden, la figura de eventos aparece en la página 5 y el unifilar IEEE-39 en la página 6.
- `scripts/verify_protected_event_figure.py` pasa.
- `scripts/scan_pdf_text.py main.pdf supplement.pdf` no encuentra términos internos bloqueados.
- El ZIP `output/source/P07_Article_Supplement_Source.zip` incluye el generador de diagramas y los PDF vectoriales usados por LaTeX; contiene 167 archivos de entrada compilables.
- `scripts/verify_source_package.py` recompiló el ZIP en una carpeta aislada: artículo 17 páginas y suplemento 27, con texto y paginación iguales a los PDF de trabajo.

La secuencia general `scripts/build_manuscript_bundle.ps1` todavía se detiene antes de compilar en `scripts/import_allevents.py`, porque falta el archivo histórico `experiments/PAPER_ALLEVENTS_V1/run/raw_ledger/iter000_legacy_hackathon/SCORE.json` en el repositorio científico. La compilación independiente de artículo y suplemento sí terminó. No se cambió ni se simuló el artefacto faltante.

## Límite de evidencia actual

C03 conserva un `execution.lock` y un proceso activo. Al revisar, no existían `run/TEST_RESULTS.json` ni `run/TEST_EVALUATION_LOCK.json`; por tanto, no se integraron resultados nuevos de F01 o P2. La conclusión científica sigue siendo la de la revisión C02 y no se presenta la segunda planta como validación confirmatoria.
