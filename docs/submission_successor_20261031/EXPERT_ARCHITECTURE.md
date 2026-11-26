# Arquitectura científica y procedencia cyber de P07 — 31 de octubre de 2026

Auditoría experta independiente bajo `ieee-access-academic-quality`. Esta ronda no consultó informes de otros revisores, resultados parciales o verdad de C01, ni RAW0002. Se inspeccionaron fuentes, configuraciones, documentos del artefacto entregado y su historial Git. No se ejecutaron datasets, modelos, entrenamiento ni simulaciones. No se modificó ningún TEX, modelo o baseline. Las recomendaciones siguientes distinguen mecanismos disponibles de resultados que aún deben medirse.

## Contrato científico en cinco frases

1. **Problema:** una intervención física, su recuperación y una degradación de PMU pueden coexistir; tratarlas como una sola etiqueta puede producir falsas nuevas intervenciones o perder su fuente.
2. **Brecha:** todavía falta demostrar que el banco de historias de P07 aporta una mejora operacional sobre un predictor físico sencillo que conserva estado, y que la integración de calidad PMU ayuda bajo el mismo contrato de observación y decisión.
3. **Idea:** mantener el estado físico durante la recuperación y representar la integridad de las observaciones como un eje distinto, con composición explícita al exportar las etiquetas de competición.
4. **Prueba que puede refutarla:** un predictor causal sencillo con idéntico catálogo, integridad, canales y publicación iguala al banco, o el componente cyber elimina eventos físicos reales sin compensarlo con menos errores de integridad.
5. **Consecuencia:** solo una mejora medida, con su coste y sus regresiones visibles, justifica la complejidad adicional; superar el artefacto del hackathon en RAW0001 es un objetivo cuantitativo de validación retrospectiva, nunca una promesa ni una evaluación independiente.

La instrucción actual incluye cyber. Esto actualiza el alcance estrecho del manuscrito; no obliga a añadir una nueva teoría de ataques, una red neuronal o el estimador conjunto histórico propuesto. La habilidad conserva su principio útil de una sola tesis y separación de tareas, pero su blueprint antiguo de learned discrepancy no es evidencia ni obligación de implementarlo en este sucesor.

## 1. Artefacto exacto que debe servir de referencia

El archivo [sgsma_2026_final_submission.zip](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/sgsma_2026_final_submission.zip) tiene SHA256:

`e0bfc17e4c5ee9b595fa51fd94d736145c2f48755696c8d2eadcff00cb23a243`

Se comprobó igualdad byte a byte mediante SHA256 de **14 miembros relevantes**, incluidos los cuatro `.joblib`, frente al runtime ya extraído en [submitted](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted). No se deserializaron los modelos. El resultado exacto está en [ZIP_RUNTIME_PARITY.json](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/legacy_reference/ZIP_RUNTIME_PARITY.json).

La ruta activa es:

```text
main.py
  -> src/models/hybrid_submission.py:run_hybrid_submission_prediction
  -> _run_ml_windows                         [30 s, sin solapamiento]
  -> _build_feature_rows
       -> extract_window_features_v2          [base]
       -> extract_dynamic_features_from_frames[rolling, rls_kalman, graph_temporal]
  -> SGSMAFinalModel.predict_from_features
       -> PhysicsRuleEngine                   [familia + integridad]
       -> typed ExtraTrees localizers         [Top-1 activo]
  -> TIMESTAMP, Bus, Predicted_Event, Predicted_Location
```

El fallback `run_bus_agnostic_prediction` se activa **solo si falta** `final_model_config.json`. No es la ruta que genera las predicciones normales del ZIP con sus modelos presentes: [selector de ruta, líneas 229–260](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/models/hybrid_submission.py:229).

### Módulos y payloads

| Elemento | Función verificable | Alcance/restricción |
|---|---|---|
| `physical_event_classifier.joblib` | Pipeline de imputación mediana y ExtraTrees; predictor de evento físico | El código de entrenamiento usa etiquetas físicas 0,1,2,3,4,8, no una salida cyber autónoma |
| `bad_data_detector.joblib` | Clasificador binario de E7 entrenado en filas sin missing | Se aplica con `bad_score >= 0.4211785821118759`; no es una probabilidad calibrada de ataque |
| `missing_composition_detector.joblib` | Binario E6 frente a otras filas con missing | El umbral archivado es **0.0**, y la confianza física mínima también **0.0**; importa la regla efectiva de abajo |
| `hierarchical_model_config.json` | Umbrales aprendidos y documentación de reglas | Los parámetros de gates físicos están duplicados como constantes en el código; modificar únicamente ese bloque JSON no reconfigura las constantes usadas |
| `feature_columns.json` | Orden de las entradas base de clasificador y detectores | Contiene **39 716** nombres; comprobación estática: ninguno contiene `label_`, `Event`, `Location` o `true_` |
| `final_dynamic_localizers.joblib` | Localizadores tipados BUS/LINE/PMU y por familia | Usa base más características dinámicas; el documento del ZIP declara 45 162 entradas para la variante completa |
| `final_model_config.json` | Variante y selección de localización | `use_hybrid_top1=false`: Top-1 usa `_predict_locations`; Top-3 sigue `HybridLocalizer.predict_topk`, por lo que no son automáticamente el mismo ranking |

La carga de payloads y las rutas Top-1/Top-3 están en [final_model.py, líneas 30–119](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/final_model.py:30). El entrenamiento documenta 750 árboles físicos y 650 en cada detector cyber, con split 70/30 estratificado por fila y calibración interna de 25% del training: [training V2, líneas 446–492](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/train_hierarchical_pipeline_v2.py:446). Es procedencia del código; no se vuelve a certificar aquí la composición de cada payload mediante deserialización.

Este ZIP no debe confundirse con los dos comparadores causales posteriores entrenados en SIM0014–SIM0017 y validados en SIM0018. Esos son referencias distintas, con 47 señales y otro extractor. Preservar identificadores y hashes separados.

## 2. Ontología exacta y reglas efectivas

| Etiqueta | Significado en el ZIP | Ubicación exportada |
|---|---|---|
| 0 | Normal | `none` |
| 1 | Fault | BUS, salvo error del clasificador/localizador |
| 2 | Line outage | LINE |
| 3 | Generation change/outage | BUS |
| 4 | Load change/drop | BUS |
| 5 | Missing data sin componente físico admitido | PMU |
| 6 | Missing data + evento físico | **Fuente física** BUS/LINE; no identifica simultáneamente la PMU ausente |
| 7 | Bad data | PMU |
| 8 | `mixed_proxy` en la configuración y familia física conocida `event8` en entrenamiento | Enruta como física; no equivale a rechazo open-set |

Fuentes: [configuración final, líneas 17–27](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/models/final_model_config.json:17), [etiquetado de entrenamiento, líneas 25–62](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/train_hierarchical_pipeline.py:25) y [routing de localización, líneas 370–394](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/train_hierarchical_pipeline_v2.py:370).

El algoritmo primero predice la familia física y su confianza, calcula missing, bad-data score y gates físicos; aplica correcciones de línea/falla, luego E7 y al final composición E5/E6. La última regla sobrescribe las anteriores en filas con missing. Missing se detecta si alguna fracción válida early/mid/late es menor que 0.999, una fracción NaN supera 0.20 o una razón de hueco temporal supera 1.5: [líneas 118–150](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/train_hierarchical_pipeline_v2.py:118).

Con los umbrales congelados 0.0/0.0, y para probabilidades finitas normales, E6 se reduce efectivamente a **missing y `physical_pred != 0`**. La documentación «strong physical/composition evidence» no describe la fuerza real de este gate particular. No retocarlo en el brazo histórico; cualquier revisión es un sucesor. Además, la regla utiliza `physical_pred`, no necesariamente el `pred` corregido por los gates. Véase [PhysicsRuleEngine, líneas 247–329](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/train_hierarchical_pipeline_v2.py:247).

La salida científica del sucesor debería conservar ejes separados: `physical_family`, `physical_source`, `integrity_state`, `affected_pmus`, `emission_time` y `last_report_used`. Un adaptador posterior genera el código 0–8 cuando corresponda. E6 no debe destruir la localización de la PMU ausente en la salida detallada. E8 necesita dos campos diferentes: la clase histórica `mixed_proxy` y la abstención/unresolved del nuevo método. Ningún mapping debe presentarlas como equivalentes.

## 3. Causalidad y fuga: lo que está comprobado y lo que no

**El ZIP puntúa ventanas completas.** `_run_ml_windows` calcula una predicción al disponer del segmento completo y la replica en todas sus filas. El extractor tiene medias centradas, interpolación bidireccional y estadísticas de toda la ventana. Es válido como clasificador al final de cada ventana; no demuestra decisiones disponibles en los timestamps anteriores que aparecen en el CSV. El adaptador causal debe emitir en el fin de ventana y conservar el intervalo observado. Cambiar a ventanas más cortas cambia el método y requiere un identificador distinto. Véanse [runtime, líneas 148–190](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/models/hybrid_submission.py:148), [V2, línea 101](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/feature_extractor_v2.py:101) y [dinámicas, líneas 175–176](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/dynamic_feature_extractor_v3.py:175).

**`Event` sí se lee dentro del extractor base, pero no se encontró como input del modelo congelado.** V2 produce `label_event_mode` y `label_abnormal` a partir de esa columna; el entrenamiento excluye sus nombres y la lista congelada de 39 716 inputs no los contiene. `SGSMAFinalModel` reindexa la matriz a esa lista. Esto no autoriza afirmar fuga predictiva demostrada del ZIP. Sí exige una frontera más limpia en el sucesor: eliminar `Event`, `Location` y toda metadata de verdad antes de llamar al extractor, y comprobar paridad de predicciones contra entradas idénticas con etiquetas eliminadas/alteradas. No basta con una búsqueda de nombres: una columna desconocida numérica puede alterar agregados genéricos, y `Location` no está en `META_COLUMNS`. Fuentes: [V2, líneas 338–386](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/feature_extractor_v2.py:338), [filtro de features, líneas 103–115](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E4_OTHER_FAMILIES/M02_V31_VS_HACKATHON_C01/submitted/src/data_factory/train_hierarchical_pipeline_v2.py:103).

**El pipeline histórico cyber alternativo no es una inferencia ciega.** [pipeline_raw_cyber_quality.py](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/pipelines/pipeline_raw_cyber_quality.py:60) invoca `Event7Estimator`, cuyo `_baseline_mask` usa `frame['Event']==0` y estadísticas del registro completo: [estimator_event_7.py, líneas 45–104](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/src/estimators/estimator_event_7.py:45). Es una herramienta histórica de análisis/calibración, no el componente E7 activo del ZIP. Reutilizarla sin cambiar esta dependencia invalidaría una nueva afirmación causal y ciega. `Event5Estimator` usa NaN/DATA_PRESENT directamente, pero pertenece también a esa ruta distinta.

**PMU ausente no es lo mismo que muestras ausentes.** El runtime descubre buses presentes y construye características sobre ellos. No hay que dar por probada detección de un archivo PMU desaparecido por completo: se necesita un inventario esperado independiente de lo observado. R11 además usa 47 coordenadas, mientras el ZIP espera señales trifásicas y calidad. Duplicar una fase o fabricar `DATA_PRESENT=1` cambiaría el problema de integridad. Registrar explícitamente el mapa de canales y qué información existe en cada población.

## 4. Los 21 contextos RAW0001: origen preciso y frontera de comparación

Se recuperaron, sin ejecutarlas, dos fuentes históricas y el CSV de timeline del commit `01178d6dbd92d5e98e80742ec02ff61f67473c8c`:

- [evaluate_raw0001_v2.py](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/legacy_reference/evaluate_raw0001_v2.py:67).
- [raw_timeline.py](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/legacy_reference/raw_timeline.py:18).
- [raw0001_event_timeline.csv](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/legacy_reference/raw0001_event_timeline.csv).

[SOURCE_PROVENANCE.json](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/legacy_reference/SOURCE_PROVENANCE.json) registra commit, ruta Git, blob y SHA256 de cada copia. [historical_contexts.json](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/PAPER_SUBMISSION_S01/evaluation/historical_contexts.json) contiene las 21 ventanas con nombre, inicio, fin, familia y ubicación; es **verdad de evaluación** y no puede entrar a inferencia.

El cargador `build_raw_context_features` lee el timeline. `_window_bounds` comienza cada caso anómalo **tres segundos antes de su inicio verdadero**, toma 30 s, selecciona un contexto de 30 s para cada control normal y descarta controles demasiado cortos. Los extremos del filtro son inclusivos. Los nombres y etiquetas de las 21 filas se comprobaron contra el CSV histórico de predicciones: nueve normales y doce anómalos. El rango total requerido por estos contextos es 537–5160 s; debe comprobarse contra la grabación limpia antes de ejecutar para preservar el clipping original.

Esto es **clasificación retrospectiva con contexto elegido por verdad**, no detección libre en toda RAW0001. No es equivalente a las ventanas no solapadas de 30 s que genera el `main.py` del ZIP. La coincidencia del nombre de modelo no une esos contratos.

La cadena histórica adicional se verificó en Git:

```text
pipelines/p5_train_localizer.py @ 01178d6db
  -> train_dynamic_localizer_fusion_v3.run_fusion
  -> _ensure_raw_v2_features
  -> build_raw_context_features + dynamic RAW table

pipelines/p7_evaluate_raw_current.py @ 618e50bbbf5fbb3f96a96ce9a950844097fc9278
  -> por defecto vuelve a reportar raw001_final_predictions.csv congelado
  -> solo recalcula features/inferencia si include_drift_check=True
```

`train_dynamic_localizer_fusion_v3.py` en `83758ca359cbef33a19d0c2d8d0ac5156b0fe419` utiliza el resultado RAW también en la selección/recomendación de variante. La configuración final declara selección por localización RAW. RAW0001 ya era referencia de desarrollo del artefacto histórico y de F01; ninguna mejora nueva allí debe llamarse generalización externa.

El CSV congelado registra 21/21 etiquetas correctas y 8/12 ubicaciones anómalas correctas. Estos conteos solo describen ese archivo; no son un replay ejecutado en esta auditoría. No se puede mejorar sobre 100% de clasificación en ese denominador. La meta honesta en ese carril es mejorar ubicación sin regresión de familia; la meta continua debe medirse de nuevo, con alarmas, retrasos y exposición normal, sin transferirle los conteos del carril oracle.

## 5. Arquitectura del sucesor implementable sin alterar referencias

**Brazo histórico:** payloads y código del ZIP preservados; observaciones limpiadas por un adaptador explícito, ventanas y publicación registradas. La paridad de limpieza es un gate, no una excusa para modificar modelos congelados.

**Brazo físico:** R11 original permanece referencia. El sucesor conserva estados y dispone de un selector de canales válidos. En muestras perdidas, propaga sin asimilar valores fabricados y utiliza submatrices consistentes de la covarianza/operador cuando sea posible. Esto cambia el filtro si R11 no lo soporta y necesita identidad nueva.

**Integridad:** separar la máscara disponible inmediatamente —timestamp, presencia y NaN— de la decisión aprendida E7 que solo llega al final de una ventana. Un diagnóstico tardío no puede proteger retroactivamente la actualización anterior sin declarar replay/suavizado y su tiempo de emisión. Mantener las decisiones de ambos ejes y su procedencia; no sobrescribir silenciosamente la física porque una clase cyber ganó.

**Familias fuera del catálogo físico:** el fallback histórico puede mantener cobertura E1/E3/E8, pero su salida es aprendida y no amplía por sí misma la validación de los operadores DAE de P07. El enrutamiento entre la salida física y la aprendida debe fijarse con observaciones y score disponibles, jamás con `true_event`, nombre de chunk o tabla de ubicaciones.

**Composición:** publicar E5/E6/E7 solo mediante una regla registrada. Conservar información más rica en el ledger interno; la etiqueta plana de competición es un formato de entrega, no la ontología científica completa.

**Discrepancia y ataques:** llamar a este componente «integridad/calidad PMU» salvo que una campaña especifique un atacante y valide ataques concretos. NaN o bad data no prueban una intrusión; una detección de outlier tampoco cubre ataques coordinados que respeten el modelo físico.

### Gates de evidencia antes de declarar submit-ready

| Gate | Comprobación concreta | Qué afirmación permite |
|---|---|---|
| G1 Procedencia | Hashes ZIP, fuentes, modelos, canales y comparador inequívocos | Comparación contra el artefacto entregado |
| G2 Frontera de verdad | Inputs sin Event/Location/timeline; perturbación/eliminación de etiquetas no cambia predicción; solo evaluador abre verdad | Inferencia ciega respecto a etiquetas |
| G3 Reloj | `emission_time >= last_report_used`; ventanas completas emitidas al final; futuras muestras no alteran emisiones anteriores | Causalidad del adaptador |
| G4 Mecanismo | Banco frente a predictor físico sencillo, mismos canales, integridad, catálogo y publicación | Utilidad atribuible al banco |
| G5 Cyber | Normal, physical-only, integrity-only y combinación; medir físico, PMU afectada y composición por separado | Beneficio de integrar integridad, sin ocultar regresiones |
| G6 RAW comparable | Carril histórico oracle separado del carril continuo; ambos métodos con el mismo contrato en cada carril | Mejora retrospectiva común y reproducible |
| G7 Evidencia independiente | Campaña de padres reservados y resultados completos sellados, con fallos en denominador | Generalización dentro del contrato simulado |
| G8 Integridad editorial | Claims generados desde resultados; ningún placeholder, resultado en curso o score inventado | Documento listo para revisión/envío |

G1 quedó comprobado para los 14 miembros de esta auditoría. Las copias históricas y el manifiesto de 21 contextos también quedaron preparados. G2–G8 no se declaran superados aquí. Que una meta no se alcance no justifica ocultar el resultado; cambia la conclusión científica.

## 6. Estructura compacta: artículo, suplemento y archivo

**Título provisional hasta ver los resultados:** *Recovery-Aware Physical Event Attribution With PMU Integrity Monitoring*. No fijar «robust», «improved» o «all-family» antes de cerrar gates. Si cyber funciona solo como fallback histórico, el título actual puede mantenerse y presentar integridad como extensión operacional evaluada.

### Artículo principal: una decisión de ingeniería, aproximadamente 15–18 páginas con referencias

| Sección | Pregunta y contenido | Presupuesto orientativo |
|---|---|---|
| Introducción | Por qué distinguir recuperación, nuevo evento e integridad; brecha frente a filtros/diagnóstico existentes; tres aportes máximo | 1–1.5 p |
| Relacionados | Trayectorias, múltiples hipótesis, detección de cambios y calidad PMU; contrastes exactos y comparadores ejecutados | 1–1.5 p |
| Problema/observación | Catálogo, terminales, integridad, ejes de salida, reloj, startup y datos reservados | 1.5–2 p |
| Método | Predicción física continua, evidencia, hipótesis, selector de canales y composición; especificar qué es histórico, aprendido y nuevo | 2.5–3 p |
| Diseño experimental | Contratos SIM, baseline sencillo, cyber factorial, oracle RAW y continuo RAW; unidades y selección | 1.5–2 p |
| Resultados | Primero efecto del mecanismo; luego integridad; luego transferencia retrospectiva y coste/fallos | 4–5 p |
| Límites/conclusión | Qué cambió de decisión y dónde falla; CT, F01, RAW conocido, calibration y tiempo de cómputo | 1–1.5 p |
| Referencias | Bibliografía primaria pertinente | Según composición final |

Conservar visibles las dos figuras protegidas. Figuras centrales adicionales: arquitectura con fronteras temporales; compromiso atribución/extras del contraste sencillo; ejemplo combinado de recuperación e integridad; comparación RAW con carriles separados. Tablas: contrato/mapping, métodos y presupuesto de selección, resultados pareados, fallos/coste. No convertir una galería de trazas o una lista de features en contribución.

**X02:** una fila o un panel compacto de severidad si sigue apoyando el argumento; detalles y trazas al suplemento. **X04:** conservar la evidencia negativa en discusión y el panel mínimo que impide presentar recuperación como información universalmente útil. **ΔM:** una ecuación y explicación; no necesita una subsección de novedad.

### Suplemento reproducible del método actual

Mantener el walkthrough causal actual, integral de amplitud y estado condicionado; todas las reglas de bank/publicación; tabla exacta de versión de cada componente; mapa PMU y unidades; máscara de integridad y composición; paridad del ZIP; código de métricas y clocks; manifiestos de campañas; resultados completos y casos negativos; limitaciones de X02/X04. La separación oracle/continuo debe aparecer también en los títulos de cada tabla suplementaria.

### Archivo histórico separado y enlazado

Mover fuera del recorrido obligatorio los estudios antiguos de reconstrucción, GLOBAL-137, cambio de prior, reconstrucción AC, teoría extensa de conos/contactos, `E_J` propuesto y piloto basado en dossiers. Conservar archivos y resultados, con un índice que indique que no son pruebas del sucesor. Este archivo no debe presentarse como la mitad necesaria del artículo para que el lector entienda el método nuevo.

No borrar las limitaciones ni los experimentos negativos al compactar. La evidencia incómoda que delimita la tesis pertenece al artículo o al suplemento vigente; la cronología de arquitecturas abandonadas pertenece al archivo.

## 7. Registro de afirmaciones recomendado

| Afirmación | Estado en esta auditoría | Evidencia necesaria para ascenderla |
|---|---|---|
| El ZIP incluye módulos para missing, composición y bad data | Verificado en código/config y hashes | Ninguna inferencia de rendimiento adicional |
| El ZIP continuo obtiene la métrica histórica de 21 contextos | No sustentado; contratos distintos | Replay continuo completo bajo contrato común |
| Los 21 contextos usan inicios conocidos | Verificado en fuente histórica preservada | Presentarlos como retrospectivos/oracle |
| El extractor introduce directamente Event al modelo congelado | No demostrado; lista base lo excluye | No acusarlo; aplicar frontera estricta y prueba de paridad |
| El pipeline `Event7Estimator` alternativo es ciego | Refutado por lectura explícita de Event en baseline | Sucesor causal sin esa dependencia |
| La combinación con cyber supera al ZIP | Objetivo empírico | Comparación común, completa y sellada, incluidas regresiones |
| La memoria mejora la atribución | Aún no aislado | Baseline físico sencillo y publicación común |
| La mejora RAW valida una nueva planta o generalización externa | No | RAW0001 sigue conocido; hace falta evidencia externa distinta |

La arquitectura propuesta permite avanzar sin atribuir resultados nuevos a R11 ni al ZIP. La salida submit-ready debe contar lo que la campaña efectivamente decida, incluido un empate o una regresión, y mantener visible la diferencia entre compatibilidad retrospectiva y confirmación independiente.
