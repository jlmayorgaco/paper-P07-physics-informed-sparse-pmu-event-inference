# Auditoría del artículo principal — 30 de octubre de 2026

**Revisión vigente posterior:** [cierre X02 y artículo de 15 páginas](FINAL_REVIEW_X02.md).
Este documento conserva la auditoría anterior; sus conteos de páginas y
descripción del ensayo pendiente no reemplazan el resultado X02 completo.

**Actualización posterior:** [integración de la revisión compartida](SHARED_REVIEW_INTEGRATION_20261030.md). La lectura histórica del banco batch queda calificada por un defecto de normalización y por la diferencia entre Top-1 conjunto y Top-3 condicionado. No se trasladan esos resultados a R11. El candidato DICE y sus pruebas algebraicas están separados de C01. La imagen de tipos de eventos está protegida por hash en el build.

## Dictamen

El artículo principal es autónomo: presenta problema, algoritmo implementado,
comparaciones, resultados de desarrollo y límites. El PDF no incluye el suplemento.
La revisión editorial no convierte C01 incompleta en evidencia confirmatoria.
No se declara aún listo para envío: faltan C01 completa, interpretación final de
sus intervalos/fallos y aprobación de contenido, autores y metadatos.

## Argumento que sostiene el artículo

Una restauración física no elimina el estado dinámico acumulado. Atribuir una
nueva intervención con ocho PMU exige compararla con esa recuperación y con
otras fuentes. R11 conserva historias de estado y causa, integra la severidad
de carga y representa incertidumbre R/X constante mediante un banco finito.
El aporte defendible es este mecanismo operacional y su evaluación causal;
no una nueva ley de Bayes/Kalman ni el nombre tensor para M.

Warner ya propone trayectorias físicas y búsqueda retrospectiva. Los modelos
múltiples y la detección secuencial también tienen precedentes. El artículo
explicita esa cercanía y no declara superioridad sobre Warner sin ejecutarlo.
Chen2016 se compara únicamente en aperturas persistentes, con su adaptación
y limitaciones documentadas. ExtraTrees identifica implementaciones concretas,
no toda la familia ML ni el score histórico de la hackathon.

## Ecuaciones y ejecución

| Elemento del texto | Qué representa el código / evidencia de comprobación |
|---|---|
| Kirchhoff, terminales, DAE y reducción algebraica | Construcción de operadores desde el modelo congelado; corriente terminal distinta de inyección nodal. Baseline F01 y derivadas C01 selladas. |
| Predictor aumentado discreto | `native_conditional_builder.py`: operadores locales por modo, historia de fase y memoria determinista del filtro de medida; estados AR de discrepancia estadística separados de estados eléctricos. No se simula la DAE no lineal en cada reporte de inferencia. |
| Contexto inicial | Los primeros 300 reportes fijan corrección constante, operación, referencia y escala instrumental. No se presenta esta estimación plug-in como posterior conjunto óptimo de parámetros. |
| Evidencia de amplitud | Integral de severidad gaussiana truncada para cargas; identidad local verificada por dos comparaciones con cuadratura. La apertura de línea es un cambio de operador. |
| M y causa retenida | Masa de evento activo distinta de masa del origen después de OFF; la trayectoria conserva estado y recuperación. M no cubre todas las familias y los 39 buses. |
| ΔM | Identidad contable entre variación dentro de cada modelo y cambio de pesos de red; no una nueva dinámica física del tensor. Identidad comprobada sobre H04. |
| Decisiones | Reglas fijas de publicación y cierre del código archivado; no parada óptima demostrada ni probabilidades calibradas. |
| Separación de respuestas | Análisis auxiliar de identificabilidad; referencia y amplitud fijadas y competidor restringido para evitar una minimización degenerada en cero. No sustituye el algoritmo R11. |

Los resultados de los comprobadores se conservan en `generated/*checks.json`
y `generated/causal_amplitude_identity.json`. Las identidades verificadas no
constituyen una prueba de optimalidad del banco aproximado o de su poda.

## Figuras conservadas y explicación corregida

| Figura del artículo | Procedencia y lectura correcta |
|---|---|
| Arquitectura | `figures/narrative_architecture.tex`, conservada byte por byte: seis bloques de la ruta causal implementada. El diagrama alternativo de tres carriles no se presenta como R11 ejecutado. |
| Tipos de evento | `figures/generated/event_signatures.pdf` y PNG originales, sin cambiar trazas ni diseño. RAW0001 es referencia retrospectiva; el reloj gris de missing es ilustrativo. No convierte seis paneles en seis clases validadas. |
| Unifilar IEEE-39 | Barras y conductores, 12 transformadores de dos círculos, 10 generadores con símbolo sinusoidal y cargas conectadas. Ocho etiquetas P indican tensión PMU; nueve puertos de carga y nueve ramas candidatas en naranja. La identidad y orientación de corriente siguen en el contrato de medición, no en la ubicación del recuadro P. |
| Señales | H04 congelado: V, I, frecuencia y ROCOF; se explica frecuencia absoluta exportada y centrado gráfico. No son ondas instantáneas ni THD. |
| Compromiso de decisión | Datos H04: aciertos a tiempo frente a extras, incluida la ablación negativa que omite BUS16. |
| Secuencia M/ΔM | Un padre H04 y condiciones fijadas. Muestra el diagnóstico BUS31 después de OFF como fallo temporal, aunque la fuente termine siendo correcta. |
| Resolución de fuentes | Experimento batch de 137 soportes, con onset conocido; no se atribuye ese resultado a R11 causal. Se preserva E_B/GH31. |

Los hashes de los gráficos aprobados están en
`archive/submission_audit_20261030/APPROVED_VISUALS.json`.
La topología se convirtió después a un unifilar eléctrico por petición del
usuario. `scripts/draw_ieee39_single_line.py` usa las 46 ramas congeladas y
el inventario de dispositivos copiado de F01 con procedencia y hash en
`figures/source/ieee39_single_line/`. Solo usa presencia de carga/generación,
sin sustituir el punto de operación efectivo por valores P/Q nominales.
`generated/single_line_topology_audit.json` registra las comprobaciones de
39 barras, 46 ramas, 12 transformadores, 10 generadores y las ocho PMU.
La figura anterior se conserva en `archive/single_line_before_20261030/`.

## Resultados que sí están ejecutados

H04: 18 intervenciones físicas repetidas en tres condiciones, no 54 ensayos
independientes. R11 obtiene 53/54 atribuciones a tiempo y 4 extras; nominal
54/54 y 7 extras; ambos ExtraTrees 27/54 y 3 extras. Los 204 s normales por
método no permiten afirmar una tasa de falsas alarmas pequeña con precisión.
El artículo explica que la diferencia observada se concentra en cargas.
La ablación de publicación consigue 0 extras pero baja a 52/54.

C01 sigue ejecutándose sin reajustes. El artículo no anticipa sus resultados.
Su importación al terminar verifica hashes y genera en el texto principal:
comparación estratificada, intervalos por padre, normales/exposición, fallos,
demoras, restauraciones y primer stop de Chen. Las tablas del adaptador se
probaron con un fixture sintético, nunca con resultados parciales para ajustar.
No se promedian medianas entre estratos ni se suman los mismos controles
normales como si fueran dos exposiciones independientes.

## Fuentes activas y pasos restantes

`main.tex` incluye `narrative_intro`, `narrative_related`, `narrative_problem`,
`article_method`, `narrative_protocol`, `narrative_results`, el resultado C01
condicional y `article_resolution`, `article_discussion`, `article_conclusion`.
Los textos antiguos preservados no son las secciones activas del artículo.

Para enviar: terminar C01 y revisar sus resultados completos; comprobar que
abstract/conclusión y tablas finales dicen lo mismo; verificar todas las citas,
PDF y paquete reproducible final; recibir aprobación de coautores y datos de
correspondencia, contribuciones y declaraciones. Se incorporó una declaración
de asistencia de Codex para revisión de los autores. No se inventan metadatos.
No hace falta otra versión para corregir buses ni ampliar ahora las familias.
