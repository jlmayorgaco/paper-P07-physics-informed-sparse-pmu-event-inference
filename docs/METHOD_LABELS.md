# Identificadores de los métodos P07

| Identificador | Método | Resultado documentado y ámbito |
|---|---|---|
| MET_HACKATON_ETREE | Entrega original de junio. ExtraTrees jerárquico sobre características de ventanas de 30 s. | Validación interna histórica: exactitud del detector 0,9693; macro-F1 0,9598; ubicación exacta 0,8524. |
| MET_C01_ETREE_CAUSAL | Comparador ExtraTrees entrenado para C01 con estadísticas retrospectivas de PMU. | 330/648 atribuciones oportunas y 29 alarmas extra; variante de ventanas cortas 352/648 y 16 extra. |
| MET_C01_BANCO_FISICO | Banco DAE del artículo. Compara la recuperación sin evento nuevo con intervenciones candidatas y evalúa diferentes hipótesis de impedancia. | 644/648 atribuciones oportunas y 72 alarmas extra en el mismo C01 de carga y línea. |
| MET_M9_BAYES_CL8 | Mantiene el clasificador congelado y cambia la ubicación de clase 8 mediante marginalización sobre inicio e intensidad. | Nueve clases M9: 54/64 aislados, 53/64 después de falla; referencia pareada 53/64 y 52/64. |
| MET_LOCAL_FIRMAS_VI | Ajusta firmas dinámicas de tensión y corriente al registro para ordenar activos, con la familia suministrada. | 256/276 exactos en tres familias físicas con activos reservados, frente a 138/276 solo con tensión. |
| MET_BAYES_MEMORIA | Filtro de partículas con recuperación física e incertidumbre condicionada a los reportes anteriores. | 171/192 eventos en tiempo, familia y activo; 12 falsas alarmas en 64 ventanas sin evento y macro-F1 0,9483 en tres familias más normalidad. |
| MET_PMU_FIRMAS_ETREE | Monitor supervisado causal. ExtraTrees para detectar, estimar inicio y clasificar; ordena activos con características que comparan la observación con simulaciones de tensión y corriente. | Prueba 70/30 de nueve clases: 0,9753 macro-F1, 1384/1444 detecciones oportunas, 1377/1444 familias correctas y 1251/1444 aciertos conjuntos. Cero alarmas en 168 registros normales; dos sin correspondencia en registros con eventos. |

Los identificadores nombran implementaciones evaluadas. El catálogo y el criterio de cada resultado son parte de su definición experimental. C01 compara directamente el banco físico y sus comparadores causales. El estudio 70/30 y el prototipo de partículas se ejecutaron en poblaciones distintas.

Fuentes: [traza histórica y C01](HACKATHON_TO_C01_METHOD_TRACE.md), [M9](../experiments/composite_identifiability/README.md), [corrientes de rama](../experiments/branch_current_trial/README.md), [partículas](../experiments/bayesian_event_stream/README.md) y [monitor supervisado](../experiments/supervised_stream/README.md).

La extensión propuesta para las cuatro familias físicas se llama [MET_BAYES_GRAFO](MET_BAYES_GRAFO.md). Tiene una derivación y una comprobación de la proyección sobre firmas de carga y línea. Su validación conjunta en las cuatro familias sigue pendiente.
