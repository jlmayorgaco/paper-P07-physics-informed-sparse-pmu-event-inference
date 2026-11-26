# DICE-PMU X01: método candidato y experimentos derivados de la revisión

Fuente: conversación de revisión compartida por el usuario,
https://chatgpt.com/share/6ae4eff8-00c4-83ea-812f-d5afe8c2f774,
leída el 30-oct-2026 (14 mensajes, siete respuestas). Es una propuesta y
crítica del usuario/LLM, no evidencia experimental ni autorización para
reescribir C01. El manuscrito revisado allí tenía 19 páginas; el P07 actual
ya separa la inferencia causal R11 del banco batch E_B.

## Decisión científica

Se preservan R11, nominal, E_B/GH31, F01 y C01. X01 es un candidato nuevo.
No se añade otro nombre al método congelado. El giro investigable es que
el estado incierto de operación cambie la **firma** de una intervención,
además de su línea base, y que esa dependencia forme parte de la evidencia.
No existe aún validación física de ese giro. Sí se ejecutaron pruebas
algebraicas y de implementación, documentadas al final.

## Modelo físico condicionado

La planta y la medición conservan su contrato:

\[
\dot x=f_q(x,z,u;\theta),\quad 0=g_q(x,z,u;\theta),\qquad
y_k=\mathcal M_q(x_k,z_k;\theta_M)+\epsilon_k.
\]

Sea \(\eta\) el contexto incierto anterior a una intervención: estado,
punto de operación y parámetros permitidos. Se estima solamente a partir
de \(Y_{<\tau}\). Los estados diferenciales se conservan a través de ON y
OFF; las variables algebraicas se resuelven consistentemente en el modo nuevo.
Una restauración no devuelve las máquinas al equilibrio anterior.

Para un soporte \(S\), severidades \(a\) y ventana posterior al onset:

\[
\mu_S(a;\eta)=\sum_{i\in S}(a_iD_i(\eta)+a_i^2Q_i(\eta))
 +\sum_{i<j\in S}a_ia_jQ_{ij}(\eta).
\]

Los coeficientes Q son los de la convención del diccionario archivado:
no se introduce silenciosamente un factor 1/2 de Hessiana.
Con \(\delta\eta=\eta-\hat\eta\), una primera extensión es

\[
r_W=\mu_S(a;\hat\eta)+B_S(a)\delta\eta+\epsilon_W,
\quad B_S(a)=N+\sum_{i\in S}a_iE_i,
\quad E_i=\frac{\partial D_i}{\partial\eta},
\quad N=\frac{\partial\mu_0}{\partial\eta}.
\]

Es una truncación: para amplitudes mayores se debe comprobar también
\(a_i^2\partial_\eta Q_i\) y
\(a_ia_j\partial_\eta Q_{ij}\). No se confunde un desplazamiento N δη con
una actualización de la firma E_i δη. Para dos eventos,
\(D_{j|i}=D_j+a_iQ_{ij}\) explica la interacción, pero reagrupar la misma
expansión no crea información ni supera a la inferencia exacta original.
No se fija una primera fuente antes de integrar sus alternativas.

Las derivadas cruzadas deben validarse contra cuatro simulaciones DAE
consistentes en \((a_i,\eta)=(\pm h,\hat\eta\pm d)\), con diferencia
mixta dividida por 4hd y un estudio de convergencia de h,d. Cada simulación
es una trayectoria continua; no se pegan estados de simulaciones diferentes.

## Incertidumbre y evidencia

Si el contexto preevento se aproxima por
\(\eta\mid Y_{<\tau}\sim N(\hat\eta,P_\eta)\), independiente del ruido
condicional declarado, la integración gaussiana local da

\[
r_W\mid S,a\sim N(\mu_S(a;\hat\eta),V_S(a)),\qquad
V_S(a)=\Sigma_W+B_S(a)P_\eta B_S(a)^\top.
\]

La hipótesis afecta tanto a la media como a la covarianza. Se conserva
\(\log|V_S(a)|\): reducir el residuo aumentando covarianza no es evidencia
gratis. Si contexto y ruido no son independientes, faltan los términos
cruzados y esta fórmula no es exacta. La calibración de P_η es un experimento,
no una consecuencia de escribir un posterior.

\[
Z_{S,\tau}=\int N(r_W;\mu_S(a),V_S(a))p(a\mid S)\,da,
\qquad p(S,\tau\mid Y)\propto p(S,\tau)Z_{S,\tau}.
\]

Para un único término lineal condicionado \(d\), residual e y prior
\(a\sim N(0,v_a)\), el factor de Bayes local es

\[
\log BF=\frac{(d^\top\Sigma^{-1}e)^2}
 {2(d^\top\Sigma^{-1}d+v_a^{-1})}
 -\tfrac12\log(1+v_a d^\top\Sigma^{-1}d).
\]

No sustituye la integral cuadrática cuando Q no es despreciable; priors
truncados requieren sus normalizadores adicionales.

## Cálculo y actualización causal

Con covarianza fija y bases blanqueadas F,

\[
\|r-Fc\|^2=r^\top r-2c^\top g+c^\top Hc,
\qquad g=F^\top r,\quad H=F^\top F.
\]

**Esto ya estaba implementado por soporte en GLOBAL-137.** X01 comparte
las 152 columnas entre soportes y evalúa conjuntamente los nodos GH31.
No lo presenta como una identidad matemática nueva. Para covarianzas de
bajo rango usa Woodbury y el lema del determinante, conservando ambos
términos; `gaussian_low_rank` se contrastó con una gaussiana densa.

Las estadísticas de innovaciones ya blanqueadas se acumulan por prefijos.
Para cada historia la actualización causal es

\[
w_{h,k}\propto w_{h,k-1}\,p(y_k\mid Y_{<k},h),\qquad
p(a,\eta,x\mid Y_{\le k},h)\propto p(y_k\mid a,\eta,x,h)
p(a,\eta,x\mid Y_{<k},h).
\]

La amplitud y el estado se arrastran en el posterior. Una ventana móvil
usa el prior anterior a esa ventana y cuenta sus reportes una vez; no
multiplica posteriores solapados ni reutiliza un prior independiente por
trama. Las condiciones de frontera del filtro temporal forman parte del
modelo; `whitened_statistics` no admite borrar muestras crudas sin tratarlas.

M agrega las historias activas; la causa retenida y la historia física
continúan después de OFF. ΔM conserva la descomposición entre evolución
condicional y reponderación de modelos. Una política de esperar/devolver
candidatos requiere calibración de cobertura/riesgo y costos declarados.
Bayes, Woodbury y ese principio de decisión son herramientas conocidas.

## Hallazgo previo a cualquier mejora de exactitud

El código del commit GLOBAL-137 `5189fa16...` coincide con las funciones
numéricas locales. Con D=Q=Qij=0 debe dar Z_S=Z_0 para todos los soportes.
La integral de una fuente devuelve Z_0/(2π); la de dos fuentes devuelve Z_0.
El prior declarado (0.20,0.50,0.30) actúa, por ello, como un prior efectivo
proporcional a (0.20,0.50/(2π),0.30). El control obtiene aproximadamente
(0.34508,0.13730,0.51762), aunque las masas sumen uno.

El candidato tiene dos modos explícitos: `normalized=False` reproduce
la aritmética archivada; `normalized=True` añade log(2π) a las evidencias
de una fuente y recupera el prior declarado en el control sin información.
No se modifica el baseline ni se corrigen métricas físicas por extrapolación.
La equivalencia R0 se declara respecto del modo apropiado, no se oculta esa
corrección como si preservara el posterior anterior.

Además, Top-1 en `support_summary` exige K=2 y soporte correcto en el banco
completo; Top-3 es el rango entre las 120 parejas, condicionado a K=2.
No son dos métricas del mismo espacio de decisión. La columna Top-1 de
`weak_weak_transition` repite un agregado global en cada severidad: no se
usará como curva Top-1 por intensidad. Estos archivos se conservan intactos.

## Campaña propuesta, separada de C01

| Prueba | Contrato y comparadores | Qué permitiría concluir |
|---|---|---|
| X01-A: equivalencia | 137 soportes, GH31, mismas constantes; original vs caché compartida vs integración por lotes | Corrección y coste del cálculo; sin afirmaciones de mejor física |
| X01-B: normalización | Integral directa, H0, una/dos fuentes y control sin información; replay por registro | Evidencias coherentes y efecto real del cambio de prior efectivo |
| X02: cambio de firma | Punto estimado por PMU; nominal vs solo recentrado vs E_i; DAE independiente | Valor del término evento–operación, aparte de desplazar la media |
| X03: incertidumbre | P_η preevento, logdet presente; caso Γ=0; cobertura, log-loss y riesgo | Si integrar contexto ayuda sin absorber la firma del evento |
| X04: horizonte/oráculo | 1,2,4,10 s; mismas trayectorias; modelo exacto vs surrogate | Separar información nueva, aproximación y error algorítmico |
| X05: causal | Onset y origen ocultos; recuperación y eventos sucesivos | Detección/localización oportunas, extras, demora y coste completo |

En X02 se reservan variaciones factibles de operación de ±1% para desarrollo
y ±2% para confirmación; no se reajustan impedancias, máquinas ni instrumentos.
Los cambios se aplican mediante operadores y configuraciones verificados,
no inventando nombres de parámetros. Semillas separadas propuestas 390501 y
390502; se congela el manifiesto antes de leer resultados. Se conservan
rechazos y denominadores. Los intervalos se agrupan por trayectoria padre.

E_B usa 16 cargas/32 coordenadas/onset conocido; R11 usa nueve cargas y
nueve líneas/47 coordenadas/onset desconocido. No se compara su porcentaje
sin igualar esa información. Group LASSO requiere una adaptación declarada
de entradas y condiciones iniciales, con ajuste solo de desarrollo. Chen
sigue limitado a líneas persistentes. El operador simultáneo debe validarse
antes de usarlo en F01; su contrato mínimo de una intervención activa no
se elimina silenciosamente. Más horizonte exige nuevas respuestas físicas,
no repetir las mismas 30 muestras.

## Ejecutado y bloqueos materiales

`run_checks.py` ejecuta seis fixtures de 960 dimensiones y todos los 137
soportes, con comparación de evidencias, posterior, momentos y Top-1/Top-3;
validación densa de covarianza, factor de Bayes por cuadratura, prefijos
causales y control de normalización. Son **pruebas sintéticas/algebraicas**,
no simulaciones físicas nuevas ni una confirmación de DICE.

Los originales D/Q/Qij y las trayectorias GLOBAL-137 no están en esta copia
de trabajo; los resúmenes y código sí. Se buscaron rutas de proyecto y tres
paquetes de revisión, sin recuperarlos. Faltan, entre otros,
`load_fd_central_operator.npz` y `load_multi_qij.npz`, además de las respuestas
usadas para Q. Sin ellos no puede certificarse replay físico E_B ni recalcular
su exactitud corregida. No se sustituyen por matrices nuevas calibradas a
RAW0001. R11/C01 continúan con sus propios artefactos, sin este bloqueo.

Los resultados numéricos completos, tiempos p50/p95/p99 y hashes están en
`run/RESULTS.json`, `run/HISTORICAL_NORMALIZATION_AUDIT.json` y `timings.csv`.
El benchmark usa un hilo BLAS y hardware local compartido; excluye adquisición,
observador, onsets y simulación. No demuestra operación a 30 fps.
