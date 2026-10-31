# Ecuaciones: qué tenemos y qué no

Las ecuaciones siguientes organizan lo discutido. No reemplazan la convención
de cada implementación ni la numeración de borradores anteriores. El artículo
y el suplemento contienen las hipótesis y límites completos.

## 1. Planta y medición — implementado con alcance F01

\[
\dot x=f_q(x,z,u;\theta),\quad 0=g_q(x,z,u;\theta),\qquad
y_k=\mathcal M_q(x_k,z_k;\theta_M)+\varepsilon_k.
\]

La integración física continua y el reporte PMU son responsabilidades distintas.
Un cambio de modo preserva x si no hay impulso; z satisface las restricciones
del modo nuevo. El modelo PMU incluye referencias y memoria instrumental.
La frecuencia reportada no debe confundirse con velocidad de rotor o desviación
sin su base y ecuación de reconstrucción. No se reelige ese contrato desde el chat.

## 2. Kirchhoff, potencia y terminales — implementado

\[
I_{\rm bus}=Y_{\rm bus}V,\quad I_{{\rm term},r}=Y_{{\rm term},r}V,
\qquad S_i=V_i I_{{\rm bus},i}^{*}.
\]

La corriente terminal conserva orientación, carga de línea y transformadores.
Su producto con el voltaje correspondiente es potencia de ese terminal;
no es automáticamente la inyección neta del bus. Referencia angular, desfase
de terminal y factor de base son partes distintas. El mapa F01, incluido
BUS5 provisional, se hereda del snapshot.

## 3. Predictor local derivado de la DAE — implementado en R11

\[
A=f_x-f_zg_z^{-1}g_x,\qquad B=f_u-f_zg_z^{-1}g_u.
\]

Tras discretizar y ampliar memoria instrumental/discrepancia:

\[
\xi_{k+1}=A_{\ell,q}\xi_k+b_{\ell,q}+B_{\ell,q}a+w_k,
\quad r_k=C_{\ell,q}\xi_k+d_{\ell,q}+D_{\ell,q}a+v_k.
\]

Fuente verificable: `sections/article_method.tex` y el código congelado
referenciado por `PAPER_CONFIRMATORY_C01/references/R11_FREEZE.json`.
La matriz M no sustituye estas ecuaciones; agrega sus explicaciones.

## 4. Severidad desconocida — implementado y contrastado por cuadratura

\[
L_{h,k}=\int_l^u \mathcal N(e;sa,S)
  \operatorname{TN}_{[l,u]}(a;\mu,v)\,da.
\]

El posterior de severidad se conserva entre reportes. La línea usa su
operador conmutado, no una severidad ficticia de carga. La identidad local
cerrada no hace exacto todo el banco con poda y covarianzas aproximadas.

## 5. Onset retrospectivo y evidencia causal — implementado, aproximado

\[
\tau\in[t-10\mathrm{s},t],\qquad
w_{h,k}\propto w_{h,k-1}p(y_k\mid Y_{<k},h).
\]

R11 conserva diez segundos de estados; su screen congelado de nuevas
historias busca lags 0–18 reportes, no todos los 300 onsets posibles.
Propone onsets elegibles y usa el estado retenido anterior a cada onset.
No evalúa exhaustivamente una DAE no lineal por cada celda/trama. Un replay
de sufijo reemplaza su contribución previa, no multiplica otra vez la misma
ventana. El score predictivo precede a la corrección con el reporte actual.

## 6. M, Γ y ΔM — implementado como agregación interpretable

\[
M_{c,k}=\sum_\ell w_{\ell,k}\sum_{h:c(h)=c}\pi_{\ell,h,k}
 \mathbf1\{h\text{ activo}\},\quad
\Gamma_{c,k}=\sum_\ell w_{\ell,k}\sum_{h:c(h)=c}\pi_{\ell,h,k}.
\]

\[
\Delta M_{c,k}=\sum_\ell w_{\ell,k}(M_{\ell,c,k}-M_{\ell,c,k-1})
 +\sum_\ell\Delta w_{\ell,k}M_{\ell,c,k-1}.
\]

La celda c es familia/activo admisible. R11 tiene 18 celdas: nueve cargas y
nueve líneas. No se implementa el tensor universal de todas las familias
en todos los buses. Las masas no tienen calibración empírica completa.

## 7. Recuperación — implementado y parte del argumento central

\[
x(\kappa^+)=x(\kappa^-),\qquad
\delta y_h(t)\simeq C_0(t)\Phi_0(t,\kappa)\delta x_h(\kappa),\ t>\kappa.
\]

Restauración física no implica residuo cero. La respuesta eléctrica y la
memoria PMU persisten. La causa sigue en Γ aunque deje de estar activa en M.
Una ablación limpia de cada operación de memoria sigue sin ejecutarse.

## 8. Banco cuadrático simultáneo — implementado histórico, contrato aparte

\[
\mu_S(a)=\sum_{i\in S}(a_iD_i+a_i^2Q_i)
 +\sum_{i<j\in S}a_ia_jQ_{ij}.
\]

E_B usa 16 cargas, 32 coordenadas rectangulares, onset conocido y 137 soportes.
No es la ecuación interna del predictor R11. El código histórico tiene un
factor de normalización de una fuente que altera el prior efectivo.
Los resúmenes no permiten recalcular la exactitud del sucesor corregido.

## 9. Evento–contexto — E_i probado en X02; incertidumbre conjunta pendiente

\[
E_i=\partial D_i/\partial\eta,\quad
r_W\simeq\mu_S(a;\hat\eta)+J_{\eta,S}(a)\delta\eta+\varepsilon_W,
\qquad J_{\eta,S}(a)=N+\sum_i a_iE_i.
\]

\[
V_S(a)=\Sigma_W+J_{\eta,S}(a)P_{\eta,\tau}J_{\eta,S}(a)^\top,
\qquad
Z_{S,\tau}=\int\mathcal N(r_W;\mu_S(a),V_S(a))p(a\mid S)\,da.
\]

El ensayo separado X02 verificó E_i con la DAE IEEE-39 y contextos de prueba:
mejoró respuesta e intensidad, sin más aciertos que recentrar. Usa un contexto
escalar estimado por PMU y familia/ON/OFF conocidos; no integra la incertidumbre
del contexto ni modifica R11/C01. Véase `../ei-x02-results.md`.

La igualdad gaussiana requiere linealización contextual y la independencia
condicional declarada. Conservar log|V|. La expansión omite derivadas de Q
respecto al contexto que pueden importar a amplitudes finitas. X01 valida
identidades densas/bajo rango; X02 añade una prueba física acotada de E_i,
no superioridad del estimador conjunto DICE.

## 10. Cálculo comprimido y resolución — herramientas conocidas

\[
\|r-Fc\|^2=r^\top r-2c^\top F^\top r+c^\top F^\top Fc.
\]

El Gram por soporte ya existía. X01 comparte columnas y agrupa GH31, con
equivalencia sintética verificada. La dependencia temporal exige tratar
el comienzo del blanqueamiento y el estado de llegada a una ventana.

\[
d_h^2=\min_{j\ne h,\eta_j\in\mathcal A_j}
 \|s_h-s_j(\eta_j)\|_{\Sigma^{-1}}^2.
\]

El margen describe competidores y restricciones explícitas. Una correlación
retrospectiva no es certificación de localización, cobertura o cota óptima
para mezclas/137 soportes. La calibración y una política de riesgo/espera son
pruebas posteriores, no resultados de escribir una fórmula bayesiana.
