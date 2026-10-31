# Qué cerrará C01 y qué significa «publicable»

Auditoría: 29-oct-2026. La campaña está en ejecución; este documento no contiene
resultados anticipados. Las decisiones se basarán en los CSV completos.

## Dictamen actual

Hay material para un manuscrito de investigación dirigido a IEEE Access:
recuperación funcional de estado frente a separación de fuentes, inferencia
mediante hipótesis físicas y evidencia que conserva ambigüedades y fallos.
Todavía no se declara listo para envío. La contribución no es renombrar una
matriz como tensor ni juntar algoritmos clásicos; esas operaciones tienen
precedentes y se reconocen como tales.

Para el artículo acotado actual no se exige implementar todas las familias de
la hackathon, abrir RAW0002 o alcanzar cero errores. Esas extensiones no se
añaden ahora como requisitos para seguir posponiendo el cierre.

## Gates finitos

| Gate | Cómo se cierra | Qué impediría cerrar |
|---|---|---|
| Comparación confirmatoria | C01 completa con R11/nominal, ambos ExtraTrees y Chen en su carril elegible; fallos/censuras/denominadores incluidos | Ejecución incompleta, pérdida de casos, ajustes después del examen o comparación de tareas incompatibles |
| Contribución respaldada | Las afirmaciones de método/teoría y utilidad resuelven a ecuaciones, código y resultados, incluyendo derrotas; contraste explícito con los precedentes | Afirmar optimalidad, novedad por M/ΔM, mejora del leaderboard o generalización no ensayada |
| Manuscrito reproducible y revisado | Tablas/figuras desde hashes, referencias comprobadas, PDF revisado, alcance consistente y aprobación de coautores/metadatos finales | Números sin fuente, citas o resultados inventados, figuras ilegibles o conclusiones más fuertes que la evidencia |

C01 no necesita que R11 gane todas las métricas. Si la mezcla y la nominal
intercambian precisión y demora, ese compromiso es parte del resultado. Si
Chen falla en F01, el paper debe distinguir el núcleo publicado correcto de
los supuestos de su adaptador, sin usar esa incompatibilidad para vender una
superioridad universal. Si desaparece la utilidad o falta novedad diferencial,
se acota o retira la afirmación correspondiente; no se arregla otro bus sobre
el examen.

## Respuesta a la pregunta del autor

Al cerrar esos gates, el manuscrito puede quedar **listo para someter** con
el alcance validado de carga/línea y sus limitaciones. Eso no equivale a una
aceptación garantizada. IEEE Access exige contribución al conocimiento,
experimentos de rigor, conclusiones respaldadas y referencias adecuadas; una
cifra de aciertos aislada no sustituye esos criterios.
[Requisitos oficiales](https://ieeeaccess.ieee.org/authors/preparing-your-article/).

## Estado y continuidad verificables

La fuente operativa es `experiments/PAPER_CONFIRMATORY_C01/run/PROGRESS.json`
del repositorio SGSMA. `COMPLETE.json` señala el fin de la campaña;
`PAPER_UPDATED.json` señala importación, gráficos y compilación P07.
`BLOCKER.json` registra un fallo de ejecución. Ninguno equivale por sí solo
a autorización de envío. Al terminar se consultan
`generated/frozen/c01_20261029/` y `docs/c01-confirmatory-results.md`.
