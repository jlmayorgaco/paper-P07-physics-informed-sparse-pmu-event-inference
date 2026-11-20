# Por qué se repiten los avisos después de una segunda perturbación

Las siete trayectorias que originaron las 23 alarmas extra del monitor congelado en `d5b8f88` volvieron a producir extras al quitar el ruido instrumental. Una prueba de factibilidad con 32 pares nuevos favoreció continuar la dinámica de la red desde el estado previo a la segunda perturbación. Esta prueba proporcionó al predictor la historia física verdadera de las primeras dos intervenciones. La versión desplegable todavía debe inferir esa historia de las PMU. [Prueba ciega original](../recovery_state/README.md)

## Qué pasa al quitar el ruido

Se regeneraron los 480 registros originales y se verificaron las huellas de sus señales y etiquetas. En las 128 ramas con dos eventos se repitió el monitor congelado con idénticos tiempos, activos, intensidades, inercias y amortiguamientos. La segunda corrida anuló únicamente el ruido de medición. El mismo umbral y la misma escala de ruido se mantuvieron en el monitor. Este diseño comprueba si las alarmas persisten sin ruido. El detector sigue calibrado para sensores ruidosos, por lo que la diferencia de conteos entre regímenes no estima cuánto aportaría instalar mejores sensores.

| Señales que recibe el mismo monitor | Registros con dos eventos | Registros con extras | Extras totales | Familia y activo correctos en el segundo evento |
|---|---:|---:|---:|---:|
| Originales | 128 | 7 | 23 | 115/128 |
| Mismas trayectorias sin ruido instrumental | 128 | 12 | 33 | 121/128 |

Los siete casos inicialmente problemáticos produjeron 27 extras sin ruido. También hubo extras en las 28 repeticiones correspondientes a cuatro sorteos de ruido adicionales por caso. Los 32 pulsos de generación y carga posteriores a una falla o apertura se diagnosticaron correctamente con y sin ruido instrumental.

En dos registros, la segunda falla en BUS31 se localizó correctamente. Los 13 avisos posteriores llegaron entre 5,83 y 14,03 s después de su despeje. El banco de continuación trunca la firma del segundo episodio a los 144 reportes (4,8 s desde el inicio). En otros cinco registros hubo diez extras durante o después de una segunda apertura. En cuatro de ellos la publicación inicial de la segunda línea indicaba una rama equivocada. Una corrección de activo puede por tanto competir con el anuncio de un evento adicional. [Datos por registro](results.json) · [Observador congelado](../recovery_state/recovery.py) · [Banco temporal](../graph_intervention/operators.py)

Se contrastó además la predicción del monitor con la del simulador usando los parámetros e intervenciones verdaderos. En las 12 muestras previas a la primera alarma extra, incluida la muestra del aviso, el RMS de las 31 innovaciones estandarizadas bajo el monitor estaba entre 6,14 y 205,28. Con la trayectoria conjunta verdadera estuvo entre 0,92 y 1,05. Se tomó el residuo del monitor antes de aplicar la corrección autorregresiva específica de la familia. Esta comparación retrospectiva usa parámetros conocidos y el mismo simulador que generó los datos.

## ¿Se puede distinguir una tercera intervención durante la recuperación?

Se simularon 32 pares nuevos de desarrollo con activos del catálogo de entrenamiento y sin ajuste de parámetros. Los dos primeros eventos fueron combinaciones de falla de barra y apertura de línea. Cada par comparte estos eventos, parámetros mecánicos, ruido y prefijo de PMU. La rama control termina recuperándose durante el resto del registro. La otra recibe un tercer pulso de generación o aumento de carga, 16 de cada familia. El intervalo posterior al segundo despeje alterna entre 30–60 y 155–185 reportes. La verificación compara los prefijos de las señales y de las alarmas.

Los tres predictores conocen los dos primeros activos, familias, inicios, despejes, intensidades y multiplicadores de inercia y amortiguamiento. La búsqueda de eventos adicionales se inicia tres reportes después del segundo inicio. Se usa el mismo banco de candidatos a un evento nuevo, la misma razón de evidencia, el mismo umbral de recuperación de 100 y el plazo de 1,5 s. Ningún brazo recibe información del tercer evento durante la búsqueda. La variable experimental es el pronóstico PMU bajo la hipótesis de que solo ocurrieron las dos perturbaciones conocidas.

| Pronóstico de recuperación | Extras en 32 controles | Extras en 32 ramas con tercer evento | Tercer evento, familia y activo exactos |
|---|---:|---:|---:|
| Suma de respuestas aisladas, segunda truncada a 4,8 s | 29 | 25 | 16/32 |
| Suma de respuestas aisladas, ambas hasta el final | 20 | 19 | 17/32 |
| Dos perturbaciones sucesivas sobre una trayectoria dinámica continua | 0 | 0 | 29/32 |

La trayectoria conjunta dio 14/16 en generación y 15/16 en carga. El RMS mediano de las innovaciones en los controles pasó de 6,21 a 4,78 al extender las respuestas aisladas y a 0,96 al integrar ambas conmutaciones sobre la misma trayectoria. El resultado cuantifica el valor de conocer el estado arrastrado entre intervenciones dentro de una planta especificada correctamente. El experimento no mide el rendimiento ciego de un estimador que deba aprender ese estado. [Resultados por par, incluidos los tres fallos](feasibility.json)

## Cambio a probar en el estimador

1. Ante una segunda intervención, heredar los ángulos y velocidades de rotor, los estados del regulador y su incertidumbre. Recalcular las variables algebraicas de tensión y corriente con la topología de cada hipótesis. Mantener la trayectoria durante el retorno mientras siga siendo relevante para las PMU.
2. Permitir varias explicaciones para el episodio reciente, incluidas ramas competidoras y tiempos de despeje alternativos. Una revisión del diagnóstico conserva la identidad del episodio. Una nueva alarma requiere que un evento adicional explique mejor reportes posteriores al instante usado para proponerlo. La comparación debe integrar la incertidumbre de ambas hipótesis con el mismo modelo de ruido.
3. Calibrar esa decisión con controles de dos perturbaciones seguidas sin intervención adicional y con sus gemelos con tercer evento real. Variar el punto de operación, la intensidad, la proximidad temporal y el error de parámetros. Incluir también secuencias de carga o generación seguidas de un nuevo pulso de generación, origen de las seis omisiones previas.
4. Congelar el nuevo estimador y exigir en otro examen los tres indicadores sobre episodios únicos, el acierto del subgrupo de segundos eventos, el plazo de 1,5 s y extras totales frente a ambos árboles. Publicar por separado extras en reposo, durante eventos y durante recuperación. Para extrapolar a otra red o a PMU de campo se necesita validación fuera de esta familia de simulador.

Para reproducir, definir `P07_SCIENCE_ARCHIVE` y usar `OPENBLAS_NUM_THREADS=1`. Ejecutar `python experiments/recovery_diagnostics/diagnose.py` y `python experiments/recovery_diagnostics/feasibility.py` desde la raíz. El primero regenera las señales del examen anterior y verifica sus huellas. El segundo genera las señales desde el diseño de desarrollo.
