# P07: respuesta a la auditoría adversarial del 4-nov-2026

**Registro historico.** B01 y C02 ya cerraron. Ver el [cierre actual](../P07_CLOSURE_CURRENT.md).

Cada fila enlaza el hallazgo con el cambio realizado y su evidencia. "Abierto"
significa que el punto no se cerró en esta revisión y aparece declarado en el
artículo.

## Cambios de fondo

| Hallazgo | Estado | Cambio y evidencia |
|---|---|---|
| R1.1 Novedad débil, sin genealogía | **Cerrado** | Nueva sección V (teoría) y reposicionamiento como detección-aislamiento con modelos DAE conmutados. Se citan Willsky–Jones 1976, Friedland 1969, Shiryaev 1963, Nikiforov 1995, Lai 2000 y Tartakovsky et al. 2014. |
| R1.2 / R12 Reset "artificial" | **Cerrado con teoría** | Predicción 3 (ec. 24): el reset genera evidencia espuria ≥2.2·10³ nats (>10² λ*) tras los 108 eventos, y con carry exactamente 0. Se observa daño en 84/108 (líneas 51/54, cargas 33/54). Fig. 11, `scripts/theory_reset_cost.py`. Se declara honestamente que la teoría no predice qué evento individual de carga se daña (AUC 0.54). |
| R1.3 / R19 GLR de desarrollo no comparable | Parcial | Se explica la diferencia de cohorte (6 eventos en 80 s frente a 120 s). La ablación decisiva con información equiparada es **C02** (en cola detrás de B01). |
| R1.4 / R11 99.38 % condicionado | **Cerrado** | El abstract declara 18 padres, 108 intervenciones y 648 réplicas pareadas, y el catálogo de 18 fuentes. |
| R2.1 / R05 Pesos de red vs. nacimientos | **Cerrado (era incorrecto)** | El código marginaliza continuación, OFF y nacimientos de todas las celdas e intervalos en ambas fases, y asegura que el prior suma 1 (`static_rx.py:40-83`). Nueva ec. (16) y texto exacto. Se declara la única diferencia: las propuestas retrospectivas no re-ponderan w_ℓ. |
| R2.2 / R06 h con severidad | **Cerrado** | h=(e,c,τ,κ,𝓘), con a continua condicionada. |
| R2.3 Propuestas dependientes de datos | Declarado | Aparece en Limitaciones (Aproximación). La enumeración exacta sigue **abierta**. |
| R2.4 / R15 Validez de la linealización | Parcial | El estrés usa la planta no lineal. La comparación lineal vs. no lineal por fuente sigue **abierta**. |
| R2.5 / R13 Varianza descartada | Declarado | Se recoge en Limitaciones; el código registra la varianza descartada. |
| R2.6 / R07 Priors temporales | **Cerrado en texto** | Se declara la discrepancia (2–5 s frente a 30/60 s) y se acota su efecto con la ec. (22): log π_c ≈ −10.4 nats, frente a ≥4.6·10³ de información. El barrido de sensibilidad sigue abierto. |
| 4.1 / R04 ExtraTrees roto | **Cerrado** | Auditoría por reporte (`N01/et_diagnosis.py`, 12 cargas + 12 líneas): durante las cargas, el argmax del modelo base es "normal" en el 100 % de los reportes y la mediana de la puntuación máxima de la clase verdadera es 0.09; en líneas acierta el 96 % de los reportes (mediana 0.93). El fallo es de representación, antes de cualquier regla de publicación. Además se declara que ya fallaba en su validación de desarrollo. El reentrenado está en C02. |
| 4.2 / R03 Chen | **Cerrado en texto** | Se presenta como transferencia bajo desajuste de modelo; se usa "Chen *et al.*" en vez de "Chen2016". |
| 4.3 / R08 Validez externa | Parcial | El estrés de ruido (N01) cubre ruido ×5–×20 y ruido PMU independiente. El segundo simulador sigue **abierto**. |
| 4.4 Alarmas extra | **Cerrado** | 68/72 fuera del banco R/X (≈63/h de tiempo fuera de banco) y 0 alarmas en 11.8 h normales (cota del 95 % <0.26/h). |
| 4.5 / R02 Cómputo | **Cerrado** | Banco nominal medido en 6 registros (4×120 s y 2×600 s): mediana 26.4 ms/reporte, máximo 30.0 ms, por debajo de 33.3 ms, con 2 trabajos concurrentes más B01. El banco de 5 modelos (99.6 ms/reporte) se declara replay offline. |
| **Nuevo N01** Estrés de ruido | **Cerrado** | 4 registros CAL (12 cargas y 12 líneas) y 2 normales de 600 s, 6 escenarios, con el código sin cambios. Paridad exacta ×1 (18/18 mensajes). Con ×5/×10/×20: líneas 12/12; cargas 11, 11 y 12/12; 0 extras y 0 alarmas normales. Ruido independiente por PMU de 0.05 % / 0.1 % TVE: cargas 3/12 y 0/12, líneas 12/12 y 10/12. Un filtro adaptado (oráculo) muestra que sigue habiendo ≥543 nats (≥36× λ*) en 1 s: el límite es el modelo de ruido (escala escalar con correlación de modo común), no la física. Extensión necesaria: estimar la covarianza entre PMUs. |
| 5.1 / R16 BUS31 | **Cerrado** | Carga ZIP existente de 9.2 MW/4.6 Mvar; el slack solo existe en el flujo de carga. |
| **Nuevo B1** Ruido diferencial de ángulo | **Cerrado** | Ruido diferencial en RAW0001 de 10⁻⁴–10⁻² °. Se declara en el protocolo y se prueba con N01. Ruido PMU independiente de solo 0.05 % TVE = 48× la escala de ángulo del modelo. |
| R20 / R21 Vocabulario interno y tono defensivo | **Cerrado** | Se reescribieron intro, relacionados, resultados, discusión y conclusión. Se eliminaron "Sealed", "Chen2016", "H04" (también dentro de la Fig. 4), "frozen" y "archived" (salvo la frase de anclaje del pie protegido). |
| R23 Referencias | Parcial | Albustami → "In press, EPSR". Para Dey no se pudo verificar páginas/DOI de revista, así que se deja tal cual. |
| **Nuevo I1** Eventos cyber de la hackathon (faltantes, corruptos) | **Añadido** | Teoría: modelo de observación con disponibilidad y corrupción (ec. integrity-observation) y Proposición 1 de aislamiento de integridad (borrar el PMU = perfilar una corrupción arbitraria); relaciones de paridad de secuencias y de acoplamiento de red con $c_p$ calculado desde $Z=Y^{-1}$ (`scripts/integrity_coupling.py`; el modelo predice ratios 0.10–0.29 frente a 0.12–0.43 observados en la falla del bus 39). Sobre RAW0001, sin entrenamiento (`scripts/integrity_raw0001.py`): 4/4 caídas y 3/3 corrupciones etiquetadas, retardo 0, PMU correcto y fase correcta 3/3; 9200/9200 reportes faltantes. Se encuentran 6 incidentes no etiquetados (4 picos de corriente de un reporte, 1 trama previa a una caída y el colapso de tensión a cero en el PMU 29 a los 2776.9 s). Con el umbral prefijado hay 19 excedencias aisladas (0.21/min); con inflación de varianza ×2 (post hoc, declarado) quedan 2 transitorios de maniobra (0.022/min). |
| **Nuevo I2** Banco físico frente a cyber (simulación, código sin cambios) | **Añadido (resultado negativo declarado)** | `experiments/PAPER_INTEGRITY_N02/integrity.py`. 40 corrupciones (equivalente de secuencia positiva de las de RAW0001): ninguna alarma física y atribuciones intactas. Caída de 27 s rellenada con el último valor (imputación de la guía): el banco falla y no se recupera tras la reconexión. La Proposición 1/Predicción 4 indica que la información sigue disponible (≥42× λ* sin el peor PMU), así que la solución es un operador de observación conmutado por disponibilidad. Queda **abierto**. |
| **Nuevo I3** Métricas de la guía de la competencia | **Añadido** | Tabla `competition_metrics` (precisión, recall y F1 por reporte, FA/min, retardo, Top-1/Top-3, s por minuto de datos) sobre la evaluación independiente. |
| **Nuevo I4** El banco no arranca en RAW0001 | **Declarado** | Arranque rechazado (ROCOF constante o cuantizado en dos PMU, deriva de 0.31°/s en la referencia angular). En RAW0001 solo se evalúan las relaciones de integridad. |
| **Nuevo I5** Todos los tipos de evento; "hombre de paja" | **Añadido** | Sección `sec:allevents`: atribuidor de red sin entrenamiento. En RAW0001 (validación, 8 iteraciones registradas) obtiene 12/12 eventos con clase y Top-1 correctos, frente a 7/12 Top-1 del sistema enviado. Prueba sellada con una pasada: líneas 36/36 detectadas, pero solo 12/36 cargas; el banco dinámico obtiene 72/72. El sistema enviado se compara con su salida real, no con una versión debilitada. |
| **Nuevo I6** Página 20 | **Ajustado** | La tabla y la figura de estrés de ruido y la figura de trayectoria ilustrativa pasan al suplemento. El artículo queda en 20 páginas. |
| **Nuevo I7** Segunda revisión de ChatGPT (reducción de historias, segundo orden, marginalización) | **Ejecutado: resultado negativo, pasa a límites y suplemento** | Planta reducida de IEEE-39 en Python, 6 predictores, 8 celdas congeladas con hash, 200 escenarios cada una (`experiments/history_conditioning/`). Ningún predictor condicionado supera a la firma nominal recentrada (diferencias de 0 a 0,5 puntos, intervalos que contienen 0); la severidad previa se recupera a 0,3 puntos de la carga base. RAW0001 coloca BUS7 primero entre 16 cargas (99,5 % de la energía explicada) pero no discrimina métodos. Se añadió la subsección del suplemento, una frase en límites y las citas Runnalls 2007 y Hiskens–Pai 2000. Detalle: `docs/HISTORY_REDUCTION_LINE.md`. |
| R10 Código/datos públicos | **Abierto: decisión del autor** | El repositorio científico no es público por decisión del autor. |
| R30 Declaración de IA, aprobación de coautores | **Abierto: decisión del autor** | `SUBMISSION_DECLARATIONS_PENDING.md`. |

## Problemas de procedencia detectados durante la revisión

- En `generated/frozen/narrative_case_20261030/`, los JSON coinciden con su
  MANIFEST tal cual (CRLF) y `branch.csv` solo tras normalizar a LF. Es un
  efecto de la conversión de fin de línea de git, no un cambio de contenido.
  Conviene añadir `*.csv -text` y `*.json -text` a `.gitattributes`; el
  script nuevo `rebuild_signals_figure.py` acepta ambas formas.
- Los datos de C01 (observaciones, matrices de derivadas, predicciones)
  fueron desalojados por la política de retención. La teoría usa un banco de
  B01 construido con el runtime byte-idéntico al de C01.

| **Nuevo I8** Líneas base justas (aprendizaje reentrenado) | **Ejecutado** | `experiments/fair_baselines/` (PLAN.md con hash, `baselines.py`, resultados). ExtraTrees sobre cambios fasoriales, ExtraTrees y regresión logística sobre firmas físicas, ajustados en TRAIN de B01, umbral en CAL (0 alarmas normales), una pasada en TEST: Top-1 41, 49 y 32 de 72 frente a 72 del banco; extras 82, 30 y 71 frente a 7. Tabla en el suplemento y una frase en el protocolo. Pendiente: GLR de estado único con información equiparada (C02, Julia). |

| **Nuevo I9** Transferencia a una planta distinta (círculo simulador-modelo) | **Ejecutado parcialmente** | `experiments/second_plant/`: las 12 secuencias de TEST de B01 re-simuladas con una planta independiente (máquinas clásicas, regulador con estatismo), mismo operador PMU y ruido; PLAN con hash y dos enmiendas de recursos. Estático 40→42 fuentes; aprendices pierden hasta 6 y multiplican los extras; ningún método localiza un registro completo. **El banco dinámico no se ejecutó** (necesita bancos por registro construidos con Julia); los registros están exportados en su formato de entrada. Declarado en el artículo y el suplemento. |

| **Nuevo I10** Comparación con la literatura más cercana | **Parcial** | Yang, Chen y Zhai (arXiv 1911.01733 y 2107.06754), leídos en texto completo: modelo AC dinámico con GLR y filtro de partículas con carta EWMA, cortes persistentes con 10 PMU. Citados, situados en trabajo relacionado y tabla; no ejecutados. Revisores previstos en `docs/ANTICIPATED_REVIEWS.md`. |
