# P07: aporte real frente a los métodos más cercanos

Revisión solicitada el 29-oct-2026. Es una comparación de mecanismos y contratos, no una nueva campaña ni una revisión por pares independiente. C01, R11, nominal, planta, semillas y evaluador permanecen congelados. No se consultaron resultados parciales de C01 para seleccionar afirmaciones o variantes.

## Decisión de cierre

El artículo se centra en **atribución física que conserva la recuperación**: decidir si las ocho PMU están mostrando una nueva intervención de carga/línea o la evolución que dejó una anterior, con inicio desconocido y una red nominal imperfecta.

La novedad defendible es una construcción operacional específica y su evaluación, no una nueva regla de Bayes, filtro óptimo o álgebra tensorial. La revisión no acredita prioridad mundial. El riesgo de que un revisor considere la combinación incremental sigue existiendo; se debe responder con mecanismo explícito, comparaciones elegibles y utilidad confirmada, no con otro nombre.

## El argumento científico en cinco frases

1. **Problema:** una red puede seguir oscilando después de restaurar un operador, y un evento posterior puede comenzar durante esa recuperación con solo ocho PMU disponibles.
2. **Diferencia que se examina:** los precedentes de detección por trayectorias y diagnóstico secuencial no constituyen por sí solos una evaluación de ese contrato de episodios sucesivos de carga/línea, OFF desconocido y recuperación conservada.
3. **Mecanismo:** comparar historias iniciadas desde estados pasados estimados, separar masa activa de causa retenida y mantener hipótesis R/X constantes con puntuación predictiva; la referencia durante recuperación es una trayectoria física.
4. **Prueba que podría refutar la utilidad:** que R11 no conserve decisiones oportunas o genere demasiadas extras frente a nominal/ExtraTrees en C01; que la explicación de recuperación no se corresponda con el código; o que un antecedente ya resuelva el mismo contrato sin diferencia sustantiva.
5. **Consecuencia:** un usuario podría reutilizar una forma verificable de atribuir episodios y examinar incertidumbre, con límites explícitos de resolución, en vez de recibir solo una etiqueta de bus.

## Comparación concreta

| Trabajo | Qué hace y dónde entra la física | Qué se comparte | Diferencia defendible / límite de comparación |
|---|---|---|---|
| Chen et al., 2016, [DOI](https://doi.org/10.1109/TPWRS.2015.2394246) | Estadísticas de incrementos angulares ligadas al modelo de red; detección/identificación secuencial de apertura persistente | Hipótesis físicas y decisión causal | C01 lo ejecuta solo en apertura persistente/normal. No es un clasificador de carga ni estimador de restauración. |
| Rovatsos et al., 2017, [texto de autores](https://aledan.ece.illinois.edu/files/2017/04/TSP_2017.pdf) | Incorpora fases transitorias y respuesta inercial/gobernador al QCD de líneas | La dinámica transitoria ya es antecedente | R11 compara historias de carga/línea y recuperación. No hay corrida común contra Rovatsos. |
| Warner et al., 2023, [preprint](https://doi.org/10.36227/techrxiv.23264519.v1) | Trayectorias DAE V/I, barrido retrospectivo y evidencia de distancia para cortocircuitos de línea; devuelve candidatos al detenerse | Modelo físico, PMU dispersas, inicio desconocido y búsqueda en ventana ya están allí | R11 conserva estados/cause mass después de OFF y admite carga como objetivo. El artículo revisado no promete vencer a Warner y distingue cortocircuito de apertura de línea. |
| Warner y Fellouris, 2024, [DOI](https://doi.org/10.3150/23-BEJ1671) | Adaptive Matrix CuSum para diagnóstico secuencial; analiza identificación, falsas alarmas y demora bajo sus hipótesis | Un inicio desconocido y evitar contaminación previa no son nuevos | R11 no hereda optimalidad ni control de error de ese algoritmo; tiene selección/poda y estimaciones por sustitución. |
| Blom y Bar-Shalom, 1988, [IEEE](https://ieeexplore.ieee.org/document/1299/) | Gestión/aproximación de hipótesis en filtrado con modos conmutados | Un banco que conserva estados condicionales y pesos tiene precedentes clásicos | R11 no es una nueva derivación IMM. Su especificación de historias y decisiones debe justificarse por la tarea física y la evidencia. |
| Katanic et al., 2024, [DOI](https://doi.org/10.1049/gtd2.13308) | Estimación recursiva de estados diferenciales/algebraicos con DAE incompleta | DAE y reconstrucción de estados | Estimar estados no equivale a clasificar/localizar episodios. P07 no reclama inventar un observador DAE. |
| Li et al., 2024, [editorial](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/gtd2.13331) | STGCN con restricciones tipo/topología y coste de localización; ventanas de PMU | Topología, firmas espacio-temporales y restricciones físicas ya se usan en ML | R11 construye la predicción de cada intervención y no aprende una cabeza de etiquetas de fuente. Esto es diferencia arquitectónica, no prueba de superioridad. |
| Ensaf y Barati, 2023, [versión leída](https://arxiv.org/abs/2309.10200) | Swing estocástico y regresión kernel para estados observados/no observados | Física más incertidumbre y pocas mediciones tienen precedentes | Su tarea es estimación/pronóstico, no atribución de episodios. Sirve para diseñar incertidumbre futura, no para atribuirle a R11 un GP inexistente. |
| Tartakovsky et al., 2023, [DOI](https://doi.org/10.1016/j.ijforecast.2022.03.007) | Media/covarianza del prior obtenidas de simulaciones de dinámica estocástica | Un prior/covarianza derivados de física ya existen | Referente para incertidumbre de forzamiento; no avala probabilidades calibradas de eventos en R11. |
| Alalem Albustami et al., 2026, [preprint](https://arxiv.org/abs/2604.15686) | Inferencia Bayes DAE de parámetros de generador/red y co-identificabilidad | DAE + Bayes + parámetros inciertos tampoco son una prioridad propia | R11 usa cinco hipótesis R/X fijas, no estima el posterior continuo de inercia, amortiguamiento e impedancias. Se cita la versión disponible en 2026; la asignación editorial posterior es 2027. |
| Eriksson et al., 2013, [DOI](https://doi.org/10.1016/j.automatica.2013.02.045) | Diagnosticabilidad cuantitativa de modelos descriptor estocásticos | Separación de fallas y parámetros nuisance tiene teoría previa | El estudio de soportes de carga de P07 es aplicación/evidencia propia, no descubrimiento de diagnosticabilidad. |

La matriz CSV compañera registra también el nivel de acceso a cada fuente. Un "no evaluado" describe el contrato reportado, no demuestra que un autor no pudiera extender su método.

## Auditoría de Warner: coincidencias que no debemos vender como nuevas

Las ecuaciones (2)-(4) del preprint acumulan la mejora de ajuste de una trayectoria de falla frente a una referencia estacionaria y maximizan sobre inicios dentro de una ventana. Por tanto, la idea original de "suponer que ocurrió hace T y comparar las curvas" tiene un antecedente directo. Su Algorithm 1 es una parada de detección/identificación; sus Sections III-IV evalúan probabilidad de identificación dentro de una ventana y falsas alarmas, incluyendo cambios de carga adversos. Su caso de IEEE-39 usa dos PMU, 60 fps y cinco tramas de memoria. No corresponde trasladar sus porcentajes a nuestra tarea de 30 fps, cargas y aperturas con restauración.

La diferencia propuesta es **condicionar al estado que trae la red y continuar atribuyendo la recuperación después de restaurar el operador**. El nuevo apartado `sec:recovery-mechanism` explicita el flujo homogéneo local después de OFF. Esa ecuación es una explicación de dinámica conocida y de la implementación, no un teorema original.

Acceso: se verificaron DOI/autoría como preprint y páginas indexadas del propio PDF (II-B p.3, Algorithm 1 p.4, III-IV p.5, IV-A/B p.6 y conclusión/apéndice p.9). La descarga directa devolvió error DNS/403; no se presenta como una copia completa obtenida. La ausencia de una corrida común se declara en el artículo.

## Qué aportamos y con qué fuerza

| Afirmación | Clase de evidencia | Estado y límite |
|---|---|---|
| R11 conserva hipótesis de causa/recuperación y compara una intervención posterior desde estados estimados | Implementación verificable | Código R11 y trazas H04; capacidad construida, no prioridad mundial. |
| La mezcla de red cambia el compromiso entre extras y demora | Empírica de desarrollo | Tabla H04 nominal/mezcla; no demuestra que todas las operaciones de recuperación causen la mejora. C01 es la confirmación pendiente. |
| Los componentes matemáticos de M/ΔM son novedosos | Rechazada | Son agregación e identidad de incrementos; no hay descomposición tensorial ni optimalidad nueva. |
| Reconstruir el estado permite siempre localizar | Rechazada | Estudios de estado y soportes son distintos; fuentes débiles se confunden. |
| La retención de recuperación es, por sí sola, la causa demostrada de la ganancia | No establecida | La ablación de admisión cambia otra operación; no se reinterpreta como ablación pura de memoria. |
| R11 vence a Warner o Adaptive Matrix CuSum | No establecida | No se ejecutaron bajo un contrato común. C01 no se altera para aparentar esa comparación. |
| Mejoramos el leaderboard oficial de la hackathon | No establecida | Dos adaptadores ExtraTrees en un contrato restringido no sustituyen una comparación oficial de todas las familias. |

## Diferencia que debe recordar el lector

**Después de OFF queda una trayectoria física que debe seguir compitiendo como explicación; cerrar el episodio no equivale a borrar el estado.** La utilidad se juzga por familia/origen a tiempo, extras y restauración, no solo por aciertos eventuales. La contribución acotada puede ser valiosa si C01 confirma utilidad y los coautores consideran suficiente la diferencia metodológica. No se promete una revolución teórica ni aceptación.

## Qué incorporamos ahora y qué no ampliamos

- Incorporado: antecedentes directos, tabla de contratos, explicación física de recuperación y registro de afirmaciones/limitaciones.
- Se conserva: R11/nominal, C01, E_B/GH31, planta y resultados históricos.
- Se difiere: GP de discrepancia, GAT/LSTM, estimación continua de impedancias, nuevas familias y nuevos umbrales. No son requisitos añadidos para cerrar este manuscrito.
- Si el examen o la revisión de novedad no sostienen una afirmación, se reduce o retira esa afirmación; no se corrige otro bus sobre C01.

El cierre pendiente sigue siendo finito: C01 completa, interpretación de sus resultados y revisión final de literatura/artefactos/coautores. La matriz se actualiza con esta búsqueda dirigida; no se declara una revisión sistemática exhaustiva.
