# P07: contraste de la revisión de Gemini y plan científico

Fecha: 3 de noviembre de 2026, America/Bogota. Revisión del commit `9aef51e5ea50f2a0a96273f81ad1dd417529e40c`. Documento de auditoría y planificación: no modifica el artículo, el método ni las campañas.

## 1. Dictamen

**Gemini acierta en varias prioridades, pero su dictamen mezcla una versión anterior, lagunas reales y afirmaciones matemáticas o de implementación incorrectas. El P07 vigente necesita fortalecimiento científico antes de enviarse; no hay evidencia para concluir que el método sea falso ni para heredar automáticamente el 4,2/10.**

La tesis defendible es que un predictor eléctrico que conserva la recuperación puede atribuir intervenciones sucesivas desde mediciones dispersas. La evidencia actual sostiene una ventaja del arrastre del estado frente a su borrado en un control concreto. Todavía no establece que mantener múltiples historias sea superior a un observador continuo competente bajo información y calibración comparables.

No recomiendo reconstruir todo el método ni agregar una colección de técnicas para buscar una nota perfecta. Recomiendo cerrar cinco frentes: correspondencia ecuaciones–código; diagnóstico de incertidumbre; comparación equiparada; generalidad física; y un artículo centrado en esos resultados.

La guía oficial de [IEEE Access](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/) pide solidez técnica, contribución distinguible, evidencia suficiente y conclusiones sustentadas. No exige inventar un nuevo principio matemático. “10/10” debe traducirse aquí en condiciones de cierre verificables, no en promesa de aceptación.

Valoración orientativa del autor de esta auditoría, no escala oficial ni puntuación calibrada: originalidad/valor 7/10; rigor matemático-estadístico 6/10; validez comparativa/generalización 6/10; coherencia editorial del principal 8/10. No se agregan en una probabilidad de aceptación. La honestidad al reconocer una limitación mejora el artículo, pero no sustituye la evidencia que falta.

## 2. Qué versión se está juzgando

- El título vigente es *Recovery-Aware Physical Attribution of Load and Line Events From Sparse PMUs* (`metadata.tex:4`).
- `main.pdf` tiene 15 páginas; el suplemento, 42. Los hashes se registran en `REVIEW_MANIFEST.json`.
- Los commits `c1808fd` y `9aef51e`, del 3 de noviembre, ya modificaron título, resumen, contribuciones, tasas por tiempo monitorizado y organización.
- El padre `c9b2e68` contiene el título y el resumen antiguo que cita Gemini. Sin el PDF exacto entregado a Gemini no se afirma identidad binaria con ese commit; sí existe correspondencia textual.
- El resumen vigente no promete una matriz del hackathon. La contribución 3 es la ablación de puntuación/severidad y arrastre de estado. X02 está incluido en el suplemento, Appendix K, y la tabla de poblaciones lo identifica como suplementario.
- La sección auxiliar criticada dejó de formar parte del principal. Sus resultados históricos no se han borrado.

Por tanto, parte del plan propuesto por Gemini **ya está ejecutada**. La continuidad correcta parte de las fuentes incluidas por `main.tex`, no de archivos `.tex` históricos que siguen en el repositorio.

## 3. Adjudicación de las críticas

| Crítica | Dictamen contrastado | Acción que sí vale la pena |
|---|---|---|
| “Experimentos fantasma” en resumen y contribución 3 | Válida para la etapa antigua; corregida en el principal vigente. X02 existe y está incluido en suplemento. | Mantener registro afirmación–evidencia y verificar los PDF realmente distribuidos. |
| El empate marginal/perfil hace irrelevante toda la inferencia bayesiana | Excesiva. La ablación cambia la puntuación de severidad y conserva actualizaciones condicionales de estado/amplitud, priors y otras reglas. No demuestra ventaja marginal en los endpoints medidos, ni equivalencia universal. | Conservar el resultado nulo, el título actual y la descripción exacta de la intervención. Si se estudia incertidumbre, medirla por separado. |
| El producto secuencial es inválido porque las observaciones están correlacionadas | Incorrecta como regla general: la factorización mediante distribuciones predictivas condicionales admite dependencia temporal. El problema real es la fidelidad de esas distribuciones aproximadas. | Diagnosticar innovaciones antes de la actualización, cobertura y efecto de covarianza/poda. |
| El filtro no representa correlación estado–severidad | Incorrecta: `m+d*a` representa una dependencia condicional explícita. No equivale a un posterior conjunto exacto de todas las historias. | Escribir las covarianzas condicional y marginal, distinguir parámetros gaussianos de momentos truncados y cuantificar la dispersión perdida al comprimir. |
| Cuatro intervalos de severidad sin explicación | Correcta como omisión expositiva. Son cuatro historias con masas de prior propias, no cuatro cuadraturas necesarias para resolver una integral sin forma cerrada. | Explicar mezcla, herencia, normalización y poda; probar equivalencia con el intervalo único antes de podar. |
| Los términos afines de apertura de línea no están definidos | Correcta para la exposición principal. El código sí calcula respuesta algebraica, fuerza y desplazamiento de observación; además condiciona operadores al prefijo. | Añadir derivación y tabla símbolo–rutina; no inventar un “arreglo” antes de contrastarlo con los operadores existentes. |
| Añadir términos cuadráticos diagonales no puede empeorar sin bug | Matemáticamente falsa. La curvatura diagonal puede cancelarse con la mixta. | Contraejemplo abajo; verificar derivadas y convergencia en amplitud si se retiene el estudio auxiliar, sin deducir un bug del error mediano. |
| El factor `1/(2π)` contamina el método principal | El defecto batch histórico es real; no pertenece a la integral causal R11. Existe corrección sucesora X01 con pruebas algebraicas, pero no debe confundirse con una campaña física corregida completa. | Mantener etiqueta de evidencia histórica defectuosa. Si se quiere usar para una conclusión vigente, revaluar en copia sucesora con salidas pareadas; conservar originales. |
| ExtraTrees sólo son artefactos originales del hackathon nunca reentrenados | La genealogía del comparador ejecutado contradice esa simplificación: se reutiliza la familia de features, con entrenamiento específico posterior y 19 clases. Véase anexo de evidencia. | Corregir la descripción de procedencia. Separar features heredadas, pesos entrenados y reglas del adaptador. |
| Toda la pérdida de ExtraTrees se debe a un umbral mal ajustado | No demostrado. La publicación incluye confirmación temporal de argmax; no hay un único umbral escalar que explique necesariamente todos los errores. Acertar cuando se publica es una precisión condicional, no cobertura. | Comparación nueva con entrenamiento/catálogo permitidos y calibración explícita. No retocar umbrales sobre C01. |
| Comparación a distinto coste de alarmas no prueba superioridad | Correcta. Sí mide los procedimientos congelados, pero no una ventaja arquitectónica a igual presupuesto. | Completar C02. Curvas operativas con ajustes seleccionados en CAL y examen independiente; contar omisiones y demoras. |
| Chen está fuera de sus supuestos y su fracaso no desacredita QCD | Correcta. El original usa incrementos de inyección gaussianos y una restricción de tiempo medio hasta falsa alarma. La garantía no pasa automáticamente al ruido de F01. | Conservar implementación fiel y brazo adaptado claramente separado; calibrar sólo en desarrollo y evaluar persistencias/normalidad con primer paro y censura. |
| Hay que calibrar Chen hasta obtener cero falsas alarmas | Insuficiente como criterio científico. Cero con poca exposición no certifica una tasa aceptable; un umbral infinito también produciría cero. | Presupuesto, exposición e incertidumbre previamente definidos junto con cobertura y demora. |
| Las alarmas fuera del banco R/X revelan una debilidad | Correcta. Las extras en registros con eventos no son automáticamente la tasa de falsas alarmas en operación normal. | Reportar ambas exposiciones y estratos; probar discrepancia y generalidad sin retocar F01. |
| 18 de “85 activos” demuestra selección de fuentes fáciles | El alcance es reducido, pero 39 buses + 46 ramas no define el catálogo admisible para las dos familias. No se ha demostrado selección por facilidad. Los buses 15 y 16 que Gemini ofrece como ejemplo difícil están ambos en el catálogo. | Mantener alcance acotado y diseñar una expansión/ensayo de indistinguibilidad por criterio eléctrico previo, no por éxito observado. |
| Corrientes remotas hacen físicamente inválida toda la inferencia | Excesiva. Se puede inferir con canales sincronizados de terminales distintos, si se modelan correctamente. Eso no demuestra una instalación de ocho PMU con V/I locales ni valida la identidad del CT. | Explicar agrupación de canales y alcance; ensayo sucesor con terminales colocados y operador de medida consistente para ambas partes. |
| Ruido añadido a f/ROCOF es necesariamente una contradicción | No necesariamente: compartir la trayectoria física y tener errores instrumentales adicionales son compatibles. El modelo actual sí es incompleto para reclamar coherencia instrumental o conformidad PMU. | Distinguir señal ideal, estimador causal y ruido; validar un sucesor de instrumento si se busca esa generalidad. |
| Jerga y erratas impiden entender el artículo | Muy mejoradas en el principal; quedan bibliografía y suplemento excesivo. | Limpieza final después de estabilizar la evidencia. Biografías sólo con información confirmada por autores. |

## 4. Método y matemática: correcciones concretas

### 4.1 Definir los afines y el cambio de carta

Sea la carta algebraica regular `z=ψ_q(x,u)` para cada topología, con referencia angular fijada. Definir

\[
F_q(x,u)=f_q(x,\psi_q(x,u),u),\qquad
\bar H_q(x,u)=H_q(x,\psi_q(x,u),u).
\]

Alrededor de un ancla constante `(x_*,u_*)`, que no tiene por qué ser un equilibrio del modo abierto,

\[
\delta\dot x=A_q\delta x+B_q\delta u+c_q,
\quad c_q=F_q(x_*,u_*),\quad
\delta y=C_q\delta x+D_q\delta u+d_q,
\quad d_q=\bar H_q(x_*,u_*)-y_*.
\]

Las derivadas reducidas del artículo dan `A,B,C,D`; aquí `f` se entiende como campo diferencial con la matriz de masas ya incorporada. Para un paso Δ, con entradas constantes,

\[
A_q^d=e^{A_q\Delta},\quad
b_q^d=\int_0^\Delta e^{A_q s}c_q\,ds,\quad
B_q^d=\int_0^\Delta e^{A_q s}B_q\,ds.
\]

Usar exponencial de bloque, sin exigir invertir `A_q`. Si el reporte cruza dos modos, componer `F=F_2 F_1` y `b=F_2 b_1+b_2`. Si el ancla se mueve se añade `-dot(x_*)`; si cambia de carta, `δx_nueva=δx_anterior+x_*anterior-x_*nueva`. El salto algebraico se resuelve con `x` fijo. Después se aplican los operadores instrumentales y sus offsets al estado aumentado. Estas ecuaciones son la plantilla a reconciliar con el código, no una certificación de que cualquier coordenada aumentada use literalmente la misma forma.

**Por qué importa:** un offset constante no significa que toda respuesta sea constante: `C_q δx` conserva dependencia del estado anterior. El problema es evaluar correctamente carta, prefijo y memoria; no prohibir términos afines.

**Cierre:** una tabla conecta `force`, `offset`, exponencial afín y mapas terminales con cada símbolo; pruebas ON/OFF verifican continuidad diferencial, consistencia algebraica, feedthrough, signo/orientación y escala temporal. Amplitudes pequeñas y puntos operativos de desarrollo separados comprueban convergencia local y su rango de validez.

### 4.2 Explicar exactamente la mezcla de severidad

Para intervalos disjuntos `I_j=[l_j,u_j]` que particionan `[-.2,.2]`,

\[
p(a)=\sum_{j=1}^4 \omega_j\,\mathrm{TN}_{I_j}(a;\mu_0,v_0),\quad
\omega_j=\frac{\Phi((u_j-\mu_0)/\sqrt{v_0})-\Phi((l_j-\mu_0)/\sqrt{v_0})}
{\Phi((.2-\mu_0)/\sqrt{v_0})-\Phi((-.2-\mu_0)/\sqrt{v_0})}.
\]

Cada hija tiene estado y parámetros propios. Se actualizan sus pesos con `ω_j L_j` y se suman al producir la masa de fuente. No se reemplazan por una única gaussiana al terminar cada reporte. Los operadores se comparten entre intervalos: la partición no aumenta la exactitud de una integral ya analítica. Puede alterar el resultado al interactuar con poda y propuestas.

**Cierre:** documentar esa razón operacional o reconocer que su utilidad no está aislada. Antes de poda, la integral por mezcla debe coincidir con la integral única para la misma verosimilitud afín. Después, medir diferencia de evidencia, decisión y masa descartada. Las pruebas existentes de R11/A01 ya comparan integral y cuadratura; no repetirlas como si la integral estuviera sin validar.

### 4.3 Separar incertidumbre representada y omitida

Si

\[
\xi\mid a,h,y_{1:k}\sim\mathcal N(m_h+d_h a,P_h),
\]

entonces, escribiendo `\bar a_h` y `V_{a,h}` para los **momentos truncados reales**,

\[
\operatorname{Cov}(\xi,a\mid h)=d_hV_{a,h},\qquad
\operatorname{Cov}(\xi\mid h)=P_h+d_hV_{a,h}d_h^\top.
\]

Los parámetros `μ,v` del núcleo gaussiano no son, en general, la media y varianza de la TN. Para comprimir historias con pesos `π_h` y medias `\bar\xi_h=m_h+d_h\bar a_h`, la identidad de covarianza total es

\[
P_{\rm mezcla}=\sum_h\pi_h\{P_h+d_hV_{a,h}d_h^\top+
(\bar\xi_h-\bar\xi)(\bar\xi_h-\bar\xi)^\top\}.
\]

R11 usa covarianzas por régimen y compresión de media; la descripción no debe prometer que transporta esta covarianza completa. A su vez, no debe afirmar que la dependencia con amplitud está totalmente ausente.

**Cierre prioritario:** cuantificar componentes omitidas y comparar una pequeña referencia lineal-gaussiana con Riccati conmutada por historia. Sólo si el diagnóstico muestra degradación material, implementar un sucesor con `P_{h,k}` y compresión por momentos. No cambiar el núcleo activo de B01 ni exigir complejidad nueva antes de medir su necesidad.

### 4.4 Innovaciones y calibración

La identidad

\[
p(y_{1:T}\mid h)=\prod_k p(y_k\mid y_{1:k-1},h)
\]

no supone independencia marginal de los reportes. Lo exigible es que el factor usado represente suficientemente bien la predicción condicionada. El código ya contiene blanqueo VAR/AR instrumental y estados AR de discrepancia: agregar otro AR por recomendación genérica puede duplicar correcciones.

Registrar por hipótesis/régimen, antes de observar el reporte que se puntúa:

- innovaciones estandarizadas, autocorrelación y correlación entre canales; diagnóstico portmanteau con incertidumbre por trayectorias, no una prueba por canal interpretada sin multiplicidad;
- NIS frente a la dimensión efectiva, con referencia empírica cuando hay selección, priors truncados o covarianza estimada;
- cobertura de severidad a varios niveles y anchura de intervalos, incluyendo cercanía a límites;
- log-score/Brier y diagramas de fiabilidad para eventos con definición probabilística explícita; no tratar automáticamente masa activa como probabilidad de corrección de fuente;
- error de predicción tras ON/OFF y pérdida de dispersión al cierre; efecto de doblar el tamaño del banco en un subconjunto de desarrollo fijado previamente.

**B01 no cierra todo esto:** ajusta varianzas diagonales por campo y régimen, recalcula DARE/ganancias y mantiene AR. Puede mejorar puntuación/operación sin eliminar dependencia temporal ni calibrar todos los pesos. El diagnóstico existente `forecast_innovation` usa la posterior corriente; no debe confundirse con la predicción anterior al reporte. Instrumentar la auditoría en el punto causal adecuado, conservando cualquier salida histórica.

### 4.5 Corregir la interpretación del estudio cuadrático

Contraejemplo suave exacto:

\[
f(a,b)=a+b+a^2+b^2-1.5ab.
\]

Para `a=b=.1`, error absoluto lineal `0.005`; al agregar sólo los cuadrados, `0.015`; al agregar el término mixto, `0`. Por ello la observación de Gemini no demuestra coeficientes corruptos.

Se ejecutó `check_mathematical_claims.py`: el contraejemplo pasa y una integral TN ilustrativa coincide con cuadratura y mezcla de cuatro intervalos a error relativo inferior a `3e-16`. Son comprobaciones de identidad matemática, **no validación del tensor empírico ni una ejecución de R11**. Si el estudio auxiliar se conserva como afirmación actual, verificar signos/factores de Hessiano mediante diferencias centrales y curvas de error al reducir conjuntamente amplitudes.

### 4.6 Teoría útil, limitada y contrastable

La identidad local de recuperación del artículo ya explica el error de reset:

\[
\Delta y(t)\simeq C_0(t)\Phi_0(t,\kappa)\delta x(\kappa).
\]

La ampliación que vale la pena es relacionar esa respuesta con la confundibilidad de nuevas fuentes, manteniendo los supuestos explícitos. Para firmas `s_i(a),s_j(b)`, covarianza temporal `Σ` y direcciones de contexto `N`, estudiar

\[
d_{ij}^2=\min_{a,b,\eta}
\|s_i(a)-s_j(b)-N\eta\|_{\Sigma^{-1}}^2.
\]

Con nuisance libre, la métrica residual usa

\[
W_\perp=\Sigma^{-1}-\Sigma^{-1}N
(N^\top\Sigma^{-1}N)^\dagger N^\top\Sigma^{-1}.
\]

Con restricciones físicas se resuelve el mínimo restringido. Aumentar el espacio libre de nuisance no puede aumentar esta distancia; no equivale a decir que más memoria siempre empeore o mejore la decisión. La separación es un diagnóstico local, no una cota certificada de error del banco podado.

**Prueba:** fijar en desarrollo una relación entre distancia, energía de recuperación y error/demora; verificarla en fuentes/condiciones retenidas. Comparar decisiones y riesgo frente a cobertura si se introduce abstención. No agregar un teorema de identifiabilidad global, una garantía bayesiana o un resultado de tiempo real sin demostrar sus supuestos.

## 5. Plan de ejecución por dependencias

| Paso | Trabajo y entregable | Dependencia | Criterio para cerrarlo |
|---|---|---|---|
| P0. Contrato/versiones | Fijar pregunta, alcance, versión revisada y registro crítica–evidencia. | Esta auditoría. | Ningún cambio ya realizado se presenta como pendiente; originales y fuentes preservados. |
| P1. Exposición matemática | Añadir afines, intervalos, momentos condicionales y aproximaciones; mapa de rutinas y orden causal. | Código congelado; sin nuevas simulaciones pesadas. | Un lector puede reconstruir un paso ON/OFF y la mezcla; ecuación, código y test concuerdan. |
| P2. Cerrar B01 | Dejar terminar la campaña activa y revisar una sola evaluación sellada A0/A1/A2. | Estado actual observado: `a2_cal`, `RUNNING`. | Resultados completos, fallos y costes; ninguna conclusión a partir de parciales; no cambiar plan/modelo tras TEST. |
| P3. Completar C02 | Integrar preparación física/exportación, banco nominal, GLR, ExtraTrees, CAL y evaluación; comprobar paridad en desarrollo. | Sin lanzar física hasta B01 completo y exclusividad/recursos verificados. | Pipeline completo, catálogo cubierto y umbrales congelados antes de TEST; todas las filas/replicas con denominador definido. |
| P4. Diagnóstico de incertidumbre | Auditoría de innovaciones, severidad, poda/compresión y referencia con covarianza por historia. | Primero desarrollo aislado; datos nuevos si se ajusta método. | Mecanismo de mala calibración identificado o acotado; cualquier corrección evaluada en sucesor independiente. |
| P5. Generalidad física | Contraste acotado de instrumento/terminales y modelo dinámico independiente; fuentes difíciles elegidas por distancia eléctrica. | Protocolo nuevo antes de resultados; capacidad verificada del simulador. | El beneficio persiste con incertidumbre cuantificada o se reduce explícitamente la afirmación. Fallos de física no se sustituyen por casos fáciles. |
| P6. Artículo y suplemento final | Reescribir sólo lo que cambió con la evidencia; separar suplemento esencial del archivo histórico. | Resultados anteriores completos. | Cada contribución tiene prueba correspondiente; tablas generadas, PDFs verificados y citas vigentes; figuras protegidas intactas. |

P1 y preparación de P3 pueden avanzarse mientras B01 corre. P4 se diseña sin tocar sus outcomes parciales. P5 no requiere abrir RAW0002. No es razonable prometer días de cómputo sin medir el pipeline completo: B01/C02 son el camino crítico, y las pruebas de planta independiente pueden costar más que la edición.

### B01: qué responde y qué no

Tiene 72 padres nuevos, separados 24/24/24 en TRAIN/CAL/TEST. Compara configuración original, cambio de umbral y likelihood aprendido con el mismo umbral seleccionado. No compara ExtraTrees, no es exclusión de fuentes y no aísla covarianza exacta por historia.

Con cero alarmas en `T` horas, el límite superior unilateral Poisson del 95% es `-log(.05)/T`. En 1,96 h resulta **1,528/h**: B01 tiene objetivo puntual de 1/h, no certificación a ese nivel. No reinterpretar su plan después del resultado.

### C02: la prueba central ya preparada

Su diseño contiene 102 padres: 24 TRAIN, 36 CAL y 42 TEST. Compara observador continuo GLR, banco nominal de historias y ExtraTrees nuevo con todas las fuentes. El banco nominal permite que la comparación de mecanismo no reciba la ventaja adicional de cinco modelos de red.

CAL tiene 3,92 h normales monitorizadas: cero alarmas da límite Poisson **0,764/h**, bajo el modelo de conteo declarado. Ese límite es criterio de selección, no garantía independiente después de buscar umbral. El TEST debe medir la tasa realizada con intervalo y exposición; tratar agrupación temporal/noise replicas de forma adecuada.

Antes de ejecutarlo hay que resolver explícitamente cómo los dos niveles de ruido entran al selector: `select_cal` exige una fila por padre y umbral. No duplicar exposición como si las replicas fueran plantas independientes. Fijar si el gate es por nivel o una agregación predeclarada, sus denominadores y manejo de fallos. Esto es una verificación pendiente de integración, no un fallo empírico ya observado.

La calibración del GLR exige ejecutar cada umbral secuencialmente, pues las decisiones afectan el estado posterior. Un barrido sobre puntuaciones guardadas sólo es válido cuando el umbral no cambia la trayectoria interna; verificar esa propiedad también en los otros brazos.

**Resultado que sostendría la afirmación fuerte:** ventaja de atribución oportuna con intervalo pareado a nivel de padre y presupuesto de alarmas cumplido; efectos reportados por familia, mismatch y recuperación. El margen mínimo relevante y cualquier no inferioridad deben fijarse antes de TEST, no inventarse al ver el resultado. La ausencia de diferencia significativa no demuestra equivalencia.

**Si GLR o ExtraTrees empatan o ganan:** conservar el resultado y reformular el artículo como caracterización reproducible del valor de la continuidad física y de sus condiciones. No buscar buses, umbrales o semillas que recuperen superioridad.

### Chen: comparación secundaria que debe ser defendible

El [artículo original de Chen et al.](https://people.ece.ubc.ca/chen/papers/journal/07041234.pdf) plantea cambios persistentes e incrementos de inyección gaussianos, y selecciona el umbral por tiempo medio hasta falsa alarma. Mantener ese dominio de evaluación. Añadir un sucesor con escala/blanqueo/umbral ajustados sólo en desarrollo si se conserva como contraste operativo destacado. Etiquetar las modificaciones y verificar de nuevo las densidades postcambio: filtrar sólo los datos no basta.

Normalidad y persistencia requieren primer paro, identificación, stops prematuros, demora y censura. No comparar automáticamente ARL de un detector que para con extras/h de un detector recurrente. No usar las 72 normales ya examinadas de C01 para seleccionar una nueva configuración y llamarla confirmatoria.

## 6. Qué exigir para calidad alta en cada dimensión

| Dimensión | Evidencia de cierre propuesta |
|---|---|
| Pregunta y valor | Una pregunta operacional precisa: nueva intervención durante recuperación; distinguir detección, fuente y cierre. |
| Originalidad/literatura | Diferencia concreta respecto a IMM/M3H y trayectorias físicas; ventaja del banco sobre control continuo o alcance limitado explícito. |
| Matemática/física | Afines, salto, estado aumentado, mezcla TN y covarianzas definidos; correspondencia con código y controles numéricos. |
| Reproducibilidad | Manifiestos, entornos, splits, configuraciones, métrica y generación de tablas; ejecución desde copia limpia y ruta NAS documentada donde corresponda. |
| Diseño/fugas | TRAIN/CAL/TEST por padre; límites de información explícitos; nada de selección mediante resultados de test. |
| Baselines/ablaciones | C02 terminado, reglas calibradas, mismo catálogo y PMU; A01 conservada con su intervención precisa; Chen contextualizado/adaptado donde proceda. |
| Estadística | Intervalos por padre, tasas con tiempo monitorizado, censura/omisiones y exposición normal suficiente; distinguir selección CAL de evaluación TEST. |
| Incertidumbre | Innovaciones y cobertura evaluadas; pesos aproximados nombrados como tales; abstención sólo con riesgo–cobertura verificado. |
| Generalidad | Sensibilidad a modelo/planta/instrumento y catálogo; ninguna extrapolación a campo, fallas o generación a partir de cargas/líneas. |
| Resultados/fallos | Mantener empate marginal/perfil, regresión R/X, costes y fallos completos; identificar dónde cambia la conclusión. |
| Escritura/visuales | Principal autónomo, una historia científica; suplemento necesario, archivo histórico aparte; dos figuras protegidas presentes y legibles. |
| Integridad de afirmaciones | Título, resumen, figuras y conclusión describen exactamente el método evaluado; no llamar tiempo real a una implementación cuya inferencia mediana supera la duración del registro. |

El coste vigente merece atención: la tabla principal registra mediana de inferencia de 358,7 s para registros de 120 s. Tener decisiones en timestamps causales no significa procesarlas en tiempo real. Optimización sólo pasa a prioridad principal si se quiere reclamar esa capacidad; medir percentiles por reporte, cola, memoria y hardware antes de prometerla.

## 7. Cambios que no recomiendo

1. No añadir GNN, Transformer, cuaterniones, una nueva factorización tensorial o un “teorema de Bayes” para aumentar apariencia de novedad.
2. No borrar resultados incómodos ni hacer que el suplemento esconda un bug vigente. Separar archivo histórico de evidencia científica usada en el artículo.
3. No exigir todas las familias de evento y todos los activos como condición automática para publicar un estudio acotado. Ampliar sólo para sostener la generalidad que se quiera reclamar.
4. No sustituir F01 en silencio por medición colocada o ruido distinto. Todo cambio físico/instrumental requiere candidato sucesor y procedencia; BUS5 mantiene 5–6 provisional en F01.
5. No cambiar C01/A01 ni usar sus resultados para seleccionar modelos y presentar el resultado como confirmatorio. B01 se conserva; C02 no se lanza durante B01.
6. No abrir RAW0002, enviar a coautores/revista ni publicar cambios como parte de esta auditoría.

## 8. Evidencia y alcance de esta revisión

Se leyeron revisión adjunta, fuentes activas del principal/suplemento, historia Git, resultados/tablas congeladas y código pertinente de operadores, filtros y comparadores. Hubo tres revisiones independientes: técnica, experimental/reproducibilidad y editorial. No se ejecutaron campañas, no se accedió a resultados parciales de B01 y no se realizó una nueva auditoría visual página por página. La verificación PDF fue de contenido/metadatos e inclusión de secciones. Se realizaron sólo las comprobaciones matemáticas pequeñas adjuntas.

Fuentes principales de repositorio:

- `main.tex:33–75`, `metadata.tex:4`, `sections/article_intro.tex:39–67`: versión y contribuciones.
- `sections/article_method.tex`: operadores, integral, covarianzas, regla de publicación, mezcla y poda.
- `sections/article_ablation_design.tex` y `sections/article_controlled_ablation.tex`: alcance de la ablación.
- `sections/08c_c01_confirmatory.tex`, `sections/narrative_results.tex`, tablas generadas: resultados y controles.
- `sections/article_interpretation.tex`, `sections/narrative_problem.tex`: límites e instrumento.
- `supplement.tex:247–250`, `sections/article_ei_x02.tex`: estudios auxiliares realmente incluidos.
- `docs/SCIENTIFIC_AUDIT_RESPONSE_20261103.md` y `docs/P07_VALIDATION_ACTIONS.md`: trabajo anterior que se conserva; esta auditoría lo amplía, no lo reinicia.
- Repositorio científico hermano: `experiments/PAPER_CALIBRATION_B01/README.md`, `protocol/PLAN.json`, `run/PIPELINE_STAGE.json`; `experiments/PAPER_RECOVERY_C02/protocol/PLAN.json`, `protocol/calibration.py`, `run/STATUS.json`.

Fuentes externas primarias consultadas, con papel acotado:

- [IEEE Access, criterios para revisores](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/): solidez, contribución, evidencia y lenguaje; la nota decimal no es su rúbrica oficial.
- [Chen et al., texto de los autores](https://people.ece.ubc.ca/chen/papers/journal/07041234.pdf): modelo de incrementos, persistencia, CUSUM y umbral bajo su distribución.
- [Boers y Driessen, M3H, registro editorial](https://www.sciencedirect.com/science/article/pii/S0005109804003243): antecedente de filtrado de sistemas conmutados; no se atribuye a P07 la invención de historias de modos.
- [Warner y Fellouris, Adaptive Matrix CuSum](https://www.imstat.org/publications/bej/bej_30_3/bej_30_3.pdf): referencia primaria para diagnóstico secuencial y separación de error de identificación/demora; no baseline nuevo ejecutado.

No se subió el manuscrito a un servicio externo.

## 9. Anexo de trazabilidad técnica

Las rutas de esta tabla son relativas a `SGSMA26-Physics-Informed-AD/`, salvo las indicadas como P07. Los números de línea corresponden a los archivos inspeccionados durante la auditoría.

| Hallazgo | Evidencia concreta |
|---|---|
| Constructor y runtime realmente usados | `experiments/PAPER_CONFIRMATORY_C01/execution/common.py:4–6`, `execution/worker.py:22–33`. |
| Álgebra con estado diferencial fijo, fuerza y medición por topología | `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/physics/build_static_rx.jl:51–59`, `:72–75`, controles `:93–95`. |
| Offset, exponencial afín y aumento AR | Mismo directorio, `native_conditional_builder.py:34–58`, `:70–82`, `:91–98`; Riccati por régimen `:111–117`. |
| Dependencia del prefijo | Mismo directorio, `static_bank.py:79–87`: relinearización por punto operativo estimado. |
| Cuatro historias/segmentos | `experiments/PAPER_CONFIRMATORY_C01/run/runtime/core_v6.py:48–50`, `retro_birth.py:12`; actualización `core_v6.py:118–126`. |
| Momentos y dispersión | `core_v6.py:115–126`, `:143`, cierre `:167–168`; existe dependencia afín y se registra dispersión omitida. |
| Blanqueo instrumental ya presente | `experiments/PAPER_CONFIRMATORY_C01/run/runtime/instrument_parent.py:20–41`. |
| Entrenamiento de ambos ExtraTrees | `experiments/E5_VALIDATION_PAPER/M03_R09_NUISANCE_DEV/ml/README.md:3–6`, `run.py:53–62`, `COMPLETE.json`: 32 padres TRAIN, ocho validación; ambas variantes incluyen las 19 clases. |
| Reglas de publicación de ExtraTrees | Mismo directorio, `infer.py:19` y `causal_ml.py:15–24`: argmax y seis etiquetas consecutivas, sin el supuesto umbral escalar único. |
| Congelación ML | `experiments/PAPER_CONFIRMATORY_C01/references/R11_FREEZE.json:1179–1204`; se verificaron hashes de adaptador, inferencia, entrenamiento y dos modelos. |
| Defecto batch y sucesor | `experiments/PAPER_METHOD_DICE_X01/kernels.py:52–61`; `run_checks.py:41–45`; `RESULTS.md:19`: normalización corregida, replay físico pendiente. |
| Pruebas algebraicas existentes | `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/observer/test_preflight.py:21–27`; `experiments/PAPER_ABLATION_A01/test_ablation.py:13–28` y `checks/UNIT_TESTS.json`. |
| Contenido realmente compilado | P07 `main.tex:63–75` y `supplement.tex:247–250`; X02 está en el suplemento. |
| Erratas vigentes menores | P07 `references.bib:612` y `:661–663`: notas redundantes de preprint. |

La tabla de genealogía pendiente debe distinguir cuatro entidades: entrega original de hackathon; modelos causales R09 reentrenados usados en C01; sucesor S01; futuro C02. Los conteos de features históricos no describen automáticamente los modelos evaluados. BASELINE usa 846 características; SHORT añade 611, para 1.457. No confundir esta corrección de procedencia con una demostración de comparación perfectamente equiparada.

Otra corrección documental puntual: P07 `docs/c01-confirmatory-results.md:18` conserva la exposición histórica de 120 s, mientras el principal ya usa 108 s monitorizados. Etiquetar ambas unidades/procedencias para que no parezcan cifras incompatibles. No alterar conteos, episodios ni intervalos originales.

Las comprobaciones de implementación de Chen bajo su ley propia incluyen 299/300 identificaciones posteriores correctas, una parada temprana y 0/100 normales hasta un horizonte finito (`comparator/MATCHED_SUMMARY.csv`, bajo C01). Eso ayuda a separar implementación y transferencia; no prueba el ARL completo ni resuelve el comportamiento en F01.
