# Segunda revisión de ideas: incertidumbre, memoria y precisión física

## Contrato científico

Problema: atribuir una nueva intervención mientras persiste una recuperación
incierta. Brecha a probar: una representación o aproximación económica puede
modificar las evidencias y la decisión. Idea de trabajo: conservar la
distribución relevante y refinar el predictor cuando la incertidumbre de su
puntuación impida decidir. Prueba refutadora: comparar con el mismo banco,
la misma incertidumbre y búsqueda, utilizando precisión fija o referencia
costosa. Consecuencia: conservar el módulo únicamente si reduce costo con
decisiones y alarmas comparables, o mejora atribución a costo declarado.

Esto es una dirección sucesora, no una nueva tesis ya demostrada para P07.
C03 conserva su contrato. Los resultados 99/108 de C02 y 3,191→0,139 grados
del predictor no se transfieren a una arquitectura IEKF/grafo/Hamiltoniana.

## Procedencia y dictamen

Los once adjuntos tienen siete contenidos distintos. El manifiesto está en
`experiments/decision_bounds_20261113/INPUT_PROVENANCE.json`. Hay tres copias
idénticas de grafos, dos de la segunda ola y dos de la dirección matemática.
La derivación de Kirchhoff coincide byte por byte con la validada antes.
Los números ilustrativos de tres barras del texto nuevo no se importan:
no se suministró aquí el paquete específico que produce esos números.

Las propuestas recientes son más cuidadosas que las primeras: reconocen
la suficiencia de la distribución del estado, limitan el Hamiltoniano y
separan clasificación binaria de inferencia con parámetros desconocidos.
Sus condiciones deben prevalecer sobre las afirmaciones anteriores.

| Propuesta | Dictamen | Acción concreta |
|---|---|---|
| Información bajo recuperación incierta | Válida en el modelo gaussiano declarado | Verificar identidad con P singular; usar para diagnóstico condicionado, no como exactitud del banco |
| Refinar según cambio posible de evidencia | Válida condicionalmente; faltan cotas baratas del error físico | Implementar radio con media y covarianza, intervalos de masa y cuadratura |
| Memoria por energía/Lyapunov | Condicional a estabilidad, observación y modo fijo | No fijar 9,34/12,71 s en F01; comprobar antes el modo neutro y la referencia |
| IEKF con prior fijo | Formulación útil, antecedente establecido | Sucesor con una asimilación por reporte; evidencia predictiva, no residual ajustado |
| Reducción port-Hamiltoniana | Válida para una realización admisible | Primero demostrar Q positivo y estructura del bloque; luego igualar dimensión y costo |
| Wavelets gráficas | Propuesta de candidatos, no likelihood adicional | Medir recall de candidatos y tiempo con retorno a búsqueda completa |
| Corrientes condicionadas a voltajes | Ya derivado y ensayado en P07 | Evitar duplicar la sección o sumar evidencias correlacionadas |
| NIS y trazas de masa para diagnóstico | Útiles como señales de incompatibilidad | No diagnosticar automáticamente PMU defectuoso, ataque o parámetro erróneo |
| Protección, estándares, placement, redes nuevas | Extensiones no validadas | No convertir en capacidades ni requisitos de compra del artículo actual |

## Correcciones a los teoremas 7–12 propuestos

**T7, error de modelo.** Una norma escalar del error no conserva la dirección
de una perturbación de parámetros: la derivada actúa sobre un vector/matriz.
K términos de sesgo constante al cuadrado suman O(K), no O(K²). Si el sesgo
crece con k, el orden depende de esa dinámica y de la covarianza temporal.
Ni una norma de error ni NIS por sí solos certifican la causa de las alarmas.
La prueba ejecutada incluye la razón gaussiana de sesgo constante como control.

**T8, Fisher y severidad.** Con media lineal y covarianza fija, el estimador
GLS sin límites es normal y eficiente ya en muestra finita. El clip introduce
sesgo. Con covarianza dependiente de a, la información es
I(a)=mu'(a)^T Sigma(a)^(-1) mu'(a)
+ 1/2 tr[Sigma^(-1) Sigma' Sigma^(-1) Sigma']; no se omite el segundo término.
El cruce de información esperada con un umbral no da probabilidad de detección
ni cobertura de intervalos después de seleccionar fuente e inicio.

**T9, retraso detección–aislamiento.** No se acepta una suma universal de
retrasos y log(catálogo)/D_min. Una misma observación puede detectar e
identificar; con soportes disjuntos ambas decisiones ocurren al primer dato.
Se requieren restricciones precisas de falsas alarmas, error de aislamiento,
tasas de información y régimen asintótico. Fano no produce esa suma sin más.

**T10, solapamiento.** Una distancia mínima cero identifica un par ambiguo
admisible, no toda realización. La genericidad no se obtiene invocando Sard;
requiere parametrización, rango y restricciones verificadas. No ampliar el
catálogo de C03 ni reinterpretar restauración residual como evento solapado.

**T11, covarianza.** La muestra necesaria depende de escala, rango efectivo,
colas, dependencia temporal, precisión absoluta/relativa y estructura conocida.
La expresión r log(p)/epsilon² sin esas condiciones no demuestra que 300
reportes basten. 47 son coordenadas, no PMU. Ruido independiente no implica
covarianza más difícil de estimar: una estructura diagonal conocida es más
simple. No atribuir los fallos a un límite de información sin comparador.

**T12, pérdida y relojes.** Las filas de C solas no acotan pérdidas de una
trayectoria blanqueada: intervienen propagación, horizonte, unidades y ruido.
La identidad de Schur ya ofrece el incremento condicional correcto para
covarianza común. Para relojes aleatorios,
Var(delta theta_i-delta theta_j)=(2 pi f)^2
[Var(t_i)+Var(t_j)-2 Cov(t_i,t_j)]. Un sesgo fijo es un sesgo, no una varianza.
A 60 Hz, 1 ms son 21,6 grados; dos errores independientes de desviación
1 ms dan 0,28424 rad² de varianza diferencial, mientras un error idéntico
se cancela en la diferencia ideal. Esto no prueba requisitos GPS/PTP ni
robustez de frecuencia/ROCOF durante transitorios.

## Correcciones a los teoremas 13–17 de grafos

**T13.** L^dagger e_i necesita declarar cómo se equilibra la inyección y la
referencia. La detectabilidad depende de la proyección de sensores y ruido;
no es una función universal monótona de distancia/resistencia a sensores.
La definición propuesta invierte una suma de resistencias y no constituye
la resistencia usual a un conjunto conectado a tierra. No explica BUS31.

**T14.** Permutar sensores etiquetados produce salidas permutadas, no iguales.
El contraejemplo de tres nodos da (2/3,-1/3) y (-1/3,2/3). Una condición
suficiente exige invariancia del mapa de observación y equivariancia de
dinámica completa, parámetros, estados/prior, controles, entradas y ruido.
Fijar sensores punto a punto no basta si otros componentes rompen la simetría.
Órbitas de automorfismos y celdas equitativas tampoco son equivalentes en general.

**T15.** En una red serie reducida invertible, Y_open=Y-y bb^T. El denominador
de Sherman–Morrison aparece en la inversa, no en el propio cambio de Y:
V_open-V=+[y/(1-y b^T Y^(-1)b)]Y^(-1)b b^T V.
El denominador debe ser no nulo. Shunts/transformadores requieren su sello
completo; el ejemplo pi ejecutado tiene rango complejo dos. Firmas colineales
no son idénticas con amplitud de apertura fijada. El caso sin flujo previo
puede dar firma cero. Una fórmula de corrientes inyectadas fijas no sustituye
la DAE con cargas y controles.

**T16.** El complemento de Schur de una Laplaciana admisible es una reducción
de Kron; cualquier eliminación algebraica no lo es. En los operadores F01
guardados, A es 114×114 y su asimetría relativa es aproximadamente 1,41;
C es 78×114. No son Laplacianas no dirigidas. La estructura de conexión sigue
siendo física y útil sin imponer una identidad falsa. Ni siquiera una
linealización AC general convierte el Jacobiano de estado en Laplaciana.

**T17.** Un corte de peso pequeño no garantiza error posterior pequeño uniforme
en tiempo, observaciones y ruido. Faltan condiciones de estabilidad,
normalización y sensibilidad de likelihood. Costo de comunicación no tiene
las mismas unidades que admitancia. No dividir 99,6 ms por k y llamar al
resultado tiempo real; se debe medir búsqueda, comunicación y sincronización.

Tampoco se aceptan: que toda FDI viole Kirchhoff (puede ser consistente con
otro estado); que wavelets necesariamente arreglen ExtraTrees; ni que el
objetivo max-min perfilado sea submodular. El contraejemplo de submodularidad
de la auditoría anterior permanece vigente. La capa cyber sigue separada.

## Derivaciones válidas para el sucesor

### Recuperación incierta

Con z~N(0,P), ruido independiente N(0,R), R positiva definida y P semidefinida,
r=O z+s a+epsilon implica Sigma=R+O P O^T. Tomando U=O P^(1/2),
G=s^T R^(-1)s-s^T R^(-1)U(I+U^T R^(-1)U)^(-1)U^T R^(-1)s.
La segunda parte es no negativa. La forma evita invertir P cuando es singular.
Si O depende de severidad, Sigma también: se evalúan determinante y cuadrática
para cada a y se integra con el prior una sola vez. Si estado y severidad
están correlacionados, se usa la distribución condicional, no independencia
impuesta. El límite de clasificación Phi(-d/2) solo es exacto para dos
hipótesis simples de igual covarianza y prior, sin búsqueda de inicio.

### Cota de puntuación que incluye covarianza

Sean p=N(mu,Sigma), p_t=N(mu_t,Sigma_t), ambas SPD y dimensión d. Elegir W
tal que W Sigma_t W^T=I. Definir r=||W(y-mu_t)||, delta=W(mu-mu_t),
E=W Sigma W^T-I. Supóngase ||delta||<=epsilon y ||E||_2<=eta<1. Entonces

|log p(y)-log p_t(y)| <= B,
B = 1/2 { -d log(1-eta) + [eta r²+2 r epsilon+epsilon²]/(1-eta) }.

Prueba: los autovalores de I+E pertenecen a [1-eta,1+eta], por lo que el
valor absoluto del logdet no supera -d log(1-eta). Además,
||(I+E)^(-1)||<=1/(1-eta) y
||(I+E)^(-1)-I||<=eta/(1-eta). Expandir
(z-delta)^T(I+E)^(-1)(z-delta)-z^T z y aplicar esas dos normas prueba
el resto. Si eta=0 se recupera r epsilon+epsilon²/2. Con media idéntica y
varianzas 1 y 4, y=0, el error de score es log(2): una cota solo de media
es inválida cuando cambia la covarianza.

Esta es una desigualdad elemental condicionada a cotas válidas, no una
garantía nueva de error de la DAE. El máximo RMSE observado o la diferencia
entre dos pasos de integración no certifican epsilon. El error temporal
de observación y los cambios de topología también deben quedar acotados.

### Ganador, masa y evidencia marginal son verificaciones distintas

Con scores que incluyen el mismo prior y |S_h-S_t,h|<=B_h, el ganador i
se conserva si S_t,i-B_i > max_j!=i(S_t,j+B_j). Ello no conserva por sí
solo un umbral de probabilidad. Para un grupo A (p.ej., evento activo), sean
L_A=sum_A exp(S_t-B), U_A=sum_A exp(S_t+B), y L_B,U_B para el complemento.
La masa del grupo está en [L_A/(L_A+U_B), U_A/(U_A+L_B)]. Evaluar con
logsumexp. Solo se aplica al mismo catálogo finito; la poda requiere cota
separada de masa omitida. No borrar una historia basándose solo en el ganador.

Para cuadratura de pesos positivos w_l, las sumas de w_l exp(ell_t,l±B_l)
acotan la misma cuadratura de referencia. No acotan el error de integrar
continuamente sin control adicional. Una cota uniforme en severidad sí se
propaga a la integral con el mismo prior por monotonía. En un sufijo revisado,
reemplazar los factores anteriores; no sumar la evidencia por segunda vez.

### Recuperación y horizonte de memoria

Si A^T P_L+P_L A <= -2 alpha P_L con P_L>0 y alpha>0, la cota energética
del adjunto es válida en modo fijo y con C/Sigma fijados. Describe la
componente determinista alineada con una firma perfilada, no la FAR del
banco. La cota probabilística requiere un posterior correcto y, para ruido
futuro, un control separado de colas y multiplicidad. Descartar una historia
puede perder identidad causal aunque su salida física actual sea pequeña.

Las dos A nativas inspeccionadas tienen un autovalor cerca de cero (módulo
menor de 1e-7), no una tasa estricta de decaimiento validada. No se sustituyó
por un valor negativo ni se eliminó el modo para forzar el resultado.
El mapa de voltajes rectangulares observa ese vector; debe analizarse la
referencia y el mapa PMU efectivo antes de hablar de cociente estable.

## Antecedentes verificados y límites de novedad

- [Dörfler y Bullo, Kron Reduction](https://arxiv.org/html/1102.2950):
  Schur de Laplacianas bajo hipótesis de red; no afirma que A/C de cualquier
  DAE sean Laplacianas. La referencia del adjunto a TCNS no se importa.
- [Anguluri, Sankar y Kosut](https://arxiv.org/abs/2201.07907): fuentes
  desconocidas con estado inicial desconocido y group LASSO; antecedente
  directo que impide anunciar esa combinación como inédita.
- [Ponce y Bindel, FLiER](https://www.cs.cornell.edu/~bindel/papers/2017-tps.pdf):
  actualización topológica, linealización y filtrado económico con PMU
  escasas. No se atribuye a P07 la invención de firmas de bajo rango.
- [Gugercin et al., Automatica 2012](https://arxiv.org/abs/1101.3485):
  reducción con estructura port-Hamiltoniana. Q_r=V^T Q V y
  W=Q V Q_r^(-1) preservan estructura si Q>0 y V tiene rango completo;
  eso no garantiza conservar separación entre fuentes.

Se verificaron registros primarios y el texto de Kron/FLiER. Esta búsqueda
focalizada no es una auditoría completa de las demás referencias sugeridas.
No se añadieron referencias sin comprobar a la bibliografía del manuscrito.

## Próximos experimentos, en orden y sin alterar C03

1. **Incertidumbre del predictor refinado:** derivada del flujo numérico
   dependiente del estado frente a perturbaciones; covarianza y densidad
   predictiva en problema pequeño enumerable; severidad por cuadratura con
   convergencia y términos cruzados. Congelar antes de puntuar escenarios nuevos.
2. **Atribución, mismo contrato:** predictor fijo frente a refinado, después
   EKF frente a IEKF, cambiando un bloque por contraste. Misma búsqueda,
   PMU, datos y presupuesto CAL; fuentes/inicios desconocidos. Ningún resultado
   se hereda del ensayo de trayectoria con evento conocido.
3. **Refinamiento selectivo:** solo tras obtener cotas de error baratas válidas;
   comparar con precisión fija y referencia costosa. Medir decisiones
   discrepantes, certificados, abstenciones y costo incluyendo la propia cota.
4. **Memoria:** estudiar representación de estado, covarianza y mezcla antes
   de longitud de historial. Mantener separados error predictivo, atribución
   causal y publicación; energía decreciente no autoriza eliminar causas.
5. **Grafo/reducción opcionales:** recall de candidatos y fidelidad de diferencias
   de fuente a costo igual. No activar si eliminan candidatos verdaderos o
   alteran las alarmas. Cyber, protecciones y especificaciones PMU requieren
   contratos nuevos y quedan fuera de esta revisión.

C03 es la prueba central pendiente del manuscrito existente. No se condiciona
su cierre a implementar todas las extensiones anteriores ni se reescribe su
protocolo a partir de esta revisión. No hay garantía de aceptación editorial.
