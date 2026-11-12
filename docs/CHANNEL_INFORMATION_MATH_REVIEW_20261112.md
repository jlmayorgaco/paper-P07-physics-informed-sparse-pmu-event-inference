# Revisión matemática independiente: diagnóstico de canales P07

Fecha: 2026-11-12
Alcance: auditoría del formalismo de `sections/article_theory.tex`, de la propuesta externa en `docs/EXTERNAL_PHYSICS_INTEGRATION_20261112.md` y, cuando esté disponible, del código/artefactos del diagnóstico nominal V/VI/all. No se modifican estimadores ni C03. La auditoría de código queda pendiente de la entrega del agente implementador.

## Dictamen provisional

La descomposición de Schur del documento externo es una identidad correcta bajo sus condiciones: medias fijas, covarianza conjunta común SPD y la misma partición de observaciones. No implica por sí sola una mejora estadística del detector ni una nueva teoría de observabilidad. La afirmación segura es que, bajo el modelo nominal, el bloque I añade una cantidad calculable de separación condicional a V para las hipótesis, ventanas y covarianza especificadas.

La fórmula de firma del artículo, `Lambda_ij`, es una energía residual determinista perfilada en coordenadas de innovación del filtro de la historia candidata. Puede usarse como diagnóstico retrospectivo tal como se describe, pero no es en general la KL gaussiana entre historias ni una comparación pareada simétrica: usa `S_j`, no incorpora los términos de covarianza si los modelos difieren, y el perfilado determinista no equivale a integrar o estimar severidad desde datos ruidosos. El propio texto reconoce las dos últimas limitaciones; cualquier lectura de la nueva figura deberá conservarlas.

## Identidades y condiciones

Con `d = (d_V,d_I)` y una covarianza conjunta común

`Sigma = [[Sigma_VV,Sigma_VI],[Sigma_IV,Sigma_II]]`,

la factorización triangular de la forma cuadrática es exacta:

`d' Sigma^{-1} d = d_V' Sigma_VV^{-1} d_V + (d_I-Sigma_IV Sigma_VV^{-1}d_V)' S^{-1}(d_I-Sigma_IV Sigma_VV^{-1}d_V)`,

con `S = Sigma_II-Sigma_IV Sigma_VV^{-1}Sigma_VI`. Por tanto las contribuciones `1/2` de ambos lados suman el Mahalanobis conjunto. Es una medida de separación entre dos medias fijas. El término segundo es la separación adicional de I condicionada a V, no la separación marginal de I.

Condiciones de validez para un diagnóstico con canales reales:

- `Sigma` debe corresponder a la covarianza de todo el vector de reportes empleado, incluidos bloques temporales. Usar bloques marginales por reporte solo es equivalente si la transformación a innovaciones blanquea exactamente el vector completo y se conserva su covarianza/normalización.
- La matriz debe ser SPD en el subespacio observado. Frecuencia y ROCOF derivados pueden hacerla singular o casi singular; entonces se necesita una representación de rango reducido/pseudodeterminante y declarar el subespacio, o regularización justificada. No aplicar inversas SPD silenciosamente.
- Para medias con covarianzas diferentes, la divergencia esperada bajo `i` respecto de `j` incluye traza, dimensión y log-determinante. La identidad de Schur sola solo descompone el término cuadrático usando una covarianza común elegida; no reparte por sí sola la KL completa.

## Perfilado de severidad y nuisances

Si `d(a)=d_0+a g` representa dos firmas comparadas con una severidad compartida, el perfil conjunto debe minimizar el Mahalanobis conjunto sobre el mismo dominio admisible. La partición de Schur sigue siendo aditiva para cada `a`, pero los dos términos evaluados en `a*_conjunto` no son, en general, iguales a `min_a` de cada término por separado. Restar dos mínimos (V+I y V), o calcular el residuo condicional con un `a` distinto, no produce una contribución condicional aditiva.

El contrato físico importa: carga con severidad acotada/no negativa debe usar ese intervalo; apertura de línea es un operador/topología fija, sin ajustar una amplitud real de cualquier signo. Si el implementador usa el perfil de las firmas existentes de `Lambda_ij`, ha de describirlo como perfil de forma nominal con el contrato específico, no como KL si no reproduce marginalización/score del filtro.

Con covarianza común fija y diseño anidado, agregar observaciones correctamente modeladas no puede reducir el Mahalanobis conjunto ni la distancia perfilada si se optimiza el mismo nuisance sobre el mismo conjunto factible. Esta monotonía puede servir de control numérico. No garantiza que un estimador online con umbrales, propuestas, cuantización o covarianzas reestimadas mejore cobertura o falsas alarmas.

## Innovaciones del filtro y comparación V / VI / all

Una secuencia de innovaciones Kalman bien formada es una transformación triangular de la secuencia observada. Su densidad conserva exactamente la log-verosimilitud si se usan en cada prefijo la media predictiva, la covarianza de innovación correcta y los términos `log|S_k|`. Por ello, sumar energías `e_k' S_k^{-1} e_k / 2` es el término cuadrático de una puntuación bajo ese filtro; sin logdet/traza no es una divergencia completa y con `S_k` de un solo candidato no es la información condicional de añadir sensores.

Para probar valor incremental de corrientes hay dos opciones coherentes:

1. Comparar medias con la covarianza conjunta nominal/fijada y aplicar la Schur sobre el vector temporal apilado; usar los mismos candidatos/severidad a ambos lados.
2. Ejecutar filtros reconstruidos con submatrices/covarianzas correctas para V, V+I y V+I+f+ROCOF, y comparar sus puntuaciones de decisión bajo una calibración separada y presupuesto común. La ablación debe quitar/reordenar canales tanto de observaciones como de covarianza, y recalcular la inferencia; poner señales en cero no es equivalente.

La innovación de V+I no es «innovación V concatenada con innovación I» salvo que se transforme la covarianza con los bloques cruzados correctos. Si V,I,f,ROCOF comparten fase o errores de estimación, asumir independencia puede inflar artificialmente el término condicional de I. La repetición temporal induce además correlaciones por el modelo de sensor/filtro; los bloques completos deben mantenerlas.

## Líneas, feedthrough y salto algebraico

La reducción dinámica `K = C Phi B` solo describe la ruta de estado. Si la eliminación de restricciones algebraicas hace que la salida dependa directamente de la entrada, debe figurar `D delta(t-s)` (o la convención discreta equivalente). Para una carga, el cambio de potencia puede cambiar el estado algebraico en el mismo reporte. Para una apertura de línea cambian la topología y las ecuaciones de restricción: la trayectoria necesita operadores pre/post, regla explícita de continuidad/reset para estados diferenciales y solución algebraica post-switch. No sustituir ese cambio por una columna genérica `B` ni extrapolar una continuidad completa de todas las coordenadas.

El artículo debe distinguir salto de magnitudes algebraicas de continuidad de estados dinámicos. Si los canales se toman después del switch, una firma observada puede contener el feedthrough implícito del operador switched aunque no se incluya una delta distribucional literal en la discretización; la documentación debe indicar cuál convención usa el predictor nominal.

## Tesis integradora defendible

Una contribución defendible y acotada sería una explicación física-estadística de atribución durante recuperación: las firmas nominales condicionadas por el estado continuo y por el operador switched explican cuándo una intervención nueva es distinguible mientras la anterior aún recupera; un diagnóstico de Schur identifica si las corrientes aportan separación condicional dado el voltaje bajo covarianza conjunta calibrada; el contraste con fallos reales del banco muestra si esa separación anticipa decisiones erróneas. La evidencia de diagnóstico debe congelarse en DEV y contrastarse con errores sin elegir pares después de leer TEST.

La novedad no sería la identidad de Schur, las ecuaciones de red, Kron ni Group LASSO. Si solo se muestran firmas deterministas, la afirmación se limita a explicación nominal retrospectiva. La expresión «explica la atribución» requiere asociación previa de pareja/horizonte con errores del procedimiento desplegado y contraejemplos; no una causalidad ni una garantía universal.

## Auditoría de implementación y resultados

Pendiente: agente `nominal_channel_evidence` aún no ha compartido ruta ni resultados. Al recibirlos verificaré: (i) identidad de operadores/canales F01 y ordenamiento V/I/f/ROCOF; (ii) forma y PSD/rango de covarianzas, incluidos términos cruzados temporales; (iii) solución triangular frente a inversas explícitas; (iv) acuerdo Schur vs Mahalanobis apilado; (v) mismo perfil de nuisance en total y bloques; (vi) convenio de línea/severidad y feedthrough; (vii) que innovaciones completas se obtengan con filtros reconfigurados y no con datos anulados; (viii) denominadores y etiquetas no filtrados por error.

## Alcance operativo confirmado para la auditoría

El responsable confirmó que puede leerse/copiarse de forma inmutable el primer banco CAL C03 terminado, `C03_a1adb9f9adcf_nominal`, para evitar reconstrucción. El sucesor es un diagnóstico posterior con banco nominal F01 y prefijo; no es un resultado de C03. No se accede a TEST ni se modifican artefactos C03.

Prioridad al revisar el código: obtener medias físicas switched del banco y hacer explícita la covarianza nula común apilada de reportes. Si el artefacto produce innovaciones, verificar el mapeo lineal triangular desde reportes y la covarianza transformada; si no, limitar el resultado al primer muestreo/one-step con Σ común allí declarada. Perfiles de competidores distintos se informan como scores deterministas; no llamarlos KL de banco completo.

### Control independiente de covarianza temporal (ejemplo escalar)

Para detectar una implementación que omite cruces temporales, evalué un caso conocido de tres reportes con `T=0.5`, `J=K=1`, `S=2`, estado inicial fijo y `e_t` blanco. La matriz causal es

`L = [[1,0,0],[1,1,0],[0.5,1,1]]`,

por lo que `Gamma=L(2 I)L' = [[2,2,1],[2,4,3],[1,3,4.5]]`. Para `d=(1,-1,0.5)`, el Mahalanobis apilado es 4.5; la suma marginal con covarianza temporal equivocadamente diagonal es 1.125. La evaluación triangular `||L^{-1}d||²/S` coincide con 4.5. Partir el primer reporte del resto y aplicar el Schur complement también da 4.5. Este control es una identidad sintética independiente, no evidencia sobre F01; aplicaré el mismo patrón al código del sucesor y al menos una matriz de canales/covarianza real.

## Auditoría del script de canales (versión visible 2026-11-12)

Revisé `experiments/channel_information_20261112/run_channel_diagnostic.py`, la copia compacta de banco y el runtime R11/C03.

### Correspondencia de canales y operadores

El orden usado por el script está sustentado por `runtime/instrument_parent.py` y `core_v6.py`: el observador concatena seis familias en orden `voltage_magnitude`, `voltage_angle`, `current_magnitude`, `current_angle`, `frequency`, `rocof`, con tamaños 8, 8, 8, 7, 8, 8. Así los intervalos 0:16 (V), 0:31 (V+I), 31:47 (f+ROCOF) sí corresponden al runtime de 47 coordenadas; la séptima coordenada de ángulo de corriente está documentada en `runtime/boundary.py` como recorte a 7.

La indexación por fuente también concuerda con `native_conditional_builder.py`: fila 0 normal; cada fuente agrega una fila `stay` y cuatro filas que alternan `on`/`off` para dos posiciones dentro del reporte. `operator_index` elige `on0=2+5c` al primer reporte y `stay=1+5c` después. La ecuación de `event_mean` conserva el estado y resta la salida normal. Las líneas están representadas por el operador switched fijo, no por una amplitud escalar: comprobé en el snapshot que `u` y `v` son exactamente cero en las 45 filas de las nueve líneas, mientras `g` y `j` registran efectos no nulos. Por ello `amp=0` para líneas es correcto; `LINE_OPENING_AMPLITUDE=1.0` es solo anotación. En las filas normales `g,j,u,v` también son cero.

### Covarianza común y control independiente

Bajo el modelo normal `m[k+1]=T m[k]+K e[k]`, `y[k]=J m[k]+e[k]`, `e[k]` blanco con `S`, y `m[0]` condicionado/fijo, la recursión del script es correcta. Construye las autocovarianzas de salida mediante `P_{k+1}=T P_k T'+K S K'` y `Cov(y_l,y_k)=J Cov(m_l,y_k)`. El snapshot contiene `S` y `Sinv0` consistentes (`max|S Sinv0-I|=8.9e-16`). Una reconstrucción densa independiente para tres reportes dio `min eig Gamma=0.8943`; la verificación raw-vs-innovations guardada en el artefacto coincide a precisión flotante. Condiciones de correlación del bloque escalado a horizonte 30 fueron aproximadamente 7.64 (V), 26.81 (V+I), 26.81 (all), así que los valores muy altos de D² observados no se explican de inmediato por una matriz casi singular.

El error Schur publicado `1.43e-6` es absoluto sobre D² máximos de aproximadamente `2.78e9`, o del orden de `5e-16` relativo. El gate debe comparar error relativo/reescalado, además de absoluto con escala adecuada.

### Corrección necesaria antes de aceptar artefactos

La versión inicial indexaba `rows[h*306+q]`, incorrectamente usando cantidad de reportes como índice de horizonte y quedando fuera de rango. El propietario ya indicó que lo sustituyó por `horizon_index*306` y vectorizó la descomposición; eso corrige el mapeo si la generación mantiene orden de horizontes y pares, que el script actual sí hace. La corrida presente en el árbol parece haberse generado antes de añadir gates; no debe tratarse como artefacto final hasta reejecutar y registrar el código/hash vigente.

En la versión revisada vi cálculos de errores, pero aún faltaban `assert`/fallos duros antes de escribir CSV/JSON. La aceptación requiere gates de error recursión-vs-transformación explícita, raw-vs-innovations, Schur relativo, mínimo autovalor/Cholesky de `S` y de bloques, incremento condicional no negativo (salvo tolerancia) y monotonicidad anidada. Los checks no deben aparecer como literales `True` sin derivación.

### Alcance interpretativo

El cálculo actual usa diferencias de medias fijas: amplitud de carga 0.10 para todas las cargas y apertura completa para líneas. No perfila amplitud competidora ni calcula la marginalización/score del banco real. Por tanto presenta una comparación nominal idealizada condicionada a esos ajustes, no `KL` del banco, no separación perfilada y no evidencia de mejora de decisiones. Las parejas dirigidas (18×17) son un catálogo exhaustivo de ese conjunto finito, no 306 observaciones independientes ni soporte para intervalos de confianza ingenuos.

La nota en el código sobre feedthrough aplica a eventos de línea: el offset `j[op]`, el estado `g[op]` y la salida switched están presentes en los operadores discretos. La justificación del operador switched viene del banco compactado y su constructor; el diagnóstico no agrega una respuesta continua `D delta` separada. Por eso la lectura debe permanecer «firma nominal de reporte después de cambio» y no atribuir una regularidad temporal de salida que el modelo no representa.

**Estado:** la inspección matemática está hecha; falta confirmar la versión final que contiene gates y contrastar sus métricas/hash posteriores a la reejecución antes de cerrar la auditoría de código.

### Cierre de revisión de la corrida con gates

El agente entregó una corrida con el índice de filas corregido por `horizon_index*306`, Schur vectorizado y gates previos a escribir CSV. Los checks guardados son: error relativo de Γ frente al transform explícito `5.95e-16`; Mahalanobis raw frente a innovaciones completas `3.06e-15`; error relativo Schur máximo `1.35e-11` (error absoluto `1.43e-6` en valores D² hasta `2.78e9`); identidad `S Sinv0` `8.88e-16`; incremento condicional mínimo 5.49; todas las distancias anidadas monotónicas. Los gates usados rechazan escritura si falla alguno de esos puntos. El Schur masivo es numéricamente estable para estos valores.

Revalidé de forma independiente hashes del script, snapshot y ambos CSV frente a `diagnostic_summary.json`; todos coinciden. La generación de salida corresponde al script visible (`6da8d960…af1c`). El snapshot mantiene el hash del banco fuente y metadatos de acceso solo CAL/nominal, sin TEST ni truth; se leyeron solo arreglos compactos del banco congelado.

La interpretación sigue siendo deliberadamente estrecha: los 306 pares dirigidos son puntuaciones cuadráticas deterministas con media fija (load=0.10; línea full-open), la misma covarianza nula quiet de reportes apilados, no resultados de filtro recalibrado, no marginalización/perfilado de severidad y no 306 réplicas independientes. El vínculo a errores del estimador es una pregunta futura, no resultado de esta corrida. El feedthrough de línea está implícito en el operador de reporte switched discreto; no hay término de respuesta continua separado.

Queda una mejora de auditabilidad solicitada al implementador: hacer explícita como gate y en el JSON la propiedad `u=v=0` para las filas de líneas, y presentar el estado PD por el éxito del Cholesky/gate, en vez de un boolean literal. Es un control de procedencia/modelo, no una objeción a la fórmula: ya comprobé independientemente que los u/v de las nueve líneas son exactamente cero en las 45 filas del snapshot y que `S` admite Cholesky. Hasta que ese check quede registrado, la matemática de la corrida es aceptable pero ese detalle debe constar en el informe.

### Estado final tras la última regeneración

El agente incorporó los dos controles pendientes: `max(|u|,|v|)=0` en los operadores de las nueve líneas (también aparece en el JSON), y `S_positive_definite` se registra solo después de que `cholesky(S)` se completa. El JSON además marca explícitamente que las medias están condicionadas a amplitudes/operadores fijos y que no se perfiló nuisance. Revalidé otra vez hashes del script, snapshot y CSV; los cuatro coinciden con la última metadata. Todos los gates declarados pasan. La revisión matemática de la implementación queda cerrada con la limitación interpretativa anterior.
