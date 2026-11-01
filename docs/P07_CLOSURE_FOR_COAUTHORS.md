# Cierre de P07 para David y Masoud

## Contrato científico

**Problema.** Una nueva intervención puede comenzar mientras la red aún responde a la restauración de otra; ocho PMU no observan directamente todos los estados ni las fuentes.

**Brecha acotada.** Comparar señales o acertar una etiqueta no basta para decidir si hay una nueva causa, localizarla antes de OFF y cerrar el episodio sin alarmas adicionales. Los precedentes ya ofrecen estimación DAE, trayectorias, búsqueda de inicio y filtros de múltiples historias.

**Idea.** Comparar historias de intervención y recuperación desde estados anteriores estimados, con el mismo mapa instrumental, separando masa activa y causa retenida.

**Prueba que puede refutar la utilidad.** Comparación congelada con nominal, dos ExtraTrees y Chen en su contrato admisible, usando decisiones emitidas, falsos positivos, demoras y fallos; conservar derrotas. X02/X04 separan la calidad del predictor de la decisión de origen.

**Consecuencia.** Un procedimiento físico ejecutable para atribución temporal y una evidencia que permite elegir entre configuraciones según errores y demora. No se deduce un filtro globalmente óptimo ni un nuevo principio de Bayes.

## Física y estadística: correspondencia con el código congelado

Raíz de código: `../SGSMA26-Physics-Informed-AD/`.

| Elemento del artículo | Implementación verificada | Qué significa |
|---|---|---|
| Eliminación algebraica y respuesta remota | `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/physics/build_static_rx.jl`, `work`, `Zx`, `Zu`, `Cpmu`, `Dpmu` | DAE en una carta regular; derivadas mediante ForwardDiff y comprobaciones locales por diferencias. La topología entra en las ecuaciones, no como embedding entrenado. |
| Observación eléctrica orientada | Mismo constructor, `observable`; `run/runtime/conditional_builder.py`, `observable` | El voltaje es nodal; la corriente es terminal. Bases, orientación y ganancias pertenecen al contrato F01. |
| Frecuencia/ROCOF y memoria | `run/runtime/conditional_builder.py`, `derivatives`, `roll`, `operator` | Aproximación lineal de 21 reportes y memoria instrumental; no sustituir frecuencia de bus por velocidad de rotor. |
| Ganancia y covarianza compartida | `run/runtime/conditional_builder.py`, bucle `solve_discrete_are`; `core_v6.py`, `process` | Covarianza Riccati del operador nominal para cada régimen. Ganancias según operador; no hay Riccati exacta por cada historia en R11. |
| Media afín en severidad | `core_v6.py`, `process`, arrays `m`, `d`, `mu`, `var` | El residuo es `e-sa`; la media corregida sigue `T*m+g+K*e`, y su dirección `T*d+u-K*s`. |
| Integral bayesiana local | `amplitude_parent.py`, `trunc`; `core_v6.py`, `process`; `observer/static_rx.py`, `integrated_loglike` | Integral de amplitud normal truncada, no perfilado de la amplitud óptima; constantes gaussianas comunes se cancelan. |
| R/X fijo por hipótesis | `observer/static_rx.py`, `predictive_log_density`, `StaticRX` | Densidad predictiva antes de seleccionar propuestas/corregir estado; mezcla finita, no identificación continua de todas las impedancias. |
| Restauración y cierre | `core_v6.py`, `transitions`, `process`; `core_v9.py`, `update_episode` | Los hijos OFF heredan estado; el cierre proyecta su media aumentada y registra dispersión omitida. Continuidad de media no equivale a posterior conjunto exacto. |
| Decisión pública | `observer/static_rx.py`; `confirmation_r08.py` | Confirmación y reemplazo de episodio son reglas congeladas, no teoremas de optimalidad ni garantías de falsa alarma. |

Las rutas `run/runtime` pertenecen a `experiments/PAPER_CONFIRMATORY_C01/`; `observer` pertenece a `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/`.

## Cambios editoriales de este cierre

- Explicitada la reducción del operador de medición: la física conecta un bus no medido con las ocho PMU mediante restricciones de red y dinámica.
- Explicitada la corrección de media y dirección de severidad; la limitación de covarianza compartida ya no queda escondida tras la palabra «Bayesian».
- La página de coautores obtiene las cifras de macros/artefactos completos y el estado de C01 solo de metadatos operacionales.
- Conservados el título, los métodos, los casos y las figuras protegidas. No se añaden GNN, wavelets, THD, nuevos candidatos ni experimentos de rendimiento.

## Qué se cierra y qué sigue pendiente

El alcance, los comparadores, el argumento y las pruebas X02/X03/X04 están cerrados para esta entrega. C01 sigue ejecutándose; una campaña activa no puede declararse terminada por una decisión editorial. `C01_COAUTHOR_STATUS.json` conserva fecha, progreso, mezcla de duraciones y proyección basada en los últimos 12 registros completos de cada duración. El rango es una envolvente de tiempos recientes, no un intervalo probabilístico.

Antes de someter: completar C01, verificar los 171/342 denominadores previstos y sus fallos, integrar las comparaciones por contrato, exposición, censuras e intervalos por padre, revisar las afirmaciones según el resultado, y obtener revisión de autores/metadatos/reproducibilidad. No escoger otra variante tras ver C01. Una derrota se reporta; no dispara otra corrección por bus.

El borrador y la página pueden circular ahora entre coautores con C01 marcada pendiente. No se han enviado mensajes a David ni a Masoud.
