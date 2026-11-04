# P07 — Auditoría verificada y plan para envío a IEEE Access (4-nov-2026)

Base: auditoría adversarial de ChatGPT sobre el PDF de 16 páginas, contrastada
contra el código congelado (`SGSMA26-Physics-Informed-AD/experiments/...`), los
resultados C01 (`PAPER_CONFIRMATORY_C01/run/results/`) y el modelo Julia
(`SIM0001_JuliaPD_F01/runtime/reference/`).

**Dictamen:** ChatGPT tiene razón en que el manuscrito **no está listo para
enviar**. Pero no todos sus puntos son correctos, y no detectó dos problemas
que considero más peligrosos (B1 y B2).

---

## A. Objeciones de ChatGPT verificadas como CORRECTAS

| ID | Hallazgo | Evidencia verificada |
|----|----------|----------------------|
| A1 | Los priors temporales no coinciden con el diseño de prueba | `PAPER_CONFIRMATORY_C01/protocol/PLAN.json`: duración U[2,5] s, separación U[3,8] s, 6 eventos/120 s. El prior asume una media de OFF de 30 s y una media de nacimiento de 60 s. P(OFF ≤ 3.5 s) ≈ 11 %. |
| A2 | Falta la comparación decisiva: observador continuo vs. banco de historias con información equiparada | El GLR del manuscrito es de desarrollo (54 réplicas, 3 padres). **C02 está diseñado exactamente para esto** (24 TRAIN / 36 CAL / 42 TEST, ET reentrenado, umbral fijado en CAL), pero está en cola detrás de B01. |
| A3 | ExtraTrees parece un baseline defectuoso | `BY_SOURCE.csv`: ET_REFERENCE da 0/48 en BUS7, 0/42 en BUS24, 0/42 en BUS31, 0/18 en BUS26 y 0/42 en BUS16, aunque se entrenó con esas 18 fuentes. Un revisor lo leerá como baseline roto y no como ventaja física. |
| A4 | Chen no opera en un punto comparable | Se detiene en 72/72 normales (normal_FA = 12/12 por estrato) y en 66/162 antes del evento. Es un umbral mal calibrado, no una comparación justa. |
| A5 | Coste de cómputo | 358.7 s por registro de 120 s (99.6 ms/reporte frente a 33.3 ms disponibles). |
| A6 | Los conteos de desarrollo no cuadran con la evaluación independiente | El banco nominal saca 44/54 en el control GLR de desarrollo, pero 643/648 en C01. Hay que explicar la diferencia de cohorte y de reglas de publicación. |
| A7 | Vocabulario interno | En las secciones activas: `Sealed/sealed` 6, `frozen` 13, `archived` 5, `Chen2016` 4, `inherited` 6, `rather than` 16, `not` 69. |
| A8 | No hay paquete reproducible público | `P07_VALIDATION_ACTIONS.md`: "El repositorio científico no se publica". Sin esto no hay citabilidad ni arbitraje verificable. |
| A9 | Declaraciones pendientes | `SUBMISSION_DECLARATIONS_PENDING.md`: falta la declaración de IA, la disponibilidad de código/datos y la financiación. |

## B. Problemas NUEVOS que ChatGPT no detectó (los más graves)

**B1. Señal física sospechosamente pequeña en BUS31 (P0, credibilidad).**
`load.csv`: BUS31 tiene P = 0.092 pu = 9.2 MW (ZIP de impedancia constante).
El rango de prueba de ±3–14 % equivale a **0.28–1.3 MW** en un sistema de
~6.1 GW, y el banco lo atribuye a tiempo en 40/42 casos con ~0.3 s de
retraso. Un revisor de sistemas de potencia preguntará qué relación
señal/ruido hace posible eso en PMUs remotas. O el ruido simulado está muy por
debajo de un PMU real (C37.118, TVE 1 %), o la atribución usa canales que un
equipo real no resolvería. Sin una tabla de SNR por fuente, esto puede invalidar
el realismo de todo el resultado.
→ Hay que reportar por fuente: ΔP/ΔQ en MW/MVAr, |Δy| máximo en la mejor PMU
y su cociente con σ. Además, conviene una prueba de estrés con ruido de
clase C37.118 (×5, ×10). Si el método cae en BUS31, se dice honestamente y se
convierte en un resultado de límite de detectabilidad, lo que tiene valor
científico.

**B2. Diseño de prueba demasiado regular para el claim de "recuperación".**
Todos los eventos están separados por al menos 3 s, no hay solapamientos y
siempre son exactamente 6 eventos alternados. El claim central ("una
intervención nueva *durante* la recuperación") solo se prueba con huecos
≥ 3 s. Falta un estrés con huecos de 0.5–3 s y eventos solapados.

**B3. Resultado positivo infrautilizado.** Los normales suman 11.76 h por
método con **0 alarmas** (cota Poisson del 95 % ≈ 0.25 alarmas/h). Eso debe ir
en el abstract, separado de las 72 "extras" en registros con eventos (68 de
ellas fuera del banco R/X).

**B4. Oportunidad de cómputo.** El banco nominal (1 modelo) obtiene
**643/648** frente a 644/648 del banco de 5 modelos. Si el coste escala con
el número de modelos (hay que medirlo), el nominal costaría ≈ 72 s por 120 s,
**dentro de tiempo real**. Esto cambia la narrativa de "offline" a "un modelo
es viable online, y la mezcla solo añade robustez a costa de cómputo".

## C. Objeciones de ChatGPT INCORRECTAS o ya resueltas en el código

**C1 (R2.1, "el peso de red no marginaliza nacimientos"): incorrecto según el código.**
`E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/observer/static_rx.py:40-83`
(`predictive_log_density`) forma la mezcla predictiva de un paso con: sin
evento, continuación, OFF en las dos fases de medio reporte y nacimientos de
**todas** las celdas × intervalos de amplitud en ambas fases. Además lanza
`ArithmeticError` si la masa a priori no suma 1. Lo que sí queda abierto:
(i) los nacimientos retrospectivos (lags 1–18) cambian el posterior interno
pero no el peso externo, y (ii) los nacimientos predictivos parten del estado
nulo `m0`. **Acción:** escribirlo con precisión en la ec. (15) y en el
Algoritmo 1, y hacer la prueba de enumeración exacta (barata) para cuantificar
la discrepancia.

**C2 (BUS31 "es la barra slack"):** solo lo es en el flujo de carga. El
modelo dinámico tiene una carga ZIP real de 9.2 MW + j4.6 MVAr. Basta con
declararlo, pero se conecta con B1.

**C3 (R2.6, la covarianza perdida al comprimir):** el código ya registra
`projection_discarded_between_variance_trace` y `discarded_mass`. Se puede
reportar desde las salidas de C01 sin volver a ejecutar nada.

---

## D. Plan por fases (orden estricto)

### Fase 0 — Bloqueante: no tocar lo que corre
- B01 está en `test_inference` y C02 en cola (`QUEUE_STATUS: WAITING`). El
  disco tiene 100 GB libres, así que el requisito de 30 GiB de C02 ya se cumple.
  No modificar sus runtimes.

### Fase 1 — Diagnósticos sobre salidas C01 existentes (sin simular; 2–3 días)
1. **SNR por fuente (B1):** a partir de `truth_private/deterministic` y de σ
   por canal, generar una tabla con ΔP en MW, |Δy|/σ máximo y la PMU dominante.
2. **Descomposición del fallo de ET (A3):** por reporte, argmax antes de la
   regla de 6 frames, votos de la clase correcta, detección vs. clasificación y
   distribución de amplitudes en el entrenamiento de ET frente a la prueba.
   Hipótesis a verificar: ET vio otro rango de amplitudes o confunde carga con
   normal.
3. **Calibración de innovaciones (R14):** NIS por familia de canal,
   autocorrelación de lag 1–5 y covarianza cruzada f/ROCOF/ángulo.
4. **Pérdida por compresión (C3):** distribución de varianza descartada y
   de masa podada por evento.
5. **Concentración de extras (B3):** extras por condición, fuente y padre;
   normal FA/h con su cota.

### Fase 2 — Cómputo nuevo barato (≤ 1 semana)
6. **Enumeración exacta (C1/R05):** modelo lineal-gaussiano pequeño (2 cargas
   + 1 línea, ~40 reportes) con todas las historias enumeradas. Comparar
   posterior y peso de red reporte a reporte contra el algoritmo (con y sin
   poda o propuestas retrospectivas). Va al suplemento como prueba numérica.
7. **Perfil de latencia (B4/R02):** banco nominal vs. 5 modelos en 3
   registros, con latencia por reporte p50/p95/p99, memoria pico y throughput
   sostenido.
8. **Sensibilidad de hazards (A1):** rejilla de nacimiento {1/60, 1/10, 1/5} y
   OFF {1/30, 1/5, 1/3} **solo en desarrollo/CAL**. Fijar los priors
   reportados *antes* de abrir TEST de C02 o declararlos como sensibilidad.
9. **Chen recalibrado (A4):** umbral elegido con ARL en normales de CAL y la
   misma tasa de FA que los demás. Si sigue fallando, moverlo al suplemento
   como "transferencia bajo desajuste".
10. **Linealización vs. no lineal (R15):** error de predicción local vs.
    trayectoria Julia por fuente, severidad y horizonte, también en
    innovaciones blanqueadas.

### Fase 3 — El experimento decisivo: C02 (en cola)
Antes de que corra, hay que verificar que C02 incluye: el mismo presupuesto de
alarmas fijado en CAL, ET reentrenado con la misma cobertura de amplitudes y el
banco nominal de historias frente al GLR de un estado con los mismos operadores.
**Árbol de decisión al abrir TEST:**
- **Banco > GLR con significancia por padre** → se mantiene la tesis, y C02
  pasa a ser el resultado principal (sustituye a C01 como evidencia del
  mecanismo; C01 queda como evaluación de transferencia).
- **Banco ≈ GLR** → se reencuadra el paper: la contribución pasa a ser *la
  continuidad del estado físico* con un observador simple, y el banco queda
  como variante de robustez. Esto es publicable y honesto; no hay que añadir
  más ecuaciones para ocultarlo.
- **Banco < GLR** → se publica el observador continuo.

### Fase 4 — Validez externa (lo que haría el paper citable)
11. **Estrés de SNR realista (B1):** ruido ×5 y ×10 y TVE de clase P/M.
    Esto produce una curva de detectabilidad por fuente frente a MW, que es un
    resultado útil por sí mismo.
12. **Estrés de recuperación (B2):** huecos de 0.5–3 s y eventos solapados.
13. **Segundo simulador (R08):** el repo ya tiene ANDES. Generar la prueba en
    ANDES IEEE-39 (otra implementación de máquinas, AVR y gobernador) con la
    inferencia sin cambios. Es la única forma de responder a "el predictor y
    la planta comparten modelo".
14. **Sensibilidad del mapa PMU (R08):** invertir la polaridad y el terminal de
    BUS5 y excluir canales.

### Fase 5 — Reproducibilidad y citabilidad
15. Paquete público (Zenodo/GitHub con DOI): runtime congelado, configuración,
    semillas, schedules, predicciones por registro, evaluador, mapa de
    terminales y hashes. Añadir la sección "Code and Data Availability".
16. Script único `reproduce_tables.py` que regenere todas las tablas desde las
    predicciones.

### Fase 6 — Editorial (después de los resultados, no antes)
17. Reescritura con afirmaciones positivas primero y **una sola** sección de
    limitaciones. Eliminar `Sealed`, `frozen`, `archived`, `inherited`,
    `Chen2016` y `H04`, y reducir "rather than/not" a lo necesario.
18. Notación: h = (e, c, τ, κ, I_a) con a continua condicionada (R2.2).
    Algoritmo 1 en pseudocódigo real. Expandir GLR y M3H en su primer uso.
19. Abstract: agregar "offline causal replay" (o el resultado de latencia del
    nominal), las 18 fuentes y los 18 padres físicos, y el 0 FA en 11.8 h.
20. Tabla de fuentes con MW/MVAr de cada carga y descripción del operador en
    BUS31.
21. Figura 2 (eventos): está **protegida por AGENTS.md** y no se puede mover
    al suplemento sin orden explícita del autor. Si se conserva, hay que
    reducir su peso en el texto.
22. Referencias: verificar contra la fuente los DOIs propuestos para Dey
    (TSG 2026) y Albustami (EPSR). ChatGPT los da, pero no están verificados
    aquí.
23. Declaración de IA conforme a la política IEEE, autoría y aprobación de
    coautores, biografías y equilibrio de la última página.

### Criterio de "submit-ready"
- [ ] C02 TEST evaluado e integrado con alarm budget común.
- [ ] Tabla de SNR por fuente y estrés de ruido realista.
- [ ] Enumeración exacta en el suplemento.
- [ ] Latencia medida (nominal y mezcla).
- [ ] ET y Chen diagnosticados o recalibrados.
- [ ] Paquete con DOI.
- [ ] Reescritura editorial y declaraciones completas.
- [ ] Aprobación de los 4 coautores.

## E. Alcance: P07 vs. el objetivo completo (8 clases + predicción)

El objetivo del proyecto (detección, clasificación y localización de las 8
clases SGSMA más predicción con 8 PMUs) **no cabe en P07** sin perder rigor.
Recomendación:
- **P07** = carga/línea con recuperación (el claim actual, ya reforzado).
- **P08** = extensión a generación (que también es un override paramétrico y
  entra en el mismo banco), falla (operador shunt) y capa de integridad de
  medición (5/6/7) como modelo instrumental. Además, predicción a horizonte
  corto: la recuperación predicha `C0 Φ0 δx(κ)` ya *es* un pronóstico
  físico, y evaluarlo como forecast es una contribución natural.
