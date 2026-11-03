# Revisor 1 — metodología, aprendizaje y estadística

Revisión independiente del manuscrito principal de 14 páginas y sus fuentes
activas, suplemento, código de entrenamiento/evaluación y artefactos sellados.
Fecha: 2 noviembre 2026. El manuscrito no fue modificado por este revisor.
No se entrenaron modelos, no se ejecutó inferencia ni se abrió RAW0002.

## Dictamen

**No está listo para envío; revisión mayor.** Los resultados ejecutados son
reales y varios controles son buenos. La evidencia confirma una ventaja del
procedimiento físico completo sobre los dos ExtraTrees congelados en atribución
de cargas del simulador. No identifica qué parte de la ventaja causa Bayes,
memoria o estructura tensorial, ni valida transferencia general a RAW.
El informe actual es honesto en esas limitaciones, pero mezcla varias familias
de estimadores y deja fuera detalles confirmatorios que promete en el suplemento.

## Hallazgos mayores

### M1. El suplemento confirmatorio prometido no se compila porque falta el archivo

`supplement.tex` usa `IfFileExists{supplement/c01_narrative_details.tex}`;
ese archivo no existe. `sections/08c_c01_confirmatory.tex:68` promete tablas
estratificadas, fallos, restauraciones y censuras en el suplemento. El PDF
suplementario contiene sobre todo contrato causal, composición y estudios
secundarios, pero no esa sección C01. Una compilación exitosa no detecta este
tipo de omisión silenciosa.

**Reparación editorial suficiente:** incluir el protocolo congelado y tablas
derivadas de `generated/frozen/c01_20261029/{SUMMARY,RECORDS,EVENTS,
PERSISTENT_FIRST_STOP,PAIRED_INTERVALS,BY_SOURCE,EVALUATION_AUDIT}.csv/json`,
con fracaso cero verificado, denominadores, primeras paradas, exposición y
censura. No recalcular la campaña con reglas nuevas.

### M2. El 70/30 del suplemento es otro modelo; la validación original comparte normales

Los comparadores que realmente corren en C01 provienen de
`experiments/E5_VALIDATION_PAPER/M03_R09_NUISANCE_DEV/ml/`.
`PROTOCOL.json`, `COMPLETE.json`, `TRAINING_TIMING.json` y `run.py:57–67`
identifican SIM14–17 para fitting y SIM18 para validación: **32/8 IDs físicos
locales, 64/16 registros, 78,784 filas de fitting**. No es un split 70/30.
El aproximadamente 70/30 del `supplement/appendix_grouped_learning.tex:5–12`
es un sucesor retrospectivo distinto: 31 grupos fitting, 8 validación y 17 reservados
(90/16/70 registros), no los artefactos evaluados en C01.

Además, el `assert` del entrenamiento original compara `campaña/physical_id`.
Al cruzarlo con el registro posterior de dependencia física
`PAPER_SUBMISSION_S01/protocol/SIM_REGISTRY.json`, resultan 26 grupos globales
de entrenamiento y 8 de validación, con **dos grupos normales compartidos**:
`G_41c4f849ad529a8d66c9`(Z001) y `G_241039bf209bb85b92fe`(Z002).
Esto prueba dependencia en la validación interna original, **no fuga demostrada
del test C01**. Las seis historias con eventos de SIM18 no aparecen en esos
grupos compartidos. El CSV/JSON de evidencia adjunto conserva los hashes.

**Reparación editorial:** tabla de identidad de cada modelo, datos, grupos,
filas, selección y cohortes evaluadas. Reconocer los normales compartidos.
No sustituir el modelo congelado de C01 por el sucesor70/30 ni atribuirle
sus controles. **Experimento futuro, si se exige validación enteramente
independiente para selección:** otro modelo/ensayo predeclarado; no retuning C01.

### M3. La ablación causal central sigue ausente

El método real usa predicción eléctrica y una integral marginal de intensidad.
La integral de `article_method.tex:95–114` tiene contenido estadístico concreto;
M/DeltaM agregan y descomponen pesos. Pero no hay comparación que mantenga
diccionario, estado, propuestas, publisher y presupuesto de alarmas fijos
mientras cambia solo integrar frente a perfilar intensidad, o mantener frente
a eliminar recuperación. Nominal y mezcla también tienen publishers distintos.
El tensor D/Q/Qij de `article_evidence_bridge.tex:62–85` pertenece a otro ensayo;
no forma parte del predictor causal final. Su reducción de error no prueba una
ganancia de detección/clasificación final.

**Reparación editorial:** presentar la contribución del procedimiento completo,
no una ganancia causal atribuida a «Bayes+tensores». **Experimento necesario para
el claim fuerte que solicita el usuario:** al menos una ablación controlada,
predeclarada, sin seleccionar parámetros en C01. Agregar ecuaciones o gráficas
no resuelve por sí solo esa brecha.

### M4. Comparadores útiles, pero cobertura insuficiente para superioridad amplia

ExtraTrees corto y referencia comparten una familia y un corpus limitado.
La debilidad de carga era conocida antes de C01: `ml/SUMMARY.csv` original
reporta **0/72** cargas correctas antes de OFF para BASELINE y **4/72** para
SHORT en validación, con 144 eventos totales. Por tanto el gran gap C01 no puede
atribuirse específicamente a un descubrimiento nuevo de insuficiencia del ML.
La comparación sigue siendo válida para esos procedimientos fijados, pero un
revisor puede objetar que el principal baseline de carga era deliberadamente
débil. Esto no implica mala conducta ni invalida la evaluación congelada.

Chen es un comparador publicado real de primera parada, con hipótesis distintas
y 72/72 normales detenidos. No se han corrido Warner/M3H/GNN bajo el mismo protocolo.
Una GNN no es obligatoria por etiqueta; sí se necesita un competidor adecuado al
claim central, o limitar la conclusión. Los umbrales/publishers diferentes
impiden una conclusión a igual tasa de falsas alarmas.

**Editorial:** informar rendimiento previo del comparador, ventajas y desventajas,
información previa y domain shift. **Nuevo experimento si se mantiene ventaja
metodológica fuerte:** comparador físico cercano o learned robusto con selección
independiente y presupuesto de alarmas comparable, sin adaptar C01.

### M5. Primer acierto de línea no equivale a mantener correctamente el estado

La tabla de primera parada 162/162 para físicos/ET es correcta. Verifiqué en
EVENTS que diagnóstico y alarma asociados coinciden temporalmente en los 162
casos de cada método. Sin embargo, el resumen oculta una distinción valiosa:

| Persistentes, 162 líneas | Extras posteriores | Restauraciones de episodios no emparejados | Abiertos al final | FN por reporte |
|---|---:|---:|---:|---:|
| Banco físico |0|0|162|810|
| Nominal |0|0|162|810|
| ET referencia |164|164|16|335374|
| ET corto |179|178|61|182600|

Fuente: `RECORDS.csv`, agrupación por lane/method. Aquí 162 abiertos al final es
censura física esperada: no hay recierre programado. No es un fallo de cierre.
Las restauraciones citadas son SOLO de episodios no emparejados; no equivalen
a todas las restauraciones físicas falsas. Chen se detiene una vez y no se
evalúa como monitor persistente. Esta tabla sería un **diagnóstico secundario
descriptivo** sobre artefactos sellados, sin cambiar el endpoint confirmatorio.
Muestra una ventaja útil adicional del procedimiento físico frente a ET y evita
reducir la historia de líneas a que todos obtuvieron162/162.

### M5b. El gap final es cobertura oportuna, no una confusión entre familias

El diagnóstico post hoc `generated/review_diagnostics_20261102/family_confusion.csv`
separa ausencia de diagnóstico antes de OFF de una familia incorrecta. En las
cuatro rutas, todas las decisiones emparejadas emitidas antes de OFF tienen
familia y fuente correctas. El banco físico pierde 2 cargas y 2 líneas; ET
referencia pierde 309 cargas y 9 líneas; ET corto pierde 294 cargas y 2 líneas.
Por tanto la ventaja principal es **obtener diagnóstico oportuno en más eventos**,
no una mejora demostrada de exactitud condicional una vez que ambos deciden.
Las extras fuera del emparejamiento permanecen separadas y no desaparecen.
Esto es diagnóstico descriptivo nuevo de predicciones congeladas, no otro
endpoint confirmatorio ni un ajuste del método.

### M6. No existe aún el protocolo «70/30 SIM y examen RAW independiente»

RAW0001 ya informó al simulador y fue explorado repetidamente; no puede convertirse
retroactivamente en un test independiente. El replay retrospectivo sigue siendo
útil. El híbrido aprendido fuente-only mejora1/24 a 2/24; el filtro físico no supera
las condiciones de arranque sobre ese registro. La entrega anterior con 21 contextos
tiene calendario incompatible con las anotaciones recuperadas; esos antiguos
scores no son una comparación reproducida. Todo ello está reconocido en
`supplement/appendix_submission_contract.tex` y `appendix_grouped_learning.tex`.

**Editorial:** diagrama de datos que separe SIM de fitting, validación interna,
C01 y RAW retrospectivo, y flecha histórica RAW→calibración del simulador.
**Exigencia de evidencia:** para transferencia independiente hace falta otra
fuente/registro no usado; no se solicita ni se abre RAW0002 en esta revisión.

### M7. Resultados de componentes heterogéneos requieren un registro legible

Figura5 combina 100 trayectorias de reconstrucción, 7,915 muestras/semilla de un
ExtraTrees 136–448 features y 32 respuestas de dos cargas. Figura6 compara otro
estimador físico temprano con el ZIP de 45,162 features. La tabla Bayes usa
onset/familia/contexto suministrados y el prior efectivo de una implementación
con normalizador histórico distinto. Todo está calificado, pero falta una
tabla simple que permita saber a qué algoritmo y cohorte pertenece cada figura.
No se deben construir intervalos tipo binomial con miles de muestras/replays
como ensayos independientes. El artículo hace bien en evitarlo en C01.

**Editorial:** clasificación de evidencias y filas por cohorte/algoritmo/inputs
oráculo/unidad/resultado. Mantener la limitación del prior del archivo histórico;
no permitir que el 100% de ese ensayo respalde calibración o novedad causal.

## Puntos correctos y aprovechables

- C01 fija semillas, métodos y métricas antes de las observaciones de test;
  `EVALUATION_AUDIT.json` conserva342 registros por método, cero rechazos y cero
  fallos, además de predicciones selladas antes de verdad.
- La unidad de remuestreo de los intervalos es el padre físico; 648 son 108
  intervenciones repetidas bajo 6 condiciones. No se publican intervalos de
  648 ensayos independientes.
- Se conserva la desventaja de 72 extras físicos frente 29/16 ET y la ausencia de
  ventaja universal de latencia.
- El manuscrito diferencia integral exacta local, plug-in del contexto,
  covarianzas compartidas, pruning y posterior aproximado. No promete calibración.
- Las matrices de confusión históricas son matrices reales, no reconstruidas
  desde un porcentaje. No son las matrices del estimador causal final.
- El algoritmo por reporte y el diagrama existen. La secuencia es clara;
  para reproducibilidad, falta cerrar la tabla de configuración y publishers.
- Hay implementación cyber/integridad heredada con estados de disponibilidad
  y composición comprobada, pero no un detector bayesiano físico-cyber nuevo
  ni validación de ataque malicioso.

## Respuestas al usuario

| Pregunta | Respuesta verificable |
|---|---|
| ¿Bayes y física son reales? | Sí: operadores DAE e integral de intensidad. No hay prueba de optimalidad global ni calibración completa. |
| ¿El tensor es necesario? | D/Q/Qij mejora ajuste local en su ensayo; M es una representación de masas. No está aislado su beneficio final. |
| ¿ML completo con 70/30? | Hay un sucesor agrupado 70/30 separado. Los ET de C01 usan otro split con normales dependientes en validación. Falta explicitarlo. |
| ¿Matrices de confusión? | Sí históricas; faltan diagnósticos comparables del algoritmo causal final en el artículo. |
| ¿Cyber? | Sí disponibilidad/bad-data heredado y composición; no validación conjunta física-cyber causal con PMU perdido. |
| ¿Otros métodos? | Dos ET y Chen elegible. GLR secundario. No ejecución comparable Warner/GNN. |
| ¿Pseudocódigo? | Sí algoritmo 1, más derivación en suplemento. Faltan detalles C01 prometidos por include ausente. |
| ¿Submit-ready? | No. Puede ser un buen borrador científico con contribución acotada; necesita integración completa y decisión explícita sobre el claim/ablación. |

## Cierre mínimo sin nuevas versiones de detector

1. Incorporar tablas confirmatorias faltantes y separar mantenimiento de primera parada.
2. Declarar identidad y split real de cada modelo; normales compartidos del ET original.
3. Mostrar alcance de cyber y RAW sin llamarlos validación conjunta/externa.
4. Completar mapa algoritmo–cohorte–figura, configuración, runtime y artefactos reproducibles.
5. Elegir entre claim del procedimiento completo con ventajas/costes, o una campaña
   adicional congelada de ablación/comparador para el claim fuerte de mecanismo.

No he encontrado evidencia que permita prometer que un revisor no objetará.
Tampoco corresponde calificar el trabajo como ficticio: la brecha principal es
la atribución causal de la mejora, la cobertura de comparadores y la integración
de evidencia, no la inexistencia del código o de los resultados.
