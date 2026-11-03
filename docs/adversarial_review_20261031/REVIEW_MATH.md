# Revisión matemática adversarial de P07 — 31 octubre 2026

## Alcance y dictamen

Revisión independiente del `main.tex` actual, sus secciones activas (incluidas las secciones de interpretación anidadas), `supplement.tex` y los seis apéndices incluidos. Se leyeron los contratos `AGENTS.md` de ambos repositorios y `SIM0001_START_HERE.md`, `SIM0001_CURRENT.json`, `SIM0001_JuliaPD_F01/START_HERE.md`. La inspección de código se limitó a fuentes del R11 congelado y sus dependencias, sin ejecutar el observador ni simulaciones. No se abrió RAW0002 ni se leyeron resultados parciales o verdad de C01. No se modificaron manuscrito, configuraciones, experimentos ni pruebas originales. Este informe no usa otros revisores ni inventa una puntuación editorial.

**No logré falsar la matemática central del R11 causal con los ataques realizados.** La reducción DAE local, la conservación de estado al restaurar, la integral de severidad truncada y la actualización afín condicional son correctas bajo las hipótesis declaradas. Esto no demuestra calibración, fidelidad de F01 frente a RAW ni superioridad empírica; el artículo ya niega esas extrapolaciones y no corresponde reprochárselas como afirmaciones realizadas.

Sí hay una afirmación inequívocamente falsa en la geometría de conos y lagunas de condiciones en teoremas del suplemento. También persiste una contradicción de presentación sobre la evidencia del estimador histórico por lotes, cuyo defecto de normalización ya está reconocido en otro apéndice. **Ninguno de esos hallazgos demuestra que R11 tenga el mismo defecto.**

Convención de ubicaciones: salvo indicación contraria, las rutas son relativas al repositorio de P07. Las líneas corresponden al texto inspeccionado. Los códigos `M1`–`M7` sirven para seguimiento, no son resultados del manuscrito.

## Hallazgos que requieren corrección

### M1. La separación mínima de conos definida en el texto sí es simétrica

**Ubicación:** `supplement/appendix_d_theory.tex:640–649`, ecuación `eq:supp-directed-cone-separation`. **Tipo:** afirmación matemática falsa. **Confianza:** muy alta. **Impacto:** apéndice teórico histórico; no es una operación del filtro causal.

El texto define

\[
\delta(C_S\to C_C)=\min_{x\in C_S,\|x\|=1}\operatorname{dist}(x,C_C)
\]

y afirma que «need not be symmetric». Para dos conos cerrados no triviales esta cantidad siempre es simétrica. Sea

\[
\rho=\max_{x\in C_S\cap\mathbb S,\,y\in C_C\cap\mathbb S}x^\top y.
\]

Las secciones unitarias son compactas. Para un par de direcciones, minimizar sobre la escala no negativa de la segunda da

\[
\min_{t\ge0}\|x-ty\|^2=1-[x^\top y]_+^2.
\]

Por tanto ambas orientaciones valen \(\sqrt{1-[\rho]_+^2}\). La convexidad no es necesaria. Ejemplo: el cono angular de 0° a 30° frente al de 60° a 90° da 0.5 en ambos sentidos. La intuición de asimetría corresponde a una distancia dirigida de tipo **máximo** sobre el primer conjunto, no al mínimo escrito.

**Corrección mínima:** eliminar la frase de asimetría y «directed», o definir otra cantidad si se necesita realmente una distancia dirigida. La equivalencia «cero si comparten un vector no nulo» y la distinción rayo/subespacio sobreviven.

### M2. Cone–Laplace necesita un cono límite con masa gaussiana positiva

**Ubicación:** `supplement/appendix_e_estimator.tex:384–424`. **Tipo:** hipótesis insuficientes para la equivalencia multiplicativa enunciada. **Confianza:** alta. **Impacto:** propuesta no ejecutada \(\mathcal E_J\); no R11.

El teorema admite cualquier cono poliédrico cerrado, pero concluye una expresión multiplicativa proporcional a \(\Pr(U\in K)[1+o(1)]\). Si el cono tiene medida de Lebesgue cero, esa expresión es cero y la demostración por convergencia dominada sólo obtiene un coeficiente principal cero, no una equivalencia relativa.

Contraejemplo regular en la **media**, con dominio admisible que se estrecha:

\[
D=\{0\le x\le1,\ 0\le y\le x^2\},\quad
\pi(x,y)=3\ \text{en }D,\quad
\mu(x,y)=(x,y).
\]

La prior es propia porque el área de \(D\) es \(1/3\). Use el kernel gaussiano centrado \(e^{-(x^2+y^2)/(2\epsilon^2)}\). La expansión local es exactamente cuadrática, \(H=I\), y el dominio reescalado converge localmente al rayo \(K=\{(u,0):u\ge0\}\), cerrado y poliédrico. Hay envolvente gaussiana integrable y la contribución distante es despreciable. Sin embargo,

\[
M_\epsilon=3\int_0^1e^{-x^2/(2\epsilon^2)}
\int_0^{x^2}e^{-y^2/(2\epsilon^2)}\,dy\,dx
\sim3\sqrt{\pi/2}\,\epsilon^3>0.
\]

El factor de cono en la fórmula publicada vale cero. La cuadratura independiente da \(M_\epsilon/\epsilon^3=3.75848\) para \(\epsilon=0.0125\), acercándose a \(3\sqrt{\pi/2}=3.75994\).

**Corrección mínima:** exigir \(\Pr(U\in K)>0\), por ejemplo un cono de dimensión completa en las coordenadas factibles declaradas, más convergencia casi en todas partes de los indicadores del dominio (o una condición equivalente que permita integrar). Si la intención son sólo ortantes/interiores regulares, decirlo. Para un límite degenerado, dar sólo una expansión aditiva con coeficiente cero y remitir a una escala anisótropa. La fórmula sí es correcta para el ortante regular que parece motivarla.

### M3. La reducción por fibras debe preservar la ley completa, no sólo la media

**Ubicación:** `supplement/appendix_e_estimator.tex:455–475`; comparar `supplement/appendix_d_theory.tex:244–257`. **Tipo:** condición omitida en proposición y prueba. **Confianza:** alta sobre la condición; no se identifica un fallo ejecutado.

La proposición supone \(\mu(\theta)=\bar\mu(\xi)\), pero la prueba concluye que la verosimilitud es independiente de \(\zeta\). Esto no se deduce sólo de la media; el propio suplemento permite covarianzas dependientes del parámetro.

Ejemplo: \(Y\mid\xi,\zeta\sim N(\xi,e^{2\zeta})\), con prior propia independiente y \(\zeta\sim U[-1,1]\). La media no depende de \(\zeta\), pero para \(\xi=Y=0\) la densidad marginal es \(\sinh(1)/\sqrt{2\pi}=0.468837\), frente a \(1/\sqrt{2\pi}=0.398942\) si se elimina la coordenada reteniendo arbitrariamente \(\zeta=0\). El cociente es 1.17520.

**Corrección mínima:** exigir \(p(Y\mid\xi,\zeta)=p(Y\mid\xi)\) en todo el soporte, por ejemplo media y covarianza constantes a lo largo de la fibra. Si se redefine \(p(Y\mid\xi)\) como una mezcla sobre \(\zeta\), la integral reducida sigue siendo posible, pero ya no corresponde a la prueba que afirma independencia ni a eliminar sin más esa incertidumbre. Con invariancia de la ley completa, Fubini y la prior inducida son correctos.

### M4. El teorema mixto omite las condiciones del dato centrado y amplitud bilateral

**Ubicación:** `supplement/appendix_e_estimator.tex:480–521`. **Tipo:** alcance insuficientemente especificado de la constante. **Confianza:** alta. **Impacto:** \(\mathcal E_J\) propuesto.

La tasa \(\epsilon^{r+1/k}\) y la constante escrita se deducen del kernel centrado **sin residuo observado**, integrado en \(a\in\mathbb R\). La prueba introduce ambas cosas sin especificarlas en el enunciado. En la misma sección hay amplitudes unilaterales y una expansión previa que sí incorpora el ruido observado.

Con \(\mu(\xi,a)=(\xi,a^2)\) y datos \(Y=(0,\epsilon z)\), el factor singular de la constante es

\[
\int_\mathbb R\exp[-(t^2-z)^2/2]dt,
\]

que vale 2.15580 para \(z=0\), 2.52665 para \(z=1\) y 0.90149 para \(z=-1\). La tasa permanece, pero la constante no es la publicada para todo dato. Si \(a\ge0\), el factor es la mitad a igual densidad local de prior; el normalizador de una prior unilateral es un factor separado.

**Corrección mínima:** definir explícitamente \(M_\epsilon\), el dato \(Y=\mu_0\), \(\dim\xi=r\), y \(a=0\) interior bilateral; o presentar la constante general dependiente del residuo y del dominio límite. La fórmula gamma centrada bilateral fue comprobada y es correcta.

### M5. La presentación de \(\mathcal E_B\) no está reconciliada con el error histórico ya reconocido

**Ubicaciones:** `supplement/appendix_e_estimator.tex:154–160,231–239,300–323,609–614` frente a `supplement/appendix_archived_source_resolution.tex:47–57`. **Tipo:** contradicción de contrato matemático/implementado; defecto histórico ya reconocido, no nuevo descubrimiento de código. **Confianza:** muy alta.

El primer apéndice presenta la prior \((0.20,0.50,0.30)\), la cuadratura correctamente normalizada y el algoritmo como el que produjo los resultados. Al final dice que \(\mathcal E_B\) calcula evidencia bayesiana normalizada. El apéndice posterior reconoce que la implementación archivada multiplicaba sólo la evidencia de una fuente por \(1/(2\pi)\). Ambas descripciones no pueden identificar la misma implementación bajo las mismas priors.

En un control sin respuesta, las probabilidades de cardinalidad deberían devolver la prior. El código histórico descrito devuelve aproximadamente

\[
(0.345079,\ 0.137303,\ 0.517618),
\]

no \((0.20,0.50,0.30)\). Esto favorece fuertemente las otras cardinalidades respecto a una fuente. Es matemáticamente posible reinterpretarlo como otra prior efectiva; no permite atribuir sus resultados a la prior declarada. El propio archivo reconoce que el sucesor corregido no tiene aún una nueva evaluación física.

**Corrección mínima:** distinguir desde el encabezado del apéndice entre «modelo/intención normalizada», «implementación histórica con prior efectiva» y «sucesor corregido sin resultados físicos». Repetir la advertencia junto a la prior y el algoritmo, y corregir la frase de líneas 609–614. Mantener las cifras archivadas con su calificación, sin presentarlas como resultados corregidos. Esto ya está adecuadamente separado de R11 en el artículo principal (`sections/article_information.tex:43–47`).

## Dos reparaciones menores de precisión matemática

**M6 — margen restringido y matrices anchas.** En `supplement/appendix_d_theory.tex:742–755`, definir \(\sigma_{\min}(A)=\inf_{\|v\|=1}\|Av\|=\sqrt{\lambda_{\min}(A^TA)}\) y exigir \(\gamma_{2K}>0\) antes de dividir. Con la convención de valores singulares rectangulares usada por bibliotecas, \(H=[1\ 1]\), \(K=1\) da un margen mínimo de 1 entre submatrices, aunque \(a=(1,0)\), \(b=(0,1)\) producen la misma salida. La cota con residuo cero se contradice. Con la definición variacional, el margen es cero y el problema desaparece. No se demuestra que esta ambigüedad afecte la matriz alta del experimento P07; la caracterización por intersección del núcleo en líneas 721–732 es correcta sin este problema.

**M7 — inversas y tangentes nulas.** El corolario preevento (`appendix_d_theory.tex:308–320`) necesita \(I_{\nu\nu}+\Lambda_{pre}\succ0\) o un cociente identificable: la sección anterior permite nuisance redundante y \(\Lambda_{pre}=0\) también está admitida. Por ejemplo \(N=[1\ 1]\) produce una matriz de información singular. El orden monótono sigue siendo correcto cuando la inversa existe. Igualmente las fórmulas escalares de separación (`:339–350`) y onset (`:678–685`) necesitan denominador positivo; un competidor con tangente nula requiere el caso separado. Son condiciones de dominio, no refutaciones del argumento geométrico.

## Qué sobrevivió y por qué

| Elemento | Resultado de la revisión |
|---|---|
| Reducción DAE, `sections/article_method.tex:30–53` | El complemento de Schur y las derivadas de salida tienen los signos correctos. Se exige explícitamente carta regular índice uno y referencia fijada. No se extiende indebidamente a saltos. |
| Consistencia en el evento, `appendix_d_theory.tex:32–111` | Derivadas implícitas primera/segunda correctas para evento programado, estado diferencial previo fijo e impulso ausente. El texto no presenta la semántica del callback como observación ya validada. |
| Funcional observability y BLUE, `:184–240` | Equivalencias núcleo/factorización y covarianza pseudoinversa correctas para objetivos estimables. La advertencia sobre rango constante en el caso no lineal evita la extrapolación más peligrosa. |
| Fisher con nuisance, `:242–306` | Proyección y complemento de Schur correctos incluso con nuisance redundante. 30 pruebas independientes: discrepancia máxima 9.33e-15. Se distingue correctamente prior propia de nuisance determinista. |
| Geometría de soportes y conos, `:414–638` | Proyecciones, amplitudes compartidas, KKT no negativo y diferencia entre cono y span correctos bajo las condiciones escritas. El error M1 no invalida estas fórmulas. |
| Unicidad sparse, `:714–742` | La condición \(\ker H\cap D_K=\{0\}\) es exactamente necesaria y suficiente. No prueba el margen físico del banco IEEE-39 ni recuperación de fuentes desconocidas; el texto no dice que lo haga. |
| Monotonía de prefijos y AR(1), `:757–887` | Prueba correcta con dominio fijo y covarianzas como prefijos de una ley común. Los 30 controles numéricos respetaron la monotonía. El artículo ya advierte que esto no garantiza mejora de un estimador aproximado. |
| Integral truncada R11, `appendix_causal_walkthrough.tex:121–154` | Completar el cuadrado, cociente de normalizadores y momentos correctos. 12 casos aleatorios: error relativo máximo frente a cuadratura independiente 6.66e-16. |
| Estado condicional R11, `:173–193` | \(m^+=Tm+g+Ke\), \(d^+=Td+u-Ks\) es la media exacta bajo el modelo gaussiano condicional declarado. Integración independiente sobre amplitud: error máximo 8.88e-16. La covarianza marginal además contiene \(d^+\operatorname{Var}(a\mid y)d^{+T}\); el artículo no afirma conservar toda la mezcla al cerrar. |
| Normalizadores regulares | Bayes factor gaussiano, factor unilateral \(2\Phi(z)\), Schur de llegada, integral cuártica y multiplicidad efectiva son correctos bajo su contrato. No confundirlos con la implementación histórica defectuosa de M5. |
| Recuperación y masas | Continuidad diferencial sin reset, superposición LTI y descomposición de \(\Delta M\) son correctas. Se presentan como mecanismos/identidades, no como teoremas novedosos ni como aumento universal de información. |

La lectura de `SGSMA26-Physics-Informed-AD/experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/observer/static_rx.py:17–36` y `protocol/new_holdout/runtime/core_v6.py:118–126` muestra la misma integral y actualización que el suplemento. Omitir \(47\log(2\pi)\) en comparaciones de la misma dimensión no es el defecto de cardinalidad histórico. El código declara explícitamente la covarianza nominal compartida y el carácter aproximado; no se ejecutó un replay completo, por lo que esta inspección no certifica toda la implementación.

## Material que recortaría y evidencia que sí aportaría

El suplemento conserva una cadena extensa de resultados estándar y una propuesta \(\mathcal E_J\) distinta del método causal. BLUE, Schur, Fano, Chernoff, fibras redundantes, Laplace singular, diseño de discrepancia y el piloto histórico son demasiadas líneas de defensa para una contribución cuya evidencia actual trata un banco causal de cargas/líneas. Las tablas de estado (`appendix_d_theory.tex:1218–1236`) reconocen correctamente que buena parte no se ha probado en IEEE-39. Esa transparencia evita sobreafirmar, pero no convierte todo el material en necesario.

Mantendría en el suplemento de este artículo la integral truncada y su dominio numérico, actualización condicional, reemplazo de sufijos, protocolo de publicación, normalizadores y límites de las aproximaciones. Condensaría observabilidad/Fisher en la distinción operacional entre ajustar y localizar. Movería el diseño conjunto no ejecutado y el piloto dossier a una nota técnica versionada, o los reduciría a trabajo futuro. Esto reduciría contradicciones como M5 sin alterar resultados ni figuras protegidas.

Para explicar una localización errónea, el experimento decisivo es un control de respuestas no lineales exactas frente a la aproximación local, con mismo contexto, medición, covarianza, prior y horizonte, y un competidor físicamente admisible. Un pequeño margen del surrogate no demuestra indistinguibilidad de la planta. `sections/article_information.tex:35–41` ya formula correctamente esta frontera. No recomiendo exigir una garantía universal ni calibración que el artículo no promete.

## SIM 70/30, RAW0001 y hackathon: consecuencia matemática

Una partición 70/30 puede organizar una nueva prueba, pero no resuelve por sí sola la pregunta científica. Debe dividir **padres físicos completos**, manteniendo juntos sus reportes, ventanas, condiciones pareadas y semillas; dividir filas de una trayectoria correlacionada no crea una prueba independiente. La selección de hiperparámetros requiere datos internos al 70% o un bloque DEV separado. R11 no entrena una cabeza supervisada de fuentes (`sections/article_method.tex:10–15`), así que «entrenar R11 al 70%» debe significar exactamente qué ruido, prior, contexto, umbrales o diccionario se ajusta.

RAW0001 ya proporcionó calibración retrospectiva a F01 (`sections/narrative_protocol.tex:18` y contrato F01). Evaluar después allí es un ensayo de transferencia/ajuste retrospectivo, **no un test externo virgen**. Un score alto podría reflejar que simulador y terminales se ajustaron precisamente a ese registro. Una separación nominal transferirá sólo si el error de modelo es pequeño respecto al margen entre candidatos; la cota de `appendix_d_theory.tex:823–834`, \([d_{nom}-\epsilon_S-\epsilon_R]_+\), expresa bien esa condición, pero no está cuantificada para RAW0001.

Para comparar con hackathon hay que fijar mismas familias, fuentes, canales, disponibilidad causal, latencia y regla de puntuación. Los nueve buses de carga y nueve líneas actuales no representan por sí solos todas las clases. El manuscrito ya limita la comparación a adaptadores ExtraTrees congelados y a un contrato compartido, sin reclamar leaderboard oficial (`sections/narrative_protocol.tex:22`). Una comparación SIM 70/30 puede ser útil como interpolación; no sustituye un ensayo por activos excluidos ni demuestra fidelidad de CT/PT o ruido entre familias. RAW0002 debe permanecer cerrado en esta tarea, tal como se ordenó.

## Reproducción de esta revisión

Ejecutar únicamente:

```powershell
python docs/adversarial_review_20261031/checks/math_independent_checks.py
```

Fuente: `docs/adversarial_review_20261031/checks/math_independent_checks.py`.
Resultados: `docs/adversarial_review_20261031/checks/math_independent_checks.json`.

El script usa ejemplos adimensionales, no importa módulos del experimento, no lee datos físicos ni verdad, y sólo escribe su propio JSON. Todas las comprobaciones/assertions pasaron. Estos checks verifican álgebra y contraejemplos; no aumentan los denominadores de ninguna campaña ni validan probabilidades R11.
