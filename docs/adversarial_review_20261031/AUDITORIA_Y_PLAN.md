# P07: auditoría adversarial y decisión científica

Fecha: 31 de octubre de 2026. Versión revisada: fuentes actuales de P07, incluidas las modificaciones locales de recuperación documental, identificadas por `SUBMITTED_MANIFEST.json`.

## Respuesta directa

**No presentaría esta versión como la mejor versión científicamente defendible del artículo.** Hay un núcleo físico y matemático razonable, pero todavía falta demostrar que la complejidad del banco de historias aporta una ventaja frente a un predictor causal mucho más sencillo. Además, encontramos errores concretos y condiciones omitidas en el suplemento, y dos problemas semánticos en las métricas de la campaña confirmatoria.

**No hay evidencia suficiente para prometer buenos resultados en RAW0001 ni una mejora sobre la solución de la hackathon.** Tampoco hemos demostrado que R11 vaya a fracasar. Los resultados actuales corresponden a un catálogo de cargas y líneas bajo F01, no a todas las clases de la competición. El reparto 70/30 no resuelve la diferencia entre simulador y datos reales.

Esta revisión no cambia el manuscrito ni el método para que sobrevivan al ataque. Deja contraejemplos, comprobaciones y reparaciones propuestas. No se ejecutó entrenamiento ni un replay del detector sobre RAW; no se consultó verdad reservada ni predicciones parciales de C01. RAW0002 sigue cerrado. No se hizo push.

## Qué encontramos, por orden de importancia

| Prioridad | Hallazgo y evidencia | Consecuencia |
|---|---|---|
| Alta | No hay una comparación que aísle el valor del banco de historias. La mezcla, nominal y el testigo de inicio cambian también publicación/admisión. | La utilidad de preservar el estado físico es razonable; la necesidad de este banco concreto todavía no está demostrada. |
| Alta | H04: mezcla 53/54 atribuciones oportunas y 4 extras; nominal 54/54 y 7; testigo 52/54 y 0. Son 18 intervenciones en tres padres con eventos, repetidas en tres condiciones. | Hay compromisos entre errores. No son 54 ensayos independientes ni evidencia de superioridad universal. |
| Alta | Una restauración emitida a 13 s, cuando el OFF verdadero es 15 s, produce `false_restorations=0` si el episodio estaba emparejado. | Ese contador no mide todos los cierres falsos. Deben añadirse cierres prematuros y duración perdida; el `off_delay_s=-2` sí conserva la evidencia. |
| Alta | Una alarma a 11 s y diagnóstico correcto a 19 s para un ON a 10 s produce `first_correct=true`, `delay_s=1` y demora de diagnóstico 9 s. | La variable no significa «fuente correcta al primer stop» como dice el plan. Los tiempos están guardados, pero hay que distinguir alarma y primera decisión de fuente. |
| Alta para el suplemento | La separación mínima entre conos definida en el apéndice D es simétrica; el texto afirma que puede no serlo. La fórmula cone–Laplace del apéndice E falla como equivalencia multiplicativa cuando el cono límite tiene masa gaussiana cero. | Corregir el enunciado y las hipótesis. Son defectos demostrados del material teórico; no refutan por sí mismos el R11 ejecutado. |
| Alta para transferencia | El runtime congelado rechaza un NaN después del arranque. RAW0001 contiene 9.200 reportes con `DATA_PRESENT=0` en BUS29. El catálogo R11 admite solamente nueve cargas y nueve líneas. | R11 no es hoy un reemplazo directo de la solución completa. Hace falta un contrato explícito de integridad, disponibilidad y clases no admitidas. |
| Alta para validez externa | F01 usa calibración retrospectiva de RAW0001, conserva BUS5 5–6 provisional, BUS39 parcial y limitaciones instrumentales. | Un buen replay RAW0001 sería evidencia retrospectiva, no validación externa independiente ni certificación del simulador. |

Los casos de métricas son fixtures artificiales sobre las funciones existentes. Demuestran qué contabiliza el código, **no que esos errores hayan ocurrido en C01**. No se debe modificar el evaluador congelado a mitad de la campaña. La salida original debe conservarse; una auditoría sucesora, con reglas escritas antes de ver los resultados, puede informar las métricas corregidas por separado.

### Otros defectos matemáticos que no conviene dejar publicados

El informe matemático documenta también:

- La reducción por fibras exige invariancia de la **ley completa**, no solamente de la media: una covarianza que cambia con la coordenada eliminada cambia la evidencia.
- La constante del teorema de evidencia de orden superior supone un dato centrado sin residuo y amplitud bilateral; esas condiciones deben figurar en el enunciado.
- La cota de estabilidad necesita definir el menor valor singular por el mínimo sobre vectores de coeficientes unitarios, y exigir margen positivo. Una matriz ancha puede tener núcleo aunque la lista rectangular de valores singulares no incluya un cero.
- Algunas inversas necesitan positividad definida o trabajar en coordenadas identificables; algunas fórmulas escalares necesitan tangente no nula.
- El estimador histórico por lotes se presenta en un apéndice como evidencia normalizada con prior `(0.20, 0.50, 0.30)`, mientras otro ya reconoce un factor erróneo `1/(2π)` solamente para una fuente. En un control sin señal, eso equivale a `(0.345079, 0.137303, 0.517618)`. Es una contradicción de presentación que debe reconciliarse, no un nuevo defecto atribuido a R11.

Las demostraciones, condiciones exactas y ubicaciones están en [REVIEW_MATH.md](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/docs/adversarial_review_20261031/REVIEW_MATH.md).

## El ataque más fuerte a la contribución

Un revisor puede aceptar todas las ecuaciones centrales y aun así preguntar:

> Si el estado físico e instrumental ya conserva la recuperación, ¿qué mejora aporta mantener este banco de historias frente a un solo predictor causal de estado y una prueba residual de nuevas intervenciones?

El competidor decisivo debe conservar el estado después de OFF, actualizar el modo de red en aperturas y usar el mismo catálogo, observaciones, prefijo y reglas de publicación. Un adversario que borre el estado después de cada evento sería demasiado débil: derrotarlo mostraría que hay que conservar la física, pero no que hacen falta las historias de R11.

Los ingredientes tienen antecedentes —IMM, hipótesis múltiples, sensibilidades DAE y evidencia bayesiana— que el artículo cita. La novedad defendible es la especificación e integración operacional, y exige medir su utilidad. La revisión bibliográfica focalizada y las fuentes primarias están en [REVIEW_DEVILS_ADVOCATE.md](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/docs/adversarial_review_20261031/REVIEW_DEVILS_ADVOCATE.md); no constituye una búsqueda exhaustiva de todos los antecedentes.

Hay dos controles particularmente importantes:

1. **X02:** recentrar y condicionar obtienen ambos 240/240 decisiones correctas y 0/15 selecciones de evento en normales. Condicionar mejora severidad y ajuste de respuesta, pero no mejora la decisión de fuente respecto al recentrado. La contribución positiva aquí es la reducción del sesgo de intensidad.
2. **X04:** la separación mediana cambia por un factor 1.0006 con historia conocida y 0.8532 al añadir incertidumbre en la severidad previa; ambos clasificadores tienen 98.35% de precisión binaria media. Este control no aporta evidencia de nueva información útil de fuente durante recuperación. Es un resultado negativo valioso y debe conservarse.

El texto actual ya reconoce esos límites. No los tratamos como engaños ni como garantías que los autores hayan prometido. El problema es que, juntos, dejan una contribución positiva más estrecha que la cantidad de material que la rodea.

## Qué sobrevivió al intento de falsificación

- La reducción local DAE y la continuidad del estado diferencial al restaurar son correctas bajo el contrato declarado.
- La integral de severidad truncada de R11 pasó 12 contrastes con cuadratura independiente: error relativo máximo `6.66e-16`. La media condicional integrada tuvo error máximo `8.88e-16`.
- Las identidades Fisher/proyección con nuisance redundante y la monotonía de información al añadir prefijos válidos pasaron 30 comprobaciones independientes.
- El documento distingue masa aproximada de posterior calibrado, inicio estimado de tiempo de emisión y éxito eventual de éxito antes de OFF. Estas distinciones son necesarias y están bien planteadas.

Estos controles verifican álgebra bajo hipótesis. No certifican estabilidad numérica en todos los regímenes, poda del banco, covarianza compartida, calibración probabilística ni transferencia real.

## SIM 70/30 y comparación con la hackathon

La partición correcta es por **trayectorias físicas padre completas**, antes de producir ventanas o réplicas. Todas las versiones de un mismo padre —condiciones de red, ruido, PMU y ventanas solapadas— van al mismo lado. Dentro del 70% se necesita validación para seleccionar umbrales, priors, diccionario o hiperparámetros. El 30% se abre una sola vez después de congelar.

Pero los SIM existentes ya participaron en iteraciones de desarrollo. Repartirlos de nuevo no devuelve independencia a los que ya se vieron. Pueden ser un banco de desarrollo retrospectivo; el test confirmatorio debe usar padres nuevos y un protocolo sellado. C01 ya cumple parte de ese propósito y sigue su curso. No se debe incorporar a entrenamiento ni escoger al ganador según sus resultados.

Además, R11 no se entrena como un clasificador supervisado convencional: hay que declarar qué se ajustaría y en qué datos. **Los ExtraTrees actuales ya fueron reentrenados con SIM0014–SIM0017 y validados con SIM0018.** No sería correcto atacar el artículo diciendo que se comparó exclusivamente contra el ZIP antiguo sin entrenamiento SIM. La comparación adicional debe igualar acceso a desarrollo, cobertura y presupuesto de selección.

Después de congelar, RAW0001 puede servir para un replay causal retrospectivo con dos informes: desempeño en las familias admitidas y comportamiento del sistema completo, incluyendo integridad y clases excluidas. No se pueden borrar los segmentos difíciles ni cambiar umbrales después de observarlos y seguir llamándolo test. La guardia de acceso RAW del runner congelado debe conservarse; el replay requiere un adaptador sucesor explícito.

«Mejor que la hackathon» necesita dos comparaciones distintas:

- Contra el artefacto histórico congelado, bajo el mismo flujo, familias, verdad y política de puntuación local: mide mejora respecto a ese artefacto en ese registro.
- Contra un competidor reentrenado con el mismo conjunto SIM y oportunidades de ajuste: mide la ventaja del método bajo acceso comparable a datos.

Ninguna comparación local demuestra mejora del leaderboard oficial. El expediente histórico consultado no conserva un score oficial verificable; tampoco se ha generado uno en esta revisión. El [protocolo propuesto](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/docs/adversarial_review_20261031/PROTOCOLO_SIM_RAW.md) especifica agrupación, métricas, congelación y criterios de interpretación.

## Qué recortaría y qué haría primero

El artículo debería concentrarse en una pregunta: **¿preservar incertidumbre sobre historias físicas mejora la atribución oportuna durante recuperación frente a conservar un único estado?** Si no mejora, la contribución debe reducirse honestamente a continuidad física y especificación reproducible.

Mantendría en el artículo el mecanismo causal, una comparación decisiva, fallos representativos y límites. En el suplemento dejaría la derivación de R11, ejemplos verificables, pseudocódigo, escenarios, contratos y reproducción. Movería a una nota histórica versionada la propuesta no ejecutada `E_J`, el piloto por dossiers y gran parte de la teoría que no interviene en R11. Eso preserva el trabajo sin obligar al lector a defender varios artículos dentro de uno. Las figuras protegidas de eventos y unifilar se conservan.

Orden recomendado:

1. Corregir los enunciados y reconciliar las descripciones históricas del suplemento, sin cambiar resultados.
2. Congelar una auditoría sucesora de métricas; preservar C01 original y sus artefactos.
3. Ejecutar en un candidato nuevo la comparación banco contra estado propagado sencillo, y separar una/redes múltiples usando idéntica publicación.
4. Evaluar padres nuevos sellados; después realizar el replay retrospectivo RAW0001 con alcance y disponibilidad explícitos.
5. Reescribir la afirmación principal según el resultado, aunque favorezca al método sencillo.

## Evidencia de esta auditoría

- [Revisión matemática](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/docs/adversarial_review_20261031/REVIEW_MATH.md).
- [Revisión de metodología](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/docs/adversarial_review_20261031/REVIEW_METHODOLOGY.md).
- [Ataque a la contribución y recortes](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/docs/adversarial_review_20261031/REVIEW_DEVILS_ADVOCATE.md).
- [Disponibilidad del runtime y RAW0001](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/docs/adversarial_review_20261031/REVIEW_RUNTIME_AND_RAW.md).
- `checks/math_independent_checks.py`, `checks/methodology_metric_checks.py` y `checks/runtime_scope_checks.py`, con resultados JSON junto a cada script.

Se usó la skill `academic-paper-reviewer` para perspectivas independientes. Sus plantillas obligatorias para una ronda editorial puntuada no estaban disponibles en la instalación; por eso se entrega una auditoría técnica, sin inventar puntuaciones, contratos de sprint ni una decisión editorial formal.
