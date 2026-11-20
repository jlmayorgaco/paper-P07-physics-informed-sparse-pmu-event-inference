# Estimador recursivo de intervenciones físicas en la IEEE‑39

Una segunda prueba sobre trayectorias emparejadas evaluó la confirmación de nuevos episodios. La variante orientada a macro-F1 pasó de 159 a 9 avisos extra y de 0,610 a 0,888 de macro-F1 en esas mismas trayectorias. El supervisado obtuvo 0,938 y un aviso extra. [Prueba de confirmación y resultados por segundo evento](episode_confirmation/README.md)

MET_BAYES_GRAFO recibe un reporte de ocho PMU cada 1/30 s. Devuelve evidencia de intervención, el par familia–activo mejor respaldado y la masa de ese par condicionada a que haya una intervención. Un aviso tiene dos marcas de tiempo, detección e identificación. Se implementaron normalidad, falla trifásica en barra, apertura de rama, escalón positivo de par de generador y aumento de carga de impedancia constante. La primera prueba usa los ocho instrumentos disponibles. El disparo de máquina y la inyección de generación en una barra PQ requieren operadores adicionales.

## Qué predice la física

El estado de 30 coordenadas reúne ángulos, velocidades y potencias mecánicas de diez máquinas clásicas con regulador. Para cada modo $j$ se resuelve Kirchhoff con el sello de cada rama, sus tomas de transformador, las cargas y las admitancias transitorias de máquina. Si $E_g=|E_g|\exp(i\delta_g)$, las tensiones son lineales en los **fasores internos** $E_g$. La potencia eléctrica que alimenta la ecuación swing es cuadrática en estos fasores. El estimador precomputa ambos operadores y los evalúa en los ángulos inferidos. Los estados de máquina continúan al abrir y al restituir un activo. La corriente que se compara con los datos es la del terminal orientado definido en el mapa B01.

La predicción discreta parte de la exponencial del sistema afín a un paso. Se corrige el par con la diferencia entre potencia no lineal y tangente al principio del intervalo. Así se evalúa la lectura terminal no lineal al final de cada paso. La aproximación conserva esa corrección de par durante 1/30 s. El generador de prueba, por su parte, integra la dinámica no lineal con cuatro pasos RK4 por reporte y varía inercia y amortiguamiento. Ambos comparten el modelo de red nominal y la familia de máquinas.

El catálogo de 237 modos incluye normalidad. Una apertura tiene intensidad fija. Los otros tres tipos integran la intensidad mediante tres nodos de Gauss–Legendre para una distribución uniforme entre 0,7 y 1,3 veces la perturbación nominal. Un cambio de intensidad continuo se aproxima por esta cuadratura. Las probabilidades iniciales se reparten primero por familia y luego por activo y peso de cuadratura. En el grafo de transiciones se puede continuar, iniciar desde normalidad o restaurar. El estado físico al restaurar conserva información de la intervención anterior.

## De la pérdida cuadrática a la ganancia

Dentro de un modo fijo, escribamos el modelo tangente como

$$
x_k=A x_{k-1}+b+w_k,\qquad y_k=H x_k+c+n_k,\qquad n_k=F n_{k-1}+\epsilon_k .
$$

$Q$ y $R$ son las covarianzas independientes de $w_k$ y $\epsilon_k$. La perturbación de proceso representa un par aleatorio por máquina, integrado durante un reporte. Para el mismo modo en reportes contiguos, restar $F y_{k-1}$ elimina el ruido instrumental anterior. Con $D=HA-FH$ y covarianza anterior $P$, la innovación tiene covarianza y covarianza cruzada

$$
S=DPD^\top+HQH^\top+R,\qquad U=APD^\top+QH^\top .
$$

Minimizar $E\|x_k-\widehat x_k^- - K e_k\|^2$ respecto de $K$ da $KS=U$. En particular el término $QH^\top$ procede del mismo choque mecánico que llega al estado y a la medición. Con $S=LL^\top$, el código resuelve sistemas triangulares para actualizar $\widehat x_k=\widehat x_k^-+UL^{-\top}L^{-1}e_k$. La covarianza posterior es $APA^\top+Q-US^{-1}U^\top$. Su punto fijo se calcula por modo mediante Riccati. En el modelo lineal gaussiano condicionado al modo y con esa covarianza inicial, esta actualización es la media condicional y minimiza el error cuadrático.

## De los estados posibles a la evidencia de evento

Si $\pi_i$ es la masa anterior y $T_{ij}$ la transición, la masa predictiva de $j$ es $p_j^-=\sum_i\pi_i T_{ij}$. Se mezclan las medias de los estados de máquina y del error instrumental con pesos $\pi_iT_{ij}/p_j^-$. A partir de esas medias, el modelo predice los terminales y calcula el error $e_j$ entre el reporte y la predicción. El mismo error corrige el estado y actualiza la causa,

$$
\pi_j^+=\frac{p_j^-\,p(e_j\mid j)}{\sum_l p_l^-\,p(e_l\mid l)} .
$$

Para ruido gaussiano la log verosimilitud depende de $\log|S_j|$ y $e_j^\top S_j^{-1}e_j$. También se ensayó una escala latente $\lambda$ con prior inversa-gamma de forma y tasa $\nu/2$. Condicionadas a $\lambda$, las covarianzas locales del estado y de la observación llevan el mismo factor, de manera que este se cancela en la ganancia. Si $v_k$ es una escala predecible, integrar $\lambda$ da una distribución de Student. Salvo constantes comunes entre modos,

$$
\log p(e_j\mid j)=-\tfrac12\log|S_j|-
\tfrac{\nu+31}{2}\log\!\left(1+\frac{e_j^\top S_j^{-1}e_j}{\nu v_k}\right).
$$

En ambos casos $v_k=1+\gamma d_{k-1}$, donde $d$ es la suma de las desviaciones cuadráticas de las 16 coordenadas de tensión en unidades nativas, dividida entre ocho. Para las coordenadas polares son log-magnitud y fase en radianes. El valor usado para puntuar el reporte $k$ proviene del reporte anterior. En polares se toma el residuo angular principal. El origen de una etiqueta de línea sigue siendo la rama completa.

Se suman las masas por activo para integrar intensidad, y se suman los activos para integrar la incertidumbre de ubicación. $1-\pi_0$ activa la detección. El activo de masa máxima condicionada a evento resuelve la decisión puntual de pérdida 0–1 entre activos, en el posterior calculado. La regla de publicación permite esperar si esa masa es pequeña. Al volver a dominar la hipótesis de normalidad se cierra el episodio.

## Qué aprende y hasta dónde llega la optimalidad

Los primeros 55 reportes tranquilos de 256 trayectorias históricas de entrenamiento aportan el centrado, las escalas, la regresión instrumental $F$ y la covarianza residual $R$. En desarrollo se estiman por conteo las tasas de inicio y restauración. Se elige la escala del ruido de par por verosimilitud predictiva sobre trayectorias etiquetadas, usando el nodo de intensidad más cercano para ese ajuste. En la variante de Student se ajusta además $\nu$ en una cuadrícula y $\gamma$ mediante optimización escalar. Los costes de publicación se eligen en desarrollo con el criterio del protocolo. Durante la prueba se desconoce el inicio, la familia, la intensidad, el activo y la duración de cada evento.

La derivación de la ganancia y la integral de escala son exactas en sus modelos locales. El monitor fusiona historias en sus medias, conserva covarianzas estacionarias por modo y usa la ganancia tangente al corregir la predicción no lineal. Después de una conmutación, la mezcla completa tendría otra distribución y otra covarianza. También se aproxima la integral de intensidad. El resultado es un filtro de modelos interactuantes con estas aproximaciones. Los umbrales se calibran para el fin operativo. La optimalidad del tiempo de parada, de la recuperación de la fuente y del macro-F1 queda abierta. La mezcla de modelos y el filtro de Kalman tienen antecedentes establecidos. [Blom y Bar-Shalom](https://doi.org/10.1109/9.1299) · [Yang et al.](https://arxiv.org/abs/2107.06754)

## Uso y comprobación

Desde la raíz del repositorio, se puede procesar un registro sin acceso al NAS. El entorno usado incluye NumPy, SciPy, Numba, pandas y NetworkX. El ejecutable carga el modelo seleccionado y comprueba su huella.

~~~powershell
$env:OPENBLAS_NUM_THREADS = '1'
python experiments/graph_recursive/monitor.py experiments/supervised_stream/successor/controls/two_fault_locations.npy
~~~

Cada reporte es una matriz de ocho filas en el orden 2, 5, 6, 10, 19, 22, 29 y 39. Las cinco columnas contienen log-magnitud de tensión relativa al punto de operación, fase relativa de tensión en radianes, magnitud de corriente de terminal en amperios, fase relativa de corriente en grados y presencia. El modelo requiere los ocho canales disponibles y un prefijo tranquilo de 30 reportes. Para otro registro se crea otra instancia de PhysicalMonitor. El método step devuelve los avisos emitidos al llegar ese reporte. Si llegan detección y diagnóstico a la vez, ambos comparten el campo detected. Una identificación posterior actualiza la misma alarma.

La auditoría compacta usa las predicciones y calendarios adjuntos y solo requiere NumPy. El chequeo de los cuatro operadores usa además el simulador científico, el entorno de la planta supervisada y la variable P07_SCIENCE_ARCHIVE apuntando al repositorio SGSMA.

~~~powershell
python experiments/graph_recursive/audit.py
$env:P07_SCIENCE_ARCHIVE = 'U:/academic/SGSMA26-Physics-Informed-AD'
python experiments/graph_recursive/check.py
~~~

Los modelos y umbrales se seleccionaron en 24 registros de desarrollo. La variante gaussiana rectangular produjo 12 aciertos conjuntos y 23 avisos extra. La distribución de Student en esas coordenadas produjo 19 aciertos y 111 extras. En las coordenadas nativas de magnitud y fase, Student produjo 21 aciertos y 23 extras. El criterio previamente especificado seleccionó esta última antes de generar la prueba. En desarrollo pasó de 0 a 6/6 diagnósticos conjuntos de generación frente al gaussiano rectangular. El cambio abarca coordenadas, covarianzas ajustadas y ley de evidencia. [Selección congelada](phasor_freeze.json)

## Prueba reservada

La revisión 443f4ca fijó la selección, los modelos y sus umbrales antes de generar las 96 trayectorias de prueba. Los 104 eventos comprenden 26 de cada familia. Se reservaron fuentes por familia para el nuevo observador. Entrenamiento y prueba del monitor supervisado histórico pueden compartir esas fuentes. El comparador es MET_PMU_FIRMAS_ETREE, el monitor causal publicado en el repositorio. La entrega de junio por ventanas de 30 s tiene otro plazo de decisión.

| Método | Detectados en 1,5 s | Familia en 1,5 s | Familia y activo en 1,5 s | Macro-F1 de 4 familias | Extras en registros con eventos |
|---|---:|---:|---:|---:|---:|
| Kalman con evidencia gaussiana rectangular | 54/104 | 49/104 | 46/104 | 0,3622 | 116 |
| Kalman con Student rectangular | 88/104 | 82/104 | 79/104 | 0,4333 | 441 |
| **MET_BAYES_GRAFO seleccionado, Student polar** | **97/104** | **94/104** | **93/104** | **0,7284** | **66** |
| MET_PMU_FIRMAS_ETREE | 93/104 | 93/104 | 89/104 | 0,9351 | 1 |

Ningún método emitió avisos en los 24 registros completamente normales. Estos aportan 9,2 minutos después del prefijo. Para el acierto conjunto del método seleccionado el intervalo bootstrap del 95 % por trayectoria es 83,49–94,87 %. La diferencia pareada frente al supervisado es +3,85 puntos porcentuales, con intervalo de −4,04 a +11,76. Su mayor número de aciertos vino acompañado de una precisión de detección de 97/163, frente a 93/94 del comparador. Los 0 s de latencia mediana del método físico significan que al menos la mitad de sus detecciones emparejadas se emitieron al primer reporte etiquetado. El simulador integra hasta ese reporte. El tiempo de cómputo y transporte queda fuera de esa latencia. [Resultados del método seleccionado](phasor_scores.json) · [Comparador y control gaussiano](scores.json) · [Control Student rectangular](robust_scores.json)

| Familia | Aciertos conjuntos del filtro seleccionado | Aciertos conjuntos del supervisado |
|---|---:|---:|
| Falla | 25/26 | 24/26 |
| Línea | 22/26 | 25/26 |
| Generación | 21/26 | 16/26 |
| Carga | 25/26 | 24/26 |

De los 66 avisos extra, 3 ocurrieron durante una intervención y 63 después de una restauración, antes del siguiente inicio o del final del registro. De esos 63, 36 siguieron al recierre de una línea y 27 al despeje de una falla. Esta clasificación temporal usa las etiquetas solo después de sellar predicciones. Identifica dónde falla el monitor. Para atribuirlo a la fusión de historias o a la covarianza estacionaria habría que variar esos dos componentes por separado con las mismas trayectorias y medir también las detecciones perdidas durante la recuperación. La tasa conjunta de 89,4 %, la precisión y el macro-F1 descartan presentar este prototipo como superior al supervisado o como una solución al objetivo operativo del 96 %. [Recuento pareado reproducible](audit.py)
