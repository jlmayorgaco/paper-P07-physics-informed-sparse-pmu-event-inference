# Revisión independiente: ingeniería eléctrica, DAE e inferencia

**Rol:** revisor de dominio. **Fecha:** 2 de noviembre de 2026.
**Veredicto:** revisión mayor; no certificaría todavía el envío bajo una afirmación de avance tensorial/bayesiano general. Sí existe un método físico implementado y una comparación útil; no es solo terminología. La limitación principal es la distancia entre ese resultado acotado y la contribución general que se desea defender.

Esta revisión leyó las secciones activas del artículo, el suplemento causal, los contratos F01 y código concreto del generador/predictor/observador. No modificó el manuscrito, las simulaciones ni resultados. Los checks de ejecución citados se inspeccionaron como artefactos existentes; no equivalen a una nueva simulación independiente. No se abrió RAW0002.

## 1. Qué física y matemática son reales

| Elemento | Verificación | Dictamen |
|---|---|---|
| Red y medición | `sections/article_method.tex:17`; `physics/build_static_rx.jl:61` obtiene tensiones y corrientes del terminal nativo, invierte el signo nativo y aplica bases/ganancias | Uso físico real. Distingue corriente terminal de inyección nodal. |
| DAE completa local | `build_static_rx.jl:73–78` usa ForwardDiff, bloques algebraicos/diferenciales y Schur; `run/runtime/model/dae/MODEL.json`: 114 estados diferenciales, 78 algebraicos, 38 entradas | Es la linealización de la DAE ensamblada, no solo una matriz Ybus o una analogía eléctrica. Sigue siendo un predictor local. |
| Derivadas de entrada y medición | `build_static_rx.jl:77–89` conserva el término directo de parámetros en corriente y el indirecto vía solución algebraica | Las ecuaciones C/D reducidas del texto son correctas bajo regularidad de g_z y referencia fijada. |
| Switches y estado | El generador mantiene estados diferenciales y resuelve algebraicos; el predictor construye operadores ON/OFF | La continuidad de x con salto posible de z es físicamente correcta para los operadores sin impulsos considerados. No implica recuperación instantánea tras OFF. |
| Frecuencia absoluta | `run/engine/reference/pmu_operator.py:23–50`: fase desenvuelta, ajuste causal cuadrático, f=60+coeficiente/360; ROCOF=2*coeficiente cuadrático/360 | No hay doble suma de 60 ni sustitución por velocidad de rotor en esta ruta inspeccionada. Hay aproximaciones instrumentales que deben explicitarse (hallazgo 1). |
| Integral bayesiano local | `observer/static_rx.py:17–37`; suplemento `appendix_causal_walkthrough.tex`, integral de normal truncada | La completación del cuadrado y razón de normalizadores son correctas para el modelo gaussiano condicional. El término común 47 log(2π) puede omitirse en cocientes entre partículas de la misma dimensión. |
| Pesos de red | `static_rx.py:40` construye densidad predictiva previa a selección/corrección; incluye nacimientos sin usar el reporte para seleccionarlos | Bayes condicional aproximado real. No acredita filtro global óptimo ni calibración de probabilidades. |
| M, Gamma, Delta M | `article_method.tex:162–183`; `static_rx.py:238–240` implementa las dos contribuciones a Delta M y comprueba suma | Identidad algebraica correcta y diagnóstico interpretable. No es una nueva ley dinámica tensorial ni crea información adicional. |
| Q_ij | Ecuación de respuesta de `article_evidence_bridge.tex:65`; CSV de validación y fórmula histórica | Representación física genuina de interacciones entre fuentes en otro experimento. No está incorporada como tensor de segundo orden en el banco continuo evaluado. |

Como control concreto, inspeccioné los 13 registros de derivadas por cada una de las cinco partículas de `run/derivatives/grid/S137/*/CHECK.json`. Sus máximos errores direccionales PMU son menores que 3.93e-8, los máximos errores direccionales de A menores que 1.16e-8, residuos algebraicos menores que 3.42e-13 y salto diferencial registrado cero. Esto respalda la implementación de derivadas en ese punto; no prueba exactitud global, respuesta a gran señal ni toda la población.

Los archivos de código anteriores están bajo `C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/`, excepto `run/...`, que está bajo `experiments/PAPER_CONFIRMATORY_C01/`.

## 2. Hallazgos mayores

### 1. La aproximación del estimador de frecuencia/ROCOF no está descrita con suficiente precisión

El generador usa ajuste cuadrático **ponderado por magnitud y robusto**: `run/engine/reference/pmu_operator.py:42–48`. El predictor usa coeficientes fijos de la pseudoinversa cuadrática **no ponderada** de 21 muestras: `physics/native_conditional_builder.py:47`. No son el mismo operador cuando cambian magnitudes o las ponderaciones robustas. El texto dice que se añaden operadores de historia de fase, sin explicar esta diferencia. Es especialmente relevante al interpretar grandes innovaciones cerca de cambios algebraicos.

**Corrección editorial posible ahora:** declarar explícitamente qué operador genera y cuál aproxima la inferencia; explicar que la memoria del predictor no vuelve exacto el estimador robusto. La afirmación de reproducción instrumental exacta exigiría una validación que aquí no se ha hecho. No cambiar el operador congelado de C01.

Relacionado: `article_interpretation.tex:70` dice que el ruido de frecuencia/ROCOF "follows phase estimation". En el código, se añade **después** del estimador como familias separadas (`noise.py:apply_noise`), no es la derivada muestra a muestra del ángulo ruidoso; la covarianza entre familias archivada no se aplica. Redactarlo sin ambigüedad. Las advertencias son compatibles con una simulación metodológica, pero limitan transferencia instrumental.

### 2. Falta un descriptor eléctrico compacto del modelo realmente ejecutado

La DAE abstracta y Schur están bien, pero el lector no sabe qué compone f: orden/tipo de máquinas, controles, qué generador no tiene control, dimensiones y ley de carga explícita. El código sí lo fija: `run/engine/reference/ieee39_source/ieee39_base.jl:138–184` usa Sauer–Pai, AVR Type I y TGOV1, con BUS39 no controlado; el contrato DAE tiene 114/78 estados. El texto especifica constant-impedance ZIP en prosa pero no muestra su dependencia de tensión.

**Corrección editorial:** tabla breve del modelo y la ecuación de carga implementada, con referencias del modelo/library y parámetros/archivos ejecutables. No hace falta llenar el paper de ecuaciones estándar: sí identificar exactamente la física cuya ventaja se atribuye. La versión de PowerDynamics por sí sola no define un IEEE39 único.

### 3. La contribución de Bayes/tensores en la ventaja final sigue sin estar aislada

La necesidad de integrar amplitud tiene una justificación válida frente al ajuste puro en soportes anidados. Sin embargo, GLR penalizado, MDL o inferencia por perfiles son alternativas; no se ha demostrado que esta integración sea necesaria para obtener la mejora de C01. Las sensibilidades Q_ij reducen error de respuesta en 32 casos conocidos de otra campaña, mientras el método continuo usa predictores locales de carga/línea. La reconstrucción Kalman de voltajes ocultos también es una validación separada.

**Consecuencia científica:** puede defenderse un procedimiento completo y su trade-off, pero no "añadir Bayes y tensor produce la mejora". Para tal atribución se necesita un contraste con el mismo diccionario, estado inicial, propuestas, publicación y presupuesto de alarmas; cambiar solo perfil/integral o interacción de firmas. Esto no se soluciona añadiendo ecuaciones al relato. La versión actual reconoce buena parte de este límite: conservar esa honestidad.

### 4. Validación acotada por generación e inferencia de la misma familia y por terminales provisionales

El generador y el predictor comparten ecuaciones F01, mapa terminal y gran parte de la instrumentación. Variar R/X dentro/fuera del banco es útil, pero no prueba error de ley de carga, controles o un CT distinto. El contrato `SIM0001_JuliaPD_F01/START_HERE.md` deja explícitamente sin identificar al productor los terminales, y BUS39 parcialmente validado. BUS5 es hipótesis 5–6. La misma incertidumbre de mapa que motivó meses de trabajo sigue siendo límite real.

**Para el artículo actual:** presentar el resultado como simulación física controlada. No requiere identificar retroactivamente RAW para ese claim limitado. Para afirmar transferencia a RAW/campo o que se recupera información en cualquier bus de IEEE39, faltan evidencias. Las nueve cargas/nueve líneas no equivalen a todos los buses/eventos de hackathon.

### 5. El resultado batch normalizado incorrectamente no debe ser pilar de una afirmación probabilística

`article_evidence_bridge.tex:112` conserva correctamente el offset de evidencia de una fuente. El prior efectivo distinto puede describir las decisiones ejecutadas, pero no prueba el modelo declarado inicialmente ni probabilidad calibrada. La tabla con 100% puede distraer del método causal que no tiene ese error. Mantenerla como análisis histórico claramente delimitado o relegarla a material técnico; nunca mezclarla con el denominador confirmatorio. La corrección de interpretación no sustituye el replay físico normalizado, que no se efectuó.

## 3. Ajustes matemáticos/editoriales menores que sí deben hacerse antes de enviar

1. **Independencia de historia en LTI.** `article_information.tex:11` debe decir "con la misma dinámica lineal y una intervención aditiva". Si el evento cambia A (apertura de línea), la respuesta incremental depende de x previo incluso si cada modo es LTI. En general `(exp(A1 T)-exp(A0 T)) x0` no desaparece.
2. **Potencia con PMU no colocada en el terminal de corriente.** `article_evidence_bridge.tex:50` es una ecuación correcta para tensión y corriente del mismo terminal. En este mapa, BUS2 mide tensión en2 y corriente en3; BUS10 tensión en10 y corriente en11. El producto de los canales exportados es un proxy, no S del terminal. Añadir esa frase para que no se interprete que se midió P/Q físicamente coincidente en las ocho PMU.
3. **Índices del predictor.** `article_method.tex:58` da una forma genérica de estado/observación. La implementación del suplemento usa `r_k=J_o xi_{k-1}+...` con propagación incluida en J, y `K=T P J' S^-1`. Declarar ese convenio de reporte evita que un implementador use por error un K de filtrado del mismo instante en lugar de la actualización de transición mostrada. No he demostrado un fallo de ejecución; es una ambigüedad de presentación.
4. **Condición de observabilidad versus buen ajuste.** La distancia perfilada actual es razonable y está calificada como local. No convertir los seis grupos o buses invisibles de una foto histórica en equivalencias exactas de la DAE completa bajo todo horizonte. El manuscrito actual no hace esa afirmación; conservarlo.
5. **Umbral0.99.** Está bien declarado como ajuste no calibrado. Una probabilidad numérica0.99 en M no permite afirmar error de decisión1%. Las reglas de seis reportes también usan evidencia dependiente; no multiplicar probabilidades como si fueran ensayos independientes.

## 4. Respuestas directas al usuario

- **¿Physics-informed real?** Sí. La DAE, condiciones algebraicas, topología, terminales y sensibilidades determinan las curvas candidatas y sus probabilidades condicionales. No es solo poner P/Q en un árbol. El método físico no necesita ser una red neuronal para ser informado por física.
- **¿Bayes real?** Sí en los cálculos condicionales de intensidad y modelo. No es un posterior conjunto exacto de planta, ruido, estado, historia y parámetros; poda, propuesta, plug-in y covarianza compartida importan.
- **¿Tensor real y necesario?** Los coeficientes D/Q/Qij son multivariados y físicos. M es un arreglo de masas. Ninguno demuestra por su nombre una ventaja de aprendizaje/compresión tensorial, y Qij no explica causalmente los aciertos de C01.
- **¿Método elegante y reproducible en papel?** Hay pseudocódigo y suplemento con fórmulas ejecutables. Falta condensar modelo e instrumentación y delimitar la novedad sin hacer pasar pruebas separadas por un único estimador validado.
- **¿Listo para journal?** No bajo la contribución amplia deseada. Para un claim acotado de procedimiento causal y comparación, primero corregir los puntos editoriales y resolver el argumento de contribución frente a bancos de hipótesis existentes. Una revisión rigurosa puede cuestionar razonablemente la necesidad de sus componentes y la robustez fuera del simulador.

## 5. Mínimo cierre recomendado

1. Incorporar las precisiones de operador instrumental, modelo eléctrico, LTI aditivo, potencia del terminal e índices. Son correcciones documentales, sin método nuevo.
2. Mantener un único claim: procedimiento causal físico-bayesiano de cargas/líneas con recuperación y trade-off medido; explicar exactamente la diferencia respecto de antecedentes de bancos/múltiples modelos.
3. Elegir entre limitar la atribución causal de la mejora o ejecutar una ablación predeclarada de componente en experimento sucesor; nunca tocar C01 para crear esa evidencia.
4. No usar RAW como validación independiente, ni prometer cobertura cyber/fallas/generación del filtro continuo por contener figuras o módulos históricos de esas clases.

No encontré en las ecuaciones activas un error algebraico fatal comparable al offset conocido del banco histórico. Eso no equivale a una certificación completa: no reejecuté toda la cadena ni audité cada operador de la librería Julia.
