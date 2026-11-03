# Dictamen editorial independiente — versión actual, 2 de noviembre de 2026

**Recomendación simulada: REJECT, updates required before resubmission.** El trabajo tiene mérito y encaja temáticamente en IEEE Access, pero el manuscrito actual no está listo para aceptación. No es un rechazo de la idea ni una predicción de la decisión de la revista. No asigno puntuaciones ni probabilidades de aceptación.

Revisión de lectura solamente: `main.pdf` (16 páginas), fuentes incluidas del artículo y material pertinente de `supplement.pdf` (15 páginas). Las referencias de página corresponden a esos PDF; las líneas a los archivos `.tex` actuales. No consulté informes previos ni otros dictámenes; no ejecuté experimentos, inspeccioné resultados parciales de A01, modifiqué figuras o abrí RAW0002. Se respetaron los AGENTS.md aplicables. Apliqué la perspectiva editorial de la habilidad `academic-paper-reviewer`; no afirmo haber hecho una auditoría independiente completa del código o de todas las referencias.

La revista utiliza decisiones binarias y reserva aceptación para trabajos publicables con ajustes menores; admite rechazo con actualizaciones antes de una nueva presentación. Sus criterios no exigen una novedad excepcional, pero sí una contribución diferenciada, solidez técnica y conclusiones respaldadas. Son los criterios pertinentes aquí, no una exigencia inventada de nuevos teoremas o de múltiples redes. [IEEE Access, Reviewer Guidelines, consultado el 2 de noviembre de 2026](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/).

## Una contribución central que sí se puede defender

**Un procedimiento reproducible de atribución secuencial de eventos de carga y línea, con PMU escasas, que compara intervenciones nuevas con trayectorias de recuperación retenidas y distingue actividad de procedencia; su evaluación caracteriza cobertura oportuna y costo de alarmas dentro de un catálogo simulado definido.**

Ese enunciado conecta la pregunta de la introducción con el método y el experimento principal. La introducción pregunta si la recuperación explica una nueva variación o debe ceder a una intervención posterior (`sections/article_intro.tex`, líneas 27–41; PDF pp. 1–2). El método especifica inicio desde estados anteriores, memoria física e instrumental y masas de actividad/origen (`sections/article_method.tex`, líneas 111–142 y 164–205). La evaluación muestra 644/648 decisiones oportunas y 72 extras; ExtraTrees, 330/648 y 29; el modelo nominal, 643/648 y 92. La alternativa ExtraTrees de ventana corta alcanza 352/648 y 16 (`sections/08c_c01_confirmatory.tex`, líneas 4–28; tabla 5, p. 11).

La significancia está en resolver más intervenciones de carga antes de su restauración y mostrar cuándo aparece el costo de falsas alarmas. No está demostrada una ventaja general de exactitud de clasificación: la auditoría afirma que todos los diagnósticos emparejados emitidos antes de OFF son correctos para los cuatro procedimientos; las diferencias son omisiones o retrasos (mismo archivo, líneas 40–57; suplemento, figura 5, p. 13). Esta distinción es material para el mensaje editorial.

## Fortalezas que deben mantenerse

1. **Separación honesta de los contratos experimentales.** El artículo no suma las realizaciones correlacionadas como eventos independientes: 648 realizaciones corresponden a 108 intervenciones y 18 padres continuos. Los intervalos usan padres físicos. El hackathon, el desarrollo, la comparación causal y los controles conocidos de antemano están diferenciados (`sections/narrative_protocol.tex`, líneas 14–21, 56–63, 96–105; suplemento, apéndice C, p. 4).
2. **Resultados desfavorables visibles.** Declara el mayor costo fuera del banco, ausencia de ventaja general de latencia, rechazo del registro RAW0001 por el prefijo y limitación del productor compartido. No presenta la falla de admisión como una prueba exitosa de transferencia (`sections/08c_c01_confirmatory.tex`, líneas 49–57; `sections/article_interpretation.tex`, líneas 44–82; PDF pp. 13–14).
3. **La matemática deja de inflar la novedad.** Reconoce que la integral local es exacta solamente bajo su modelo condicional, que el banco completo es aproximado, que la descomposición de ΔM es una identidad y que un arreglo tensorial no produce por sí solo una ventaja (`sections/article_method.tex`, líneas 129–137, 195–205; `sections/article_evidence_bridge.tex`, líneas 85–107). Esa precisión favorece una contribución de ingeniería verificable.

## Problemas mayores y forma concreta de resolverlos

### E1. El manuscrito se presenta todavía como un estudio en ejecución

**Evidencia:** sección IX.A, p. 12, y apéndice M del suplemento, p. 15: el estudio factorial está en progreso y no hay resultados de efecto de componentes. Las fuentes son `sections/article_controlled_ablation.tex`, líneas 1–3, y `supplement/ablation_a01.tex`, líneas 1–4. La introducción lo anticipa y la conclusión lo menciona (`article_intro.tex`, líneas 62–65; `article_final_conclusion.tex`, líneas 33–38).

**Implicación:** no equivale a datos inventados; el estado pendiente está correctamente declarado. Sin embargo, una sección metodológica dedicada a una prueba aún sin desenlace hace que esta versión sea un borrador, y deja abierta la pregunta que motiva buena parte de su complejidad. No cabe resolverlo con una corrección menor de estilo.

**Cambio necesario:** elegir una versión científica cerrada. Si A01 se incorpora, debe incluir las cuatro ramas y todos los registros previstos, fallos y denominadores incluidos, con resultados favorables o nulos y carácter posthoc explícito. Si no se incorpora, debe salir del cuerpo de resultados como trabajo pendiente, y la contribución debe limitarse al procedimiento completo y su comportamiento. Esto no autoriza detener, retocar o seleccionar resultados de la corrida en curso.

### E2. El contraste principal no demuestra que la complejidad específica sea necesaria

**Evidencia:** los clasificadores causales ya tenían 0/72 y 4/72 atribuciones oportunas de carga en validación de desarrollo; el texto admite que no representan clasificadores optimizados con éxito para cargas (`sections/narrative_protocol.tex`, líneas 46–54; p. 9). El modelo nominal cambia también reglas de publicación, por lo que no aísla promediado de modelos (líneas 80–86). Existe un GLR físico más simple, pero solo en desarrollo: 37/54 con 37 extras, frente a 51/54 y 3 del banco de cinco modelos (suplemento, tabla 1, p. 7; `sections/narrative_results.tex`, líneas 39–49).

**Implicación:** la gran brecha frente a ExtraTrees es válida para esos artefactos congelados, pero un comparador conocido como débil para cargas no permite atribuir la brecha a Bayes, memoria o manejo de hipótesis. Tampoco la comparación nominal/mezcla demuestra una ganancia causal del banco de redes. No acuso fuga al conjunto confirmatorio: la dependencia interna de controles normales está declarada y no es prueba de fuga a C01.

**Cambio necesario para sostener una contribución metodológica fuerte:** un contraste estrecho que ataque la decisión nueva, conservando observaciones y reglas pertinentes. El factorial previsto puede aportar parte de esa evidencia, pero solo estudia puntuación de amplitud y estado físico al cierre inferido; no elimina toda memoria ni todo cálculo bayesiano (`sections/article_ablation_design.tex`, líneas 4–11, 27–43). Alternativamente, un comparador físico sencillo en una evaluación independiente puede establecer el valor de la complejidad. No es necesario ejecutar ambos ni exigir una colección indiscriminada de modelos modernos. Para una contribución más limitada de sistema, se debe explicar expresamente que el resultado compara procedimientos completos y no demuestra necesidad de los componentes.

### E3. La diferenciación frente al antecedente más próximo sigue siendo más descriptiva que demostrativa

**Evidencia:** Related Work reconoce bibliotecas de trayectorias, búsqueda de inicio y filtros multihipótesis; Warner no se ejecuta en la cohorte (`sections/article_related.tex`, líneas 16–24 y 34–55; pp. 2–4). La discusión repite que la novedad reivindicada es la competencia entre nuevas intervenciones y recuperación retenida (`sections/article_interpretation.tex`, líneas 24–34; p. 14).

**Implicación:** hay una diferenciación plausible de tarea y de procedimiento, suficiente para merecer evaluación, pero la tabla de capacidades no establece por sí sola una innovación algorítmica frente a filtros que ya retienen historias. No se puede concluir que no exista novedad; tampoco certificar prioridad a partir de esta lectura.

**Cambio necesario:** delimitar en una comparación operacional breve qué transición, estado o regla permite resolver el caso de restauración seguido de intervención, qué parte ya existía y qué prueba del artículo evalúa esa diferencia. No hace falta un teorema nuevo ni ejecutar un método de cortocircuitos en un problema incompatible. Si se reclama superioridad sobre ese antecedente, sí haría falta un contraste comparable; el texto actual hace bien en no reclamarla.

### E4. El cuerpo mezcla demasiadas contribuciones secundarias sin dependencia demostrada del estimador final

**Evidencia:** la primera contribución combina reconstrucción de voltaje, características y sensibilidades; la tercera añade transferencia histórica (`sections/article_intro.tex`, líneas 42–55). La sección V afirma que sus cohortes no son ablaciones del estimador continuo; el tensor de segundo orden no se inserta en ese banco (`sections/article_evidence_bridge.tex`, líneas 4–10 y 65–93). Además conserva un estimador histórico con prior efectivo distinto del declarado (líneas 120–128). El resumen y la conclusión vuelven a las ramas históricas (`main.tex`, líneas 41–43 y 52–56; `article_final_conclusion.tex`, líneas 20–31).

**Implicación:** es correcto preservar los resultados y reconocer sus límites, pero el lector recibe varias historias de investigación en paralelo. La evidencia auxiliar no se convierte en respaldo de la contribución central por presentarse junto a ella. El error del prior histórico, aunque transparentado, exige especial cuidado para no usar ese bloque como validación limpia de Bayes.

**Cambio necesario:** jerarquizar la pregunta principal y tratar los demás experimentos como antecedentes o controles explícitamente auxiliares. Reducir su protagonismo en resumen, contribuciones y conclusión; remitir el detalle secundario al suplemento cuando convenga. No borrar resultados incómodos ni las figuras protegidas: la imagen de eventos y el unifilar deben conservarse. Esto es una reorganización de argumento, no una exigencia de nuevos experimentos.

## Evidencia imprescindible frente a evidencia opcional

| Necesaria para esta versión y sus afirmaciones | Condicional u opcional |
|---|---|
| Resolver el estado editorial de A01 sin presentar resultados parciales como finales. | Que A01 produzca una mejora positiva: un resultado nulo también informa. |
| Fijar una contribución central y vincular cada afirmación con su experimento. | Mantener todos los estudios históricos en el cuerpo principal. |
| Respaldar de forma estrecha cualquier ventaja atribuida a memoria o evidencia de amplitud, o retirar esa atribución causal. | Un benchmark amplio de aprendizaje profundo o ejecutar todos los antecedentes citados. |
| Describir el comparador de cargas débil y la diferencia entre cobertura oportuna, exactitud condicional y extras. | Igualar falsas alarmas si solo se comparan puntos congelados; sí sería necesario para afirmar superioridad al mismo costo. |
| Mantener la restricción a un simulador, catálogo y mapa PMU concretos. | Otra red, productores distintos o registros de campo para este alcance restringido; serían necesarios para una afirmación de transferencia general. |
| Mantener masas aproximadas y causalidad de datos como tales. | Calibración probabilística o rendimiento en tiempo real si esas capacidades no se reivindican. |

## Juicio sobre título, resumen y cierre

El título es temáticamente correcto. “Bayesian” describe el uso de evidencia local; no prueba que el algoritmo completo sea un posterior exacto ni que Bayes explique la mejora. El resumen ya comunica el costo de alarmas, el catálogo simulado y las cuestiones abiertas, pero dedica espacio a experimentos periféricos y destaca el ExtraTrees más débil sin dar el total de la variante corta. Incluir el contraste más informativo o justificar la referencia principal mejoraría el equilibrio sin cambiar datos.

La conclusión es prudente: no ofrece calibración, transferencia de campo ni tiempo real. No debe endurecerse artificialmente para sonar más novedosa. Sí debe cerrar la pregunta concreta de cobertura/recuperación y evitar que la mención del estudio en curso parezca un resultado disponible. Su frase sobre un control excluyendo fuentes es una propuesta futura, no evidencia presente.

**Decisión final:** recomendaría rechazo con actualizaciones antes de nueva presentación. El defecto editorial principal es la combinación de un estudio aún abierto con una contribución metodológica cuya ventaja específica permanece poco aislada, agravada por dispersión narrativa. La evidencia existente sí justifica un artículo focalizado sobre el procedimiento y su cobertura/costo dentro del simulador. Una revisión centrada y una respuesta verificable a E1–E3 pueden mejorar sustancialmente su defendibilidad; no garantizan aceptación ni autorizan cambiar los resultados congelados.
