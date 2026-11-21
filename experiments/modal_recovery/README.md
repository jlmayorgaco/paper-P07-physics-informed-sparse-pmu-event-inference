# ¿Qué parte de la oscilación del fasor ayuda a diagnosticar un segundo evento?

Las ocho PMU entregan la magnitud de la tensión y de la corriente de la rama instrumentada a 30 reportes/s. La señal estudiada es la modulación lenta del fasor fundamental. Para cada carga, línea y tamaño se simula su respuesta temporal y se proyecta sobre la misma base que los datos. La covarianza de las recuperaciones sin un segundo evento permite ponderar conjuntamente PMU y coordenadas temporales. La base sinusoidal emplea 1,0743 Hz, seleccionado a partir del jacobiano de las ecuaciones de máquina. La estimación de THD de la corriente requeriría formas de onda o fasores armónicos.

## Primera prueba

Se suministró el instante del primer despeje. Cada variante buscó el segundo evento y decidió al primer cruce de su propio umbral. Los umbrales se ajustaron al mismo presupuesto. Cada caso positivo tenía un gemelo con el mismo primer evento y el mismo ruido que seguía recuperándose. Las ventanas solo usaron los reportes disponibles al publicar. [Protocolo](PROTOCOL.md) · [Predicciones selladas](results/predictions.json) · [Resultados](results/scores.json)

| Base temporal | Detección a tiempo / 96 | Familia / 96 | Activo / 96 | Alarmas en 96 gemelos sin segundo evento |
|---|---:|---:|---:|---:|
| Media | 70 | 46 | 33 | 10 |
| Media, seno y coseno | 81 | 51 | 33 | 4 |
| Media, pendiente y curvatura | 78 | 50 | 33 | 6 |

Frente a la media, el estimador sinusoidal ganó once detecciones a tiempo sin perder ninguna (*p* exacta bilateral = 0,00098, desenlace secundario). Ganó ocho clasificaciones correctas y perdió tres (*p* = 0,227, desenlace principal). Dio 35/48 familias de carga correctas y 16/48 de línea. En 30 aperturas publicó «carga» durante el evento, con una mediana de 0,08 s desde el inicio. Este análisis posterior motivó una nueva prueba. Las tres variantes dieron cero alarmas en las mismas 5,86 horas evaluables de reposo (límite Poisson unilateral del 95 % de 0,51/h).

## Confirmación en otras 96 historias y sus gemelos

Todas las variantes recibieron la primera alarma del estimador sinusoidal al umbral fijado en la prueba anterior. Cada clasificador posterior recibió 29 reportes adicionales (0,967 s). Para contemplar el retraso del disparo, una variante marginaliza las respuestas de 30 posibles instantes de inicio en la misma verosimilitud. El caso de inicio fijo permite medir por separado el efecto de contemplar un inicio anterior a la alarma. [Protocolo de confirmación](fixed_lag/PROTOCOL.md) · [Predicciones selladas](fixed_lag/results/predictions.json) · [Resultados](fixed_lag/results/scores.json)

| Decisión sobre los mismos disparos | Familia / 96 | Activo / 96 |
|---|---:|---:|
| Sinusoidal, inmediata | 48 | 25 |
| Sinusoidal, 29 reportes adicionales, inicio fijado en la alarma | 81 | 64 |
| Sinusoidal, 29 reportes adicionales, inicio marginalizado | 83 | 73 |
| Media, mismo plazo e inicio marginalizado | 83 | 73 |
| Cuadrática, mismo plazo e inicio marginalizado | 84 | 74 |

El disparo común captó 84/96 segundos eventos a tiempo. Seis cargas quedaron sin alarma y el disparo se anticipó a seis segundos eventos (cuatro líneas y dos cargas). En 8/96 gemelos de recuperación produjo una alarma falsa, por encima del presupuesto del 5 %. Los cinco diagnósticos de la tabla comparten esas alarmas. El estimador modal marginalizado acertó 40 cargas y 43 líneas. El cambio conjunto de plazo y tratamiento del inicio ganó 35 familias frente a la decisión inmediata sin perder ninguna (*p* exacta = 5,82 × 10⁻¹¹). Al mismo plazo, la comparación de familia entre la base modal y cada uno de los otros dos estimadores marginalizados dio *p* ajustada por Holm = 1. Las cifras son condicionales al primer despeje suministrado y al modelo conocido de la segunda planta. No establecen el rendimiento del filtro continuo del artículo ni el de otras ubicaciones de PMU.

## Reproducción

El registro anterior al primer sorteo es `6107661` y las predicciones se fijaron en `8342946`. La confirmación se registró en `fc0365c` y sus predicciones en `0abf237`. Ninguna etiqueta de los segundos eventos entra en el código de decisión. La evaluación incluye todos los eventos programados, también los omitidos, anticipados y tardíos.

`python experiments/modal_recovery/report.py` verifica los sellos de etiquetas y predicciones y vuelve a contar las tablas de ambas pruebas con la biblioteca estándar de Python. Con las observaciones locales de ambas cohortes, `python experiments/modal_recovery/check_pairs.py` comprueba sus hashes y la igualdad exacta de los 192 prefijos contrafactuales, y repite la inferencia en 16 registros repartidos entre ambas cohortes.

Para regenerar datos y pesos en una copia de trabajo nueva, instale NumPy, SciPy, scikit-learn, joblib y las dependencias del simulador SGSMA y defina `P07_SCIENCE_ARCHIVE` como su raíz. Use directorios de salida nuevos para preservar los archivos publicados. Los datos de ajuste y calibración y el catálogo físico se generan con `data.py fit` y `data.py cal`. Siguen `study.py fit`, `data.py test`, `study.py predict` y `study.py score`. El estudio posterior usa `fixed_lag/trial.py fit`, `generate`, `predict` y `score` en ese orden. Las observaciones grandes quedan bajo `tmp/`. Los resultados pequeños, modelos y sellos forman parte del repositorio.
