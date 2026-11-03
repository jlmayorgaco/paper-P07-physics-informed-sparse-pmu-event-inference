# Revisor 1 — ingeniería eléctrica y método matemático

Revisión independiente del manuscrito vigente el 2 de noviembre de 2026.
No se modificaron el manuscrito, métodos, resultados ni campañas. No se abrió RAW0002.
No se consultaron informes previos de revisión. Las referencias de línea son
al código/LaTeX inspeccionado; el documento principal compilado tiene 16 páginas.

## Dictamen

**Revisión mayor antes del envío.** Existe un método físico implementado y
resultados sustanciales de simulación; no es una colección vacía de palabras.
Sin embargo, la evidencia todavía no identifica cuánto de su ventaja procede
del mecanismo que el artículo propone como aporte central. El límite entre
una implementación física razonable y una nueva contribución metodológica
debe resolverse con los controles pendientes, no con más vocabulario.

No encontré un error algebraico fatal confirmado en las ecuaciones principales
que revisé. Esto no equivale a certificar todo el código o el modelo IEEE-39.
El mayor riesgo es atribuir al mecanismo físico-bayesiano una mejora que la
comparación de procedimientos completos no puede aislar, seguido por la
robustez no demostrada ante discrepancias instrumentales/dinámicas.

## Lo que está técnicamente bien

1. **La física entra en el cálculo, no solo en el título.** El generador Julia
   y el constructor de predictores tienen derivadas de la DAE y del mapa PMU.
   `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/physics/build_static_rx.jl:72`
   usa diferenciación automática, eliminación algebraica y operadores PMU;
   `native_conditional_builder.py:11` discretiza esos operadores e incorpora
   memoria instrumental. El texto distingue el generador no lineal de la
   inferencia con modelos locales.
2. **Corriente terminal versus inyección nodal está correctamente separado.**
   `sections/article_method.tex:16` y `sections/article_evidence_bridge.tex:54`
   no identifican una corriente de rama con la inyección del bus. La suma
   trifásica de potencia exige tensión y corriente colocadas en el mismo terminal;
   el texto reconoce que BUS2/BUS10 tienen productos que solo son proxies.
3. **La eliminación de Schur es correcta bajo sus hipótesis.** Las ecuaciones
   `eq:narrative-reduction` y `eq:electrical-output-reduction` coinciden con
   la diferenciación implícita cuando g_z es invertible en la carta utilizada.
   No debe interpretarse como válida automáticamente en cualquier conmutación
   o régimen cercano a singularidad.
4. **El integral local de amplitud es realmente bayesiano.** La fórmula de
   `supplement/appendix_causal_walkthrough.tex:128` completa el cuadrado,
   conserva determinantes y normalizadores de truncamiento, y concuerda con
   `run/runtime/core_v6.py:122` y `observer/static_rx.py:17` de la ruta C01.
   La constante común 47 log(2 pi) omitida por código cancela entre candidatos
   con el mismo espacio observado. Eso no convierte el banco podado completo
   en un posterior exacto.
5. **La corrección condicional m+d a está bien derivada.** El suplemento
   `eq:implemented-conditional-correction` usa el gain de transición
   K=T P J' (R+J P J')^-1, que coincide con el constructor en
   `native_conditional_builder.py:113`. No es un gain de estado que se pueda
   reemplazar sin cambiar la indexación.
6. **Continuidad física y causalidad están tratadas con cuidado.** El texto
   conserva x al cambiar el modo algebraico; separa ON estimado de tiempo de
   emisión, no confunde frecuencia de bus con velocidad de rotor, y reconoce
   que la búsqueda efectiva es de 0–18 reportes, no todos los 300 almacenados.
   La suma/resta del sufijo anterior en `retro_birth.py` evita multiplicar
   simplemente la misma ventana muchas veces. La selección adaptativa y la poda
   siguen siendo aproximaciones declaradas.
7. **El manuscrito ya evita la inflación tensorial.** M y Gamma son masas
   agregadas; DeltaM es una identidad temporal. Los coeficientes mixtos Q_ij
   pertenecen a otro ensayo de respuestas simultáneas. Esta separación debe
   conservarse, incluso si una implementación futura usa GPU.

## Objeciones mayores

### R1-M1. El aporte central de recuperación/Bayes no está identificado por la evidencia principal

**Confirmado.** La contribución 2 (`sections/article_intro.tex:41`) es mantener
recuperación y separar actividad/causa. Pero el resultado central compara
procedimientos completos. El propio texto reconoce que nominal y mezcla tienen
publicadores diferentes (`article_method.tex:223`) y que el GLR histórico cambia
búsqueda, tratamiento de amplitud y semántica (`narrative_results.tex:42`).
`article_controlled_ablation.tex:1` todavía contiene “in progress”.

**Por qué importa:** 644/648 es evidencia de desempeño del paquete, no prueba de
que Bayes, memoria o DeltaM sean la causa de ese desempeño. Un revisor puede
aceptar que el paquete funciona y aun así rechazar la novedad atribuida.

**Remedio mínimo:** terminar e incorporar la ablación autorizada del mismo banco,
sin ajustes. Explicar qué mecanismos se mantienen en ambos brazos. Si no hay
ganancia aislada, formular la contribución como implementación/evidencia de un
procedimiento causal, no como superioridad intrínseca de Bayes o del tensor.
No exige inventar otro método ni buscar otra corrección por bus.

### R1-M2. Falta evaluar la consistencia del predictor y su incertidumbre durante ON/OFF y recuperación

**Confirmado como brecha de evidencia, no como fórmula incorrecta.**
`article_method.tex:133` declara covarianza compartida y pérdida del spread
entre historias. El constructor resuelve Riccati solo con el operador normal
(`native_conditional_builder.py:110–116`) y reutiliza P en modos conmutados.
Al cierre, `run/runtime/core_v6.py:167–170` retiene la media, registra el spread
omitido y borra historias; no transporta una covarianza exacta por trayectoria.
El manuscrito reconoce la aproximación, pero no muestra su efecto cuantitativo
en innovaciones, cobertura de estados o sesgo de intensidad.

**Por qué importa:** una masa 0.99 puede provenir de una incertidumbre demasiado
pequeña. Esto es especialmente pertinente cuando las alarmas extra aumentan
con R/X fuera del banco. La buena localización no valida las incertidumbres.

**Remedio mínimo:** un diagnóstico descriptivo, sin reajuste, de innovaciones
pre-update y de cobertura/error de las cantidades que se decida reportar como
estimadas; separar normal, ON, OFF y recuperación. Los residuos posteriores a
selección no sirven como sustituto de una innovación predictiva. Si esos datos
no están conservados, declarar la validación pendiente y no vender intervalos
de severidad/estado como incertidumbre validada. No exigir calibración perfecta
para un paper que limita sus afirmaciones a pesos aproximados.

### R1-M3. El ensayo estresa parámetros, pero no una discrepancia estructural independiente

**Confirmado.** `sections/article_interpretation.tex:63–75` dice que simulador
y predictores comparten la familia de ecuaciones y el mapa PMU. La planta
congela cargas de impedancia constante y controles específicos
(`article_method.tex:30–40`). Cambiar R/X dentro/fuera de cinco partículas
es una prueba útil, pero no somete el modelo a otra ley ZIP, control, productor
o instalación instrumental.

**Por qué importa:** el método conoce precisamente los operadores que generan
sus clases, mientras su robustez más difícil puede depender del error estructural.
No es fuga de etiquetas: es una frontera de validación física. No debe llamarse
replicador validado de RAW0001 ni prueba de generalización de campo.

**Remedio mínimo para este envío:** delimitar la afirmación a identificación
dentro de esta familia de simulación y poner ese alcance en el enunciado central,
no solo al final. Para una afirmación más amplia haría falta una prueba independiente
prespecificada; no introducirla silenciosamente en C01 ni seleccionar otro caso
porque dé mejores resultados. El artículo ya declara mucho de este límite,
lo cual reduce el riesgo, pero también acota la magnitud de su contribución.

### R1-M4. Las hipótesis instrumentales son demasiado decisivas para permanecer dispersas

**Confirmado como contrato incompleto en el artículo, no como error del exportador.**
`narrative_problem.tex:28` informa 47 coordenadas y BUS5/BUS39; el contrato F01
contiene ocho asignaciones de terminal, polaridad, ganancia y sesgo. BUS2 toma
V en 2 e I en 3; BUS10 toma V en 10 e I en 11. El diagrama ubica las PMU de tensión
pero el mapa completo de corrientes no aparece como tabla en el manuscrito/suplemento
actual leído. Las identidades de CT del productor siguen sin confirmarse.

Además, `article_method.tex:67–70` reconoce un generador de f/ROCOF robusto
ponderado versus predictor no ponderado; `article_interpretation.tex:69–73`
reconoce ruido independiente por familia después de derivar fase, omitiendo
el factor histórico entre familias.

**Por qué importa:** esta no es simplemente una elección de nomenclatura.
La identidad de una rama medida y el ruido conjunto pueden cambiar qué fuentes
son distinguibles y cuánto pesa cada canal. Ocho flujos virtuales emparejados
no prueban una instalación física estándar de ocho PMU con V/I colocadas.

**Remedio mínimo:** tabla autocontenida de los ocho terminales, polaridades,
unidades, referencia y estado de procedencia, más una ecuación compacta de f/ROCOF
y un esquema de dónde se añade el ruido. Distinguir la red de sensores simulada
del productor RAW desconocido. No ajustar el mapa al resultado confirmatorio.
No afirmar consistencia instrumental completa, TVE de cumplimiento o instalación
de campo a partir de esta campaña.

### R1-M5. La receta reproducible del método final sigue repartida entre reglas y archivos heredados

**Confirmado.** El algoritmo principal es comprensible como flujo, pero el
comportamiento depende de pantallas de nacimiento, cualificación de fuente,
dos relojes OFF, sustitución, poda, cuatro regímenes y estimación de prefijo.
`appendix_publication_rules.tex:17–44` aclara varias de ellas. El PROTOCOL.json
congelado también conserva campos heredados de `continuous_bank` y compresión
Tucker, aunque el método final declara otra búsqueda efectiva. Un tercero no
debería inferir qué campos son activos leyendo una genealogía de versiones.

**Por qué importa:** una mejora puede deberse a reglas de publicación y no al
estimador anunciado. La reproducción ejecutable puede ser posible con el snapshot,
pero reimplementarlo desde el artículo todavía es costoso y ambiguo.

**Remedio mínimo:** un contrato reducido y generado desde la ruta activa con
dimensiones, ecuaciones, parámetros, máscaras de configuración activa y orden
exacto de actualización; trazabilidad a funciones. No cambiar el código congelado.
El diagrama y pseudocódigo deben señalar explícitamente observador versus publicador.

### R1-M6. La regla de búsqueda limita los eventos detectables más que la ventana de 10 s

**Confirmado y parcialmente resuelto por el texto.** El artículo ahora distingue
300 reportes almacenados de 19 lags explorados (`article_method.tex:113–115`).
El código usa una pantalla de cambios y evita repetir ticks ya propuestos
(`run/runtime/core_v6.py:74–79`). El propio protocolo admite que puede perder
eventos débiles, suaves o instantáneamente invisibles. C01 contiene un catálogo
de acciones abruptas; no demuestra vigilancia general de perturbaciones físicas.

**Remedio mínimo:** incluir esa admisión en la descripción del problema soportado
y la tabla de alcance, no describir la implementación como búsqueda completa
de diez segundos. Cuantificar el papel de la pantalla con registros ya disponibles
si se conserva su salida; no es obligatorio añadir rampas como otra campaña para
mantener la afirmación estrecha actual.

## Objeciones menores y precisiones

1. **No confundir causalidad de streaming con inferencia causal estructural.**
   El keyword “causal inference” del suplemento puede atraer expectativas de
   identificación causal estadística. El algoritmo es causal en disponibilidad
   de reportes y físicamente condicionado a hipótesis; eso debe quedar explícito.
2. **El umbral F no tiene una ley nula operacional demostrada.** El suplemento
   ya lo reconoce. Mantenerlo como regla congelada; no usar su cuantil nominal
   para prometer una tasa global de falsas alarmas en ruido coloreado, máscaras
   cambiantes o ventanas solapadas.
3. **El integral analítico no implica numerics exactos en colas extremas.**
   `amplitude_parent.py:13–24` usa pisos/clips por estabilidad. Sería útil incluir
   el rango probado contra cuadratura y verificar los casos de extremos;
   no detecté en esta revisión una falla numérica concreta del conjunto ejecutado.
4. **La eliminación de Schur es local.** Incluir qué sucede ante singularidad
   o mal condicionamiento g_z y rechazo del solver. Una derivada verificada por
   diferencias finitas valida esa derivada local, no toda una falla severa.
5. **DeltaM no es indispensable para decidir.** El código la calcula como
   diagnóstico y no le atribuye una ganancia aislada. Puede permanecer como
   visualización interpretativa, pero no presentarse como ley nueva de aprendizaje.

## Qué afirmaría como revisor y qué no

| Pregunta | Dictamen técnico |
|---|---|
| ¿Es realmente physics-informed? | Sí, en un sentido más fuerte que features: las hipótesis producen predicciones desde ecuaciones de red y dinámica. |
| ¿Es bayesiano? | El integral local y las mezclas condicionales sí; el sistema completo es una aproximación con reglas, estimaciones plug-in y poda. |
| ¿Es un estimador bayesiano óptimo general? | No, y el texto actual correctamente no lo afirma. |
| ¿Es un método tensorial novedoso? | No está demostrado. M/DeltaM no lo hacen tensorial en sentido algorítmico; Q_ij es otro ensayo físico. |
| ¿Hay física eléctrica falsa confirmada en las ecuaciones principales? | No encontré una contradicción algebraica fatal. Hay hipótesis instrumentales y dinámicas fuertes, explícitas pero no validadas externamente. |
| ¿Valida todos los eventos de la hackathon o cyber conjuntamente? | No. El banco causal probado es carga/línea; la integridad está separada. |
| ¿Está listo para envío? | No mientras la prueba central de componentes esté pendiente y el alcance/evidencia sigan sin cerrarse. |

## Cierre exigible sin otra cadena de versiones

1. Cerrar A01, reportando también empates, regresiones y falsas alarmas.
2. Elegir una afirmación central que el resultado realmente permita; no prometer
   que la combinación de tres términos conocidos es nueva por su nombre.
3. Completar el contrato instrumental y de ejecución del método vigente.
4. Añadir, si están disponibles, diagnósticos de predicción/incertidumbre ya
   registrados; de lo contrario mantener explícito el límite correspondiente.
5. Separar aportes demostrados, evidencia histórica y extensiones no implementadas.

Estas correcciones son acotadas. No requieren seguir corrigiendo BUS31 ni tocar
baselines; sí requieren aceptar que un buen resultado de simulación y una nueva
teoría general son contribuciones de alcance distinto.
