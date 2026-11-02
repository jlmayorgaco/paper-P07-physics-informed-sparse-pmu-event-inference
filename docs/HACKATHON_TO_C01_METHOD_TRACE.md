# De la entrega de la hackathon al experimento causal de P07

## Tres contratos que no se deben mezclar

| Ruta | Artefacto verificable | Decisión y datos | Resultado verificable |
|---|---|---|---|
| Entrega original | `SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/` | ExtraTrees jerárquico en ventanas de 30 s; nueve códigos de evento; detector, clasificador y localizadores por tipo | `models/final_metrics.json`: en validación SIM interna, exactitud del detector 0.9693, macro-F1 del clasificador 0.9598 y localización exacta 0.8524. No son métricas causales de episodios ni puntuación oficial externa. |
| Comparador causal de P07 | `experiments/E5_VALIDATION_PAPER/M03_R09_NUISANCE_DEV/ml/` | ExtraTrees nuevo sobre 47 coordenadas PMU, 30 reportes/s, 846 features retrospectivas; variante corta 1.457; 400 árboles y seis tramas de confirmación | `generated/frozen/c01_20261029`: referencia 330/648 atribuciones oportunas y 29 alarmas extra; corta 352/648 y 16 extras. |
| Banco físico de P07 | `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/` | Predictores DAE con topología y terminales PMU, estado inicial estimado, historias de evento y recuperación, evidencia de severidad y cinco hipótesis R/X | Mismo C01: 644/648 atribuciones oportunas y 72 extras; 68 extras con R/X fuera del banco. |

## Procedencia de las features

La entrega original está documentada en `submitted/MODEL.md` y ejecuta `submitted/src/models/hybrid_submission.py`. `feature_extractor_v2.py` calcula magnitud y ángulo de V/I, frecuencia, ROCOF, calidad de dato, dispersión de fases, proxies P/Q y estadísticos por segmentos. `dynamic_feature_extractor_v3.py` añade cambios multiescala, innovaciones de nivel RLS/Kalman y relaciones temporales entre PMU. El archivo seleccionado registra 45.162 features en `models/final_metrics.json`; `models/feature_columns.json` enumera la base seleccionada y los bloques dinámicos se agregan aparte. Las columnas de etiqueta no figuran en esa lista seleccionada. Esta comprobación de nombres no equivale a una auditoría completa de fuga de información en toda la preparación histórica.

El comparador de C01 **no carga los árboles de la entrega**. `ml/causal_features.py` define seis estadísticas pasadas en ventanas de 30, 150 y 300 reportes para cada una de 47 coordenadas, dando 846 features. `ml/run.py` agrega 611 features de 3, 8 y 15 reportes en la variante corta. Su entrenamiento usa padres simulados anteriores; `ml/infer.py` carga modelos congelados y un adaptador causal. La puntuación del árbol no es una probabilidad calibrada. El código de C01 invoca exactamente esos ejecutables en `experiments/PAPER_CONFIRMATORY_C01/execution/worker.py`.

## Qué permite afirmar C01

En el catálogo de nueve cargas y nueve líneas, la ganancia principal del banco físico es la atribución oportuna de cargas: 322/324 frente a 15/324 de ExtraTrees de referencia y 30/324 de la variante corta. Las líneas ya son fuertes para todos: 322/324 físico, 315/324 referencia y 322/324 corta. La física paga 72 alarmas extra, frente a 29 y 16. La comparación usa las mismas observaciones y el mismo evaluador, pero cada método conserva su umbral y regla de publicación. No prueba superioridad a igual tasa de falsas alarmas ni que ExtraTrees en general sea incapaz de aprender las cargas.

El aporte defendible es una inferencia causal de fuentes físicas que deja competir nuevas intervenciones con trayectorias de recuperación mediante predicciones del modelo eléctrico. La ventaja empírica es del **procedimiento completo**. El efecto aislado de la memoria, de la mezcla R/X y de cada regla de publicación no está identificado por C01. La entrega original sigue siendo valiosa como sistema amplio de features y diagnóstico de nueve clases, pero sus métricas históricas no se restan de las de C01.

## Restricciones del manuscrito

El artículo principal solo valida carga y línea en este simulador IEEE-39 con ocho PMU. RAW0001 fue evidencia retrospectiva del simulador, no examen independiente. No se ha demostrado rendimiento de campo, todas las clases de la hackathon, calibración probabilística ni operación en tiempo real. El mapa provisional de corriente BUS5 y la exclusión del ángulo de corriente BUS39 siguen declarados.
