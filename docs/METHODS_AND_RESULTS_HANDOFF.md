# Métodos y resultados entregados con P07

## Lectura en diez minutos

1. [Artículo compilado](../output/pdf/P07_Event_Attribution_Article.pdf): pregunta, algoritmo, comparación y límites.
2. [Comparación de rutas](HACKATHON_TO_C01_METHOD_TRACE.md): qué es la entrega original, qué es el ExtraTrees causal y qué es el banco físico.
3. [Resumen confirmatorio](c01-confirmatory-results.md): denominadores, estratos, fallos, falsas alarmas, demoras y censuras.
4. [Suplemento](../output/pdf/P07_Event_Attribution_Supplement.pdf): protocolo y detalles matemáticos.

## Código que produjo cada ruta

La raíz hermana es `../SGSMA26-Physics-Informed-AD/`. La entrega original de la hackathon está preservada en `experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/`; su entrada es `main.py` y su descripción ejecutable es `MODEL.md`. No fue el modelo ejecutado en C01.

El comparador causal congelado está en `experiments/E5_VALIDATION_PAPER/M03_R09_NUISANCE_DEV/ml/`: `causal_features.py` y `run.py` definen features y ajuste; `infer.py` carga los árboles para una nueva secuencia. El método físico congelado está en `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/`; `physics/` construye operadores desde la DAE y `observer/` implementa historias y decisiones. El código de la campaña que ejecutó las rutas y el evaluador está en `experiments/PAPER_CONFIRMATORY_C01/execution/`.

**No se debe volver a ejecutar el entrenamiento o la campaña para obtener las cifras del artículo.** Los resultados de C01 fueron sellados antes de esta revisión editorial. El paquete incluye el manifiesto y tablas importadas bajo `generated/frozen/c01_20261029/`; el repositorio SGSMA conserva predicciones, entradas, logs, hashes y fuente de cada método.

## Resultado que se puede citar

En 108 intervenciones continuas de 18 padres físicos, reproducidas en tres condiciones R/X y dos niveles de ruido, el banco físico atribuyó correctamente familia y fuente antes de OFF en 644/648 casos y produjo 72 alarmas extra. El ExtraTrees causal de referencia logró 330/648 con 29 extras; su variante corta, 352/648 con 16. La diferencia se concentra en cargas: 322/324 frente a 15/324 y 30/324. En líneas: 322/324 frente a 315/324 y 322/324. Bajo R/X fuera del banco el método físico elevó las extras a 68. Las 648 realizaciones son correlacionadas; el artículo informa intervalos por padre y conserva las pérdidas.

La comparación no prueba una mejora de la puntuación oficial de la hackathon ni superioridad a igual tasa de falsas alarmas. El simulador y el predictor físico comparten familia de ecuaciones y mapa PMU; no hay validación externa con un productor distinto. Esta es la frontera de la afirmación científica actual.
