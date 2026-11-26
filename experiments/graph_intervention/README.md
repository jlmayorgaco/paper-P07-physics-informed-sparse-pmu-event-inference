# MET_BAYES_GRAFO con evidencia de una intervención nueva

El observador recibe ocho PMU a 30 Hz. En cada ventana compara la continuidad de la red, incluida la recuperación, con el inicio de una falla en barra, una apertura de rama, un pulso de par de generación o una variación de carga de impedancia. Estima el instante, la familia y la ubicación física. La alarma y el diagnóstico se publican juntos. El estimador y los dos comparadores se congelaron en `243a98c` antes de simular la prueba independiente sobre la misma familia de planta IEEE-39. [Protocolo](PROTOCOL.md) · [Selección del punto principal](operating/PROTOCOL.md)

## Prueba ciega sobre activos reservados

Se puntuaron 336 trayectorias independientes con 208 eventos, 52 por familia. Las 9 barras y 8 ramas reservadas no tienen etiquetas de fuente en el entrenamiento del grafo ni en el de la réplica de los árboles. Son distintas de los activos usados en la prueba de confirmación anterior. El clasificador supervisado histórico sí había visto ejemplos de todas ellas. Se conservaron sus pesos originales y se reentrenó por separado la misma arquitectura con los 1.592 registros admisibles de los 2.100 históricos. Los tres monitores recibieron las mismas lecturas e ignoraron los tiempos, familias y activos verdaderos durante la inferencia. El plazo para detectar y publicar familia y activo fue de 1,5 s.

| Método | Detección | Familia | Ubicación exacta | Familia y activo | Macro-F1 | Avisos extra | Segundos eventos exactos |
|---|---:|---:|---:|---:|---:|---:|---:|
| MET_BAYES_GRAFO, ajuste principal | 195/208 | 195/208 | 195/208 | 195/208 | 0,9608 | 2 | 51/64 |
| MET_PMU_FIRMAS_ETREE histórico | 187/208 | 186/208 | 174/208 | 174/208 | 0,9386 | 2 | 36/64 |
| MET_PMU_FIRMAS_ETREE reentrenado sin las fuentes de prueba | 177/208 | 173/208 | 166/208 | 166/208 | 0,9024 | 0 | 33/64 |
| Grafo con el umbral inicial de desarrollo (secundario) | 196/208 | 196/208 | 196/208 | 196/208 | 0,9432 | 11 | 52/64 |

La mejora observada del grafo principal frente al histórico fue +0,0222 de macro-F1 (IC pareado del 95 % de +0,0017 a +0,0428) y +10,10 puntos porcentuales de ubicación (+5,24 a +14,89). El recuento de extras fue igual, con intervalo para la diferencia de −4 a +4 avisos. Frente a los árboles con exclusión de activos, la mejora fue +0,0584 de macro-F1 (+0,0315 a +0,0881) y +13,94 puntos de ubicación (+9,34 a +18,63), con dos avisos adicionales observados. El remuestreo por trayectoria refleja la variación dentro de esta planta y este conjunto de activos. Los tres monitores produjeron cero avisos en 73,6 minutos de registros íntegramente normales. La latencia mediana desde el comienzo hasta la publicación fue 0,10 s para el grafo y 1,13 s para ambos árboles, según el reloj de los reportes y entre episodios detectados.

El grafo acertó los 144 primeros episodios. Las 13 omisiones fueron segundos eventos posteriores a una apertura de línea (7) o una falla (6). Incluyen 11 pulsos de par y 2 aumentos de carga. Los 195 eventos detectados recibieron familia y activo correctos antes del plazo. Los dos avisos extra identificaron erróneamente una carga en BUS15 durante la recuperación de una falla en BUS38, en registros distintos. Para alcanzar 0,96 en ubicación sobre esta cohorte harían falta 200/208 aciertos. Los resultados y las predicciones corresponden al umbral fijado antes de generar la prueba. [Puntuación principal e intervalos](operating/scores.json) · [Comparadores](results/scores.json) · [Activos y huellas del conjunto](results/test_manifest.json)

## De los reportes a la evidencia

Para un inicio, un activo y una intensidad fijados, se propagan las ecuaciones de máquina y la red AC con el sello eléctrico correspondiente. El operador de terminal genera la trayectoria de tensión y corriente en los canales disponibles. Las direcciones de corriente pierden peso cerca de cero amperios. Se usa un filtro de innovaciones común para la historia observada y la firma del candidato. En el caso gaussiano local, si el error inicial de estado tiene covarianza $P$, su proyección en los terminales es $O$ y el resto del ruido tiene covarianza $R$, la covarianza marginal es $S=R+OPO^\top$. Si $r$ y $g$ ya están blanqueados, la contribución gaussiana es $r^\top g-g^\top g/2$.

La versión ejecutada integra una escala latente de error con una distribución predictiva de Student. En cada reporte, para 31 coordenadas y una escala predecible $v$, la contribución al logaritmo de la razón de verosimilitudes es

$$
\frac{\nu+31}{2}\log\frac{\nu v+\|r\|^2}{\nu v+\|r-g\|^2}.
$$

Se acumula la evidencia a lo largo de cada trayectoria y se suma en probabilidad sobre inicios, intensidades y duraciones. La intensidad de una apertura completa está determinada por la rama. En las otras familias se emplean tres nodos de cuadratura. La masa de cada familia se reparte entre sus activos. La decisión se evalúa cada tres reportes con umbrales congelados y nunca se retrotrae la hora de publicación al inicio estimado. [Implementación](intervention_monitor.py)

Una restitución conserva los estados mecánicos. Después de declarar un evento, el observador mantiene una distribución sobre duraciones enteras e intensidades de ese episodio. Un modelo temporal de dos retardos, común a todos los activos de cada familia precedente, corrige el error predecible de la recuperación. La misma transformación se aplica a datos y firmas. Este aproximante fija el inicio y el activo del episodio declarado, propaga firmas desde el punto nominal y representa la dispersión de la restitución con una escala común. [Ajuste de la discrepancia](discrepancy.py)

## Reproducir y usar

El control compacto de resultados requiere NumPy y los archivos versionados. La reproducción desde las series guardadas usa también SciPy, Numba, scikit-learn y joblib. La opción de regeneración requiere el archivo científico de SGSMA en `P07_SCIENCE_ARCHIVE` y el entorno Python utilizado por el simulador. Reconstruye la cohorte en una carpeta temporal, comprueba las huellas de todas las observaciones y etiquetas y compara decisiones para los registros indicados.

~~~powershell
$env:OPENBLAS_NUM_THREADS='1'
python -B experiments/graph_intervention/results/audit.py
python -B experiments/graph_intervention/check.py
$env:P07_SCIENCE_ARCHIVE='U:/academic/SGSMA26-Physics-Informed-AD'
python -B experiments/graph_intervention/results/replay.py --regenerate
~~~

El comando de producción para un registro de forma `(reportes,8,5)` es **python experiments/graph_intervention/operating/run.py registro.npy**. Desde Python se crea un `primary_observer()` por flujo y se llama a `step(reporte)` con cada muestra. Se requiere un prefijo tranquilo de treinta reportes. En una instalación nueva se calculan y verifican las firmas físicas a partir de los modelos distribuidos. [Entrada del monitor congelado](operating/run.py)
