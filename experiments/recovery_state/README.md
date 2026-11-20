# Recuperación dinámica de MET_BAYES_GRAFO

En la prueba ciega, estimar la recuperación resolvió los 32 pulsos de generación y aumentos de carga que siguieron a una falla o apertura. El nuevo grafo acertó los 32 activos, frente a 18 con el grafo anterior. Superó 0,96 en las tres estimaciones puntuales primarias. El requisito conjunto quedó incumplido porque emitió 23 alarmas extra, frente a 3 del árbol histórico y 0 de la réplica. El método, el umbral y el diseño quedaron congelados en `d5b8f88`, y las predicciones se sellaron en `5014fe2` antes de abrir las etiquetas. [Protocolo](PROTOCOL.md) · [Huellas y activos reservados](results/freeze.json)

## Cuatro métodos sobre las mismas PMU

Se simularon 480 registros de 24 s con 416 episodios, 104 por familia. Nueve barras y ocho líneas quedaron fuera del entrenamiento y de desarrollo del grafo y de la réplica de los árboles. El árbol histórico conservó el entrenamiento original, que incluía esos activos. Todos los resultados cuentan las omisiones y exigen publicación en 1,5 s.

| Método | Macro-F1 | Familia | Activo exacto | Familia y activo en el segundo evento | Extras totales |
|---|---:|---:|---:|---:|---:|
| MET_BAYES_GRAFO con recuperación ajustada | 0,9663 | 410/416 | 403/416 | 115/128 | 23 |
| Grafo anterior, recalibrado sobre el mismo entrenamiento | 0,9667 | 396/416 | 393/416 | 105/128 | 6 |
| MET_PMU_FIRMAS_ETREE histórico | 0,9293 | 369/416 | 361/416 | 76/128 | 3 |
| MET_PMU_FIRMAS_ETREE reentrenado sin los activos reservados | 0,8925 | 349/416 | 314/416 | 62/128 | 0 |

Los cuatro métodos emitieron cero alarmas en los 192 registros totalmente normales, que aportaron 73,6 minutos de vigilancia después de la inicialización. La mediana del tiempo hasta el diagnóstico del nuevo grafo fue de 0,10 s entre episodios detectados. En el remuestreo por pares, el IC del 95 % fue 0,9412–0,9865 para macro-F1, 0,9733–0,9954 para familia y 0,9513–0,9842 para ubicación. Frente al grafo anterior se ganaron 2,40 puntos porcentuales de ubicación (IC de +0,48 a +4,46) y se añadieron 17 alarmas extra (IC de +2 a +38). [Puntuaciones, matriz de confusión e intervalos pareados](results/scores.json)

Cada uno de los 128 pares comparte un primer evento y se divide en dos futuros. El denominador primario cuenta ese inicio en ambas ramas. Al conservar solo la rama con intervención de cada par, los 32 registros simples independientes y los 192 normales, quedan 288 episodios distintos. En este análisis de sensibilidad el grafo nuevo obtiene **0,9520 de macro-F1, 282/288 familias (97,92 %), 275/288 activos (95,49 %) y 23 extras**. En las mismas ramas, el grafo anterior obtiene 0,9503, 268/288, 265/288 y 6 extras. La sensibilidad depende de la proporción de segundos eventos en la población que se quiera diagnosticar.

## Qué cambió y dónde falla

El monitor ajusta a las PMU ya recibidas una trayectoria de retorno al régimen normal. Usa el modelo eléctrico del activo declarado y estima la inercia y el amortiguamiento efectivos para ese registro. En una falla ajusta también su intensidad. El siguiente aviso depende de cuánta evidencia aporta un evento nuevo por encima de esa recuperación prevista. Un ajuste robusto local y la propagación aproximada de su incertidumbre mantienen la decisión causal. [Observador](recovery.py) · [Configuraciones de desarrollo](results/development.json)

| Segundo evento después de falla o apertura | Casos | Grafo nuevo | Grafo anterior | Árbol histórico | Árbol reentrenado |
|---|---:|---:|---:|---:|---:|
| Pulso de generación, familia y activo correctos | 16 | 16 | 3 | 1 | 0 |
| Aumento de carga, familia y activo correctos | 16 | 16 | 15 | 1 | 0 |

El nuevo grafo tampoco generó extras en las 128 ramas de recuperación sin segundo evento. Sus 23 extras se concentraron en siete ramas con un segundo evento real. Trece fueron avisos de generación posteriores a una segunda falla en BUS31 en dos registros. Los diez restantes ocurrieron durante o después de una segunda apertura de línea en cinco registros. Los seis episodios omitidos eran pulsos de generación tras una carga (cinco casos) o tras otro pulso de generación (un caso). Otros siete segundos eventos recibieron familia correcta y ubicación errónea. [Predicciones selladas](results/predictions.json) · [Etiquetas abiertas tras el sello](results/test_truth.json)

El ajuste actual propaga el primer evento fuerte. Después del segundo aviso usa la continuación del banco y detiene el ajuste de los parámetros del primero. Los errores observados justifican probar una trayectoria de dos conmutaciones que parta del estado físico estimado al segundo inicio. Cualquier ajuste posterior requiere otros datos para evaluar su eficacia. Esta prueba usó una sola familia de simuladores IEEE-39 y un único punto de operación nominal.

## Reproducción

Desde la raíz del repositorio, `python experiments/recovery_state/results/replay.py` recalcula los indicadores y verifica sus sellos con las predicciones y etiquetas publicadas. La opción `--regenerate` usa el archivo científico indicado por `P07_SCIENCE_ARCHIVE`, simula otra vez los 480 registros, verifica las huellas de los datos y ejecuta los cuatro monitores sobre 24 registros de selección determinista. En el entorno de la prueba se usó `OPENBLAS_NUM_THREADS=1`. El punto de entrada `python experiments/recovery_state/apply_recovery.py registro.npy` acepta una trayectoria de forma (reportes, 8 PMU, 5 campos) y publica cada decisión al recibir el reporte correspondiente. [Auditoría reproducible](results/replay.py) · [Monitor congelado](apply_recovery.py)

La auditoría comenzó con un directorio vacío de señales. La repetición desde la red del archivo científico reprodujo los bytes de las 480 trayectorias y las alertas de los cuatro monitores en los 24 registros seleccionados. El atajo `design.py replay-test` del código congelado tiene una limitación al comparar claves numéricas en memoria con claves de texto del manifiesto JSON cuando debe regenerar los datos. El script de auditoría compara ambos manifiestos una vez serializados.
