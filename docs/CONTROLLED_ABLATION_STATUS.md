# Estudio controlado de puntuación y memoria

Autorizado el 2 de noviembre. Ejecución:
`../SGSMA26-Physics-Informed-AD/experiments/PAPER_ABLATION_A01/`.

Cuatro brazos, mismo banco de cinco modelos, mismos datos y publicación.
Se cambia únicamente (1) integral marginal versus incremento de likelihood
perfilada de amplitud; (2) transferencia versus eliminación de 114 estados
físicos estimados al cierre. La planta observada nunca se reinicia. El
estimador condicional, la memoria instrumental y los umbrales se conservan.

No es una ablación de toda la inferencia bayesiana ni de toda memoria
temporal. M es una representación de pesos, no una operación tensorial
necesaria. No se insertan los términos Qij del ensayo histórico en el filtro.

La selección fijada contiene 24 registros: 18 secuencias continuas,
tres controles normales y tres aperturas persistentes. Se reutilizan
registros ya conocidos; los intervalos por padre describen esta ablación
posterior y no una nueva confirmación independiente.

Consultar `run/PROGRESS.json`, `run/BLOCKER.json`, `run/COMPLETE.json` y
`run/PAPER_UPDATED.json` en la carpeta de ejecución. La copia de código debe
superar primero paridad de un registro completo contra C01. Los caches
reconstruidos deben coincidir con sus hashes originales.

El evaluador importa tablas y gráficas solo después de contabilizar las 96
salidas. Compila P07 y deja explícita la revisión visual pendiente. Hasta
entonces, las secciones nuevas muestran estado pendiente y no cifras de
efecto. No presentar este borrador como listo para envío.
