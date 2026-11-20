# MET_BAYES_GRAFO

## Estimación conjunta a partir de PMU, congelada en 555057c

El monitor estima cada nueva perturbación desde el estado físico dejado por las anteriores. En una prueba ciega con 416 trayectorias independientes y 17 activos reservados, detectó, clasificó y ubicó los 480 episodios dentro de 1,5 s. El macro-F1 fue 1,0000, con cero extras frente a 4 de los árboles históricos y 3 de su réplica. Identificó los 32 segundos eventos objetivo de generación y carga y los 64 terceros eventos. El alcance es la IEEE-39 simulada con topología conocida, ocho PMU disponibles e intervenciones sucesivas. [Resultados, alcance y reproducción](../experiments/joint_pmu/README.md)

## Recuperación dinámica, congelada en d5b8f88

Tras una falla o apertura, el monitor estima la trayectoria de recuperación con las PMU y busca una segunda intervención en el residuo. En la nueva prueba ciega acertó los 32 segundos eventos de generación y carga posteriores a fallas o aperturas, frente a 18 del grafo anterior sobre las mismas señales. En la cohorte completa obtuvo 0,9663 de macro-F1, 410/416 familias y 403/416 ubicaciones, con 23 alarmas extra frente a 3 y 0 de los dos árboles. Contando cada primer evento compartido una sola vez, el macro-F1 fue 0,9520 y la ubicación 275/288 (95,49 %). [Prueba pareada, errores y reproducción](../experiments/recovery_state/README.md)

Las siete trayectorias con alarmas extra volvieron a producirlas al suprimir el ruido de medición. En 32 pares nuevos de desarrollo, una trayectoria conjunta que conocía los dos primeros eventos y los parámetros de planta produjo cero extras en controles e identificó 29/32 terceros eventos. Esta prueba evalúa la factibilidad física. El estimador en línea debe inferir la historia de las dos primeras perturbaciones a partir de las PMU. [Ablación de ruido y prueba de una tercera intervención](../experiments/recovery_diagnostics/README.md)

## Versión de evidencia de intervención, congelada en 243a98c

Esta versión compara directamente un inicio nuevo con la continuación o recuperación. En una prueba ciega de 336 trayectorias y 208 eventos físicos obtuvo 0,9608 de macro-F1, 195/208 ubicaciones exactas y dos avisos extra. En idénticas señales MET_PMU_FIRMAS_ETREE histórico obtuvo 0,9386, 174/208 y dos extras. Al reentrenar los árboles excluyendo las mismas nueve barras y ocho ramas reservadas se obtuvo 0,9024, 166/208 y cero extras. Los valores corresponden al punto principal fijado antes de simular la prueba. [Resultados, intervalos, ejecutable y auditoría](../experiments/graph_intervention/README.md)

## Observador multihipótesis anterior

El observador de cuatro familias ya se puede ejecutar reporte a reporte. La ganancia sale de un problema local de mínimo error cuadrático con ruido de PMU correlacionado en el tiempo. Una distribución de Student integra una escala de error desconocida al actualizar las probabilidades de los modos físicos. Se congeló la variante en magnitud y fase antes de generar 96 trayectorias nuevas. Logró 93/104 diagnósticos conjuntos en 1,5 s y 66 avisos extra. El comparador supervisado logró 89/104 y un aviso extra. La propuesta original de este documento cubre también mecanismos que requieren validación separada, entre ellos el disparo de máquina, la inyección PQ y los canales ausentes. [Derivación ejecutada, modelo y prueba](../experiments/graph_recursive/README.md)

## Prioridades después de la prueba de cuatro familias

Los once fallos conjuntos se reparten en siete omisiones de detección, tres familias equivocadas y un único activo equivocado con la familia correcta. Al eliminar por etiqueta solo los 63 avisos extra posrestauración y conservar todos los demás, el macro-F1 pasaría de 0,7284 a 0,9201. Eliminando los 66 extras llegaría a 0,9338 y el acierto conjunto seguiría en 93/104. Ambos cálculos usan la verdad para retirar alarmas ya emitidas. Cuantifican el efecto de esos errores en la prueba existente. [Auditoría reproducible](../experiments/graph_recursive/diagnose.py)

**Primera corrección física.** En las tres aperturas de la línea 2–3, el medidor asociado a PMU 2 pasa de centenares de amperios a una mediana de 0 A. Durante la apertura la mediana del valor absoluto de la fase supera 179,99°, mientras que el modelo abierto predice un fasor nulo y asigna 0° al ángulo. El cableado y la polaridad no resuelven la fase de un fasor nulo. Al cambiar exclusivamente la fase de las muestras de corriente de magnitud exactamente cero a 0°, sin cambiar un solo fasor complejo, dos primeros diagnósticos cambian de falla en BUS2 a apertura 2–3. Aparecen otros avisos, y el tercer registro sigue sin resolver la línea. Es una prueba de invariancia que falla, no una mejora global medida. Para reproducirla desde la raíz, ejecutar **python experiments/graph_recursive/diagnose.py --observations tmp/graph_recursive/test/pmu.npy**.

Una verosimilitud de terminal debe comparar todas las hipótesis en la misma observación y admitir que la fase pierde precisión a baja corriente. Como modelo de referencia, con ruido gaussiano cartesiano isótropo de varianza $\sigma^2$ por componente, corriente prevista $A e^{i\phi}$ y magnitud medida $r>0$, la densidad de fase condicionada a $r$ es von Mises con concentración $rA/\sigma^2$. Para $A=0$ es uniforme. Si el instrumento recorta la magnitud a cero, se modela la probabilidad de esa lectura y se integra la fase sin definir. La ley real se calibra con lecturas de corriente pequeña y banderas instrumentales. La comprobación de regresión consiste en que cualquier recodificación de la fase a magnitud cero produzca decisiones idénticas.

**Generación débil.** Cuatro de los ocho pulsos de par en BUS39 quedaron sin alarma oportuna. En esos cuatro, la masa máxima de intervención dentro de 1,5 s fue 0,9827, 0,9986, 0,9936 y 0,9955. El umbral congelado era 0,999. La prueba de desarrollo debería variar por separado intensidad, inercia y ruido, y comprobar si la trayectoria de ángulo y velocidad prevista por la ecuación swing explica los reportes mejor que la continuación normal. El ajuste estadístico prioritario es la distribución del error de predicción según la amplitud y el punto de operación. La comparación exige el mismo presupuesto de falsas alarmas.

**Principal pregunta científica.** Tras un despeje o recierre, el monitor actual usa la masa de modos activos y mezcla los estados recuperados en su media. Para detectar un *segundo* episodio, comparar dos predicciones desde la misma distribución física posterior al primer evento. Una continúa la recuperación y la otra introduce una nueva intervención de inicio desconocido dentro del horizonte causal. Integrar inicio, intensidad e historias en ambas hipótesis según corresponda. El cociente de verosimilitudes actualiza la razón de probabilidades previa de un episodio nuevo. Una nueva prueba deberá mostrar si conservar historias distintas mejora la predicción y si la regla de publicación reduce duplicados.

Una condición local aclara cuándo la memoria de varias historias puede cambiar la decisión. Sean $m_i$ las medias de reportes futuros bajo recuperación, $w_i$ sus pesos previos comunes a ambas hipótesis, $\bar m=\sum_iw_i m_i$, y $S$ una covarianza gaussiana común positiva definida. En el experimento local, el nuevo evento suma la misma firma $s$ a cada media. Denotemos por $B_{\rm mix}$ el factor de Bayes evento/recuperación de la mezcla y por $B_{\rm media}$ el que sustituye todas las medias por $\bar m$ con el mismo $S$. Para $q_i(y)=p(i\mid y,\text{recuperación})$, la razón de densidades gaussianas da

$$
\log B_{\rm mix}(y)-\log B_{\rm media}(y)
=\log\sum_i q_i(y)\exp[-s^\top S^{-1}(m_i-\bar m)].
$$

El lado derecho queda entre el mínimo y el máximo de los exponentes antes de exponenciar. Por tanto, el valor absoluto del cambio de log-evidencia está acotado por $\max_i|s^\top S^{-1}(m_i-\bar m)|$. Si la separación al umbral en log-odds supera esa cota, fusionar las medias conserva esa decisión binaria a ese horizonte. La cota depende de la firma y del mapa de PMU. Puede ser grande o poco informativa. En la variante Student o ante una apertura cuyo efecto depende de la historia, se deben contrastar las densidades predictivas de cada historia directamente. La identidad no certifica la política secuencial ni el rendimiento de la implementación. La sección III del artículo ya cuantifica la pérdida predictiva de una fusión gaussiana. Aquí interesa su efecto sobre la decisión entre una fuente concreta y la recuperación.

**Experimento que decidiría el aporte.** Partir de una misma trayectoria de falla o apertura y bifurcarla al despeje o al recierre. En una rama solo hay recuperación; en la otra se inyecta una intervención en un activo y momento desconocidos para el monitor. Sortear varias separaciones, incluyendo segundas intervenciones tempranas, con errores instrumentales y dinámicas de máquina diferentes de las de ajuste. Cruzar la representación (media o distribución de recuperación) con la decisión (masa activa o evidencia de nuevo episodio), manteniendo igual la corrección de baja corriente. Comparar con el supervisado y con sustracción de una sola trayectoria previa. Seleccionar parámetros solo en desarrollo, reservar activos y otra planta, y congelar antes del examen nuevo. Contar falsas segundas alarmas por recuperación, detecciones y diagnósticos exactos dentro de 1,5 s, macro-F1 y alarmas por hora normal con intervalos por trayectoria. Un filtro que silencia todas las recuperaciones también perdería las segundas intervenciones.

Un antecedente directo predice y resta el efecto de sucesos previos para clasificar el siguiente con una CNN. También existe detección y localización espectral de aperturas en grafos, y la reducción de mezclas tiene teoría propia. La contribución por demostrar es determinar **cuándo las PMU disponibles distinguen una nueva fuente de las recuperaciones plausibles**, y si esa distinción permite emitir menos alarmas sin ocultar el segundo evento. [Li y Wang](https://sites.ecse.rpi.edu/~wang/pub/TPWRS19_2.pdf) · [Dwivedi y Tajer](https://sites.ecse.rpi.edu/~tajer/papers/J48.pdf) · [Runnalls](https://kar.kent.ac.uk/2782/)

## Pregunta y alcance

¿Qué cambio en la red explica las tensiones y corrientes que acaban de llegar, dada la trayectoria que seguía el sistema antes del cambio? Se propone extender el banco de recuperación de P07 a cuatro familias. En cada episodio interesa la hora a la que se detecta el evento y la hora a la que se identifica el activo. Ambas son horas de publicación. La estimación retrospectiva del inicio se informa aparte. El alcance inicial admite sucesos consecutivos, con recuperación aún visible cuando llega el siguiente.

La guía SGSMA (tabla 4) distingue normalidad (0), falla (1), apertura de línea (2), cambio o salida de generación (3) y cambio de carga (4). El 5 y el 7 son condiciones del instrumento. En el 6 interesa inferir el componente físico con los canales disponibles. El 8 es una etiqueta abierta. El objetivo físico incluye barras sin PMU y ramas observadas desde otros terminales. El artículo vigente ensaya nueve cargas y nueve líneas. La guía está en `guidelines.pdf` del archivo científico SGSMA, p. 13. [Artículo](../output/pdf/P07_Event_Attribution_Article.pdf)

## De la intervención a lo que ve cada instrumento

Cada rama tiene una matriz compleja de dos puertos $Y_\ell$ y una matriz $E_\ell$ que selecciona sus dos barras en el orden declarado. Para el modo de red $q$,

$$
Y(q)=Y_{\rm sh}+\sum_{\ell\ {\rm en\ servicio}}E_\ell^\top Y_\ell E_\ell,\qquad
i_\ell=Y_\ell E_\ell V,\qquad I_{\rm iny}=Y(q)V,\qquad
S=\operatorname{diag}(V)\overline{I_{\rm iny}}.
$$

Los sellos de rama incluyen resistencia, carga capacitiva, toma y desfase del transformador. En esta convención las corrientes de los dos puertos salen de su barra hacia el elemento. Los shunts se contabilizan una sola vez. El flujo AC fija un punto de operación consistente. Durante el transitorio las ecuaciones algebraicas se resuelven junto a las de las máquinas. Para la planta de referencia, con velocidad $\omega_g$ en pu,

$$
\dot\delta_g=\omega_b(\omega_g-1),\qquad
2H_g\dot\omega_g=\tau_{m,g}-\tau_{e,g}-D_g(\omega_g-1).
$$

El estator conecta la potencia eléctrica con el par y los reguladores gobiernan su evolución. La frecuencia de una PMU se deriva de la fase de su tensión. Tras una reconexión se conserva el estado mecánico compatible con el episodio anterior. [Balance verificado en la planta](../supplement/hamiltonian_graph_bayes.tex)

| Hipótesis | Intervención que se aplica al predictor | Fuente que se publica |
|---|---|---|
| Ninguna nueva | Continuar la red y el estado estimados, incluida la recuperación | Ninguna nueva fuente |
| Falla | En el primer alcance, cortocircuito trifásico equilibrado en barra mediante admitancia de falla y su despeje | Barra de falla |
| Apertura | Retirar el sello completo de la rama y resolver el nuevo modo. Reinsertarlo al recierre | Rama por sus extremos e identificador de circuito |
| Generación | Modificar la consigna/par de una máquina o conmutar su conexión si dispara. Para generación representada como inyección PQ, usar el modelo de esa inyección | Barra de conexión |
| Carga | Modificar la demanda P/Q con su ley de dependencia de tensión y rango de severidad | Barra de carga |

La distinción en generación importa. El generador de trayectorias supervisadas aplica un pulso de par en una de diez máquinas. El archivo AllEvents interpreta la generación de RAW0001 en BUS2 como una inyección PQ. Un catálogo limitado a las diez máquinas excluiría la respuesta correcta antes de leer el primer fasor. Si una variación de generación y una reducción de carga en la misma barra generan leyes idénticas para los reportes admitidos, los datos no identifican la familia. Haría falta una diferencia observable en la dinámica, la ley reactiva o una medición adicional. [Generador del estudio supervisado](../experiments/supervised_stream/plant.py)

El operador de observación selecciona tensiones en $\{2,5,6,10,19,22,29,39\}$ y corrientes de **terminal** con su polaridad, ganancia y fase. En el modelo de P07, el canal asociado a PMU 2 mide la tensión en 2 y la corriente del extremo 3 de la línea 2–3. Su producto sin corrección no es potencia de ese terminal. La asignación de BUS5 es provisional y el banco omite el ángulo de corriente de BUS39. La máscara de disponibilidad se aplica al operador y a la covarianza. Una potencia derivada de V/I o una frecuencia derivada de fase exige conservar su dependencia estadística. El THD precisaría mediciones armónicas adicionales. [Tabla de terminales](../tables/generated/main_terminal_map.tex)

## El problema inverso y su reducción

Se fija la referencia angular y se elimina la tensión algebraica local mediante el complemento de Schur del jacobiano de flujo $g_z$, cuando es invertible. Por ejemplo, $A_q=f_x-f_zg_z^{-1}g_x$. El modelo reducido con su operador terminal produce $\mu_h(a)$, la historia de reportes para la hipótesis $h=(\text{familia},\text{activo},\text{inicio},\text{modo})$ y severidad $a$. Esta es la señal del evento sobre el grafo muestreada por ocho instrumentos. La reducción completa, la actualización del estado y los offsets al conmutar ya están en la sección III. Las aperturas y disparos finitos requieren su propio modo de red. [Derivación del banco](../sections/article_method.tex)

Considérese una historia previa y la ventana causal desde un inicio candidato hasta el presente. $\mu_0$ es la predicción si continúa la recuperación, $r=y-\mu_0$ y $s_h(a)=\mu_h(a)-\mu_0$. En la aproximación local de covarianza gaussiana común, $\Sigma=LL^\top$ incluye la incertidumbre de recuperación **una vez**. En el caso aditivo, si $O$ propaga la incertidumbre inicial $P$ y $R$ reúne las restantes fuentes independientes, $\Sigma=R+OPO^\top$. Con correlación temporal, $L$ debe blanquear el bloque temporal completo o se deben usar innovaciones condicionales causales. [Derivación de la covarianza](../supplement/recovery_information_geometry.tex)

Escribamos $z=L^{-1}r$, $d_h(a)=L^{-1}s_h(a)$. Al restar dos log densidades, el término cuadrático común en $z$ se cancela. Así se obtiene la evidencia del candidato frente a la continuación,

$$
\log\frac{p(y\mid h,a)}{p(y\mid 0)}
= d_h(a)^\top z-\tfrac12\|d_h(a)\|^2 .
$$

Si las columnas de $U$ forman una base ortonormal de todas las diferencias $d_h(a)$ admitidas, en el término anterior basta sustituir $z,d_h(a)$ por $U^\top z,U^\top d_h(a)$. La componente de la observación perpendicular a todas las firmas se cancela en cada comparación. La igualdad se conserva al integrar la severidad con su prior. Para firmas afines deben incluirse los offsets y las pendientes. Para varios inicios debe abarcarse el diccionario correspondiente. Si cada hipótesis tiene su propia covarianza, se evalúa la densidad gaussiana de cada una con su determinante y su forma cuadrática. La proyección anterior solo tiene garantía para el experimento de covarianza común.

Para una carga con firma local $d_h(a)=a v_h$, el ajuste de severidad sale de una derivada. Un prior gaussiano de centro $m$ y varianza $v$ da precisión posterior $J=v^{-1}+v_h^\top v_h$ y centro $b/J$, con $b=m/v+v_h^\top z$. En un intervalo físico $[a_-,a_+]$, el MAP es el centro recortado al intervalo. El estimador de mínimo error cuadrático es la **media de la normal truncada**. La evidencia usada para comparar activos integra sobre el intervalo e incluye su normalización, como en el banco actual. Para una falla de severidad no lineal se integran las predicciones sobre admitancias factibles. Una apertura completa tiene magnitud determinada por el sello retirado.

## Del reporte a la decisión

1. Estimar el estado y la escala instrumental en un prefijo admitido. Continuar la trayectoria al restaurar una rama o carga. Durante un episodio cerrado, una oscilación residual puede pertenecer a la hipótesis «ninguna intervención nueva».
2. En cada reporte extender cada trayectoria plausible con continuidad, restauración o nuevo inicio. Multiplicar su probabilidad previa de transición por la densidad **predictiva de ese reporte**. Para reconsiderar un inicio reciente se reemplaza la verosimilitud de su sufijo. Esto evita sumar dos veces reportes compartidos por ventanas. Integrar tamaño, inicio alternativo e historia anterior. Distribuir una masa previa por familia entre sus activos evita favorecer una familia solo porque tiene más candidatos.
3. Para el episodio en búsqueda, calcular $p_{\rm evt}=1-p_0$, donde $p_0$ suma las historias sin un nuevo episodio en el intervalo de decisión. Publicar una sola detección al cruzar el umbral calibrado. Mientras esté abierto, seguir el mismo episodio y reconocer la restauración. La masa de una familia es la suma de sus activos. Para el diagnóstico exacto se publica el par familia–activo de mayor masa cuando hay soporte suficiente. Se pueden anunciar el evento y luego el activo en tiempos distintos. Si solo hay soporte para un conjunto de activos, se pueden informar los rivales y el reloj de ubicación exacta sigue corriendo.
4. A un instante fijo, el MAP conjunto minimiza el error de par bajo pérdida 0–1. La media posterior minimiza error cuadrático de estado o severidad. Optimizar el tiempo de alarma requeriría definir costes de espera, omisión y falsa alarma, y resolver el problema de parada. En la propuesta los umbrales se calibran. La linealización, la poda y el error de planta limitan la interpretación de sus probabilidades.

## Aprendizaje y experimento decisivo

La primera variante aprendida ajustaría exclusivamente la covarianza de discrepancia de las innovaciones en función del punto de operación y los canales disponibles. Se ajusta una parametrización positiva definida y compartida entre activos, minimizando en entrenamiento la suma de $\log|\Sigma_{\phi,k}|+e_k^\top\Sigma_{\phi,k}^{-1}e_k$ en predicciones a un paso de historias de entrenamiento. Las entradas de contexto están disponibles antes de observar el reporte puntuado. Los activos reservados se excluyen del ajuste, la calibración y la selección del modelo. En inferencia reciben su firma de las ecuaciones eléctricas. Conviene conservar un brazo de covarianza fija para comprobar si el ajuste aporta algo.

La prueba debe separar **visibilidad** frente a cero y **resolución** frente al rival mejor ajustado. En el caso común, para una intensidad verdadera fijada se puede calcular $\min_b\|d_h(a)-d_j(b)\|^2$ sobre los tamaños admisibles del rival. Un cambio visible puede seguir siendo compatible con dos barras. El valor es una separación nominal y su utilidad se comprueba contrastándolo con errores posteriores en otra planta. El suplemento ya incluye un diagnóstico de este tipo para cargas y líneas. [Perfilado de los rivales](../experiments/channel_profile_20261112/README.md)

Comparar en las mismas trayectorias un GLR físico de estado único, el banco físico de cuatro familias con covarianza fija, su variante aprendida y el monitor supervisado causal. La entrega de junio conserva su contrato de ventanas de 30 s y se puntúa a su hora real de publicación. Separar el efecto de permitir dos tiempos de decisión del efecto de aprender la covarianza. Reservar fuentes completas, incluir rangos solapados de severidad y duración entre familias, reactiva y colocalización carga/generación, sucesos repetidos, largas exposiciones normales, variación de impedancia y ruido instrumental independiente. Registrar casos rechazados y abstenciones. Informar macro-F1 con unidad explícita, detección y diagnóstico oportunos, activo y familia correctos sobre **todos** los episodios, extras en registros con eventos, falsas alarmas por hora normal e intervalos pareados por trayectoria. Para la meta del 96 % hacen falta resultados nuevos al mismo presupuesto de falsas alarmas.

## Qué está comprobado

En el monitor supervisado congelado se volvieron a asociar las predicciones selladas con los episodios por el criterio original de 1,5 s. La selección usa las etiquetas verdaderas 1–4 de la prueba de nueve clases. Se trata de un desglose retrospectivo con el clasificador de nueve clases intacto. [Conteos por familia](../experiments/supervised_stream/successor/per_family.csv) · [Regla de emparejamiento](../experiments/supervised_stream/score.py)

| Familia | Episodios | Sin alarma oportuna | Familia errónea tras alarma | Familia correcta y activo erróneo | Acierto conjunto oportuno |
|---|---:|---:|---:|---:|---:|
| Falla | 183 | 2 | 1 | 19 | 161 |
| Línea | 174 | 2 | 0 | 1 | 171 |
| Generación | 189 | 33 | 0 | 5 | 151 |
| Carga | 168 | 16 | 0 | 1 | 151 |
| Total | 714 | 53 | 1 | 26 | 634 |

Aun corrigiendo todas las identificaciones de los 661 eventos detectados a tiempo, el techo de ese monitor en este subconjunto sería 661/714 (92,6 %). Para llegar al 96 % se precisan 686 aciertos conjuntos, incluidos al menos 25 de los 53 episodios sin alarma oportuna.

La segunda comprobación corresponde al álgebra del estimador propuesto. Se tomaron los operadores nominales de desarrollo, un inicio conocido, cargas de +10 %, nueve aperturas completas, estado inicial fijado y la covarianza común de operación normal. Treinta reportes de 31 coordenadas V/I dan 930 observaciones escalares. El espacio de las 18 alternativas fijas tiene rango numérico 18. Las 306 distancias dirigidas archivadas se reprodujeron con error escalado inferior a $3\times10^{-15}$ en las dos ejecuciones locales. Las 1.368 razones logarítmicas frente a cero en observaciones de comprobación coincidieron con error escalado inferior a $10^{-12}$ en ambas ejecuciones. El error se divide por el mayor de uno y el valor absoluto de referencia. La prueba verifica la equivalencia, sin medir ahorro de tiempo, precisión nueva ni desempeño sobre otras familias. Desde la raíz se reproduce con **python -B experiments/graph_signature_projection/check.py**. [Comprobación](../experiments/graph_signature_projection/check.py)

El filtrado multihipótesis, la proyección sobre firmas y la detección de aperturas mediante la dinámica tienen antecedentes. La hipótesis científica es más concreta. Condicionar las firmas terminales en la recuperación y separar el momento de detección del momento de atribución podría permitir detectar una segunda intervención antes de poder distinguir su origen, y explicar cuáles son los activos rivales. La comparación ciega debe mostrar si esto mejora el diagnóstico oportuno y conserva el presupuesto de alarmas al cambiar de planta. [Scharf y Friedlander](https://mountainscholar.org/items/06a68de8-560b-47ac-93a8-c9839b17aab3) · [Rovatsos et al.](https://doi.org/10.1109/TSP.2017.2673802) · [Yang et al.](https://arxiv.org/abs/2107.06754) · [Jamei et al.](https://arxiv.org/abs/1809.04014)
