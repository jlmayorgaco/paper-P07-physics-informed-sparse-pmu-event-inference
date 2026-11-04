# P07: respuesta a la auditoría adversarial del 4-nov-2026

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
