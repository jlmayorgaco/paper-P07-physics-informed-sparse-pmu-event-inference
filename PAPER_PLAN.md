# P07 — argumento y mapa de lectura revisados

**Cierre para coautores, 31-oct:** [contrato y auditoría del método](docs/P07_CLOSURE_FOR_COAUTHORS.md) y [página de contribución/evidencia](docs/P07_COAUTHOR_BRIEF.md). No se crean más versiones ni se agregan métodos. La DAE, el mapa de medición y la integral condicional se explican con su correspondencia al código; las aproximaciones quedan explícitas. C01 se deja terminar y sus resultados completos determinarán las conclusiones, sin reajustes.

El [corpus de continuidad](docs/corpus/README.md) reconcilia conversación, ideas y fuentes. El [ensayo IEEE-39 X02](docs/ei-x02-results.md) ya prueba E_i en un contrato restringido: mejora respuesta e intensidad, sin más aciertos de origen que recentrar. No se añade silenciosamente a R11/C01. El atlas predictivo, la incertidumbre conjunta y el refinamiento selectivo siguen pendientes.

Actualización con [la revisión compartida](docs/SHARED_REVIEW_INTEGRATION_20261030.md): se separan el método causal congelado y el candidato DICE. El banco batch archivado requiere calificar su normalización y sus métricas Top-1/Top-3; sus valores no se modifican ni se transfieren a R11. La imagen de tipos de evento queda protegida mediante hashes durante el build.

Título de trabajo: *Physics-Based Event Attribution From Sparse PMUs With Recovery Memory*. Autores, modelos y resultados conservados. La revisión de literatura solicitada el 29-oct-2026 concreta la diferencia frente a Warner; no es una nueva versión de inferencia.

La pregunta es: con ocho PMU, ¿qué intervención explica mejor la historia observada, y cuándo puede distinguirse de las alternativas?

El texto sigue problema → modelo de medición → historias físicas → evidencia y M/ΔM → comparación causal → prueba separada de firmas → interpretación. La reconstrucción de estado y el banco batch quedan en suplemento/corpus, con sus contratos y la normalización calificada. E_B/GH31 no se reemplaza por R11, ni E_J se presenta como terminado.

## Tres contribuciones acotadas

1. Atribución con recuperación: comparar una nueva intervención de carga/línea con el estado que dejó una anterior; separar masa activa de causa retenida bajo hipótesis R/X constantes.
2. Prueba operacional reproducible: familia/fuente a tiempo, extras y restauración; nominal/mezcla, ablación negativa y C01 congelada. Ni esa ablación ni C01 aíslan cada operación de memoria.
3. Prueba física controlada de firmas: mismo prefijo/horizonte, nominal frente a recentrado y E_i, midiendo ajuste, origen e intensidad por separado. Es conocida la familia y el ON/OFF; no es otra puntuación del detector causal.

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
| Ablación de firmas | ¿Qué cambia al recentrar y qué añade E_i? |
| Señales X02 | ¿Qué predice cada modelo en un caso fijado? |
| Secuencia y M/ΔM | ¿Cómo evoluciona la decisión y dónde llega tarde? |
| Compromiso de decisión | ¿Qué se gana y qué se pierde al reducir extras? |

El artículo es autónomo; el suplemento se compila por separado. La revisión actual está en [PAPER_REVISION_X02.md](docs/PAPER_REVISION_X02.md). El predictor causal es local y conserva memoria física/instrumental; no resuelve una DAE no lineal por celda y reporte. X02 construye sus derivadas con trayectorias no lineales completas, en otro contrato. El artículo anterior y su PDF están en `archive/before_EI_X02_revision/`.

## C01 sigue intacta

No se miran resultados parciales para reescribir o ajustar el método. El ejecutor sigue congelado en SGSMA. Al completar la importación, `scripts/refresh_narrative_c01.py` y `scripts/c01_main_tables.py` integran en el artículo principal la comparación continua, Chen en aperturas persistentes, normales, exposición, fallos, demoras y censuras. Los detalles adicionales siguen en el suplemento. La campaña no debe sobrescribir esta revisión con la estructura anterior.

Falta terminar C01, interpretar resultados completos y revisar afirmaciones/reproducibilidad/coautores para envío. No se exige ahora otra familia ni otra corrección por bus. No se abre RAW0002 ni se hace push.

## Auditoría del chat público y recuperación — 31-oct-2026

La revisión completa de `6ae64dc7` está en [el corpus](docs/corpus/REVIEW_6ae64dc7.md). X03 reproduce los 108 casos del prototipo externo y sus 14 pruebas; no sustituye F01. X04 ejecutó 38 trayectorias continuas F01: las firmas condicionadas no mejoran la exactitud media frente a equilibrio en las 12 comparaciones con inicio e historia conocidos (98,35 % ambas). Una dirección incierta de severidad previa reduce la separación mediana a 0,8532 de equilibrio. Son controles de componente, no resultados del detector ni prueba universal de no identificabilidad.

El artículo incorpora M3H y el antecedente de sensibilidad DAE, explicita el orden causal y las reglas congeladas del banco, y distingue ajuste, identidad y calibración. La comparación nominal/mezcla no aísla el efecto del banco R/X porque también cambian reglas de publicación. La [revisión independiente](docs/REVIEW_RECOVERY_20261031.md) registra las correcciones. C01 permanece intacta y en ejecución; el manuscrito se prepara para revisión de coautores, no se declara listo para envío hasta integrar y auditar la campaña completa.
