# P07 — argumento y mapa de lectura revisados

Actualización con [la revisión compartida](docs/SHARED_REVIEW_INTEGRATION_20261030.md): se separan el método causal congelado y el candidato DICE. El banco batch archivado requiere calificar su normalización y sus métricas Top-1/Top-3; sus valores no se modifican ni se transfieren a R11. La imagen de tipos de evento queda protegida mediante hashes durante el build.

Título de trabajo: *Recovery-Aware Physical Event Attribution From Sparse PMUs*. Autores, modelos y resultados conservados. La revisión de literatura solicitada el 29-oct-2026 concreta la diferencia frente a Warner; no es una nueva versión de inferencia.

La pregunta es: con ocho PMU, ¿qué intervención explica mejor la historia observada, y cuándo puede distinguirse de las alternativas?

El texto sigue problema → predicción física → evidencia causal → M/ΔM → decisión → límite de resolución → comparación y fallos. La reconstrucción de estado y el banco batch son evidencia de apoyo con contratos propios; E_B/GH31 no se reemplaza por R11, ni E_J se presenta como terminado.

## Tres contribuciones acotadas

1. Atribución con recuperación: comparar una nueva intervención de carga/línea con el estado que dejó una anterior; separar masa activa de causa retenida bajo hipótesis R/X constantes.
2. Análisis acotado de resolución: aplicar observabilidad/diagnosticabilidad conocidas a la diferencia entre recuperar voltaje e identificar fuentes. El batch conserva su propio contrato.
3. Prueba operacional reproducible: familia/fuente a tiempo, extras y restauración; nominal/mezcla, ablación negativa y C01 congelada. Ni esa ablación ni C01 prueban por sí solas la contribución causal de cada operación de memoria.

## Diferencia frente a precedentes

Warner ya usa trayectorias físicas, PMU dispersas y barrido retrospectivo. Rovatsos ya incorpora transitorios al QCD. Adaptive Matrix CuSum ya tiene teoría de diagnóstico secuencial. La diferencia de P07 se busca en la atribución de episodios sucesivos con restauración y recuperación conservadas; no se reclama prioridad mundial ni superioridad numérica sobre métodos que no ejecutamos.

La comparación detallada y sus límites están en [novelty-and-closest-methods.md](docs/novelty-and-closest-methods.md). La revisión de Barati y la decisión de no ampliar métodos antes de cerrar C01 están en [barati-physics-informed-options.md](docs/barati-physics-informed-options.md).

## Lectura de las figuras

| Figura | Pregunta que responde |
|---|---|
| Arquitectura | ¿Dónde entran física, datos, hipótesis y decisiones? |
| Tipos de evento (original conservado) | ¿Qué fenómenos muestra RAW0001 y cuáles sí evaluamos causalmente? |
| Red IEEE-39 | ¿Qué medimos y qué fuentes admite el banco? |
| Señales | ¿Cómo se manifiestan dos intervenciones en las ocho PMU? |
| Resolución batch | ¿Detectar multiplicidad permite identificar las fuentes? |
| Secuencia y M/ΔM | ¿Cómo evoluciona la decisión y dónde llega tarde? |
| Compromiso de decisión | ¿Qué se gana y qué se pierde al reducir extras? |

El artículo es autónomo; el suplemento se compila por separado. La auditoría de ecuaciones, datos, figuras y fuentes activas está en [MAIN_ARTICLE_AUDIT_20261030.md](docs/MAIN_ARTICLE_AUDIT_20261030.md). El predictor de inferencia es local, derivado de la DAE, con memoria instrumental y discrepancia estadística: no simula la DAE no lineal completa en cada reporte. El suplemento preserva pruebas, convenciones, estudios de estado y formulaciones propuestas. El texto anterior completo y su PDF están en `archive/narrative_before_20261030/`.

## C01 sigue intacta

No se miran resultados parciales para reescribir o ajustar el método. El ejecutor sigue congelado en SGSMA. Al completar la importación, `scripts/refresh_narrative_c01.py` y `scripts/c01_main_tables.py` integran en el artículo principal la comparación continua, Chen en aperturas persistentes, normales, exposición, fallos, demoras y censuras. Los detalles adicionales siguen en el suplemento. La campaña no debe sobrescribir esta revisión con la estructura anterior.

Falta terminar C01, interpretar resultados completos y revisar afirmaciones/reproducibilidad/coautores para envío. No se exige ahora otra familia ni otra corrección por bus. No se abre RAW0002 ni se hace push.
