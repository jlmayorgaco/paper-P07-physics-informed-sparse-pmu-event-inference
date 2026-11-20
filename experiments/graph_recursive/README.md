# Estimador recursivo de intervenciones físicas en la IEEE‑39

MET_BAYES_GRAFO recibe un reporte de ocho PMU cada 1/30 s. Devuelve evidencia de intervención, el par familia–activo mejor respaldado y la masa de ese par condicionada a que haya una intervención. Un aviso tiene dos marcas de tiempo, detección e identificación. Se implementaron normalidad, falla trifásica en barra, apertura de rama, escalón positivo de par de generador y aumento de carga de impedancia constante. La primera prueba usa los ocho instrumentos disponibles. El disparo de máquina y la inyección de generación en una barra PQ requieren operadores adicionales.

## Qué predice la física

El estado de 30 coordenadas reúne ángulos, velocidades y potencias mecánicas de diez máquinas clásicas con regulador. Para cada modo $j$ se resuelve Kirchhoff con el sello de cada rama, sus tomas de transformador, las cargas y las admitancias transitorias de máquina. Si $E_g=|E_g|\exp(i\delta_g)$, las tensiones son lineales en los **fasores internos** $E_g$. La potencia eléctrica que alimenta la ecuación swing es cuadrática en estos fasores. El estimador precomputa ambos operadores y los evalúa en los ángulos inferidos. Los estados de máquina continúan al abrir y al restituir un activo. La corriente que se compara con los datos es la del terminal orientado definido en el mapa B01.

La predicción discreta parte de la exponencial del sistema afín a un paso. Se corrige el par con la diferencia entre potencia no lineal y tangente al principio del intervalo. Así se evalúa la lectura terminal no lineal al final de cada paso. La aproximación conserva esa corrección de par durante 1/30 s. El generador de prueba, por su parte, integra la dinámica no lineal con cuatro pasos RK4 por reporte y varía inercia y amortiguamiento. Ambos comparten el modelo de red nominal y la familia de máquinas.

El catálogo de 237 modos incluye normalidad. Una apertura tiene intensidad fija. Los otros tres tipos integran la intensidad mediante tres nodos de Gauss–Legendre para una distribución uniforme en [0,7, 1,3] veces la perturbación nominal. Un cambio de intensidad continuo se aproxima por esta cuadratura. Las probabilidades iniciales se reparten primero por familia y luego por activo y peso de cuadratura. En el grafo de transiciones se puede continuar, iniciar desde normalidad o restaurar. El estado físico al restaurar conserva información de la intervención anterior.

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
