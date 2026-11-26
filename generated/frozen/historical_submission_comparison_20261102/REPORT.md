# M02 V3.1 frente al paquete entregado: comparación ejecutada

**Respuesta: M02 mejora en esta prueba de carga y línea.** Se ejecutaron ambos sobre las mismas observaciones. No se comparó el 96/96 con porcentajes de otra campaña.

## 1. Resultado con las métricas usadas en la entrega

124 ventanas compartidas: 96 con evento y 28 normales. E0 = normal, E2 = línea, E4 = carga. Las predicciones de otras familias permanecen como errores. Top-1/Top-3 se evalúan sobre todos los eventos, incluidos los omitidos; no se ocultan fallos condicionando al clasificador correcto.

| Métrica | ZIP entregado: ExtraTrees | M02 V3.1 | Cambio |
|---|---:|---:|---:|
| Detección: accuracy | 48.39 % | 100.00 % | +51.61 pp |
| Detección: precisión | 100.00 % | 100.00 % | +0.00 pp |
| Detección: recall | 33.33 % | 100.00 % | +66.67 pp |
| Detección: F1 | 50.00 % | 100.00 % | +50.00 pp |
| Clasificación E0/E2/E4: accuracy | 41.13 % | 100.00 % | +58.87 pp |
| Clasificación: F1 ponderado | 39.75 % | 100.00 % | +60.25 pp |
| Clasificación: macro-F1 E0/E2/E4 | 40.71 % | 100.00 % | +59.29 pp |
| Localización Top-1 (todos los eventos) | 0.00 % | 100.00 % | +100.00 pp |
| Localización Top-3 (todos los eventos) | 13.54 % | 100.00 % | +86.46 pp |
| Familia + ubicación Top-1 | 0.00 % | 100.00 % | +100.00 pp |
| Familia + ubicación Top-3 | 9.38 % | 100.00 % | +90.62 pp |

- Eventos detectados: **32/96 → 96/96**.
- Familias físicas correctas: **23/96 → 96/96**.
- Familia y origen exactos: **0/96 → 96/96**.
- Falsas alarmas: **0/28 → 0/28 ventanas normales**; a nivel de registro, **0/16 → 0/16**.
- Exposición normal total: 840 s, con semillas repetidas; es insuficiente para certificar una tasa operativa de falsas alarmas.
- Predicciones fuera de E0/E2/E4 del paquete entregado: 9. Se contaron como clasificación incorrecta, aunque en detección binaria cuentan como alarma.

## 2. Qué pasó en cada familia

Una decisión por registro completo (112 registros), conservando el primer resultado no normal del entregado y la causa final de M02 cuando hubo alarma:

| Familia | Registros | Familia correcta: entregado | Familia correcta: M02 | Familia+origen: entregado | Familia+origen: M02 |
|---|---:|---:|---:|---:|---:|
| Carga E4 | 48 | 7/48 | 48/48 | 0 | 48 |
| Línea E2 | 48 | 16/48 | 48/48 | 0 | 48 |
| Normal E0 | 16 | 16/16 | 16/16 | — | — |

En la comparación emparejada hay **96 recuperaciones y 0 regresiones** de familia+origen Top-1; para Top-3, 87 recuperaciones y 0 regresiones. Para clasificación, 73 recuperaciones y 0 regresiones.

Se comprobó el resultado llamativo de 0/96 ubicaciones Top-1 del entregado contra sus CSV efectivos. No es una conversión incorrecta de nombres: por ejemplo, los casos de LINE23-24 se atribuyen a LINE22-35. En 18 ventanas, el primer candidato del Top-3 auxiliar no coincide con `Predicted_Location`; en 4 ni siquiera contiene esa salida. Se conserva este comportamiento del paquete original: Top-1 usa el CSV oficial y Top-3 la lista auxiliar exportada, sin corregir ni reordenar el modelo después de ver resultados. `results/SUBMITTED_OUTPUT_AUDIT.csv` contiene cada caso.

## 3. Tiempo y causalidad

- M02: 96/96 alarmas dentro del evento, 0 prematuras; demora mediana **0.0667 s**. El diagnóstico causal se lee 0,5 s después de la alarma, con demora mediana **0.5667 s** y 96/96 familia+origen correctos.
- Entregado: decide al terminar una ventana de hasta 30 s; en estos registros de eventos, la ventana parcial termina a 20 s. Entre los 32 eventos que detectó, el tiempo hasta esa decisión tiene mediana **11.9000 s** desde el inicio físico; los 64 omitidos no tienen alarma y no entran en esa mediana. Es disponibilidad de la decisión, no una demora de detector causal validada.
- La tabla principal permite a ambos usar el registro hasta el mismo final de ventana. Las etiquetas retrospectivas del entregado, copiadas hacia atrás a todas las filas, no se contabilizan como alarmas anticipadas.

## 4. Qué prueba y qué no prueba

La mejora observada demuestra una ventaja del candidato físico **en el banco SIM0001 actual de carga/línea**. El programa entregado se transfiere a este banco sin reentrenamiento; M02 conoce el modelo de la planta y su catálogo de 12 orígenes (6 buses de carga y 6 líneas). El entregado conserva su catálogo original más amplio. La comparación mide esos sistemas tal como están, con información previa y dominios de desarrollo distintos.

Son 36 trayectorias físicas con eventos y 6 normales, repetidas con semillas: **96 realizaciones con evento no son 96 escenarios físicos independientes**. Las particiones llamadas development/validation son ahora regresiones conocidas de M02. No se presenta esta campaña como prueba final independiente.

**No es un nuevo puntaje oficial de la hackatón ni demuestra superioridad en RAW0001 o en E0–E8 completos.** No se abrieron datos RAW en esta comparación. M02 aún no cubre falla, generación e integridad; sus intervalos de incertidumbre siguen sin calibración validada. Los resultados históricos de la entrega sobre RAW0001 pertenecen a otra campaña y no entran en estas diferencias.

Para el artículo IEEE Access, ya hay una comparación ejecutada y reproducible con el sistema entregado. La afirmación respaldada es la mejora en este banco y alcance. Una afirmación de superioridad general requiere una evaluación independiente, con el mismo catálogo y condiciones, y las familias que se incluyan en dicha afirmación. Este resultado por sí solo no prueba novedad ni preparación para publicación.

## 5. Integridad y reproducción

- ZIP realmente ejecutado: `sgsma_2026_final_submission.zip`, SHA-256 `e0bfc17e4c5ee9b595fa51fd94d736145c2f48755696c8d2eadcff00cb23a243`. Código extraído intacto, ruta `ml_windowed`, ventana por defecto 30 s; ningún fallback físico.
- M02: 112 replays nuevos; todos idénticos al archivo cerrado salvo tiempos de cómputo. No se volvió a simular la planta ni se reiniciaron estados dentro de una trayectoria.
- Exportador original F01: 14 canales por PMU, ocho PMU, V/A/deg/Hz/Hz/s, fases equilibradas, máscaras de arranque conservadas. No se recalculó el ruido.
- Características disponibles en la prueba de contrato R001: 39716/39716 para clasificación y 45162/45162 para localización. El CLI original y el lanzador dieron exactamente las mismas predicciones en R001.
- 5159 archivos protegidos de campañas previas comprobados; 0 cambios. Código de métricas y protocolo sellados antes de ejecutar; predicciones selladas antes de abrir la verdad reservada.
- Sin reentrenar, reajustar umbrales, modificar baselines, abrir RAW0002 ni hacer push.

Archivos: `results/SUMMARY.csv`, `results/PAIRED.csv`, `results/BY_SOURCE.csv`, matrices de confusión, `PROTOCOL.json`, `EXECUTION_SEAL.json`, `PREDICTIONS_SEAL.json`, `CHECKS.json`, `AUDIT.json`.

Para reproducir en una carpeta sucesora vacía: copiar los scripts de esta carpeta y seguir `RUNBOOK.md`. Mantener el mismo Python y las referencias a los candidatos archivados. No ejecutar preparación otra vez dentro de esta carpeta cerrada.
