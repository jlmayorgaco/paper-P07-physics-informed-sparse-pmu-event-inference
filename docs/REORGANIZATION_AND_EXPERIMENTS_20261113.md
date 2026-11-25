# Revisión del argumento y experimentos de desarrollo

El artículo presenta el mecanismo en el orden problema, predictor,
separación nominal, evaluación y límites. Cada figura acompaña la
pregunta que responde. El resumen identifica al GLR continuo y su
diferencia pareada como la comparación física principal. Las figuras
protegidas se conservan completas. Las 20 páginas se toman como presupuesto
de lectura, siguiendo la [guía de IEEE Access](https://ieeeaccess.ieee.org/authors/submission-guidelines/).

| Adjunto | SHA-256 | Decisión |
|---|---|---|
| Organización de páginas | 9498c462ae6f73923183e01fc664d15fbc917067897da0597ecc59c8962013e9 | Integrar teoría y evidencia cerca de la pregunta. La propuesta de IMM igualado queda pendiente de una ejecución comparable. |
| Dirección matemática | 3f1190fe4f20b56b099ea6ff90b4fbaa8b66e8f61ef20ff3f7e9a4da8b51dd7c | Duplicado del adjunto auditado. Extender la marginalización de incertidumbre a una dirección de recuperación de IEEE-39. |
| Diez teoremas | 7997ebefb7f50678b8bf38c56e7da6b2f1b7c9ddae218dd67e9df25d785c05d2 | Conservar las identidades bajo sus condiciones y revisar las inferencias del cuadro siguiente. |
| Método publicable | 108fa55c9c5e8c03a8a01e537dc173ac8e9cb30c8e35c9da0ac7cc52d4aded4b | Ejecutar los tres primeros diagnósticos: incertidumbre, tiempos y evidencia secuencial. |

| Teoremas propuestos | Qué se sostiene y con qué alcance |
|---|---|
| 1 y 6 | Distancia entre conjuntos de medias con restricciones explícitas. Un cero establece que existe un caso ambiguo para ese contrato. La covarianza de la diferencia acoplada no es la predictiva de cada historia. La monotonicidad bajo marginalización no implica submodularidad. |
| 2 | La masa podada es la distancia de variación total al condicionar un posterior ya calculado sobre las historias retenidas. Consistencia y tasa exponencial necesitan control de información acumulada y de fluctuaciones. Una cota local de Riccati necesita sus condiciones de estabilidad y condicionamiento. |
| 3 | Con el convenio de innovación predictiva del banco, el error previo evoluciona por T−KJ. La cota de ganancia determinista se refiere a la energía del nulo en ese modelo. Las alarmas dependen además de ruido, pesos y confirmación. El radio espectral por sí solo no garantiza la cota de potencias con esa misma tasa. |
| 4 | Las cotas minimax dependen del contrato de cambio, la tasa de información y la restricción de falsas alarmas. Sustituir la KL por un perfilado de la firma requiere una demostración adicional. |
| 5 | El momento de segundo orden de una mezcla incluye la dispersión entre medias. La cota KL propuesta falla en el ejemplo reproducible de la auditoría anterior. |
| 13–16 | El acoplamiento proviene del grafo. La reducción de la DAE general tiene alcance distinto de Kron. Para comparar simetrías se requiere invariancia de observaciones etiquetadas y del modelo completo. Una apertura serie en DC puede ser de rango uno, mientras un sello pi completo puede ser de rango dos. |

Los contraejemplos previos se documentan en
[la auditoría de la segunda ola](IDEAS_SECOND_WAVE_AUDIT_20261113.md).

## Reproducir

Desde una copia aislada, ejecutar
`python -B experiments/recovery_nuisance_20261113/run.py`. El protocolo y
los hashes de los operadores se fijaron antes del cálculo. La geometría
usa el banco nominal y la covarianza apilada del nulo. Los resultados
son deterministas y comparten operadores, por lo que los 1.296 contrastes
no son padres estadísticos. Los tiempos se ajustan en intervalos
conocidos sobre datos generados con el mismo predictor. La prueba de Ville
usa 20.000 registros gaussianos de 120 reportes por condición y ruido
emparejado. Las tres pruebas son de desarrollo.

`python -B experiments/recovery_nuisance_20261113/present.py` verifica
el sello y genera las cifras del manuscrito y la figura. En el entorno
registrado, reproducir el cálculo devuelve los mismos resultados. La
extensión de la geometría a errores de parámetros, recuperación multimodal
y ruido independiente requiere nuevos operadores y validación. Para
atribución, la prueba que sigue es comparar precisiones fijas con las
mismas reglas de búsqueda, actualización y calibración. La regla de Ville
necesita una ley nula válida y un presupuesto explícito para reinicios.

## Estado de la evaluación

Al corte de 18:58 Bogotá, el registro de C03 indicaba 69/72 registros de
TEST de F01 procesados y no había resultado final de ambas plantas.
La lectura fue operativa. P07 mantiene la comparación sellada de
procedimientos y el estado de borrador para revisión.
