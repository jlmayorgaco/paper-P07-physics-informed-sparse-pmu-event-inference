# P07: criterio de envío y ruta de cierre

**14 de noviembre de 2026. Dictamen: borrador para revisión.**

La pregunta principal es si conservar alternativas de recuperación
mejora la atribución oportuna frente a un control continuo. C02 compara
procedimientos completos. C03 separa la retención de historias de
conservar la media del estado, con la covarianza nominal compartida.
Ese control no conserva la dispersión completa de la mezcla. El artículo
no debe atribuir un contraste positivo a etiquetas de historia por sí solas.

| Puerta | Estado y acción concreta |
|---|---|
| C03, ambas plantas | COMPLETO. Importacion verificada: 528 predicciones y 16 archivos compactos. F01: 144/144 frente a 90/144; P2: 67/144 frente a 65/144. Incluye estres, fallos y restauraciones. |
| Tesis y alcance | Ventaja de historias frente a fusion de medias solo demostrada en F01; continuidad frente a reset en ambas plantas. No se afirma superioridad sobre fusion con toda la covarianza ni transferencia general. |
| Ruido independiente | Cerrado como replay secundario: a las dos escalas el oráculo no superó a la estimación por familia. La cota normal de 9,17/h en TEST no verifica 1/h. |
| Posterior con inicio desconocido | Reproducción del ejemplo swing y una semilla nueva; la ganancia pequeña por la mezcla cambia de signo. No cambia las conclusiones del caso IEEE-39. |
| Comparador Yang | La comprobación de su recursión fue sintética. Conservarlo como antecedente y explicitar la ausencia de reproducción del caso publicado; no reportar una comparación cuantitativa inexistente. |
| Fuente y PDF | PASS local: 19 paginas de articulo y 44 de suplemento. ZIP editorial y reproducible compilados aisladamente, con texto/paginacion iguales. Figuras protegidas: 16 hashes verificados y ambas visibles. Falta evidencia del build remoto de Overleaf; publicar por Git no demuestra que el servidor haya compilado. |
| Revisión y declaraciones | Con C03 integrado, completar la lectura técnica, la reconstrucción independiente y la revisión editorial. Coautores confirman versión, afiliaciones, orden, financiación, conflictos, ORCID del remitente, permisos de datos/código, exclusividad y divulgación de IA según su uso real. |

## Experimento sucesor, solo si cambia la conclusión de C03

Si C03 favorece historias frente a fusión, pero se desea afirmar que la
mezcla supera un estado gaussiano comparable, ejecutar un sucesor con
tres brazos: covarianza nominal compartida, cierre por momentos y mezcla.
Conservar igual admisión, reloj, representación de severidad y estado
instrumental. Incluir la varianza de severidad dentro de componente y entre
componentes; no fusionar modos con distinta dinámica futura bajo un
mismo modelo de transición. Registrar compresión, publicación OFF y
siguiente onset en el evaluador, sin entregar verdad al filtro.
Congelar CAL, TEST nuevos, balance por fuente, métrica y manejo de
simulaciones fallidas antes de inferir TEST. Reportar calibración, cobertura
por padre, extras, incertidumbre y costo. La ablación de swing no sustituye
esta prueba. No hace falta añadirla para una tesis limitada al contraste
exacto de C03.

## Entrega editorial

Tipo propuesto: Research Article. Cargar el PDF y las fuentes que
reproduzcan exactamente su contenido, el suplemento y las declaraciones
aprobadas. La [guía de IEEE Access](https://ieeeaccess.ieee.org/authors/submission-guidelines/)
también exige biografías, ORCID del remitente y divulgación del texto
generado con IA. El borrador trae las cinco biografías. Véase
[declaraciones pendientes](SUBMISSION_DECLARATIONS_PENDING.md).
