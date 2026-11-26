# P07: plan de ejecución para el cierre

Fecha: 15 de noviembre de 2026. Estado: trabajo en curso, no listo para envío.

## Contrato científico

Problema: una respuesta de recuperación puede confundirse con la siguiente intervención. La pregunta es qué información de esa recuperación necesita conservar el estimador para atribuir familia y fuente antes de OFF. C03 separa historias, fusión de medias y reset bajo su aproximación de covarianza. C04 compara dos cierres con el mismo motor, masa, media y regla de publicación: covarianza condicional frente a covarianza que también retiene dispersión entre historias y varianza de severidad. La prueba puede refutar una ventaja de esa retención. Su consecuencia será una recomendación limitada por planta, presupuesto de alarmas y costo observado.

## Responsabilidades y orden

1. **Luna ejecución C04:** reparar el verificador de preparación, registrar procedencia y probar la corrección. Reutilizar observaciones existentes verificadas; no regenerar física. Pasar gates DEV y smoke legado antes de CAL. Congelar métodos y umbrales antes de TEST. Arrancar supervisor con logs y límites de recursos.
2. **Luna auditoría independiente:** revisar contraste, covarianza, publicación, causalidad, denominadores, emparejamiento, congelaciones y tratamiento de errores. Verificar C03 contra sus hashes. Comunicar cualquier veto antes de avanzar a TEST.
3. **Luna editorial:** auditar los archivos realmente incluidos en main.tex; entregar cambios concretos de narrativa, ecuaciones y pseudocódigo, y registro de afirmaciones. No atribuir resultados a C04 antes de su cierre.
4. **Coordinación principal:** revisar correcciones y hallazgos; aplicar cambios editoriales sustentados; mantener sincronizados estado y entrega. Integrar cifras solo desde resultados sellados, después de revisar ambas plantas y los fallos. Compilar y revisar visualmente la versión final, verificar figuras protegidas y publicar el paquete por Git.

## Evidencia necesaria para integrar C04

- Gates matemáticos y de desarrollo aprobados, con prefijo causal reproducible y fusión activada por OFF publicado.
- CAL completo con la misma rejilla y presupuesto por brazo; cualquier brazo sin umbral factible queda identificado.
- TEST nuevo de ambas plantas sellado antes de evaluar; fallos conservados en sus denominadores.
- Diferencias pareadas por padre, intervalos, alarmas normales y extra, restauraciones y costo computacional.
- Resultado favorable, nulo o adverso descrito sin cambiar retrospectivamente la hipótesis ni la selección.

## Límites que permanecen

C03 está cerrado y es solo lectura. Su ventaja de historias sobre fusión de medias está demostrada en F01, no en P2. Los fallos de admisión con ruido independiente y la degradación con pérdida de PMU permanecen visibles. No se añade una afirmación de robustez general sin una campaña sucesora. El costo piloto de C04 no permite afirmar ejecución en tiempo real. F01 conserva su mapa provisional de BUS5; RAW0002 permanece cerrado.

## Puerta editorial y de autores

Repetir la reconstrucción aislada y la revisión visual después de integrar la evidencia final. Conservar las dos figuras protegidas y sus hashes. La sincronización Git no equivale a verificar la compilación remota de Overleaf.

La [guía oficial de IEEE Access](https://ieeeaccess.ieee.org/authors/submission-guidelines/), consultada el 15 de noviembre, pide fuentes y PDF coincidentes, archivos de hasta 40 MB, biografías de todos los autores, ORCID del remitente y declaración del texto generado con IA. Recomienda menos de 20 páginas; no es un límite absoluto. Preparar las declaraciones y metadatos para revisión de los autores sin inventar aprobación, financiación, permisos o exclusividad.

El estado solo cambia a listo cuando la evidencia final, el paquete y las aprobaciones de autores estén cerrados. Las tareas de varios días permanecen en ejecución o bloqueadas según sus logs; no se consideran completadas por haber arrancado el supervisor.

## Verificación de esta revisión

Compilación local del artículo: 19 páginas, sin referencias/citas indefinidas. Persisten advertencias de sustitución tipográfica Formata de la plantilla. Revisión visual de páginas 5, 6, 9, 10, 16 y 17; figuras protegidas visibles y 16 hashes correctos. El paquete PDF publicado combina el artículo actual con el suplemento sin cambios (44 páginas).

El detector editorial `scan_pdf_text.py` sigue devolviendo 41 coincidencias en artículo y suplemento, principalmente identificadores F01/C03 y términos de procedencia como frozen/sealed. No es un error de compilación, pero su revisión editorial permanece abierta: decidir una nomenclatura científica consistente y modificar texto/figuras/generadores conjuntamente cuando se integre C04. No se relajó el detector para convertir estas coincidencias en un PASS automático. La reconstrucción aislada y la verificación remota deberán repetirse para la versión final.
