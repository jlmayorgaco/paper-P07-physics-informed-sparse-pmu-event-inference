# Revisor 3 — claridad, lectura experta y utilidad operativa

Fecha: 2 de noviembre de 2026. Revisión independiente del manuscrito actual de 16 páginas. Se leyeron el texto extraído completo, `main.tex`, las fuentes principales del método, introducción, protocolo y estado de la ablación; se inspeccionaron visualmente las páginas 2, 5 y 10–13. No se consultaron informes de revisión anteriores. No se modificaron manuscrito, experimentos, figuras ni datos. Esta evaluación no verifica implementación ni referencias externas.

## Dictamen

**Revisión mayor de presentación y delimitación antes del envío; no rechazo del resultado principal.** Un lector de sistemas eléctricos puede entender el problema y la idea: comparar intervenciones posibles con la respuesta todavía presente de sucesos anteriores, usando un modelo eléctrico y conservando estados después de OFF. Las ecuaciones de reducción, las masas activa/causal y el ejemplo de seis eventos sostienen esa explicación. El resultado defendible es una mejora de cobertura oportuna de cargas para un catálogo y simulador declarados, acompañada de más alarmas ante error de red. No equivale a superioridad general en clasificación, despliegue operativo ni probabilidades calibradas.

Los bloqueos que identifico son corregibles con delimitación y organización de material existente. No exijo otro simulador, otra arquitectura aprendida ni experimentos nuevos como condición automática de publicación. Si se mantiene una afirmación causal sobre el beneficio individual de Bayes o de la memoria, sí haría falta evidencia correspondiente; el texto actual puede evitar esa obligación conservando su afirmación de procedimiento completo.

## Fortalezas verificables

- **Problema comprensible y relevante.** La introducción, p. 1, explica por qué una fuente no instrumentada afecta varias PMU y por qué OFF no suprime la dinámica. No comienza con una lista genérica de tecnologías.
- **Separación física/estadística razonable.** Secciones III–IV, pp. 3–7: distingue simulador no lineal de predictores locales, corriente terminal de inyección nodal, frecuencia de barra de velocidad de rotor, y filtrado instrumental de discrepancia latente. Evita varios atajos físicamente engañosos.
- **Trazabilidad temporal clara.** Figura 1, p. 2, y Algoritmo 1, p. 7: guardan densidad predictiva antes de corregir, reemplazan el sufijo reproducido y registran el último reporte utilizado. La distinción entre causalidad de reportes y velocidad de cómputo es explícita.
- **Honestidad sobre la evidencia.** Pp. 8–9 reconocen el prior efectivo incorrecto en un archivo histórico; pp. 9–11 separan unidades, cohortes y condiciones de los comparadores; p. 14 reconoce familia de ecuaciones compartida, terminal provisional y rechazo de RAW0001. Estas limitaciones deben preservarse, aunque se consoliden para mejorar lectura.
- **Figuras con una historia física.** Figura 4, p. 7, muestra persistencia después de OFF; Figura 8, p. 12, muestra un fallo concreto con masa tardía; Figuras 9–10, p. 13, presentan beneficio y costo de alarma juntos. Son más informativas que una sola exactitud agregada.
- **Las figuras protegidas cumplen funciones distintas.** Figura 2, p. 4, introduce fenómenos más amplios con alcance claramente acotado en III; Figura 3, p. 5, ubica PMU y activos candidatos. Conservar ambas, y conservar byte por byte la imagen de eventos. El unifilar no debe sustituirse por un grafo.

## Hallazgos prioritarios

### P1 — Cerrar el estado editorial del estudio de componentes antes del envío

**Evidencia:** p. 2, Introducción, anuncia que un estudio posterior «separates» los componentes; sección IX, pp. 11–12, dedica ecuaciones (19)–(20) y protocolo a ese estudio; IX-A dice «The component study is in progress. No component-effect result is claimed in this draft». La conclusión, p. 14, vuelve a «The controlled component study addresses…».

**Problema:** el lector recibe un artículo aparentemente terminado que incluye una investigación abierta en la misma jerarquía que resultados ejecutados. La frase de ejecución evita una fabricación de resultados, pero no elimina la ambigüedad sobre qué contribución está disponible para revisión. No considero que la ausencia de ablación invalide por sí sola la comparación completa, ya correctamente acotada.

**Remedio mínimo:** escoger un estado inequívoco. Si el estudio sigue pendiente, identificarlo como protocolo propuesto/trabajo futuro en todas sus apariciones y compactarlo o remitirlo al suplemento; la conclusión debe referirse al diseño, no sugerir un mecanismo ya establecido. Si termina, actualizar de forma coherente con sus resultados reales. No completar la sección con resultados anticipados.

### P1 — Hacer que el titular describa cobertura oportuna y el comparador concreto

**Evidencia:** VIII, pp. 10–11, informa que todas las diagnosis emparejadas emitidas antes de OFF son correctas en los cuatro métodos; las diferencias provienen de diagnosis ausentes o tardías. VI-A, p. 9, registra 0/72 y 4/72 atribuciones oportunas de carga ya en validación de desarrollo y reconoce que no son clasificadores de carga optimizados. Tabla 4, p. 10, resume su limitación con «May miss load sources absent from its learned feature boundaries».

**Problema:** la gran diferencia 644/648 frente a 330/648 puede leerse como precisión clasificatoria superior, aunque el manuscrito revela después que se trata de cobertura temporal. Además, la frase de Tabla 4 sugiere una explicación de las fronteras aprendidas que no se demuestra con el conteo. Este riesgo importa más que cualquier adjetivo promocional.

**Remedio mínimo:** trasladar al resumen o a la formulación inicial del resultado la distinción «más sucesos reciben una diagnosis correcta antes de OFF»; mantener el comparador congelado explícito. En Tabla 4 usar la limitación observada —baja cobertura oportuna de cargas bajo esta configuración— en vez de atribuir una causa no identificada. Conservar la advertencia de puntos de alarma distintos. No afirmar que el banco mejora precisión condicional, toda clasificación aprendida o latencia.

### P1 — Completar el puente entre evidencia de historia, pesos y decisión

**Evidencia:** IV-C, p. 6, define `L_h,k` en (11); IV-D define `w_l,k` en (12); IV-E introduce `pi_l,h,k` directamente en (14). Algoritmo 1, p. 7, agrupa puntuación, corrección, actualización y poda en su paso 3. IV-F remite al suplemento el filtro de fuentes, regla temprana de líneas y reemplazo de episodios.

**Problema:** se entiende el flujo general, pero el lector del artículo principal no puede seguir cómo una likelihood se convierte en la masa que cruza 0.99. El vínculo más directamente relacionado con el título bayesiano queda implícito. No es una acusación de error matemático ni de falta de reproducibilidad del suplemento, que esta revisión no examinó.

**Remedio mínimo:** insertar una definición compacta de la actualización de masa de historia, indicando prior/hazard, normalización, hipótesis nula y qué cambia al reproducir un sufijo; apuntar a la ecuación exacta del suplemento. En el algoritmo separar predict–score–correct–normalize/prune y señalar dónde se evalúa cierre. No hace falta duplicar toda la implementación. Aclarar también el borde 0–18 de IV-C/Figura 1 frente a «latest 18 reports» del paso 2: decidir si son 19 lags incluyendo cero y emplear una convención única.

### P2 — Dar una ficha operativa mínima del dominio evaluado

**Evidencia:** III, p. 3, da 47 canales, 30 reportes/s, 300 reportes de calibración y warmup de 12 s; IV-F, p. 6, da persistencias de 6 y 15 reportes; VI, p. 9, presenta número de padres, perturbaciones y ruido, pero remite calendarios completos al suplemento. X-E, p. 14, reúne las exclusiones operativas. Figura 10, p. 13, muestra diferencias de alarmas por hora, mientras Tabla 5 informa conteos.

**Problema:** para valorar utilidad un ingeniero necesita saber cuánto duran y cuán grandes son las perturbaciones evaluadas, qué representa exactamente ruido ×1 y ×2, y cuánta exposición produjo las alarmas. «Antes de OFF» depende directamente de duración y severidad. Una diferencia de tasas entre métodos no ofrece por sí sola la carga absoluta de atención del método propuesto.

**Remedio mínimo:** añadir al protocolo una ficha compacta con rangos ya archivados de severidad/duración, ruido nominal en unidades o referencia precisa, magnitud del R/X fuera del banco y duración/exposición monitorizada de los eventos. Presentar tasa absoluta de extras del banco junto al conteo o referencia directa al cuadro suplementario. No inferir estos números de figuras ni producir una nueva campaña. Expresar 6 y 15 reportes como 0.2 y 0.5 s, aclarando que son persistencias, no garantías de latencia total.

### P2 — Reducir la competencia entre la contribución central y archivos históricos

**Evidencia:** V, pp. 7–9, incluye reconstrucción, características, interacciones y cardinalidad con prior efectivo distinto; VI-A introduce varios entrenamientos; VII, pp. 10–11, añade transferencia histórica, secuencia y comparador físico anterior. El resultado sellado empieza al final de p. 10; sus gráficos principales aparecen en p. 13, dentro de la discusión.

**Problema:** el lector debe mantener demasiados estimadores y cohortes antes de ver el desenlace principal. Las advertencias son correctas, pero su repetición no reemplaza una jerarquía narrativa. El artículo se aproxima a un registro de campañas, aunque el resultado central sí tiene una pregunta unificadora.

**Remedio mínimo:** abrir los resultados con la comparación principal y su costo; reunir los antecedentes en una subsección de evidencia auxiliar con el mapa de Tabla 4. Mantener los resultados adversos y el prior incorrecto visibles donde corresponda, sin mezclarlos con el estimador final. Acercar Figuras 9–10 a VIII y Figura 8 a VII-B mediante ajuste de flotantes. No eliminar las figuras protegidas ni su contexto.

## Claridad de ecuaciones, algoritmo y figuras

- **Ecuaciones (7)–(10), pp. 5–6:** la cadena DAE → reducción → observación → predictor se puede seguir. Conviene una frase que indique cuáles objetos se precomputan por modo y cuáles se actualizan por reporte; facilita juzgar la carga operativa sin prometer tiempo real.
- **Ecuaciones (14)–(15), p. 6:** la diferencia entre actividad y causa resulta útil, y el texto reconoce que la causa no es un archivo permanente. Mostrar en el ejemplo existente una frase del tipo «puede terminar la actividad mientras la historia sigue explicando la recuperación» basta; no se necesita otro formalismo. `Delta M` tiene interpretación, pero no se muestra qué decisión depende de él: señalar explícitamente si solo se registra/visualiza.
- **Ecuación (20), p. 12:** la reconstrucción `b_k = mu_k/v_k` requiere el supuesto correspondiente sobre el término lineal del prior; si es prior de media cero, declararlo junto a la fórmula. Solicito claridad de la condición, no concluyo que el código sea incorrecto.
- **Figura 1, p. 2:** bien segmentada, flechas y etapas legibles al tamaño revisado. La lectura serpenteante 1–8 se sigue gracias a numeración. Es densa, pero no necesita otro rediseño general. Debe concordar exactamente con el algoritmo sobre actualización y cierre.
- **Figura 3, p. 5:** el unifilar conserva sentido eléctrico y cabe en una columna; etiquetas son pequeñas pero identificables en la imagen revisada. El texto «All routes are orthogonal» describe una elección de dibujo sin beneficio científico: comentario cosmético, no bloqueo. No redibujar conexiones ni retirar equipos/PMU.
- **Figura 8, p. 12:** el detalle de bus 31 es la explicación más inmediata del fallo. La posición actual la separa dos páginas de su primera discusión; acercarla beneficia más que añadir nuevos colores o paneles.
- **Figura 9, p. 13:** comunica el beneficio de cargas y costo fuera del banco con claridad. El panel B usa líneas entre categorías nominales; no es error, pero puntos agrupados evitarían sugerir una escala continua de R/X. Opcional y cosmético.
- **Figura 10, p. 13:** intervalos y estratos legibles; la advertencia de población finita está presente. El eje derecho ofrece diferencias, no el volumen total de alarmas: complementar la lectura con tasas absolutas existentes, no sustituir esta figura.
- **Página 16:** una biografía sola añade una página; revisar composición si la revista impone extensión. No afecta validez ni prioridad científica.

## Escritura y tono

No observo un problema dominante de lenguaje promocional. Son valiosas las frases concretas sobre respuesta remanente y las cifras con sus denominadores. La principal carga de estilo es una secuencia repetida de negaciones correctivas: «not a new Bayes rule» (p. 8), «not a new tensor factorization» (p. 6), «does not require a tensor… library» (p. 8), junto con múltiples listas de lo que cada resultado no demuestra. Parecen responder a controversias previas que el lector nuevo no conoce.

Recomiendo conservar las delimitaciones sustantivas —sin calibración, sin garantía de tiempo real, sin generalización externa, cohortes separadas— y condensar las aclaraciones defensivas de novedad en un párrafo de alcance. Repetir nombres técnicos definidos es preferible a introducir más sinónimos de banco/estimador/ruta. Aclarar una vez que «causal» significa uso de reportes disponibles, mientras «attribution» es selección entre hipótesis del modelo; no es identificación causal general del sistema real.

Este juicio se refiere exclusivamente a legibilidad y precisión. El estilo no permite atribuir autoría humana o automática, y no hago esa inferencia.

## Condición mínima de salida

Antes del envío: resolver el estado de IX; hacer inequívoco el significado de la ventaja y su comparador; enlazar likelihood y masas; y permitir evaluar el endpoint temporal con severidad, duración y exposición existentes. Después, mejorar ubicación de figuras y compactar reiteraciones. El manuscrito no necesita sacrificar Figura 2 ni el IEEE-39, ni ocultar resultados negativos, ni prometer experimentos de moda para sostener su contribución acotada.
