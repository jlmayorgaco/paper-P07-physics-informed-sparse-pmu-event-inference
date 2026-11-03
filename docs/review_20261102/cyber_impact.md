# Revisión independiente: integridad/cyber, aplicabilidad y claridad

**Revisor 3 — perspectiva de despliegue y usuario técnico.** 2 de noviembre de 2026.
**Documento revisado:** `main.pdf` de 14 páginas y `supplement.pdf` de 11 páginas,
leídos completos; fuentes activas, código de composición e integridad y evidencia
S01 verificada. No consulté informes de otros revisores. No modifiqué manuscrito,
métodos, resultados ni baselines. No abrí RAW0002.

## Dictamen

**No está listo para envío en su estado actual. Revisión mayor, con correcciones
editoriales concretas y una decisión explícita de alcance.** La implementación
física es real y el manuscrito ya es más honesto que una simple acumulación de
etiquetas «physics-informed/Bayesian/tensor». Sin embargo, no satisface la
aspiración amplia de un estimador físico-cyber unificado validado en RAW0001.
Sí puede sostener un artículo más acotado sobre atribución causal carga/línea
con PMU dispersas, comparaciones dentro del simulador y fallos de transferencia.
Para ese alcance no hace falta simular que la parte cyber conjunta ya funciona.

No prometo que coautores o revisores carecerán de objeciones. El objetivo factible
es que cada afirmación sea precisa, comprobable y proporcionada a la evidencia.

## Qué sí es real

1. **Physics-informed sustantivo.** El predictor emplea DAE, reducción de Schur,
   Ybus, corrientes terminales orientadas, operadores de carga/línea y memoria
   instrumental. Se predice la respuesta remota de causas candidatas; no se trata
   solo de nombrar features eléctricas. El artículo distingue esas ecuaciones del
   componente estadístico AR de discrepancia (sección IV, ecuaciones 5–8).
2. **Cálculo bayesiano local real.** El método integra intensidad con distribución
   gaussiana truncada, emplea densidades predictivas y pondera hipótesis. Describe
   honestamente filtros locales, sustitución de contexto, podado y covarianzas
   compartidas. Esto respalda «inferencia bayesiana aproximada», no optimalidad
   global ni probabilidades de eventos calibradas.
3. **Pseudocódigo y diagrama existen.** Algorithm 1 está en sección IV-G y Figura 1
   muestra 4 regiones y 19 bloques. El orden predicción→propuesta→replay→evidencia→
   actualización→publicación coincide a nivel de interfaz con lo documentado.
4. **Integridad implementada.** `runtime/integrity.py` y `runtime/cyber_replay.py`
   implementan máscaras observadas y publicación de missing; heredan la diagnosis
   de bad data del ZIP. `system_replay.py` compone esos resultados sin inventar
   restauraciones ni reabrir una pérdida ya terminada.
5. **Evidencia reproducible de composición.** Comprobé todos los hashes de
   `generated/frozen/submission_s01_system_20261031/MANIFEST.json`. La validación
   ejecutada conserva 180 ventanas, 206 mensajes, 161379 reportes y sus componentes.
   Es una comprobación de equivalencia de datos/tiempos, no una nueva exactitud.

## Hallazgos prioritarios

### C1 — La parte física/cyber conjunta solicitada NO está implementada/validada

**Severidad: crítica si se pretende anunciar una solución físico-cyber general;
mayor de delimitación para el artículo carga/línea.**

El plan de composición declara literalmente que el filtro físico está no
 disponible en RAW bajo su contrato de arranque. El código exporta
`physical_filter.available=False`, `component_inference_reexecuted=False`,
`malicious_intent_inferred=False` y `persistent_corruption_inferred=False`.
La ruta denominada híbrida es ZIP + un localizador ExtraTrees segmentado, no el
banco físico bayesiano funcionando junto a un estimador de ataques.

Evidencia:
- `generated/frozen/submission_s01_system_20261031/plan.json`;
- `generated/frozen/submission_s01_system_20261031/runtime.py`, funciones
  `completed_window`, `availability_message`, `run`;
- `supplement/appendix_submission_contract.tex:20–56`;
- `supplement/appendix_grouped_learning.tex:77–112`.

**Corrección mínima:** una tabla visible de alcance: pérdida de datos = máscara
observada causal; corrupción = clasificador heredado por ventanas; composición =
publicación de componentes; inferencia física ante corrupción/missing = no
validada; atribución de ataque/intención = no realizada. Si se mantiene el alcance
carga/línea, estas capacidades son contexto/suplemento. Si cyber es contribución
central, falta un experimento adversarial conjunto y un modelo de amenaza,
incluyendo pérdidas benignas, corrupción que imite un evento, concurrencia y
fuentes no medidas. No se debe resolver esta ausencia cambiando el nombre de
«bad data» a «cyberattack».

### C2 — Se promete un suplemento de resultados que el PDF NO contiene

**Severidad: mayor, bloquea envío; reparación editorial/artifactual inmediata.**

`sections/08c_c01_confirmatory.tex:68–69` afirma que tablas estratificadas, fallos,
restauraciones y censuras están en el suplemento. Sin embargo,
`supplement/c01_narrative_details.tex` no existe y `supplement.tex:64` lo incluye
con `IfFileExists`, de modo que la compilación omite el contenido en silencio.
Leí las 11 páginas: presentan contratos de C01, pero no esas tablas de resultados.

**Corrección:** importar los artefactos congelados prometidos y usar inclusión
obligatoria; verificar en PDF las tablas, denominadores y exposición. Una
alternativa es indicar su destino real en el paquete reproducible, pero eso no
satisface la promesa actual de un suplemento autocontenido.

### C3 — Confusión entre éxito de interfaz y eficacia cyber

**Severidad: mayor para claridad/evidencia.**

La cifra 161379 reportes expresa equivalencia de reconstrucción del estado de
 disponibilidad. No significa 161379 ataques detectados. La validación archivada
contiene resultados útiles, bastante más modestos:

| Objetivo y unidad | Resultado archivado | Interpretación |
|---|---:|---|
| Missing, ventanas positivas | 14/14; cero FP | La máscara observada reconoce disponibilidad |
| Corrupt, familia+PMU, ventanas positivas | 1/2; 2 FP y 1 FN | Evidencia muy pequeña y no perfecta de bad data |
| Primer aviso y PMU, intervalos missing | 4/4 | Mensaje en el reporte recibido; no latencia de red/cómputo cero |
| Familia+fuente física, RAW, ventanas positivas | ZIP 1/24; híbrido aprendido 2/24 | Un cambio favorable, no transferencia amplia |

Fuente: `generated/frozen/submission_s01_system_20261031/validation.json`, campos
`existing_interval_integrity_metrics`, `existing_missing_latency_metrics` y
`existing_physical_metrics`. El documento actual es cauteloso, pero el resumen de
composición en el main deja fuera el denominador y fallo de corrupción.

**Corrección mínima:** incluir una pequeña tabla con esos resultados y contratos
en el suplemento; conservar en el main solo la síntesis necesaria. No atribuir a
Bayes ni al tensor los resultados del clasificador heredado.

### C4 — No está validado «entrenar SIM y funcionar en RAW» para el banco físico

**Severidad: mayor científica si se desea esa afirmación.**

La evidencia más directa es
`SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/run/raw_physical_prefix/RESULT.json`:
`available=false`, `reports_used=300`, `prefix_selected=false`,
`thresholds_changed=false`, y error
`Noise estimate outside support: rocof 0.0009971766263150836`.

El banco se abstiene por fuera del soporte de ruido; no produce una validación
física completa en RAW0001. Además, RAW0001 ya informó calibración retrospectiva
 y no es un test externo independiente. El reentrenamiento supervisado S01 tiene
partición agrupada aproximada 70/30 de desarrollo/reservado (31 fit, 8 validación,
17 reservado sobre 56 grupos), pero usa campañas previamente vistas y es una ruta
distinta de los ET congelados en C01. No hay razón científica para sustituir esto
por un 70/30 aleatorio por muestra.

**Corrección editorial inmediata:** `sections/article_interpretation.tex:54`
dice que fallan «noise/stationarity assumptions». El RESULT revisado solo
certifica el rechazo por escala ROCOF. Escribir eso exactamente, salvo que exista
otra prueba separada de estacionariedad. Mantener explícita la diferencia entre
los modelos C01 y el modelo de partición agrupada S01.

**Evidencia adicional si se exige transferencia:** otra evaluación prespecificada
con un productor/registro no usado para calibrar, y un contrato instrumental
verificado. Eso no se obtiene retocando C01 ni desplazando el prefijo de RAW.

### C5 — La explicación principal aún depende demasiado de reglas «archivadas»

**Severidad: mayor de reproducibilidad comprensible.**

Algorithm 1 describe la secuencia pero no define suficientemente qué es
«source-qualified support» ni las reglas de confirmación/reemplazo. Main
`article_method.tex:191–196` remite a reglas archivadas; suplemento A-D da
hazards, intensidad, beam y clocks, pero vuelve a remitir la confirmación de
fuente al archivo. Un lector no puede reproducir la decisión fuente/episodio
solo con esos documentos.

**Corrección sin cambiar el método:** agregar nombres matemáticos y definición
exacta de las funciones de admisión, confirmación de fuente, reemplazo de
 episodio y salida OFF; una tabla de parámetros y pseudocódigo con bucles y
condiciones. Diferenciar el conjunto de historias evaluadas de las 18 celdas
agregadas de M. El procedimiento completo debe ser ejecutable en la cabeza del
lector, aunque las optimizaciones queden en código.

### C6 — Novedad y utilidad no se deducen del nombre tensorial/Bayes

**Severidad: mayor respecto de la aspiración del usuario.**

Las respuestas D/Q/Qij sí tienen contenido físico y una mejora de aproximación
demostrada en un ensayo separado. En el estimador continuo, M/Gamma/Delta M son
resúmenes útiles de la distribución de historias. Delta M es identidad contable
 y no una ley dinámica adicional derivada de Kirchhoff. No hay evidencia de que
el almacenamiento tensorial produzca la mejora final de clasificación.

La mayor virtud del manuscrito actual es reconocer esto. Su riesgo es reunir
reconstrucción, features, tensor batch, inferencia continua y cyber en una
«historia de desarrollo» más que una contribución experimental única. El lector
necesita saber qué bloque usa el algoritmo central y cuál solo informa su diseño.

**Corrección:** una matriz método↔componentes↔experimento y una tesis única:
comparar explicaciones físicas continuas bajo PMU dispersas, con intensidad
integrada y memoria de recuperación, y mostrar su exactitud/coste de alarmas
frente a comparadores. Bayes es sustantivo para la evidencia; su necesidad
empírica exclusiva no está aislada. Si esa necesidad se quiere como claim,
falta ablación con idéntico predictor, propuestas y publicación.

## Claridad y presentación

- El problema, la Figura 1 y el ejemplo temporal ya son útiles; no parecen una
  mera cadena de siglas sin mecanismo.
- El artículo no demuestra tiempo real, protección automática ni calibración de
  incertidumbre. Su uso defendible es diagnóstico offline/experimental y análisis
  de hipótesis, con potencial de monitoreo sujeto a validación de ejecución.
- El texto repite varias veces la lista de cosas que no establece. Conservar una
  tabla de límites y referirla mejoraría la narrativa sin ocultar fallos.
- Frases como «not silently substituted» o «original submission is preserved»
  describen gestión interna, no contenido científico; trasladarlas al registro
  reproducible. Algo similar ocurre con «frozen»/«sealed» repetido fuera del
  protocolo. No es prueba de autoría AI; es una señal de prosa de auditoría.
- `supplement.tex:26` y metadata PDF mantienen el título anterior, incompatible
  con main. Corregir en la misma entrega.
- La arquitectura no contiene cyber: es correcto para el método físico, pero debe
  llamarse explícitamente «physical inference» en todos los textos que la
  referencian. No añadir un bloque cyber como si compartiera posterior y estados.
- Las matrices de confusión existentes son de transferencia histórica, no del
  clasificador causal final. Ese rótulo es correcto. Para afirmar análisis ML
  completo falta identificar claramente partición/modelo para cada matriz,
  métricas por fuente/clase y condiciones, denominadores, abstenciones y demora.
- No es obligatorio entrenar una GNN solo para tener una sigla SOTA. Sí es
  necesario evitar «mejor que ML» y, si la ventaja frente al mejor diagnóstico
  moderno es central, ejecutar un comparador cercano con presupuesto de datos y
  falso-alarmas definido. Chen no cubre cargas ni restauración y falla bajo su
  adaptación actual; no puede sostener ese claim general.

## Secuencia mínima para cerrar, sin crear versiones de estimadores

1. Reparar inclusión real de las tablas C01 en el suplemento y título coherente.
2. Definir en papel las reglas de publicación/fuente y vincular pseudocódigo al
   contrato numérico exacto; no tocar parámetros.
3. Presentar tabla de capacidades y resultados cyber, y diferenciar la ruta de ML
   70/30 retrospectiva de C01; corregir la causa exacta de inadmisión RAW.
4. Comprimir la historia de componentes alrededor de una sola pregunta, con una
   contribución medida sobre el procedimiento completo. Mantener tensor batch y
   cyber como evidencia separada cuando no participan en ese procedimiento.
5. Decidir con coautores si el alcance carga/línea/simulador es suficiente para
   envío. Si quieren claims de ataque conjunto, transferencia real o necesidad
   causal de Bayes/memoria, esos claims requieren pruebas nuevas; no hay reparación
   editorial que los produzca.

**Resumen del revisor:** hay implementación física real, evidencia local bayesiana,
un resultado comparativo fuerte en carga y código de integridad real. No hay aún
un estimador conjunto físico-cyber validado en RAW ni un efecto final aislado del
tensor. El artículo puede ser defendible al acotar esos objetivos y reparar
omisiones concretas; llamarlo perfecto o submit-ready hoy sería prematuro.
