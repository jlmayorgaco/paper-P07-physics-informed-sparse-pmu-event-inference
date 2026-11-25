# C04: calibración reanudada

15 de noviembre de 2026, 20:00 Bogotá. Estado observado: `CAL_INFERENCE`, supervisor PID 22924, `test_access=false`. El código de ejecución quedó congelado antes de CAL; no hay resultados TEST ni una ventaja de covarianza demostrada.

Cambios preservados en el commit local científico `9dc780135`; no se publicó ese repositorio. Las 53 fuentes del sello de ejecución permanecen idénticas después del arranque.

Tres agentes Luna cubrieron reparación operativa, auditoría independiente y plan editorial. La revisión principal verificó sus propuestas y descartó dos exigencias incorrectas: los eventos no disponibles ya permanecen en el denominador, y no se exige que dos brazos con covarianza distinta mantengan posteriores iguales después de la intervención.

## Cambios y comprobaciones

- Reparado el conteo de estratos de preparación CAL: los 72 archivos originales se conservan. Un sidecar de metadata enlaza IDs con los 36 padres de eventos y 36 normales; el detector no recibe etiquetas de eventos.
- El verificador del sello CAL comprueba escenario, calendario, manifiesto, metadata y archivos de observación por hash antes de inferencia.
- Nuevo sello de los seis outputs DEV: COMPLETE, audit, events y prediction. Los sellos previos no se sobrescribieron.
- Gates de desarrollo y prefijo causal, comprobaciones matemáticas y smoke legado aprobados. Ambos pilotos de 3.601 reportes ejercitaron seis OFF públicos y seis fusiones.
- Nueve pruebas de infraestructura aprobadas; una prueba independiente adicional verifica score, agregación y contraste con un padre no disponible. El algoritmo estadístico no se modificó.
- Espacio mínimo de 16 GiB verificado antes de lanzar padres, bancos y umbrales; máximo cuatro padres activos. Un fallo impide seguir encolando padres. Las tareas activas conservan sus salidas auditables.
- C03: sus 16 hashes de referencia coinciden. F01 y RAW0002 no se modifican.

## Continuación automática y límites

El supervisor ejecuta CAL, exige umbrales factibles y congela la selección antes de generar e inferir TEST en F01 y P2. La evaluación espera los sellos de predicciones de ambas plantas. Ante un fallo se detiene; no modifica el método para eludirlo.

La ejecución necesita que el equipo permanezca encendido y puede tardar varios días. La integración del artículo requiere una auditoría posterior de resultados: no ocurre automáticamente por terminar un proceso. La procedencia y el estado vivo están en `experiments/PAPER_RECOVERY_C04/run` del repositorio científico.
