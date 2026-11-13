# Auditoría de progreso C03 — 2026-11-13

**Corte observado:** 13 de noviembre de 2026, hora Bogotá (UTC−05:00). Revisión de solo lectura del directorio `experiments/PAPER_RECOVERY_C03/run` del repositorio científico. No se abrieron truth, predicciones ni métricas parciales de TEST; no se ejecutó ni alteró C03.

## CAL y selección

Los registros de scoring CAL terminan el 13-nov a las 07:18:23; `CAL_SELECTION.json` y `METHOD_FREEZE.json` se escribieron a las 07:21:40–07:21:41. Tomo ese sello como cierre de la selección CAL y congelamiento del método. Los tres hashes de `METHOD_FREEZE.json` (detectability, execution y selection) coinciden con los SHA-256 recalculados de sus archivos. También coinciden los 29 hashes fuente enumerados en `EXECUTION_FREEZE.json`; no se encontraron discrepancias.

La selección CAL declara factibles las tres configuraciones evaluadas: `history`, `carry` y `reset`. Los umbrales congelados son 6.90675478 para `history`, 6.90675478 para `carry` y 5.29330482 para `reset`. La tabla de selección CAL reporta cero alarmas normales en 5.88 h para las tres; ello corresponde a la métrica de selección, no es una revisión de TEST. `SCENARIO_FREEZE.json` precede a CAL y registra el estado `FROZEN_BEFORE_OBSERVATIONS`.

## Sellos, P2 y ejecución

En el inventario de `run/` aparece `CAL_PREDICTIONS_SEAL.json`; también existen `OBSERVATIONS_F01_CAL.json` y `OBSERVATIONS_F01_TEST.json`. `METHOD_FREEZE.json` afirma que las observaciones TEST no se accedieron antes del freeze. No aparece un marcador separado de sello final F01, de sello P2 ni de bloqueo de evaluación (`eval lock`) en el inventario revisado. `PLANT2_VALIDATION.json` existe y declara `valid: true`, pero es un artefacto de validación de planta; no es un sello de evaluación P2.

El proceso señalado por `execution.lock` (PID 32480) seguía vivo en el corte (`python3.13`, iniciado 11-nov 17:19). `logs/campaign_stdout.log` termina con el avance `INFERENCE F01 TEST 7 72`; por tanto la ejecución seguía en curso y no hay base aquí para declarar cerrada la evaluación. La existencia de solicitudes y observaciones TEST confirma que esa fase comenzó, pero este informe no consulta sus resultados.

## Alcance

Se inspeccionaron únicamente los metadatos nombrados en la solicitud, inventarios, estado del proceso y registros de campaña/scoring para las marcas temporales. Se excluyeron `truth_private`, los contenidos de predicciones y los resultados parciales de TEST. Esta nota documenta progreso operativo y consistencia de hashes; no valida métricas científicas finales ni sustituye los sellos de evaluación.
