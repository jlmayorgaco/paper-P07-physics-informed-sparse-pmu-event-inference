# Derivación teórica: atribución física de eventos desde PMU dispersas usando energía hamiltoniana, grafos y evidencia bayesiana

**Estado:** derivación bajo hipótesis explícitas; no es un artículo validado ni una nueva evaluación del banco DAE Sauer–Pai. Elaborada para el proyecto IEEE-39 sparse-PMU. Fecha de trabajo: 12 de noviembre de 2026.

## 0. Objetivo y distinción de contribuciones

Inferir el origen físico `c` (bus/línea), la familia `e` (carga, apertura de línea, generación, falla), el inicio `tau`, la restauración `kappa` y la historia previa `h` dadas las mediciones de ocho PMU en buses `P={2,5,6,10,19,22,29,39}` a 30 reportes/s. Las mediciones incluyen fasores de tensión, corrientes de terminal, frecuencia y ROCOF. El banco causal publicado se restringe a 9 cargas y 9 líneas. Las fallas y generación se plantean como extensiones **pendientes de implementación y validación**.

Se distinguen tres objetos diferentes:

1. **Hamiltoniano físico**: energía de un modelo de red y su balance de potencia. No es una probabilidad.
2. **Función de verosimilitud**: probabilidad de las mediciones bajo una hipótesis, una trayectoria y un modelo instrumental.
3. **Log-evidencia**: integral de la verosimilitud sobre severidad, estados y parámetros desconocidos. Es el objeto pertinente para selección bayesiana de hipótesis; minimizar una acción/negativo log-posterior conjunta no equivale a maximizar evidencia de modelo.

La aportación potencial —por demostrar— está en operadores físicos de intervención/restauración con incertidumbre de historia, no en inventar port-Hamiltonian, Green's functions, Kron, Bayes, Schur o Group LASSO.

## I. Grafo, potencia y modos

Con la incidencia orientada `B` y las admitancias de rama `y_e`, para ramas simples recíprocas se tiene `Ybus(q)=B diag(y_e(q)) B^T+Ysh(q)`. En AC real, las contribuciones completas de los transformadores, shunts y taps reemplazan esa fórmula simplificada. Las corrientes terminales siguen `Iterm=T_q V`, no una inyección de bus. La potencia nodal es `S_i=V_i conj((Y_q V)_i)`.

La DAE completa en el modo `q` es:

```math
\dot x=f_q(x,z,u;\theta),\qquad 0=g_q(x,z,u;\theta),
\qquad y_k=\mathcal H_{q,M}(x_k,z_k,\eta_k)+\epsilon_k.
```

Un cambio de carga altera una dirección de entrada/admitancia según su ley ZIP; una apertura de línea cambia las estampas de `Ybus`, `T_q`, los términos algebraicos y las matrices del predictor. Una falla trifásica modifica una admitancia de shunt (o impone las condiciones de cortocircuito); una falla desequilibrada necesita un modelo trifásico o redes de secuencia independientes y datos que contengan esa información. La frecuencia y ROCOF proceden del estimador de fase de la PMU y su memoria temporal.

## II. Derivación hamiltoniana en un modelo reducido

En el modelo lossless de oscilación con ángulos de nodos dinámicos `delta`, frecuencias incrementales `omega=dot(delta)`, pesos `K_e>0`, inercia `M>0`, amortiguamiento `D>=0`, `beta=B^T delta`:

```math
U_q(\delta)=\sum_{e\in E_q} K_e[1-\cos((B^T\delta)_e)],
\quad \mathscr H_q(\delta,\omega)=\frac12\omega^T M\omega+U_q(\delta).
```

Las ecuaciones Lagrange–d'Alembert son:

```math
M\dot\omega+D\omega + B\operatorname{diag}(K_q)\sin(B^T\delta)=u.
```

En un intervalo de modo fijo:

```math
\frac{d\mathscr H_q}{dt}=\omega^T u-\omega^T D\omega.
```

**Prueba:** derivar, sustituir la ecuación de oscilación y cancelar los términos `omega^T grad U_q`. Esta identidad solo describe el modelo considerado. Los excitadores, gobernadores y resistencias requieren un modelo y contabilidad energética propios; no se extrapola directamente a la DAE completa.

### Firma de una carga

Para un cambio de entrada asociado a `f`, `u^+=u^-+b_f a`, el gradiente `grad U_q` no cambia, pero la aceleración inmediata sí: `M (dot omega^+-dot omega^-)=b_f a`. Para un bus puramente algebraico, `b_f` se obtiene de la reducción física y no coincide en general con el vector canónico del bus.

### Firma de una línea

Para una apertura de rama `e` sin islanding, `U_{q+}=U_{q-}-K_e[1-cos(b_e^T delta)]`. Con estados diferenciales continuos y el resto de las entradas iguales:

```math
M(\dot\omega^+-\dot\omega^-)=K_e b_e\sin(b_e^T\delta).
```

Además:

```math
L_q(\delta)=\nabla_\delta^2 U_q(\delta)
=B\operatorname{diag}(K_{e,q}\cos(b_e^T\delta))B^T,
```

luego la apertura elimina una contribución de rango uno `K_e cos(beta_e) b_e b_e^T` **en este modelo reducido**. Esto separa el cambio del vector de entrada de una carga del cambio de operador de una línea. Las tensiones/corrientes algebraicas pueden saltar en ambos casos: no usar la presencia de un salto como clasificador universal.

### Balance sobre conmutaciones

Cada tramo de topología fija cumple `H(t1)-H(t0)=int(omega^T u-omega^T D omega)dt`. En cada conmutación `tau`, además se contabiliza el cambio de potencial efectivo `H_{q+}(x(tau))-H_{q-}(x(tau))`. No atribuir automáticamente ese salto del **potencial equivalente** a energía electromagnética liberada por una línea física.

## III. Propagación de perturbaciones (Green, space-state y grafos)

La eliminación local de variables algebraicas de índice uno requiere `g_z` invertible (referencia angular fijada):

```math
\delta z=-g_z^{-1}(g_x\delta x+g_u\delta u),
\quad A_q=f_x-f_zg_z^{-1}g_x,\quad B_q=f_u-f_zg_z^{-1}g_u,
\quad C_q=H_x-H_zg_z^{-1}g_x,\quad D_q=H_u-H_zg_z^{-1}g_u.
```

El modelo linealizado/descretizado y ampliado con el estimador instrumental es `xi_{k+1}=F_{q,k} xi_k+G_{c,q,k} a_k+b_{q,k}+w_k`, `y_k=C_{P,q,k}xi_k+D_{c,q,k} a_k+d_{q,k}+v_k`. En un tramo LTI:

```math
\mathscr K_{c,q}(t)=C_{P,q}e^{A_q t}B_{c,q},\quad
\mathscr G_{c,q}(s)=C_{P,q}(sI-A_q)^{-1}B_{c,q}+D_{c,q}.
```

Para un descriptor `E dot xi=A xi+B u` la transferencia formal es `C(sE-A)^{-1}B+D`, con hipótesis de regularidad y ausencia de modos impulsivos inadmisibles. La conmutación exige composiciones de transiciones de cada modo; no se trata como una carga equivalente arbitraria.

En el swing homogéneo `m ddot delta+d dot delta+L delta=b_c u`, las firmas espectrales tienen componentes `(C u_r)(u_r^T b_c)/(m s^2+d s+lambda_r)`. Son modos electromecánicos de banda baja, NO ondas electromagnéticas de propagación ultrarrápida reconstruibles con PMU de 30 fps.

### Reducción de Kron en la aproximación DC

Dividiendo nodos con dinámica `g` y algebraicos `l`:

```math
L_{\mathrm{red}}=L_{gg}-L_{gl}L_{ll}^{-1}L_{lg},
\quad p_{g,\mathrm{eff}}=p_g-L_{gl}L_{ll}^{-1}p_l.
```

Luego un evento en un bus no instrumentado altera la entrada efectiva de los nodos dinámicos: `Delta p_{g,eff}=-L_gl L_ll^{-1} Delta p_l`. Kron **no** recupera inyecciones internas arbitrarias; necesita hipótesis/priors sobre ellas. Para IEEE-39 completo la reducción principal debe ser por bloques del Jacobiano DAE y estampas AC.

## IV. Historia de recuperación y mediciones

Defina una historia `h` con estado posterior al último OFF, topología/modalidad, fuentes pasadas e incertidumbre. Para un nuevo evento candidato `(e,c,tau,a)`, evalúe dos trayectorias **desde el mismo estado previo**:

```math
\mu_h=\mathbb E[Y\mid h,\mathrm{no\ new\ event}],
\quad s_{e,c\mid h}=\left.\frac{\partial\mathbb E[Y\mid h,e,c,a]}{\partial a}\right|_{a=0}
```

para una entrada escalar pequeña, o `Delta mu_{e,c|h}=mu_{h\oplus(e,c)}-mu_h` para conmutaciones finitas. Un nuevo evento no exige que el estado vuelva al equilibrio. Las reconstrucciones de buses ocultos son salidas condicionadas del modelo; nunca se cuentan como mediciones nuevas en la likelihood.

La covarianza de los reportes apilados, incluyendo las ventanas de fase/ROCOF, puede escribirse `Sigma_h=R+O_h P_h O_h^T+Sigma_process` si sus incertidumbres son independientes y se han separado correctamente. Si `O_h P_h O_h^T` representa la incertidumbre de la recuperación, NO debe luego volver a perfilarse `O_h x` como variable libre sin ajustar el modelo: es doble contabilización de la incertidumbre.

## V. Estimador MAP y evidencia cerrada para una entrada de carga

Para una hipótesis `(h,e=load,c,tau)` y ventana apilada:

```math
r_h=Y-\mu_h=O_h x_0+s_{c\mid h} a+\epsilon,
\quad x_0\sim N(0,P_h),\ \epsilon\sim N(0,R_h),\ a\sim N(0,v_a),
```

con independencia asumida. El negativo del log posterior conjunto, ignorando constantes independientes de las variables, es:

```math
J(x_0,a)=\frac12\|r_h-O_hx_0-s_ca\|_{R_h^{-1}}^2
+\frac12\|x_0\|_{P_h^{-1}}^2+\frac{a^2}{2v_a}.
```

Igualando gradientes a cero:

```math
\begin{bmatrix}
O_h^T R_h^{-1}O_h+P_h^{-1}&O_h^T R_h^{-1}s_c\\
s_c^T R_h^{-1}O_h&s_c^T R_h^{-1}s_c+v_a^{-1}
\end{bmatrix}
\begin{bmatrix}\hat x_0\\\hat a\end{bmatrix}
=\begin{bmatrix}O_h^T R_h^{-1}r_h\\s_c^TR_h^{-1}r_h\end{bmatrix}.
```

Defina `Sigma_h=R_h+O_h P_h O_h^T`. Woodbury/Schur producen:

```math
\boxed{\hat a=\frac{s_c^T\Sigma_h^{-1}r_h}{s_c^T\Sigma_h^{-1}s_c+v_a^{-1}}},\quad
\boxed{V_a=(s_c^T\Sigma_h^{-1}s_c+v_a^{-1})^{-1}},
\quad \hat x_0=P_h O_h^T\Sigma_h^{-1}(r_h-s_c\hat a).
```

Éste es el óptimo global de **ese problema cuadrático condicionado** con matrices PD; NO de un problema no convexo con fuente/topología desconocida. Con severidad en intervalo, el MAP de amplitud es la proyección de la media no truncada al intervalo, y la evidencia requiere la corrección de normalización de la gaussiana truncada.

Integrando estado y amplitud gaussianos:

```math
H_0:\ r_h\sim N(0,\Sigma_h),\qquad
H_c:\ r_h\sim N(0,\Sigma_h+v_as_cs_c^T).
```

Con `G_c=s_c^T Sigma_h^{-1}s_c`, `b_c=s_c^T Sigma_h^{-1}r_h`, la razón de Bayes es

```math
\boxed{\log BF_{c\mid h}=
\frac{v_a b_c^2}{2(1+v_aG_c)}-\frac12\log(1+v_aG_c)}.
```

**Prueba:** el lema del determinante da `det(Sigma+vss^T)=det(Sigma)(1+vG)`. Sherman–Morrison da `(... )^{-1}=Sigma^{-1}-v Sigma^{-1}s s^T Sigma^{-1}/(1+vG)`. Sustituyendo en las dos densidades gaussianas se obtiene la expresión. El primer término premia ajuste; el logdet penaliza flexibilidad del modelo. Minimizar solo J omite esta penalización de evidencia (Occam).

Para línea o falla que cambia el modo, se comparan directamente gaussianas de predicción con sus **propias medias y covarianzas**:

```math
\log BF_{j\mid h}
=-\frac12[\|Y-\mu_{j,h}\|_{\Sigma_{j,h}^{-1}}^2
-\|Y-\mu_{0,h}\|_{\Sigma_{0,h}^{-1}}^2
+\log |\Sigma_{j,h}|-\log|\Sigma_{0,h}|].
```

La ubicación es discreta: derivar respecto de la etiqueta del bus no tiene sentido. Las ecuaciones normales determinan variables continuas **dentro de cada modelo**, y las evidencias normalizadas comparan los modelos.

## VI. Mezcla bayesiana de historias para origen y clase

Sea `pi_h` el peso de una historia anterior condicionado por mediciones recibidas hasta ANTES del inicio propuesto. La evidencia del nuevo candidato integra incertidumbre de historia:

```math
p(Y\mid e,c,\tau)=\sum_h \pi_h\,p(Y\mid e,c,\tau,h),
\quad p(e,c,\tau\mid Y)\propto
p(e,c,\tau)\sum_h\pi_h p(Y\mid e,c,\tau,h).
```

Para obtener la clase `e`, se suman posteriors por fuentes y onsets; para ubicar se suman por clases admitidas. Se incluye el modo **sin nuevo evento** y un mecanismo explícito de detección fuera de catálogo; de lo contrario una clase conocida siempre gana aunque ninguna explique los datos. Si los reportes se usaron para construir `pi_h`, no deben reintroducirse como una observación independiente: los replays reemplazan una verosimilitud de sufijo anterior.

## VII. Identificabilidad y límites de localización

Para dos firmas `s_i,s_j` bajo h y covarianza común Sigma positiva definida, conocida la amplitud verdadera `a`, permitiendo al competidor amplitud `b` sin restricciones:

```math
\begin{aligned}
\delta_{i\mid j,h}^2(a)
&=\min_b\|a s_i-b s_j\|_{\Sigma^{-1}}^2\\
&=a^2\Big[s_i^T\Sigma^{-1}s_i-
\frac{(s_i^T\Sigma^{-1}s_j)^2}{s_j^T\Sigma^{-1}s_j}\Big]
\end{aligned}
```

si `s_j!=0`. Es un mínimo de un polinomio cuadrático obtenido de `d/db=0`, y se puede escribir `a² ||s_i||^2_{Sigma^-1}(1-rho_ij²)`. Esta es una **separación nominal perfilada**, no la KL entre modelos compuestos. Para dos hipótesis **simples gaussianas de igual covarianza** la KL es la mitad de la distancia cuadrática entre medias, y con priors iguales el error mínimo de decisión de dos modelos simples es `Phi(-delta/2)`. No transferir esa fórmula sin más a fuentes con amplitudes desconocidas y priors mixtos.

Si una incertidumbre se perfila *sin prior* mediante direcciones `N`, la geometría usa `Pi_{Sigma^-1/2 N}` para proyectar la firma sobre su complemento. Si la misma incertidumbre **ya fue marginalizada** en `Sigma`, no se proyecta otra vez salvo que se redefina explícitamente el modelo. Si una variable de amplitud libre de ambas fuentes puede tender a cero, la separación global trivialmente puede ser cero: fijar amplitud mínima, amplitud verdadera o prior adecuado.

Se pueden evaluar operadores de observabilidad `O_T=[C;CF;...;CF^{T-1}]`, respuesta forzada y ceros invariantes, conforme a la literatura de Anguluri et al. La mera adición de sensores no garantiza mejorar la inferencia bajo mala calibración, aunque bajo modelos simples gaussianos correctos nunca reduce la información de observaciones nuevas condicionada por las anteriores.

## VIII. ¿Qué aporta Hamiltoniano al estimador bayesiano?

1. **Forma del operador físico y tipos de evento:** el potencial del grafo determina el laplaciano local; una línea cambia el modo y su Hessiano, una carga cambia una entrada física; un generador puede cambiar torque, frecuencia y controles.
2. **Balance como comprobación física:** para cada trayectoria candidata, computar `r_H=Delta H - integral(power_in - dissipation) - sum(switch_work)`. Permite detectar inconsistencia de una aproximación reducida y diseñar límites de error.
3. **Prior físico alternativo de estados iniciales:** cerca de un equilibrio estable y con referencia angular fijada, `H_shift≈.5 x^T Q_H x` con `Q_H=Hess H_shift>0`. Se puede explorar `p(x_0) ∝ exp(-beta H_shift(x_0))`, que induce `P^{-1}=beta Q_H` localmente. **No** multiplicar por un prior de filtro basado en los mismos datos como si fuera independiente; calibrar beta, y evaluar frente al prior original.
4. **No usar energía como segundo detector independiente:** si la DAE y las observaciones ya están en la likelihood, una función energética determinista de ellas no es información nueva; construir `p(Y|h)p(r_H(Y)|h)` sin covarianza conjunta cuenta las observaciones dos veces. El DEF clásico puede localizar falsamente la fuente según modelo de cargas/amortiguamiento.

## IX. Optimización no lineal y adjuntos

Para los candidatos de mayor evidencia, definir acción estadística discreta:

```math
\begin{aligned}
\mathscr A_h(x,z,a)&=\frac12\|x_0-m_h\|_{P_h^{-1}}^2
+\frac12\sum_k\|x_{k+1}-F_{q_k}(x_k,z_k,a_k)\|_{Q_k^{-1}}^2\\
&\qquad+\frac12\sum_k\|y_k-h_{q_k}(x_k,z_k,a_k)\|_{R_k^{-1}}^2
-\log p(a\mid h),\quad g_{q_k}(x_k,z_k,a_k)=0.
\end{aligned}
```

Con multiplicadores en las restricciones dinámicas y algebraicas, se obtienen ecuaciones adjuntas y condiciones KKT. En el modelo no lineal pueden aparecer óptimos locales; igualdad de gradiente a cero no implica óptimo global. Comparar evidencias requeriría integrar trayectorias y parámetros, o aproximar por Laplace incluyendo curvatura/normalización sobre el espacio factible; no es correcto identificar `argmin A` con `argmax p(h|Y)` en general.

## X. Tests realizados y resultados (NO resultados del paper)

El script `verify_hamiltonian_graph_bayes.py` implementa una red ilustrativa de 4 buses / 5 ramas, con M y D positivas, un pulso de potencia y una apertura de línea, y un ejemplo separado de evidencia gaussiana a partir de firmas discretas de esa red.

Resultado reproducible con seed 261112:

- Residuo máximo de balance energético por tramo: `3.516e-13`.
- Salto del potencial efectivo en apertura: `-1.359727180e-04` (unidades internas del modelo).
- Residuo de actualización Hessiana de rango uno: `1.570e-16`.
- Log Bayes factors ilustrativos para dos fuentes candidatas: `114.993064323` y `44.067872847`.
- Máxima discrepancia entre el BF analítico y razón exacta de densidades gaussianas: `7.816e-13`.

Estos números verifican identidades y una instancia sintética, **no** precisión de localización para IEEE-39, ni los datos SGSMA, ni rendimiento frente a ruido PMU independiente.

Ejecutar: `python verify_hamiltonian_graph_bayes.py` (requiere numpy, scipy).

## XI. Próxima evaluación falsable para IEEE Access

1. **Congelar** el banco causal y su log de 99/108, 72/108, 22/108 de la cohorte común; no reciclar la misma evaluación para optimización de hiperparámetros.
2. Construir operadores AC/DAE por tipo y fuente (18 fuentes existentes) y verificar el mapa de las corrientes terminales, diferencial de frecuencia y ROCOF.
3. Probar hipótesis individuales con `BF_{c|h}` y modelo de recuperación covariante, comparar contra evidencia actual de severidad truncada. Las fórmulas pueden ser matemáticamente equivalentes al banco actual bajo gaussianidad: si empatan **no hay mejora nueva**.
4. Ejecutar contraste de **Hamiltoniano auxiliar**: (a) sin balance energético, (b) balance solo como diagnóstico, (c) prior energético calibrado con conjunto development independiente. Ninguna versión debe contar dos veces mediciones.
5. Medir el valor incremental de V, I, f y ROCOF con su covarianza conjunta y ventanas temporales reales; pruebas leave-one-PMU-out.
6. Para cargas 16/24 y rivales más cercanos, cuantificar `delta_ij|h` con ruido correlacionado, independiente 0.05% TVE, con y sin historia de recuperación y parámetros R/X fuera de banco.
7. Probar clase desconocida, PMU ausentes y datos corrompidos; máscaras y priors explícitos.
8. Aislar el beneficio de historias alternativas frente a un único estado continuo con el **mismo** predictor/covarianza/propuestas/publicación y presupuesto de alarmas.
9. Medir p50/p95/p99 de latencia por reporte para evitar equiparar causalidad lógica con procesamiento en tiempo real.

## Referencias externas verificadas

- Fiaz, Zonetti, Ortega, Scherpen, van der Schaft, “A port-Hamiltonian approach to power network modeling and analysis,” *European Journal of Control*, 2013, DOI: https://doi.org/10.1016/j.ejcon.2013.09.002.
- van der Schaft y Stegink, “Perspectives in modeling for control of power networks,” *Annual Reviews in Control*, 2016, DOI: https://doi.org/10.1016/j.arcontrol.2016.04.017.
- “Propagation of Disturbances in AC Electricity Grids,” *Scientific Reports*, 2018, https://www.nature.com/articles/s41598-018-24685-5.
- Anguluri, Kosut, Sankar, “Localization and Estimation of Unknown Forced Inputs: A Group LASSO Approach,” *IEEE Transactions on Control of Network Systems*, 2023, https://arxiv.org/abs/2201.07907.
- “Analysis of Energy Flow Method for Oscillation Source Location,” *IEEE Transactions on Power Systems*, 2021, https://doi.org/10.1109/TPWRS.2020.3024866.
- “DSE-assisted DEF strategy for locating forced oscillations in synchronous generators,” *International Journal of Electrical Power & Energy Systems*, 2023, https://www.sciencedirect.com/science/article/abs/pii/S0142061522007402.
- Dörfler y Bullo, “Kron Reduction of Graphs With Applications to Electrical Networks,” *IEEE Transactions on Circuits and Systems I*, 2013, https://doi.org/10.1109/TCSI.2012.2215780.
- Masoud Barati, “A Global Solution Algorithm for AC Optimal Power Flow through Linear Constrained Quadratic Programming,” arXiv:2406.11899v1, documento aportado por el usuario (2024). No demuestra optimalidad global de esta inferencia dinámica.

**Conclusión:** la arquitectura investigable es una *historia física DAE conmutada* + *predicción por funciones de Green* + *integración de incertidumbre de recuperación* + *selección bayesiana de fuente y familia*. Hamiltoniano fundamenta operadores y balance, pero no debe añadirse como likelihood independiente de las mismas medidas. La novedad debe validarse frente a antecedentes y datos reales antes de reclamarse en IEEE Access.
