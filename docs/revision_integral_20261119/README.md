# Auditoría de la versión para IEEE

La revisión parte del artículo y del suplemento compilados en la revisión f474a65. Tres revisores GPT-6-Luna recibieron encargos de visualización, matemáticas y evidencia. Ante un fallo de acceso a la carpeta desde los procesos Luna, se les entregaron las páginas renderizadas de todas las figuras, el texto del artículo, las expresiones LaTeX y los resúmenes experimentales. Una segunda pasada matemática recibió el inventario completo de ecuaciones numeradas del suplemento. Las notas desglosadas describen la versión de entrada. La revisión editorial posterior comprobó las observaciones contra las fuentes activas. Es una auditoría técnica interna; las personas citadas no actuaron como revisores.

## Dictamen

Revisión mayor para una afirmación de atribución general de eventos. El manuscrito tiene una pregunta de revista más precisa: tras la restauración, ¿qué parte del estado inferido hay que conservar para atribuir la siguiente intervención antes de que termine? El aporte está en formular esa decisión sobre una DAE con instrumentos y en medir las consecuencias de tres tratamientos de la recuperación bajo un reloj común. El contrafactual de continuidad permite que una intervención restaurada siga explicando los fasores. El resultado con mayor respaldo entre plantas es conservar la media del estado físico.

### Qué muestran las comparaciones

| Pregunta | Evidencia | Alcance de la conclusión |
|---|---|---|
| ¿Compensa el banco frente a un GLR continuo y a ExtraTrees entrenado para el catálogo? | Atribución correcta antes de restauración, 99/108, 72/108 y 22/108. Alarmas sin correspondencia en registros con eventos, 8, 85 y 0. | Ventaja en atribución a costa de más alarmas que ExtraTrees. Los 108 eventos pertenecen a 18 trayectorias. |
| ¿Qué aporta conservar el estado físico? | Llevar la media frente a reiniciar: +50,7 puntos en la planta de referencia y +31,2 en la segunda para eventos tras intervalos cortos. | La continuidad tiene respaldo en ambas plantas simuladas con ese catálogo. |
| ¿Hace falta conservar cada historia? | Historias frente a media: +37,5 puntos en referencia y +1,4 en la segunda, con IC del 95 % de −12,5 a +16,0 en esta última. | La ventaja adicional en cobertura depende de la planta. La fusión también cambia la dispersión y la memoria de búsqueda. |
| ¿Se ganó a SGSMA? | El ZIP original y el híbrido se compararon en las mismas ventanas artificiales. En la tercera cohorte: macro-F1 0,1933 y 0,9814. El localizador eléctrico acertó 2/72 fuentes físicas nuevas y 24/96 ubicaciones contando PMU. | Son datos sintéticos con un compuesto conocido. La validación histórica del ZIP y el concurso oculto tienen otros denominadores. El banco dinámico rechazó el arranque de estos registros. |
| ¿Hay un estimador óptimo? | La media de severidad y la del estado condicionado a una historia minimizan riesgo cuadrático bajo el modelo local. La gaussiana de momentos minimiza pérdida logarítmica a un informe. | La poda, las propuestas, la covarianza compartida, la localización y la política de seis informes carecen de esa garantía global. |

## Literatura y novedad

Revisión dirigida de trabajos primarios. Los ejes de búsqueda fueron diagnóstico secuencial, dinámica posterior a una maniobra, localización con PMU escasas, cadenas de medida y las contribuciones pertinentes de los tres investigadores. Las métricas publicadas con otras redes, fallas, sensores y plazos no se trataron como comparaciones numéricas de P07.

| Trabajo y contrato | Qué resuelve | Relación con P07 |
|---|---|---|
| GLR para saltos y filtros de historias múltiples | Estimar tiempo y tamaño de un salto a partir de innovaciones; conservar caminos discretos alternativos. | Antecedentes de la recursión. El aporte propio exige especificar qué caminos continúan después del cierre y medir el efecto de conservarlos. Véanse Willsky–Jones y Boers et al., citados en la sección I. |
| Yang et al., detección de salidas de línea | Usa transitorios de ángulo de tensión y PMU parciales en redes IEEE-39 y 2383. | Incorporar dinámica a una detección con pocas PMU ya tiene precedentes. [Artículo de los autores](https://arxiv.org/abs/1911.01733) |
| Warner et al., identificación secuencial de fallas | Contrasta trayectorias transitorias de alta fidelidad con PMU remotas. | Competidor conceptual directo en la predicción por candidato. P07 examina qué hace el monitor tras revertir la primera maniobra. [Prepublicación](https://doi.org/10.36227/techrxiv.23264519.v1) |
| Li et al., CNN y emplazamiento de PMU | Simulan fallas en IEEE-39 y 68 con distintos niveles de observabilidad y distinguen la línea exacta de un vecindario. | Una región de búsqueda es otro producto operativo. El resultado primario de P07 exige coincidencia exacta. [Artículo de los autores](https://arxiv.org/abs/1810.05247) |
| Noori et al., SGSMA 2026 | Método de admitancia y cambios fasoriales en un alimentador radial de 134 barras con diez PMU; devuelve localización o región de búsqueda. | Antecedente directo del diccionario eléctrico. Aquí se prueba en transmisión mallada, ante otras familias y con resultado débil en activos nuevos. [IEEE](https://doi.org/10.1109/SGSMA65955.2026.11618782) |
| Xing et al., evaluación con tensiones transitorias | Separan la sensibilidad al emplazamiento y a las condiciones físicas; el intervalo del efecto de emplazamiento en la extensión IEEE-39 incluye cero. | La separación geométrica y acertar el bus son preguntas distintas. [Sensors](https://doi.org/10.3390/s26196203) |
| David Celeita et al., co-simulación de estimación de estado | Combinan PMU virtuales, OpenPMU y simulación en tiempo real. | Ruta para probar la cadena de medida del estimador y sincronizar sus entradas reales. [Artículo institucional](https://pure.qub.ac.uk/en/publications/iec-61850-9-2-based-module-for-state-estimation-in-co-simulated-p/) |
| Tamara Becejac y Payman Dehghanian, pruebas de PMU | Evalúan en hardware cómo los errores durante fallas se propagan hasta la localización en una red de 23 barras. | Motiva medir el error de la aplicación además del error fasorial. La prueba de ruido de P07 todavía es simulada. [Artículo de los autores](https://doi.org/10.1109/JPETS.2019.2900064) |
| Masoud Barati, pronóstico de disrupciones | Usa PMU y unidades recurrentes para anticipar disrupciones. Basulaiman y Barati también estudian predicción multi-paso del estado. | Un pronóstico de riesgo o estado tiene un blanco y un reloj diferentes de nombrar el activo después del inicio y antes de restauración. [ISGT](https://doi.org/10.1109/ISGT.2019.8791625) · [Trabajo de predicción multi-paso](https://arxiv.org/abs/2305.13215) |

## Cambios aplicados y observaciones descartadas

Se explicita el filtro multihipótesis al abrir la sección III. El nuevo paso de la derivación expresa la media truncada mediante la derivada del normalizador de la misma integral que puntúa la historia. Se explica el factor de transición en la ganancia del estado siguiente. La figura 1 adopta el símbolo de la ecuación de separación y reduce operaciones intermedias. La figura 5 indica en la leyenda qué intervalo contiene cero. Se corrigió un signo de exclamación literal en el operador de proyección del suplemento y se unificó el símbolo del ruido de proceso con el artículo. El texto compara trabajos cercanos y reduce la discusión SGSMA a sus dos condiciones decisivas: catálogo y plazo de decisión.

Las notas independientes también piden datos que ya constan en los documentos completos: las 47 coordenadas están enumeradas en el modelo de observación, las estadísticas de la normal truncada tienen tratamiento numérico en el suplemento y el reloj tras el cambio de topología está definido. Esas observaciones sobre fragmentos no constituyen errores del manuscrito. Las recomendaciones de legibilidad específicas de cada figura se conservan como revisión editorial. Las dos figuras protegidas se mantienen en el PDF.

## Experimento decisivo

Si la tesis sigue siendo la recuperación, la comparación de mayor valor es cruzar memoria de búsqueda del inicio y representación de la covarianza de recuperación con las mismas propuestas, umbrales y trayectorias. Esto separaría tres cambios hoy confundidos al fusionar historias. Si se pretende afirmar localización en activos nuevos, hace falta otra prueba: cambios físicos generados por un segundo modelo eléctrico, fuentes reservadas, errores instrumentales independientes y puntuación ciega por activo, incluyendo abstenciones. Más realizaciones del mismo patrón M9 solo estrecharían la incertidumbre para ese simulador.

## Material de revisión

- [Cada figura del artículo y del suplemento](figuras.md)
- [Ecuaciones 1–17 del artículo](ecuaciones_articulo.md)
- [Ecuaciones del suplemento](ecuaciones_suplemento.md)
- [Matriz de afirmaciones, calibraciones y comparadores](afirmaciones.md)

## Comprobaciones de cierre

Se revisaron 5 figuras y 17 ecuaciones numeradas del artículo, junto con 23 figuras y 67 ecuaciones del suplemento. Las tres baterías de identidades, fronteras bayesianas y límites de información pasaron 11/11, 12/12 y 12/12 comprobaciones. La integral escalar de severidad coincidió con la cuadratura hasta 1,67 × 10⁻¹⁶. Una diferencia central independiente aplicada a la nueva expresión de la media truncada discrepó en menos de 4,7 × 10⁻¹¹ de la media calculada por SciPy en doce combinaciones de centro e intervalo. Son controles locales de álgebra; el desempeño del diagnóstico sigue siendo el que figura en las pruebas congeladas. La versión final conserva las 11 páginas del artículo y las 46 del suplemento.
