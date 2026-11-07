# Líneas base justas: aprendizaje reentrenado en el SIM del banco (protocolo congelado)

Pregunta: ¿un modelo de aprendizaje entrenado con los datos simulados del propio banco alcanza la atribución del banco dinámico? Mismo evaluador, mismos registros, mismo catálogo de 18 fuentes.

Datos: cohorte simulada de B01. Ajuste con TRAIN (24 registros, 72 eventos), selección de umbral en CAL (24 registros), evaluación una sola vez en TEST (24 registros, 72 eventos). Ningún dato de RAW0001 interviene. El TEST ya fue abierto por otros métodos; aquí cada línea base se ejecuta una vez, con el umbral fijado en CAL antes de mirar el TEST, y el paper lo declara.

Entradas causales por reporte k (30 reportes/s): cambio de la media de las últimas 15 y 45 muestras de los 16 canales fasoriales (8 tensiones, 8 corrientes) respecto de una referencia tomada entre 4 y 1,5 s antes, blanqueado con la desviación del arranque (10 s) del propio registro.
Etiquetas de entrenamiento: fuente verdadera durante 1 s tras el ON; clase «apagado» durante 1 s tras el OFF; «normal» en el resto (submuestreo 10:1).

Modelos:
- ML: ExtraTrees (300 árboles) sobre las características crudas (cambios blanqueados).
- FIS: ExtraTrees sobre características físicas: ganancia de ajuste y amplitud con signo de cada una de las 18 firmas del modelo de red, en las dos ventanas.
- LR: regresión logística multinomial sobre las mismas características físicas.

Episodios: p(evento) = 1 − p(normal) − p(apagado) ≥ τ durante 3 reportes seguidos; el episodio termina tras 15 reportes bajo τ/2. Ubicación: argmax de la probabilidad media de fuente en los 30 primeros reportes del episodio; Top-3 análogo. Familia: la de la fuente predicha.
τ: el menor de {0,05…0,95} con 0 alarmas en los registros normales de CAL; desempate por Top-1 de CAL.
Evaluador: score_sim del banco (ventana de detección [ON−0,1 s, OFF+1 s]).
Se reporta: detectados, familia, Top-1, Top-3, alarmas por hora normal, extras por hora, con intervalos de Wilson. Un resultado en contra no se corrige después.

Enmienda antes de abrir el TEST (6-nov-2026): en el humo sobre CAL el umbral cayó en el borde inferior de la malla; la malla se amplió a 0,05–0,95 para no penalizar a las líneas base, y la regresión logística pasó a 2000 iteraciones. El TEST no se ha leído.
