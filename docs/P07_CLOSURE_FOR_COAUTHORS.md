# Cierre de P07 para David y Masoud

**Revisión científica del 3-nov:** [respuesta completa a la auditoría](SCIENTIFIC_AUDIT_RESPONSE_20261103.md). Las cifras de C01/A01 se conservan. Las tasas por hora de eventos usan ahora solo tiempo monitorizado; la tabla de prior defectuoso pasa a evidencia auxiliar. El artículo es un borrador para revisión, con brechas científicas explícitas antes del envío. La página de contribución se regenera desde las cohortes completas.

## Contrato cientÃ­fico

**Problema.** Una nueva intervenciÃ³n puede comenzar mientras la red aÃºn responde a la restauraciÃ³n de otra; ocho PMU no observan directamente todos los estados ni las fuentes.

**Brecha acotada.** Comparar seÃ±ales o acertar una etiqueta no basta para decidir si hay una nueva causa, localizarla antes de OFF y cerrar el episodio sin alarmas adicionales. Los precedentes ya ofrecen estimaciÃ³n DAE, trayectorias, bÃºsqueda de inicio y filtros de mÃºltiples historias.

**Idea.** Comparar historias de intervenciÃ³n y recuperaciÃ³n desde estados anteriores estimados, con el mismo mapa instrumental, separando masa activa y causa retenida.

**ComparaciÃ³n con nuestro trabajo de hackathon.** La entrega original usa
ExtraTrees jerÃ¡rquico y 45.162 features en ventanas de 30 s para nueve
clases. C01 compara dos sucesores causales de esa idea, entrenados antes
del conjunto sellado, con el banco fÃ­sico sobre el mismo flujo de ocho PMU.
La tabla principal ahora muestra cargas, lÃ­neas y extras para las cuatro
rutas. La puntuaciÃ³n histÃ³rica de la entrega no es una mÃ©trica de C01.

**Prueba que puede refutar la utilidad.** ComparaciÃ³n congelada con nominal, dos ExtraTrees y Chen en su contrato admisible, usando decisiones emitidas, falsos positivos, demoras y fallos; conservar derrotas. X02/X04 separan la calidad del predictor de la decisiÃ³n de origen.

**Consecuencia.** Un procedimiento fÃ­sico ejecutable para atribuciÃ³n temporal y una evidencia que permite elegir entre configuraciones segÃºn errores y demora. No se deduce un filtro globalmente Ã³ptimo ni un nuevo principio de Bayes.

## FÃ­sica y estadÃ­stica: correspondencia con el cÃ³digo congelado

RaÃ­z de cÃ³digo: `../SGSMA26-Physics-Informed-AD/`.

| Elemento del artÃ­culo | ImplementaciÃ³n verificada | QuÃ© significa |
|---|---|---|
| EliminaciÃ³n algebraica y respuesta remota | `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/physics/build_static_rx.jl`, `work`, `Zx`, `Zu`, `Cpmu`, `Dpmu` | DAE en una carta regular; derivadas mediante ForwardDiff y comprobaciones locales por diferencias. La topologÃ­a entra en las ecuaciones, no como embedding entrenado. |
| ObservaciÃ³n elÃ©ctrica orientada | Mismo constructor, `observable`; `run/runtime/conditional_builder.py`, `observable` | El voltaje es nodal; la corriente es terminal. Bases, orientaciÃ³n y ganancias pertenecen al contrato F01. |
| Frecuencia/ROCOF y memoria | `run/runtime/conditional_builder.py`, `derivatives`, `roll`, `operator` | AproximaciÃ³n lineal de 21 reportes y memoria instrumental; no sustituir frecuencia de bus por velocidad de rotor. |
| Ganancia y covarianza compartida | `run/runtime/conditional_builder.py`, bucle `solve_discrete_are`; `core_v6.py`, `process` | Covarianza Riccati del operador nominal para cada rÃ©gimen. Ganancias segÃºn operador; no hay Riccati exacta por cada historia en R11. |
| Media afÃ­n en severidad | `core_v6.py`, `process`, arrays `m`, `d`, `mu`, `var` | El residuo es `e-sa`; la media corregida sigue `T*m+g+K*e`, y su direcciÃ³n `T*d+u-K*s`. |
| Integral bayesiana local | `amplitude_parent.py`, `trunc`; `core_v6.py`, `process`; `observer/static_rx.py`, `integrated_loglike` | Integral de amplitud normal truncada, no perfilado de la amplitud Ã³ptima; constantes gaussianas comunes se cancelan. |
| R/X fijo por hipÃ³tesis | `observer/static_rx.py`, `predictive_log_density`, `StaticRX` | Densidad predictiva antes de seleccionar propuestas/corregir estado; mezcla finita, no identificaciÃ³n continua de todas las impedancias. |
| RestauraciÃ³n y cierre | `core_v6.py`, `transitions`, `process`; `core_v9.py`, `update_episode` | Los hijos OFF heredan estado; el cierre proyecta su media aumentada y registra dispersiÃ³n omitida. Continuidad de media no equivale a posterior conjunto exacto. |
| DecisiÃ³n pÃºblica | `observer/static_rx.py`; `confirmation_r08.py` | ConfirmaciÃ³n y reemplazo de episodio son reglas congeladas, no teoremas de optimalidad ni garantÃ­as de falsa alarma. |

Las rutas `run/runtime` pertenecen a `experiments/PAPER_CONFIRMATORY_C01/`; `observer` pertenece a `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/`.

## Cambios editoriales de este cierre

- Explicitada la reducciÃ³n del operador de mediciÃ³n: la fÃ­sica conecta un bus no medido con las ocho PMU mediante restricciones de red y dinÃ¡mica.
- Explicitada la correcciÃ³n de media y direcciÃ³n de severidad; la limitaciÃ³n de covarianza compartida ya no queda escondida tras la palabra Â«BayesianÂ».
- La pÃ¡gina de coautores obtiene las cifras de la importaciÃ³n C01 sellada y verifica sus hashes y denominadores antes de compilar.
- Conservados el tÃ­tulo, los mÃ©todos, los casos y las figuras protegidas. No se aÃ±aden GNN, wavelets, THD, nuevos candidatos ni experimentos de rendimiento.

## QuÃ© se cierra y quÃ© sigue pendiente

El alcance, los comparadores, el argumento y las pruebas X02/X03/X04 estÃ¡n cerrados para esta entrega. C01 terminÃ³ sin reajustes: 171 trayectorias fÃ­sicas, 342 registros observados y predicciones selladas antes de abrir la verdad. `C01_COAUTHOR_STATUS.json` y la [sÃ­ntesis confirmatoria](c01-confirmatory-results.md) reemplazan la proyecciÃ³n de tiempo anterior. Los 648 eventos continuos son seis replays correlacionados de 108 intervenciones, no 648 eventos independientes.

Antes de someter: revisiÃ³n cientÃ­fica de autores de la afirmaciÃ³n metodolÃ³gica y de la derrota de alarmas fuera del banco R/X; verificaciÃ³n final de citas, metadatos, figuras y paquete reproducible. Los denominadores, fallos, exposiciÃ³n, censuras e intervalos por padre ya estÃ¡n integrados. No escoger otra variante tras ver C01. Una derrota se reporta; no dispara otra correcciÃ³n por bus.

El borrador y la pÃ¡gina pueden circular ahora entre coautores con C01 completa y sus lÃ­mites explÃ­citos. No se han enviado mensajes a David ni a Masoud.
