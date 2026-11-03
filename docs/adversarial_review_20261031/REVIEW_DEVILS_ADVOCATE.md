# Revisión adversarial independiente de P07 — 31 de octubre de 2026

**Objeto:** la versión activa de *Physics-Based Event Attribution From Sparse PMUs With Recovery Memory*, resuelta desde `main.tex` y `supplement.tex`. Esta es una auditoría técnica independiente, no una ronda editorial puntuada. No se consultaron informes de otros revisores, resultados parciales de C01 ni RAW0002. No se ejecutaron simulaciones, entrenamiento, cambios de método o modificaciones del manuscrito. Una corrección factual comunicada después de la primera entrega se verificó directamente en la fuente de entrenamiento ExtraTrees y se incorporó abajo.

Se leyeron las reglas de ambos repositorios, `SIM0001_START_HERE.md`, `SIM0001_CURRENT.json`, el contrato de continuidad F01 y sus decisiones. F01 se interpreta como candidato congelado de investigación, con BUS5 5–6 provisional. Los resultados siguientes son los publicados en los archivos actuales; no se reconstruyeron desde versiones archivadas.

## Dictamen técnico central

La crítica más fuerte es que **P07 especifica una integración física razonable, pero todavía no demuestra que su banco de historias de recuperación sea necesario o ventajoso frente a un predictor de estado mucho más sencillo**. La continuidad del estado es correcta. La utilidad operacional de conservar múltiples explicaciones del pasado sigue sin aislarse.

No he encontrado en esta lectura focalizada un error algebraico que refute el mecanismo. Tampoco encuentro soporte para presentarlo como un nuevo principio de inferencia: el propio texto reconoce correctamente los antecedentes de trayectorias, IMM y filtros de múltiples hipótesis. El problema es de suficiencia de la contribución y del diseño experimental, no una acusación de falsedad o de omisión deliberada.

La formulación adversarial más difícil de responder sería:

> «Ustedes han construido un filtro aproximado de modos e historias para una planta y un catálogo conocidos. La recuperación ya está contenida en el estado dinámico de cualquier predictor consistente. Las comparaciones cambian también las reglas de publicación; los comparadores ExtraTrees entrenados en SIM no aíslan la necesidad de mantener historias físicas; el único comparador físico publicado resuelve otro subproblema. X02 no mejora las decisiones de fuente y X04 no muestra información adicional útil. ¿Qué resultado exige realmente el banco de historias y no se obtiene con un solo predictor de estado y un test residual de hipótesis?»

Esto **no demuestra que el algoritmo sencillo vaya a ganar**. Es la explicación rival más económica que los experimentos publicados todavía no descartan.

## Hallazgos priorizados y su categoría

### P1 — Falta identificar el efecto del mecanismo que da título al artículo

**Categoría: carencia confirmada del diseño; no resultado negativo demostrado.**

El aporte se presenta como competencia entre nuevas intervenciones y recuperación retenida: [introducción, líneas 40–44](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_intro.tex:40). Sin embargo, el artículo reconoce que la ablación de admisión no es una ablación pura de memoria y que nominal y mezcla tienen rutas de publicación propias: [método, líneas 195–199](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_method.tex:195). El reconocimiento aparece también en [trabajos relacionados, líneas 41–46](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_related.tex:41) y [discusión, líneas 9–15](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_interpretation.tex:9).

H04 da 53/54 atribuciones oportunas y cuatro alarmas extra para cinco modelos; nominal da 54/54 y siete extras; la regla de testigo de inicio da 52/54 y cero extras. Son tres compromisos entre sensibilidad y publicación. No identifican un efecto causal de la memoria ni de promediar redes. La tabla es honesta al presentarlos como procedimientos completos: [tabla actual](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/tables/generated/narrative_results.tex:1).

**Consecuencia:** la afirmación limitada «se especificó y ejecutó este procedimiento» sobrevive; «la memoria propuesta mejora la atribución» todavía no está demostrada. Un C01 positivo entre los mismos procedimientos tampoco resolvería por sí solo esta identificación del mecanismo.

### P1 — El competidor decisivo no es un detector que reinicia la física

**Categoría: hipótesis de falsificación prioritaria.**

La explicación física en [método, líneas 143–157](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_method.tex:143) es estándar: restaurar la entrada no restablece el estado. En un modelo de Markov correctamente aumentado, el estado físico e instrumental actual y el modo activo contienen la información necesaria para predecir el futuro. La historia sirve para representar la incertidumbre sobre esas cantidades; su identidad pasada no constituye por sí sola una nueva variable física necesaria.

Por tanto, el rival fuerte es un **predictor causal de estado que nunca se reinicia a equilibrio**, con una hipótesis de «ninguna nueva intervención», plantillas o direcciones físicas para las nuevas fuentes y un test secuencial residual. Para cargas, la superposición local hace especialmente plausible esta explicación rival; el propio artículo lo dice en [información, líneas 12–19](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_information.tex:12). Para líneas, el rival debe actualizar el modo topológico y el operador de medida; no se permite representarlas como cargas ficticias.

Un segundo rival razonable es un IMM/GPB con los mismos operadores admitidos. No se afirma que cualquiera de estos sea equivalente a R11, ni que herede garantías bajo sus aproximaciones. Se pide comprobar si una representación más comprimida basta. Un control que borre toda recuperación puede mostrar que borrar física perjudica, pero no que la representación compleja elegida aporte valor.

### P1 — La novedad es de especificación e integración; los ingredientes no la sostienen por separado

**Categoría: antecedencia confirmada; suficiencia editorial por resolver.**

El texto actual delimita bien esta frontera en [trabajos relacionados, líneas 24–46](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_related.tex:24). La verificación primaria confirma:

- IMM ya trata la gestión y mezcla de hipótesis en sistemas con coeficientes que conmutan: [Blom y Bar-Shalom, IEEE, 1988](https://ieeexplore.ieee.org/document/1299/).
- M³H mantiene historias de secuencias de modos, con filtros condicionados y gestión mediante poda y mezcla: [Boers y Driessen, Automatica, 2005](https://www.sciencedirect.com/science/article/pii/S0005109804003243).
- El preprint de Warner y colaboradores ya utiliza simulaciones dinámicas de alta fidelidad y PMU escasas para diagnosticar fallas de línea: [preprint TechRxiv, versión 1, 2023](https://doi.org/10.36227/techrxiv.23264519.v1). Su objetivo evaluado no es el catálogo de sucesivas cargas/líneas con restauración de P07.
- Sensibilidades de trayectorias DAE y evidencia bayesiana analítica tampoco son nuevas por sí mismas: [Nagi, Huan y Chen, IEEE TPWRS, 2022](https://ieeexplore.ieee.org/document/9512471/).

La literatura no demuestra que toda la configuración exacta de P07 ya exista. Sí impide que «historia», «mezcla», «evidencia» o «física DAE» sean la contribución autónoma. La defensa tiene que concentrarse en qué decisión operacional mejora esta combinación, en qué condiciones y con qué coste. La identidad de incremento de masas tampoco añade una teoría nueva; el artículo ya lo reconoce en [método, líneas 174–184](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_method.tex:174).

### P1 — Los ExtraTrees sí tienen entrenamiento SIM; falta el comparador físico sencillo que aísle la complejidad

**Categoría: ausencia confirmada del contraste decisivo; equivalencia del presupuesto de ajuste por auditar.**

La fuente de entrenamiento declara que **ambos ExtraTrees se reentrenaron en SIM0014–SIM0017 y se validaron en SIM0018**, manteniendo juntos los hermanos de cada padre. BASELINE conserva 846 características; SHORT añade 611 características causales. Ambos reciben 47 señales, referencia de 300 reportes, primera decisión desde el reporte 360 y persistencia de seis argmax consecutivos. La misma fuente declara que no hubo búsqueda de hiperparámetros a partir de esos resultados: [README del comparador, líneas 3–12](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/experiments/E5_VALIDATION_PAPER/M03_R09_NUISANCE_DEV/ml/README.md:3).

Por tanto, sería incorrecto describirlos como el ZIP del hackathon aplicado sin adaptación a SIM. Que se mantengan congelados en H04/C01 es una propiedad correcta del protocolo, no una debilidad: [protocolo, línea 22](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/narrative_protocol.tex:22). Su 0/27 cargas y 27/27 líneas es evidencia de esos dos diseños entrenados bajo el contrato declarado. No demuestra que toda alternativa supervisada falle, pero tampoco puede descartarse por ausencia de entrenamiento SIM.

La crítica que permanece es distinta: estos clasificadores no aíslan cuánto aporta el banco de historias sobre un predictor físico sencillo con el mismo conocimiento de planta. Además, una afirmación amplia de superioridad requeriría hacer explícitos cobertura de fuentes/severidades y presupuesto de desarrollo comparable. Esta auditoría no ha demostrado una desigualdad de ese presupuesto; la identifica como dato necesario para interpretar el contraste, no como sesgo confirmado.

Chen es una referencia publicada válida, pero su prueba común es la primera apertura persistente de línea; no cubre carga ni restauración: [protocolo, líneas 24–26](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/narrative_protocol.tex:24). El artículo original modela fluctuaciones de generación/demanda y cambios en ángulos para detectar e identificar aperturas: [texto de los autores](https://aledan.ece.illinois.edu/files/2017/04/TPWRS_2016_b.pdf). Rovatsos incorpora dinámica transitoria, por lo que no es sostenible contraponer «métodos físicos anteriores estáticos» a «P07 dinámico»: [texto de los autores, 2017](https://aledan.ece.illinois.edu/files/2017/04/TSP_2017.pdf). P07 no incurre actualmente en esa simplificación.

**Consecuencia:** falta el competidor físico sencillo adecuado al mismo problema continuo. No hace falta ejecutar todo el catálogo bibliográfico ni reentrenar los ExtraTrees con datos de confirmación. La ausencia de ese contraste pesa más que añadir otra tabla de capacidades.

### P2 — X02 demuestra un efecto sobre amplitud; su éxito de fuente tiene una explicación mucho más simple

**Categoría: resultado confirmado con alcance limitado; no defecto oculto.**

La tabla actual es decisiva: nominal tiene 114/240 decisiones conjuntas correctas y 12/15 selecciones de evento en ventanas normales; recentering y conditioning tienen ambos 240/240 y 0/15. El término mixto cambia la mediana de error de severidad de 1.2% a 0.329% y el error de respuesta de 1.25% a 0.0561%: [tabla X02](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/tables/generated/ei_x02_results.tex:1).

La explicación rival más simple del éxito de localización es **corregir el offset**. X02 no la derrota: la variante que solamente recentra ya alcanza el techo. El término mixto sí mejora la fidelidad y la severidad en ese experimento. La mejora no puede despreciarse como falsa ni atribuirse a una referencia privilegiada: ambos métodos corregidos comparten prefijo y offset, como especifica [X02, líneas 28–35](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_ei_x02.tex:28).

Con familia y ON/OFF suministrados, cuatro fuentes, un contexto escalar y ruido común, la pregunta operacional permanece abierta. Para hacer central este componente sería necesario un resultado donde cambie decisiones fuera del techo, o justificar que reducir el sesgo de severidad es el objetivo final. El resumen actual describe correctamente el resultado y no afirma una mejora de localización: [resumen, líneas 42–46](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/main.tex:42).

### P2 — X04 contradice una narrativa de «recuperación como nueva información» y favorece una narrativa de consistencia

**Categoría: control negativo confirmado; no refutación del uso de un predictor continuo.**

X04 reporta razón mediana de separación 1.0006 con historia conocida, 0.8532 al incorporar una dirección de incertidumbre de severidad anterior y precisión binaria media idéntica de 98.35%: [X04, líneas 36–48](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_recovery_x04.tex:36). La nueva información no aparece en estas comparaciones. El artículo conserva expresamente esta conclusión negativa.

El control también tiene límites que impiden convertirlo en una refutación general: solamente cuatro historias y doce celdas correlacionadas; familia, inicio, trayectoria previa y par de fuentes suministrados; horizonte fijo; precisión próxima al techo. Además, la geometría perfila amplitudes no negativas y el experimento de clasificación integra amplitudes firmadas. El manuscrito declara esa diferencia, así que no corresponde acusarlo de afirmar una cota de error que no afirma.

Añadir covarianza de nuisance reduce precisión a firmas fijas por construcción; la reducción no prueba un fallo descubierto del estimador. Lo informativo para el argumento central es la escasa modificación de la geometría física y la ausencia de ganancia observada en la clasificación. X04 debe mantenerse como límite de la tesis, no emplearse como evidencia indirecta de que R11 mejora.

### P2 — La exposición normal de H04 y su número de padres no sostienen una afirmación operacional fuerte

**Categoría: limitación de evidencia confirmada y reconocida.**

H04 tiene tres padres con eventos y un padre normal, repetidos en tres condiciones; la tabla declara solamente 204 s normales por método. Cero alarmas en esa exposición no demuestra una tasa baja a escala de horas. Como ilustración, incluso suponiendo un proceso de Poisson homogéneo, cero observaciones en 204 s deja un límite unilateral de 95% de aproximadamente 52.9 alarmas/h, obtenido de `-log(0.05)/(204/3600)`. Este cálculo no es un intervalo válido para el diseño real sin justificar ese modelo; su propósito es mostrar la debilidad de la exposición, no estimar la tasa del algoritmo.

C01 está diseñado para ampliar evidencia y agrupar por padre; sus resultados permanecen fuera de esta revisión. Más realizaciones instrumentales de los mismos padres no sustituyen diversidad de trayectorias.

### P2 — Transferencia a RAW0001: el riesgo dominante es estructural, no el porcentaje 70/30

**Categoría: límite reconocido de validez externa; desempeño futuro desconocido.**

El generador y el predictor comparten planta, ley de carga, operador de medida y familia física. Usar integración no lineal para generar datos y predictores locales para inferir evita una equivalencia trivial entre verdad y predictor, pero no demuestra transferencia fuera de esa familia de modelos. Perturbar R/X tampoco prueba robustez a errores de terminal, de ley de carga, de regulación o de instrumentación.

El contrato F01 documenta diferencias de amplitud, historia previa incompleta frente a RAW0001, CT no confirmado, BUS39 parcial y dependencias instrumentales no reproducidas: [contrato F01, líneas 60–85](C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD/SIM0001_JuliaPD_F01/START_HERE.md:60). El artículo conserva estos límites: [discusión, líneas 36–48](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_interpretation.tex:36).

Por ello, no es honesto pronosticar una mejora numérica de hackathon a partir de H04, X02 o X04. Tampoco hay evidencia para pronosticar fracaso inevitable. El método tiene un mecanismo útil y probado dentro de su contrato; la magnitud de su transferencia sigue sin medirse.

## Las pruebas mínimas que decidirían el argumento

Estas son propuestas para un sucesor, no instrucciones de modificar R11, F01 o C01 ni experimentos ejecutados en esta auditoría.

1. **Prueba principal: banco frente a estado propagado sencillo.** Comparar R11 y un predictor con estado físico/instrumental retenido pero sin el mismo banco largo de historias, usando el mismo modelo nominal, catálogo, canales, prefijo, oportunidades de proponer eventos y reglas de publicación. El rival puede usar evidencia o un GLR de amplitud y un modo topológico explícito para líneas. Ajustar las decisiones solamente en desarrollo; evaluar padres nuevos pareados con recuperación sola, evento aislado y evento durante recuperación. Informar atribución antes de OFF, extras durante recuperación, omisiones y coste. Si el rival iguala a R11 dentro de un margen práctico prespecificado y cuesta menos, la tesis debe reducirse a la necesidad de propagar estado, no a la superioridad del banco. Un tercer brazo que reinicie a equilibrio sirve como control de consistencia, pero no como único adversario.

2. **Prueba secundaria: separar red y publicación.** Comparar una y cinco redes con idéntica publicación y admisión. Mantener ambos procedimientos congelados existentes como referencias externas al contraste. Esto responde a si la mezcla aporta algo; la comparación publicada de 53/54 con cuatro extras frente a 54/54 con siete no lo identifica. Elegir el criterio de utilidad antes de mirar resultados: sin valorar alarmas y omisiones no existe un ganador escalar.

3. **Prueba de transferencia: distinguir interpolación SIM y replay RAW.** Si se decide un 70/30, dividir por padres físicos antes de crear ventanas o réplicas de ruido y congelar toda selección de modelo, calibración y umbrales con el 70%; el 30% no se usa para retocar. R11 no tiene una cabeza supervisada de etiquetas, por lo que «entrenar el 70%» debe definir exactamente qué se estima. Conservar los ExtraTrees ya entrenados en SIM como referencias y declarar la cobertura y el presupuesto de desarrollo de cualquier nuevo baseline. Después, un replay causal de RAW0001 sin nuevos ajustes puede medir compatibilidad retrospectiva, pero no convertirse en evaluación externa independiente: RAW0001 ya influyó en F01. Mantener RAW0002 cerrado.

Antes de invertir en una campaña grande, la primera prueba es la más informativa. Para sostener una afirmación de beneficio de f/ROCOF o de robustez instrumental, añadir posteriormente una ablación de canales pareada; la dependencia entre fase, frecuencia y ROCOF no está completamente reproducida por F01. Para defender X02 como contribución central a localización, llevar recentering y conditioning a casos que no estén saturados, conservando su contrato común; no hace falta repetir su victoria de amplitud con más réplicas casi idénticas.

Como competidor adicional para cargas, existe una ruta de estimación conjunta de estado inicial y entradas escasas mediante group LASSO: [Anguluri, Sankar y Kosut, versión de autores en arXiv](https://arxiv.org/abs/2201.07907). No es un reemplazo automático para la conmutación de líneas ni una implementación exigible antes del contraste sencillo anterior.

## Qué pesa más de lo que aporta al argumento actual

| Material actual | Juicio adversarial | Tratamiento propuesto, sin editarlo ahora |
|---|---|---|
| X02, sección completa con dos figuras a dos columnas | Resultado limpio de severidad, pero pregunta distinta y sin ganancia de fuente | Mantener un resultado compacto y su límite; trasladar las trazas ilustrativas al suplemento si la tesis continúa siendo recuperación |
| X04, figura completa | Control negativo pertinente al título | Conservar el resultado negativo y el contraste conocido/incierto; no expandirlo como una segunda contribución positiva |
| Descomposición de `ΔM` | Ayuda a explicar BUS31; es identidad contable | Una ecuación y una interpretación bastan; no darle peso equivalente al algoritmo |
| Matriz bibliográfica extensa del suplemento | Mucha capacidad «no probada» no identifica el rival decisivo | Reducirla a contratos realmente próximos y precisar qué baseline falta |
| Teoría de reconstrucción, conos, contacto de orden superior, cotas y otros resultados antiguos | No valida el banco R11 actual; el suplemento ya distingue contratos | Separar un archivo histórico claramente opcional del suplemento necesario para reproducir el artículo |
| Estimador conjunto `E_J` propuesto y piloto de septiembre basado parcialmente en dossiers | Añade otra arquitectura y resultados no auditables desde este checkout, sin cerrar la tesis actual | Sacarlo del recorrido obligatorio del lector; conservarlo como archivo de investigación con procedencia |
| Figura de señales por todas las PMU | Puede ilustrar la tarea, pero se solapa con arquitectura, secuencia y controles | Evaluar si el panel detallado pertenece al suplemento |

Las ubicaciones comprobadas son [entradas del suplemento, líneas 174–258](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/supplement.tex:174), [teoría, líneas 1177–1235](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/supplement/appendix_d_theory.tex:1177), [estimador conjunto propuesto, línea 341](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/supplement/appendix_e_estimator.tex:341) y [procedencia del piloto, líneas 1–4](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/supplement/appendix_f_single_event_pilot.tex:1). Esta recomendación afecta a la organización editorial; no invita a borrar evidencia adversa. Las figuras protegidas de eventos y unifilar deben conservarse conforme a `AGENTS.md`.

## Qué sobrevive al ataque

- La distinción física entre OFF y recuperación es correcta y operacionalmente pertinente.
- El orden de predecir, puntuar y corregir, la sustitución de sufijos y la separación entre tiempo estimado de inicio y tiempo de emisión son una especificación útil y revisable. Esta lectura no constituye una auditoría completa del código que la ejecuta.
- Reportar atribución antes de OFF, extras y cierres evita que una localización tardía parezca un éxito operacional.
- X02 aísla de manera razonable el término de contexto respecto al offset y muestra un beneficio de severidad bajo el contrato declarado.
- X04, el fallo BUS31 y la pérdida BUS16 por admisión más estricta son evidencia negativa que hace más creíble el artículo.
- Las advertencias sobre masas no calibradas, publicación distinta, pocos padres, fuente conocida frente a fuente excluida, CT provisional y RAW0001 retrospectivo son claras. No corresponde revisarlo como si aún afirmara recuperación universal, posterior exacto, todo el hackathon o tiempo real.

## Expectativa honesta para SIM 70/30 → RAW0001 → hackathon

**Dentro de SIM:** es plausible que un método que conoce operadores y catálogo funcione bien; H04 respalda esa posibilidad para cargas/líneas concretas. Un split por padres comprobaría generalización dentro de la distribución generada, no validaría la planta respecto a RAW.

**En RAW0001:** cabe una prueba retrospectiva útil de detección, atribución y persistencia de recuperación. Las discrepancias de estado previo y medición pueden destruir una firma precisa aunque el clasificador SIM tenga una cifra alta. El resultado de ese replay no se puede anticipar con un porcentaje defendible y no sería independiente de la calibración histórica.

**En el hackathon:** R11 actual no cubre fallas, generación e integridad, ni acredita por este solo hecho el contrato completo de la competición. La mejor perspectiva justificable hoy es que podría aportar un componente físico para cargas/líneas dentro de un sistema más amplio. No hay una base científica para afirmar que reemplazará o superará la solución completa. El plan más corto hacia evidencia convincente es demostrar primero que la complejidad extra vence al predictor de estado sencillo en la tarea que sí cubre.

## Fuentes primarias verificadas y límites de consulta

| Fuente | Qué se verificó | URL primaria |
|---|---|---|
| Blom y Bar-Shalom, 1988 | Gestión/mezcla de hipótesis e IMM; ficha y resumen IEEE | https://ieeexplore.ieee.org/document/1299/ |
| Boers y Driessen, 2005 | Historias de modos, filtros condicionados, poda/mezcla y adaptación del número de hipótesis; texto del editor | https://www.sciencedirect.com/science/article/pii/S0005109804003243 |
| Warner, Hamilton, Fellouris y Aliprantis, 2023 | Preprint v1: modelos dinámicos, PMU escasas y diagnóstico de falla de línea; documento primario indexado con portada TechRxiv | https://doi.org/10.36227/techrxiv.23264519.v1 |
| Chen y colaboradores, 2016 | QCD de aperturas mediante fluctuaciones y ángulos; PDF de autores | https://aledan.ece.illinois.edu/files/2017/04/TPWRS_2016_b.pdf |
| Rovatsos y colaboradores, 2017 | Extensión de detección de aperturas con dinámica transitoria; PDF de autores | https://aledan.ece.illinois.edu/files/2017/04/TSP_2017.pdf |
| Nagi, Huan y Chen, 2022 | Sensibilidades DAE, aproximación local y evidencia/posterior analíticos; resumen IEEE y versión de autores | https://ieeexplore.ieee.org/document/9512471/ |
| Anguluri, Sankar y Kosut | Estado inicial desconocido e inputs escasos, group LASSO y simulaciones de red; preprint de autores | https://arxiv.org/abs/2201.07907 |

Consulta web realizada para esta auditoría. El acceso directo al DOI de Warner y después a su PDF devolvió error; el buscador sí devolvió el documento primario con portada, fecha, autores, DOI y resumen. No se certifica una revisión de todo su texto ni se infiere una publicación posterior. Tampoco se reclama una búsqueda exhaustiva capaz de demostrar ausencia mundial de antecedentes.
