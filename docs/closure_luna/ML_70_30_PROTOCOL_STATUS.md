# Estado del protocolo ML 70/30

Auditoría documental acotada de los artefactos congelados; no se entrenó,
reevaluó ni retocó ningún modelo. “90/30” se interpreta aquí según la
aclaración del autor: el estudio retrospectivo agrupado de ExtraTrees, no
90% ni la frecuencia de 30 reportes/s.

| Aspecto | Estado y evidencia | Qué falta / límite |
|---|---|---|
| Unidad y partición | `generated/frozen/submission_s01_learning_20261031/split.json` y el `ML_PLAN.json` fuente definen componentes conectados globales por trayectoria física: 56 grupos repartidos 31/8/17, es decir 90/16/70 registros. La proporción de grupos solicitada fue 56% fit + 14% validación interna + 30% holdout de desarrollo. El orden se deriva por SHA256 con semilla identificada `P07_S01_GROUPED_DEVELOPMENT_20261031_v1`. | Es retrospectivo: campañas SIM ya abiertas, mismo linaje F01 y fuentes conocidas. No es test ciego ni validación externa o por fuente excluida. |
| Fit e hiperparámetros | `experiments/PAPER_SUBMISSION_S01/protocol/ML_PLAN.json` en el repositorio SCIENCE: fit solo en `train_56`; 400 árboles, `min_samples_leaf=2`, `max_features=sqrt`, `class_weight=balanced`, `random_state=2601026`; ajuste con cada tercer reporte desde índice 360. No hay búsqueda de hiperparámetros ni refit train+validación. | La comparación respalda únicamente las variantes congeladas y esta cohorte; no estima superioridad general de ML. |
| Señales, features y escala | 47 canales de las ocho PMU; referencia empírica de 300 reportes y centro/MAD de reportes 30–299 por registro; primera monitorización en k=360. BASELINE tiene 846 features trailing y SHORT 1457 (adición de 611). La escala de señales usa el prefijo de cada registro; no consta un scaler global ajustado con el holdout. | El prefijo empírico no tiene garantía de estacionariedad inicial. El documento técnico no informa una auditoría de fuga de estadísticas del prefijo a través de ventanas; la unidad agrupada evita cruces de trayectorias, no este límite de dominio. |
| Selección y umbral | La validación interna elige SHORT por joint-before-OFF (108/192 frente a 92/192), con extras como desempate. El publicador congelado exige seis reportes consecutivos con argmax estable; no usa umbral de confianza ni probabilidad calibrada. La validación contiene 0 grupos normales y 0 s de exposición normal. | La validación no calibra ni valida una tasa de falsas alarmas normales. No se informa retroalimentación del 30% al seleccionar o modificar el modelo; `model_freeze.json` declara `holdout_observations_read: false` y `refit: false`. |
| Holdout del 30% | SHORT quedó congelado antes de abrirlo. La evaluación reservada reportada es 302/576 diagnósticos oportunos (carga 28/288, línea 274/288) y 3 alarmas extra; es evidencia descriptiva de desarrollo retrospectivo, no una confirmación independiente. | Su único grupo normal no es exposición operativa independiente suficiente. No convertir el resultado en promesa para RAW o campo. |
| Modelo que entra en C01 | C01 congela dos ExtraTrees previos del linaje R09: `ET_REFERENCE`/BASELINE SHA256 `8be07d…b65f` y `ET_CANDIDATE`/SHORT SHA256 `e4afa2…d00c`, enumerados en `experiments/PAPER_CONFIRMATORY_C01/references/R11_FREEZE.json` y reflejados en predicciones selladas. El SHORT del estudio agrupado S01 es SHA256 `9b8397…78efcb`, en `submission_s01_learning_20261031/model_freeze.json`. Los hashes no coinciden. | El estudio agrupado S01 no valida los modelos de C01. C01 sí conserva los dos modelos R09 fijados antes de su ejecución; sus resultados aplican a esos hashes y a su contrato congelado. |
| Antecedente de hackathon | La entrega original es un clasificador jerárquico por ventanas de 30 s; la comparación R07 sobre SIM es retrospectiva y usa 6 padres de evento y 2 normales (`R07_HACKATHON_COMPARISON_20261027/PROTOCOL.json`). Los documentos de revisión advierten sobre validación histórica con grupos normales compartidos. | No describir la validación histórica como split agrupado limpio. La auditoría de este cierre no reconstruyó su partición original completa; su alcance no se transfiere al S01 56/14/30 ni a C01. |
| RAW0001 | Es una reproducción retrospectiva sobre un registro ya usado en desarrollo/calibración, con fallos de transferencia documentados. | No es un test externo limpio; no usarlo para afirmar generalización fuera de distribución. |

## Fuentes revisadas

- P07: `generated/frozen/submission_s01_learning_20261031/split.json`,
  `model_freeze.json`, `validation_events.csv`; `supplement/appendix_grouped_learning.tex`,
  `docs/claims-and-evidence.md`.
- SCIENCE: `experiments/PAPER_SUBMISSION_S01/protocol/ML_PLAN.json`,
  `experiments/PAPER_SUBMISSION_S01/ml/RESULTS.md`,
  `experiments/PAPER_CONFIRMATORY_C01/protocol/PLAN.json`,
  `experiments/PAPER_CONFIRMATORY_C01/references/R11_FREEZE.json`,
  `experiments/PAPER_CONFIRMATORY_C01/run/COMPLETE.json`.
- El artículo vigente y la auditoría estricta describen C01 como confirmación
  de sus procedimientos congelados; no cambian la procedencia de estos dos
  ExtraTrees ni elevan S01 a validación de C01.
