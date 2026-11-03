# Auditoría adversarial de método, datos y evaluación — P07

31-oct-2026. Auditoría independiente del manuscrito activo y evidencia completada. C01: solo código y contratos; no se leyeron observaciones, predicciones parciales, resultados ni verdad reservada. No se modificaron C01, baselines ni manuscrito; no se lanzó entrenamiento/simulación ni se abrió RAW0002. Los únicos checks ejecutados son fixtures inventados en `checks/methodology_metric_checks.py`, con resultados en `checks/methodology_metric_checks.json`. No se inventa puntuación ni contrato formal de revisión.

Referencias: `P/` significa este repositorio; `R/` significa el hermano `SGSMA26-Physics-Informed-AD`. Las ubicaciones archivo:línea corresponden al código inspeccionado.

## Dictamen

**No hay evidencia de que entrenar/ajustar con todo SIM0001 y otras campañas, reservar 30% y después evaluar RAW0001 vaya a superar la hackathon.** Es una hipótesis que requiere un experimento. Más datos del mismo generador pueden ayudar a un comparador supervisado; no resuelven por sí solos familias ausentes, incertidumbre de terminales, recuperación ni cambio de dominio. R11 es inferencia basada en modelos, no una red que necesite simplemente más entrenamiento: también sus priors, covarianzas, umbrales y reglas de publicación pueden sobreajustarse al desarrollo (`P/sections/article_method.tex:10–15,62–72,186–205`).

Un 70/30 por filas, ventanas, PMU, semillas o realizaciones hermanas es inválido. Un 70/30 por padres completos sí organiza desarrollo, pero **repartir campañas ya examinadas no convierte su 30% en confirmación inédita**. H03/H04 y el historial SIM contribuyeron al desarrollo. C01 conserva sus métodos congelados. RAW0001 ya es calibración retrospectiva por contrato (`R/SIM0001_JuliaPD_F01/START_HERE.md:85`), aunque el clasificador nuevo nunca lea sus filas: el simulador hereda información de esa calibración.

El artículo actual reconoce estos límites (`P/sections/narrative_protocol.tex:18–22`; `article_interpretation.tex:36–55`). Por tanto no corresponde acusarlo de prometer una victoria oficial que explícitamente niega. Falta evidencia para ampliar su resultado desde implementaciones concretas en F01 hacia ventaja general, aporte causal específico de memoria o superioridad RAW/hackathon.

## M1 — Alto: el agregado de falsas restauraciones omite cierres prematuros emparejados

**Defecto verificable de cobertura de métrica; no resultado observado de C01.** `R/experiments/PAPER_CONFIRMATORY_C01/execution/evaluate.py:41–48` cuenta `false_restorations` únicamente cuando el episodio restaurado no se emparejó con ningún evento verdadero. Una restauración prematura de un episodio verdadero emparejado no lo incrementa. `off_delay_s` sí conserva el error firmado; el resumen usa la mediana (`evaluate.py:59`), que puede ocultar colas o compensar errores opuestos. El texto promete separar falsas restauraciones y episodios abiertos (`P/sections/narrative_protocol.tex:28`) sin precisar esta definición restringida.

Fixture: ON=10, OFF=15, alarma=11, diagnóstico correcto=12, restauración=13. Resultado ejecutado: `off_delay_s=-2`, `false_restorations=0`. No prueba que ocurra en C01; prueba que el contador no captura ese fallo.

**Corrección:** conservar la evaluación original congelada y crear una auditoría sucesora que separe restauraciones de episodios extra, restauraciones anteriores al OFF verdadero, cierres posteriores al siguiente ON y ausencia de cierre. Mostrar conteos, denominadores y distribución firmada de demora OFF por padre/familia/condición. Nombrar el agregado original “restauraciones de episodios no asociados”. No modificar C01 ni elegir tolerancias después de ver resultados.

## M2 — Alto: atribución posterior a alarma bajo el rótulo “correct line at first stop”

**Desajuste de estimando textual; los tiempos internos no están retrodatados.** C01 declara `correct line at first stop` (`R/experiments/PAPER_CONFIRMATORY_C01/protocol/PLAN.json:21`). `execution/metrics.py:4–8` asocia cada alarma con el primer diagnóstico posterior del episodio; `metrics.py:35–38` calcula `first_correct` con ese diagnóstico, mientras `delay_s` usa alarma. Chen emite alarma y fuente juntas (`execution/evaluate.py:38–40`). El método principal distingue alarma/diagnóstico (`P/sections/article_method.tex:186–193`), pero el protocolo describe decisiones en primera parada (`narrative_protocol.tex:12,24–26`).

Fixture persistente: ON=10, horizonte=30, alarma=11, diagnóstico=19. Se probaron fuente correcta/incorrecta en el mensaje de alarma, cruzadas con diagnóstico correcto/incorrecto/ausente. `metrics.alarms` ignora el campo fuente de alarma y utiliza el diagnóstico. Diagnóstico correcto: `first_correct=true`, `delay_s=1`, `restricted_correct_delay_s=9`, incluso con fuente inicial incorrecta. Diagnóstico incorrecto: fallo incluso con fuente inicial correcta. Sin diagnóstico: ABSTAIN/fallo, pero `right_censored=false` porque sí hubo alarma. Esto no demuestra que los métodos publiquen realmente una fuente inicial incorrecta: demuestra qué información usa la métrica.

**Corrección:** auditoría sucesora con (a) primera alarma y falsa parada, (b) primera atribución emitida y su fuente, (c) ausencia de atribución hasta horizonte. Comparar disponibilidad de decisión conjunta usando diagnóstico; `restricted_correct_delay_s` ya preserva ese tiempo. Si se retiene el agregado original, llamarlo “diagnóstico asociado a la primera alarma”, no “fuente conocida al parar”. No vender demora de detección como demora de localización. Conservar C01 original.

## M3 — Alto para la tesis fuerte: no se aísla el efecto de la memoria

Nominal frente a mezcla cambia procedimientos completos, incluida publicación; R12 cambia admisión, no elimina memoria. El artículo lo reconoce (`P/sections/article_method.tex:195–199`; `article_interpretation.tex:12–15`). La geometría con historia suministrada y EI-X02 con ON/OFF conocidos no prueban la ganancia causal de la memoria (`narrative_protocol.tex:14`; `article_ei_x02.tex:59–65`). H04 da 53/54 oportunos y cuatro extras para mezcla frente a 54/54 y siete para nominal (`P/tables/generated/narrative_results.tex:6–13`): tampoco hay dominancia de mezcla en ambos objetivos.

**Contraste primario necesario en un sucesor:** comparar el banco R11 contra un predictor más sencillo que conserve el estado físico e instrumental y la topología tras cada conmutación, con las mismas señales, reglas de publicación y umbrales. Declarar la reducción de historias competidoras y su presupuesto computacional: así se prueba el valor adicional del banco de historias frente a conservar correctamente el estado. Parear padres con intervalos cortos/largos tras OFF y controles sin nuevo evento; predefinir diferencias en atribución oportuna, extras y cierre. Un reset a equilibrio puede añadirse como control secundario, pero es físicamente inconsistente y por sí solo no demuestra que sea necesario el banco R11. Añadir mezcla con publicación idéntica. Si el banco no mejora donde se predice, reducir la tesis de su aporte específico. No elegir estos ablations con C01.

## M4 — Alto para un ranking general: distinguir comparadores actuales y ZIP histórico

**Los ExtraTrees actuales sí fueron reentrenados en SIM.** R09 usa SIM0014–17: 24 padres de eventos y ocho controles; validación de desarrollo SIM0018: seis padres de eventos y dos controles. Son 18 fuentes, 47 señales, prefijo de 300 reportes y seis argmax consecutivos para publicar. El código exige las 19 etiquetas incluyendo normal (`R/experiments/E5_VALIDATION_PAPER/M03_R09_NUISANCE_DEV/ml/README.md:3–12`; `RESULTS.md:10`; `run.py:51–69`). `GROUP_AUDIT.json` registra 30 programaciones sin duplicados. Sería incorrecto afirmar que H04 solo derrotó un modelo que jamás vio F01.

Persisten diferencias válidas para comparar sistemas pero insuficientes para atribuir toda la ventaja a física: R11 conoce planta/instrumento/direcciones físicas y acumula sucesores; ET tiene dos variantes y ninguna búsqueda de hiperparámetros (`ml/PROTOCOL.json`; `README.md:10`). Esto no invalida el ensayo de artefactos congelados; limita “mejor que ML”. Para un nuevo benchmark: catálogo y disponibilidad temporal comunes, presupuesto de desarrollo declarado, ajuste exclusivamente interno y baselines competentes. Las diferencias entre default y ajuste pueden ser del orden de diferencias entre algoritmos: [estudio primario sobre ajustes por defecto](https://arxiv.org/abs/1703.06777).

El ZIP original se evaluó por separado en SIM0017 ya abierto, con restricciones de una decisión/30 s y cobertura desigual (`R/experiments/E5_VALIDATION_PAPER/R07_HACKATHON_COMPARISON_20261027/REPORT.md:7–17,39–55,76`). Su derrota no aísla el clasificador. Chen tiene ley DC/blanca; su fallo normal en H04 no demuestra inferioridad del algoritmo bajo su ley (`R/experiments/PAPER_CONFIRMATORY_C01/comparator/README.md:20–38`). C01 separa correctamente su carril persistente.

## M5 — Alto para un test nuevo: reutilización adaptativa y dependencias

No encontré prueba de fuga de verdad a las características actuales. Hay separación de rutas, sellos y checks causales. Usar un prefijo PMU del registro no es fuga si la adaptación es causal y estaba prefijada. El riesgo principal es selección del procedimiento a través de campañas y pseudorreplicación al volver a repartirlas.

H03/H04 son desarrollo (`P/sections/narrative_protocol.tex:20`; C01 `PLAN.json:7`). SIM0004 es desarrollo de V3 (`R/SIM0005_PMU_ADAPTIVE_HOLDOUT/README.md:11–14`); SIM0006 es desarrollo de V5 (`SIM0007_RECLOSURE_HOLDOUT/README.md:3–4`). Congelar cada candidato antes de su examen no convierte todos esos exámenes en confirmación independiente del ganador elegido después. Véase [Cawley y Talbot, JMLR 2010](https://jmlr.org/papers/v11/cawley10a.html).

El assert train/validation de `ml/run.py:48–51` utiliza `campaign/physical_id`; su auditoría separada de programaciones es valiosa. Una combinación nueva necesita parentesco global y fingerprints, no confiar en nombres SIM. Ejemplo puramente ilustrativo: con seis clones y split independiente 70/30, probabilidad de repartir un padre en ambos lados = `1−0.7^6−0.3^6=88.1622%`. No es una fuga observada del split actual.

## M6 — Medio/alto: exposición e intervalos limitan las garantías

H04 tiene tres padres de eventos y un padre normal; sus 204 s normales no acreditan baja tasa operativa. Incluso bajo Poisson homogéneo ilustrativo, cero alarmas daría límite superior unilateral 95% de 52.87/h; las realizaciones pareadas no satisfacen automáticamente esa ley. C01 planea 12×588 s disponibles por estrato R11/ML: aun con cero alarmas, ese cálculo sería 1.53/h. Un límite 0.1/h con cero alarmas requeriría cerca de 29.96 h bajo esa ley, más diversidad y justificación de dependencia. No sumar estratos pareados como independientes.

C01 remuestrea correctamente padres (`PLAN.json:19,27`; `execution/metrics.py:45–54`), pero 10.000 resamples no son 10.000 plantas. Los intervalos siguen condicionados a F01, catálogo y ley instrumental. Se necesitan supports por fuente/padre y evitar seleccionar el mejor estrato. `execution/evaluate.py:64–74` genera diferencias R11/nominal contra ET/Chen, pero no diferencia pareada mezcla−nominal. Si se invocan intervalos para el trade-off de co-referencias (`P/sections/article_final_conclusion.tex:14–15`), ese contraste requiere un análisis sucesor declarado, conservando el original.

## Inventario de procedencia

| Bloque | Evidencia y unidad pertinente |
|---|---|
| SIM0001 histórico | Cinco referencias/replays ANDES y siete smoke scenarios; RAW0001 calibración. No fusionar silenciosamente con Julia F01 (`R/SIM0001/DATASET_CARD.md:3–23`). |
| Julia F01 | Research candidate, misma planta, BUS5 provisional y BUS39 parcial. Falla/generación, identidad CT/PT y fidelidad integral abiertas (`START_HERE.md:15,58,67,85`). No son muchas redes físicas. |
| SIM0002 | Dos trayectorias de eventos, 40 intervenciones, un normal; tres semillas: nueve registros (`README.md:7–19`). SIM0002 es nombre de dataset, no otra planta ni RAW0002. |
| SIM0003 | Tres trayectorias, 24 eventos, nueve replays (`GENERATION_MANIFEST.json`). Agrupar trayectoria y semillas. |
| SIM0004/5 | Ocho integraciones cada uno, cuatro condiciones; 64/48 replays y 576/432 realizaciones planeadas (`GENERATION_MANIFEST.json`). Condiciones/ruidos repiten calendario padre. |
| SIM0006/7/8 | Ocho integraciones; 20 eventos padre repetidos entre operación/ruido. El padre estadístico es el calendario continuo, no cada evento. README SIM0006 dice 432/72, pero `PROTOCOL.json:91` dice 480/80: resolver contra manifiestos finales antes de sumar corpus. |
| SIM0009/10 | Dos padres de eventos, cuatro puntos, tres ruidos; 12 trayectorias y 36 replays planeados (`GENERATION_MANIFEST.json`; README SIM0010). Plan no certifica completitud. |
| SIM0011–18 | Manifiestos: ocho trayectorias, 72 eventos, seis calendarios de eventos por campaña. SIM14–17 utilizados en ML y SIM18 validación: desarrollo, no reserva recuperable renombrando. |
| SIM0019 | 24 trayectorias planeadas, seis padres, MATCH/DYN/NET_DYN (`GENERATION_MANIFEST.json:2–11`): no 216 ensayos independientes. |
| H03/H04 | Cada uno tres padres con seis eventos y uno normal × tres condiciones; 54 realizaciones (`R11/R12 protocol/PLAN.json:5–28`). Hoy abiertos. |
| C01 | 18 padres continuos, 27 persistentes y 12 normales; 171 trayectorias/342 registros planeados (`P/sections/narrative_protocol.tex:30`). Confirmación de referencias fijadas, no del nuevo entrenamiento. |
| ANDES 690/batch | Contratos distintos. Réplicas por fuente en ordinary split; onset/familia suministrados en otros componentes (`P/supplement.tex:172,204,214`). No sumar al denominador causal R11. |

No se certificó el número global de padres reutilizables ni se deduplicaron todos los archivos. Esa tarea debe preceder al entrenamiento. El inventario ya refuta que número de registros equivalga a ejemplos independientes o que cada SIM sea otra planta.

## Protocolo 70/30 defendible, propuesto y no ejecutado

1. Fijar estimando: atribución causal de carga/línea en catálogo conocido para P07. All-family exige contrato aparte de familia, fuente física/integridad y simultaneidad.
2. Construir registry por registro: motor/versión, hashes de planta/terminales/instrumento, calendario padre, estado inicial/operación, perturbación estructural, fuentes, severidad, ON/OFF, ruido padre/semilla/escala, archivos físicos/observados, uso histórico y estado de ejecución. Deduplicar trayectoria sin ruido y calendario+estado; copias/exportaciones no son nuevos casos. RAW0001 siempre calibración/desarrollo.
3. Particionar componentes de dependencia completos: todas las ventanas, PMU, eventos, condiciones, semillas, escalas y reexportaciones del mismo padre en un lado. Agrupar también innovaciones comunes si se pretende inferir sobre ruido; alternativamente declarar inferencia condicional. Estratificar familias/fuentes por grupos sin romperlos; aceptar fracción de filas distinta de 70/30. [Documentación oficial de validación agrupada](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data).
4. Dentro del 70%, reservar 20% de grupos para validación interna: aproximadamente 56/14/30 global, o folds agrupados internos. Features aprendidos, escalas globales, selección de canales, calibración, priors y umbrales se eligen solo dentro del 70%. La adaptación causal de prefijo del test es válida si su regla está congelada. Tras selección, refit sobre 70% con política de calibración predefinida; sellar antes del 30%.
5. En el corpus ya abierto, llamar a ese split desarrollo comparativo. Para confirmación del sucesor, definir nuevos padres antes de mirar sus resultados; el histórico puede añadirse solo al entrenamiento. C01 conserva métodos/plan actuales. No prometer tamaño suficiente solo porque es 30%: calcular precisión/potencia por padre y coste.
6. Separar known-source con padres nuevos, source-excluded con activo ausente de toda selección supervisada, condiciones/motor/instrumento excluidos y RAW0001 retrospectivo. Una hipótesis física del activo excluido puede generarse del modelo público, sin sus ejemplos etiquetados. Un único split no demuestra todas las generalizaciones. RAW0002 permanece cerrado.
7. Congelar R11/nominal, sucesor, ExtraTrees causal con ajuste interno y baseline causal simple competente. Misma entrada, catálogo, reloj, prefijo y abstención/fallo; presupuesto de desarrollo declarado. ZIP original permanece comparador histórico y también se puntúa en ventanas comunes, separado del benchmark causal.
8. Evaluar todos los casos previstos: timely family+source, recall, extras/h y FA normal con exposición/disponibilidad, fuente tardía/incorrecta, cierre prematuro/tardío/ausente, severidad oracle-source y end-to-end separados, coste y supports por fuente/padre. No excluir misses/fallos ni condicionar a familia correcta. Intervalos pareados por padres; bootstrap no corrige selección previa.
9. Predefinir victoria: mejora mínima en atribución oportuna y margen de no inferioridad en extras/FA, o utilidad con costes fijados por aplicación. No declarar ganador porque gana alguna de muchas métricas ni ajustar costes mirando RAW0001.

## RAW0001 y hackathon: respuesta explícita

El archivo histórico registra 21 chunks RAW0001, 12 anómalos y ocho localizaciones correctas: 66.67% localización anómala (`R/experiments/E5_VALIDATION_PAPER/R07_HACKATHON_COMPARISON_20261027/REPORT.md:115–119`). Compararlo con 53/54 o 144/144 simulados es una resta sin significado. Una nueva ejecución común sobre RAW0001 seguiría siendo comparación retrospectiva de un registro usado para calibración, no score oficial ni validación externa.

Un contraste concreto requeriría ambos sistemas congelados, mismas observaciones, ontología/corrientes verificadas, mismos targets y tiempos emitidos. Si R11 no soporta falla/generación/integridad, deben aparecer como fuera de catálogo/abstención o limitarse explícitamente el análisis al subconjunto común; no eliminarlos para proclamar victoria global. F01 mantiene abiertos esos operadores y fidelidad multicanal (`START_HERE.md:67`). Más entrenamiento no crea automáticamente un operador físico faltante.

La evidencia sostiene ventajas de implementaciones físicas en ensayos específicos de carga/línea simulados y retrospectivos. No sostiene victoria RAW0001/hackathon. Los siguientes pasos útiles son linaje global, benchmark agrupado con desarrollo justo y auditoría sucesora de las dos semánticas de evaluación, preservando C01 y todos los candidatos.
