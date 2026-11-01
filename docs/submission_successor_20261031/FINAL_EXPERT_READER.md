# Revisión final como lector experto de P07

Revisión del árbol activo de `main.tex` y del suplemento vigente, 31 de octubre de 2026. No modifica TEX, no consulta informes de otros revisores y no abre resultados parciales de C01. Al revisar, no existen `generated/c01_macros.tex` ni `sections/08c_c01_confirmatory.tex`. Al cerrar esta revisión ya está integrada la adición H04 del SHORT S01 —27/54 oportunos, 0/27 carga, 27/27 línea, tres extras—, junto con la diferencia de publicador y el normal compartido. La revisión incorpora esa actualización. La paginación y apariencia final quedan pendientes del nuevo build.

## Dictamen científico y prueba de treinta segundos

**La tesis ya es defendible como procedimiento físico de atribución y estudio de sus límites. Todavía no es una demostración aislada de que la memoria de recuperación cause la mejora, ni una validación de transferencia física a RAW.** La integración reconoce esas diferencias con bastante precisión. El problema restante es de jerarquía: la evidencia que mejor responde al escéptico aparece tarde, mientras dos experimentos auxiliares conservan una prominencia mayor de la que tienen para el método ejecutado.

Un lector puede resumir el trabajo de manera fiel así:

> Con ocho PMU, un banco de predictores físicos condicionados al estado mantiene la recuperación como explicación alternativa para atribuir intervenciones sucesivas de carga y línea. Un contraste de desarrollo favorece al procedimiento completo frente a un predictor de estado único. La comparación no aísla la memoria y la transferencia física a RAW sigue sin validarse.

El título, las primeras nueve líneas de la introducción y el inicio del resumen transmiten problema y mecanismo. El lector de treinta segundos **no encuentra todavía el contraste nuevo más informativo**: 51/54 con tres extras frente a 37/54 con 37 extras bajo el reloj físico común. En su lugar recibe el contraste original nominal/mezcla y la reducción de error de severidad de X02. Esta selección dirige su atención hacia la pregunta equivocada: parece que la evidencia principal continúa siendo una elección entre dos versiones propias y un ensayo de respuesta con tiempos suministrados.

La prueba de lectura quedaría mejor resuelta si el resumen, la lista de contribuciones y el primer bloque de resultados compartieran esta prioridad: procedimiento → comparación sencilla ejecutada → confirmación independiente cuando esté completa → límite de transferencia. X02 y X04 pueden explicar el resultado sin ocupar el lugar de su prueba principal.

## Cambios prioritarios antes de cerrar la versión de envío

### 1. Identificar inequívocamente cada método y cada política de publicación

**Defecto editorial confirmado; no es una contradicción numérica demostrada.** H04 aparece con dos conjuntos de cifras válidos bajo políticas diferentes:

| Procedimiento | Política archivada original | Reloj físico común sucesor |
|---|---:|---:|
| Banco de cinco modelos | 53/54; cuatro extras | 51/54; tres extras |
| Banco nominal | 54/54; siete extras | 44/54; seis extras |

La diferencia está explicada en el texto, pero el lector debe descubrirla al avanzar entre secciones. Los encabezados de las tablas no nombran con suficiente precisión la versión del procedimiento. Un revisor que encuentre 54/54 y luego 44/54 para «nominal» puede sospechar selección de resultados antes de alcanzar la explicación.

Anclas: [tabla original H04](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/tables/generated/narrative_results.tex), [método, líneas 195–199](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_method.tex), [control sucesor, líneas 13–30](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_submission_checks.tex), [tabla del control](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/tables/generated/single_state_control.tex).

**Acción concreta:** etiquetar cada aparición como política original o publicación física común, y explicar una sola vez qué se vuelve a publicar. Mantener ambos resultados solo si cada uno cumple una función distinta. La tabla común debe ser el contraste principal de simplicidad; la tabla original conserva la trazabilidad de los métodos congelados para C01.

La misma necesidad se aplica a ExtraTrees. «ET short» en la tabla H04 original y «SHORT» en el nuevo entrenamiento agrupado designan artefactos con corpus de fitting distintos. La frase «dos adaptadores congelados» no identifica al tercer artefacto seleccionado en S01. Usar identificadores inequívocos, por ejemplo **ET-R09 BASELINE**, **ET-R09 SHORT** y **ET-S01 SHORT**, con una tabla compacta de corpus, referencia y publicación. No hace falta repetir esos identificadores internos en cada frase de la discusión.

La adición H04 del ET-S01 ya integrada es valiosa porque elimina la comparación entre cohortes como explicación inmediata de su debilidad en carga. Informa 27/54 y tres extras y declara correctamente que **su reloj no es idéntico al control GLR/masa**: comparte seis reportes de persistencia, pero usa argmax sin el umbral de evidencia del control físico. También reconoce el normal compartido. Mantener esas dos precisiones y distinguir el nombre del artefacto; este punto ya no es una adición científica pendiente. Ni siquiera los tres métodos físicos operan a una tasa de falsas alarmas igualada.

### 2. Convertir la comparación sencilla en evidencia central, conservando el alcance de la inferencia

**Brecha causal reconocida, no defecto oculto.** El nuevo competidor mantiene estado físico e instrumental y no se reinicia artificialmente al equilibrio. Esto fortalece mucho el trabajo. La mejora conjunta frente a él —más atribuciones oportunas y menos extras— es un resultado relevante del procedimiento completo.

Sigue siendo posible que integración de severidad, horizonte de alternativas, selección de régimen y calibración de evidencia expliquen parte de la diferencia. El texto lo reconoce expresamente en [article_submission_checks.tex, líneas 24–30](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_submission_checks.tex) y [appendix_single_state.tex, líneas 37–63](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/supplement/appendix_single_state.tex). Compartir `log 99` y seis reportes no iguala un GLR perfilado con unas masas aproximadas.

**Acción concreta:** presentar el resultado como comparación entre procedimientos especificados y congelados. Evitar que el título o una frase de transición lo convierta en «prueba de que la memoria es la causa». Si se desea esa afirmación más fuerte, queda pendiente una ablación con el mismo tratamiento de severidad, búsqueda, régimen y publicación, cambiando solo la retención de historias; una comparación de compromisos alarma/atribución calibrada con controles normales independientes sería más decisiva que otro umbral numéricamente igual. No es necesario ejecutar ese nuevo experimento para sostener el alcance limitado que el texto actual declara.

### 3. Actualizar el mapa experimental y la contribución principal

**Desajuste de organización confirmado.** La tabla de poblaciones en [narrative_protocol.tex, líneas 6–16](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/narrative_protocol.tex) contiene X02 y X04, pero no las nuevas comparaciones de estado único, aprendizaje agrupado y transferencia RAW. Estas aparecen después, bajo una sección larga de controles. La lista de contribuciones todavía destaca X02 como tercera contribución, y el resumen le dedica el único resultado nuevo de componente.

Anclas: [contribuciones, líneas 40–59](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_intro.tex), [resumen, líneas 38–53](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/main.tex), [sección sucesora](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_submission_checks.tex).

**Acción concreta:** añadir las nuevas poblaciones al mapa de evidencia con sus denominadores y naturaleza retrospectiva; situar la comparación sencilla junto a H04; describir agrupación e integridad como verificaciones de alcance del procedimiento. La tercera contribución puede reducirse a una evaluación trazable de atribución, cierre y límites de transferencia, sin presentar cada verificación como otra novedad metodológica.

### 4. Abrir el bloque RAW con el resultado del método físico

**La redacción es honesta, pero la jerarquía puede inducir una lectura demasiado favorable.** La restricción principal está al final: el contrato físico congelado rechaza el prefijo RAW. Por tanto, los resultados posteriores del ZIP y del híbrido no validan la transferencia de R11. El artículo lo dice correctamente en los párrafos del híbrido segmentado y del rechazo del prefijo de [article_submission_checks.tex](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_submission_checks.tex), pero después de varios resultados de disponibilidad y localización.

**Acción concreta:** comenzar ese bloque indicando la no admisión del método físico. Presentar a continuación el replay ZIP y el híbrido como un diagnóstico complementario de transferencia e integridad. Conservar el fallo de reconstrucción del calendario histórico en una frase principal y trasladar su historia documental al suplemento/archivo.

El resultado 1/24 → 2/24 permite afirmar **una corrección emparejada de fuente de línea en este registro**. No respalda una mejora general: la clase permanece correcta en 4/24 ventanas y limita cualquier híbrido que solo cambie fuente a un máximo de 4/24. La carga continúa en 0/11 y la generación en 0/11. Además, la fuente de cada familia procede de un único registro y la tabla no contiene diversidad de localizaciones dentro de cada familia. Su utilidad es comprobar el contrato y localizar fallos, no demostrar generalización espacial.

Precisar que los 179 fallbacks son **179 de las 180 ventanas totales**, mientras 24 es el denominador físico positivo. Su proximidad en el mismo párrafo mezcla dos universos que el lector no debería reconstruir. La [tabla RAW](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/tables/generated/raw_source_hybrid.tex) ya retiene correctamente todos los positivos y no convierte ventanas sostenidas en acciones independientes.

### 5. Cerrar C01 o definir explícitamente un artículo de desarrollo

El texto actual no inventa confirmación: resumen, introducción, protocolo y conclusión dicen que está en progreso. Eso es correcto. Sin embargo, una comparación anunciada como confirmatoria y todavía sin resultado deja abierta una parte central del argumento de envío. C01 podría reforzar o debilitarlo; esta revisión no predice su resultado.

Para la ruta de envío actualmente elegida, el cierre requiere resultados completos, fallos en denominador e intervalos por padre según el contrato. Si el equipo optara por un artículo limitado a desarrollo, debe formularlo explícitamente y dejar de presentar la campaña pendiente como parte de la evidencia del artículo. No deben importarse resultados por la sola existencia de un archivo: las ramas `IfFileExists` de [main.tex](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/main.tex) necesitan el gate de finalización y sello en el importador. En el snapshot revisado los archivos C01 están ausentes; no se observó inclusión parcial.

## Lo que puede quitarse o comprimirse sin perder la ciencia

1. **X02 en el resumen y como contribución autónoma.** La reducción 1.2% → 0.329% es relevante para severidad bajo familia y tiempos suministrados; no mejora la fuente frente a referencia corregida y no cambia R11. Mantener una síntesis de tres o cuatro frases en resultados/discusión y los detalles en el suplemento. [article_signature_summary.tex](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_signature_summary.tex) ya permite esa compactación. La aparición adicional en resumen, introducción y conclusión produce una segunda tesis.
2. **La exposición completa de X04 en el principal.** Conservar visible su resultado negativo: separación prácticamente igual con historia conocida y menor al añadir la incertidumbre considerada. La figura completa, pares, amplitudes, prior firmado y 300 draws pueden pasar al suplemento; una referencia breve mantiene la falsación de «recuperación aporta información universalmente útil». No eliminar el resultado adverso. [article_recovery_x04.tex](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_recovery_x04.tex).
3. **La contabilidad de ΔM como tema independiente.** Una ecuación y su uso para leer el ejemplo tardío bastan. La identidad no debe competir con la comparación sencilla por espacio conceptual; el propio texto reconoce que no es una nueva factorización. [article_method.tex, líneas 174–184](C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference/sections/article_method.tex).
4. **Repeticiones de alcance.** «No all-family», «no calibración», «no real time» y «no superioridad sobre procedimientos no ejecutados» aparecen reiteradamente. Mantenerlas en el resumen, una tabla de contratos y la discusión pertinente; reducir repeticiones dispersas. La precisión puede mejorar al concentrar las limitaciones, sin suavizarlas.
5. **Detalle de integridad que sigue directamente de flags y máscaras.** El aviso inmediato de missing es una mejora legítima de interfaz temporal, no un detector nuevo. En el principal bastan el contrato, cuatro episodios y el contraste 12.13 s → emisión en el reporte afectado; conservar los 9.200 reportes, reglas de emparejamiento y pruebas en el suplemento. La nomenclatura E5/E6/E7/E8 es necesaria para reproducción, pero no requiere un desarrollo metodológico largo en el cuerpo.
6. **Cronología de reparación del histórico.** Preservar fuentes, hashes y fracaso de reproducción; el principal necesita la consecuencia para la comparación, no la historia completa de recuperación del artefacto.

**No recortar** la convención de corriente terminal, la exclusión del ángulo de BUS39, el terminal provisional de BUS5, la definición temporal de diagnóstico, los resultados adversos, el rechazo RAW y las dos figuras protegidas. Esos elementos delimitan qué experimento se hizo. Tampoco enviar al archivo histórico las nuevas pruebas negativas de transferencia: son evidencia actual.

## Cómo podría argumentar un rechazo un revisor competente

La objeción más fuerte ya no es «los autores ocultaron los fallos» o «compararon contra un reinicio trivial». El manuscrito los muestra y ejecuta un competidor que conserva estado. Una objeción todavía sostenible sería:

> La motivación física es válida y la implementación está especificada, pero el artículo ofrece una integración de elementos establecidos cuya ventaja se observa en pocos calendarios de desarrollo. El experimento de simplicidad cambia varios componentes y opera con evidencias no calibradas al mismo punto de falsas alarmas; no identifica la aportación de la retención de historias. El método principal no admite el registro RAW bajo su propio contrato. Los experimentos de severidad y geometría, aunque informativos, no cierran esas dos brechas. Se necesita demostrar utilidad suficiente del procedimiento completo en la campaña independiente, o reducir de manera sustancial el alcance y el volumen de la afirmación metodológica.

Es una posible lectura crítica, no un informe externo recibido ni una predicción de decisión editorial. La respuesta defendible combina la comparación sencilla, el resultado independiente completo cuando exista y una formulación concreta de la integración implementada. Enumerar más módulos o más limitaciones no sustituye esa respuesta.

## Aspectos que resisten la revisión

- La diferencia entre restauración física y recuperación eléctrica es pertinente para decisiones sucesivas; las ecuaciones y el estado retenido la conectan con el algoritmo.
- La construcción explicita predicción antes de corrección, sustitución del sufijo de likelihood y separación de reloj de reporte y cómputo. Las masas aproximadas no se venden como probabilidades calibradas.
- La posición frente a IMM, M3H, diagnóstico por trayectorias y estimación DAE reconoce precedentes. La sección relacionada evita atribuirse la invención de historias, estados inciertos o búsqueda de onset.
- El control de estado único fortalece la comparación operacional; los conteos de extras y restauraciones huérfanas impiden que la precisión de eventos esconda su coste.
- El entrenamiento agrupado responde a la objeción de un comparador aprendido sin adaptación SIM. Documenta selección, ausencia de refit, dependencia de padres y escasez de normales. Su mala carga no se oculta tras la línea.
- El híbrido RAW conserva clases, integridad, huecos y emisiones; la única mejora se informa sin convertirla en validación del banco físico.
- El suplemento vigente se concentra en el método ejecutado. El traslado de estudios anteriores al archivo histórico ya corrige una fuente importante de dispersión.

## Cierre de lectura recomendado

El artículo puede conservar su título actual si presenta **un mecanismo físico implementado y evaluado bajo contratos acotados**, y sitúa la mejora del procedimiento completo por delante de cualquier interpretación causal de la memoria. La revisión editorial más eficaz es de selección y orden, no de añadir otra subsección experimental.

Quedan como cierre visible: distinguir los artefactos ET y las dos publicaciones físicas; incorporar las nuevas poblaciones al protocolo; terminar C01 o reformular explícitamente el alcance; y hacer el build final con inspección de figuras y verificación de las dos protegidas. Esta revisión textual no confirma paginación, legibilidad final ni una decisión formal de aceptación.

Corte final de fuentes revisadas: `main.tex` SHA256 `05bf7a96e0ede3bb…`; `article_submission_checks.tex` `866b296ad67907c8…`; `appendix_grouped_learning.tex` `1591fc2e4367aaba…`; `single_state_control.tex` `f90ef61af284ca93…`. Los anclajes de línea corresponden al corte de lectura; cambios posteriores deben cotejarse con estas versiones.
