# Revisión independiente: abogado del diablo

**Fecha:** 2 de noviembre de 2026. **Objeto:** snapshot entregado, `main.pdf` (14 páginas) y `supplement.pdf` (11 páginas), leídos completos; contraste puntual con fuentes TeX y tablas locales. No se consultaron informes de otros revisores, no se modificó el manuscrito, no se ejecutaron nuevas simulaciones ni se abrió RAW0002. La revisión visual global se hizo con las 25 páginas renderizadas; los hallazgos científicos proceden del contenido completo, no de miniaturas.

**Dictamen:** revisión mayor antes de dar por cerrado un envío exigente. Hay un resultado de ingeniería defendible y una delimitación excepcionalmente explícita de sus límites. No encuentro una contradicción que invalide los resultados reportados ni fundamento para pronosticar rechazo editorial. Sin embargo, el paquete entregado todavía no permite comprobar adecuadamente el desempeño de restauración y omite un control ejecutado especialmente pertinente. La contribución específica del mecanismo propuesto permanece menos demostrada que la ventaja de disponer de un catálogo físico del mismo entorno generador.

## Fortalezas que sobreviven a la objeción adversarial

El algoritmo define una pregunta operativa concreta: distinguir una intervención nueva de la recuperación de una anterior, conservando estado físico e instrumental y separando tiempo estimado de inicio, emisión y restauración. El manuscrito distingue con cuidado componente, procedimiento completo y experimento retrospectivo, retiene resultados negativos y no presenta 648 replays como 648 intervenciones independientes. La ganancia de atribución oportuna de cargas en el catálogo evaluado es grande y no desaparece porque la novedad algorítmica sea incremental.

## Contraargumento más fuerte

Una interpretación más austera de los resultados es que un catálogo de respuestas construido con las ecuaciones, activos candidatos y mapa instrumental del mismo simulador identifica cargas mejor que dos clasificadores que reciben resúmenes temporales y supervisión finita. Esta interpretación explica simultáneamente la ventaja de cargas, el empate casi completo en líneas, el rendimiento casi idéntico del banco nominal y la mezcla, y el aumento de alarmas cuando la red sale del catálogo. No necesita atribuir la mejora a la integración bayesiana, al tensor ni a conservar múltiples historias de recuperación.

La física empleada es legítima y útil, pero reducción de DAE, predictores conmutados, filtrado condicional, integración de amplitud y bancos de historias tienen precedentes. El arreglo de masas y su incremento son contabilidad interpretable, no una nueva fuente de información. El propio texto lo admite. Por ello, el valor científico debe residir en una adaptación específica y verificablemente útil de esos mecanismos al problema de intervenciones sucesivas. El ensayo final compara procedimientos completos a distintos puntos de alarma; no identifica qué adaptación es responsable del beneficio. Además, el control de recuperación encuentra esencialmente la misma separación cuando la historia es conocida y ninguna ganancia media de exactitud binaria; con severidad previa incierta, la separación empeora.

Nada de esto prueba que el método sea innecesario. Sí permite a un revisor sostener que se ha demostrado una ventaja del conocimiento del simulador, pero no todavía la necesidad del mecanismo que organiza el relato. La respuesta más convincente sería un contraste físico cercano y una explicación causal limitada de sus diferencias, acompañados de los resultados completos de restauración. Añadir más formulación o más nombres a los componentes no resuelve esa objeción.

## Hallazgos

### CRITICAL

**Ninguno demostrado.** No identifico fraude, fuga de etiquetas, invalidez general del modelo o colapso matemático a partir del material examinado. La explicación alternativa anterior sigue siendo compatible con una contribución aplicada; no justifica clasificarla como refutación fatal.

### MAJOR

**DA-1. La necesidad del mecanismo distintivo permanece abierta.**

- **Localización:** main pp. 1–3, contribuciones y estado del arte; pp. 5–6, método; p. 8, componentes tensor/Bayes; pp. 11–13, interpretación y conclusión. Supplement pp. 6–8, control single-state y geometría de recuperación.
- **Evidencia:** el texto reconoce que no se ha aislado el beneficio de memoria de recuperación ni de Bayes/tensor. El nominal obtiene 643/648 frente a 644/648 de la mezcla y usa otra publicación. El control X04 obtiene exactitud binaria media 98.35% en ambos casos, razón mediana de separación 1.0006 con historia conocida y 0.8532 con incertidumbre previa. Esos resultados apoyan una predicción coherente, no una mejora universal de identificabilidad.
- **Objeción:** la descripción de una combinación específica no equivale por sí sola a demostrar una contribución metodológica necesaria. Si la tesis central es el procedimiento práctico, se debe distinguir claramente qué adaptación es nueva, qué mecanismo simplemente se aplica y qué beneficio concreto se ha observado.
- **Cierre mínimo:** priorizar una sola contribución verificable: atribución física secuencial de catálogo con recuperación explícita y balance aciertos/alarmas. Mostrar el control físico próximo ya ejecutado y explicar qué contrasta realmente. Para afirmar necesidad o ganancia atribuible a Bayes/memoria, hará falta un contraste que mantenga diccionario, observaciones, búsqueda y publicación comparables; si no se ejecuta, conservar explícitamente esa afirmación fuera del resultado. No hace falta reclamar novedad del tensor ni añadir otra versión de buses.

**DA-2. El suplemento entregado no contiene resultados que el artículo promete, incluidos los más cercanos al mecanismo central.**

- **Localización:** main p. 11, remisión a tablas completas, ledger de fallos, restauración y censura; supplement pp. 4–6, protocolo y métricas; Appendix H p. 6, control de estado único. Verificación de fuentes: `submitted_snapshot/supplement.tex` incluye condicionalmente `supplement/c01_narrative_details.tex`; ese archivo no existe en la raíz revisada. En el PDF de 11 páginas no aparecen las tablas C01 prometidas.
- **Evidencia:** `tables/generated/single_state_control.tex` contiene un control abierto con reloj de seis reportes: estado único/GLR 37/54 oportunos y 37 extras; banco nominal 44/54 y 6; mezcla 51/54 y 3. Incluye además Early OFF y No OFF. El suplemento explica ese control pero no incorpora su tabla ni sus resultados. `tables/generated/c01_continuous.tex` contiene también resultados estratificados ausentes del suplemento entregado.
- **Objeción:** un lector puede verificar la elevada tasa de aciertos, pero no la calidad del cierre de episodios que motiva conservar recuperación. La ausencia también oculta un control más informativo sobre el aporte de historias que ExtraTrees. No atribuyo intención selectiva ni digo que el control no se ejecutó: la evidencia local indica una omisión de integración documental.
- **Cierre mínimo:** incorporar los resultados existentes correspondientes al snapshot, con procedencia inequívoca y sus limitaciones, o corregir las remisiones si esos resultados pertenecen a otro documento. Publicar para C01 cierres prematuros, retraso firmado, cierres ausentes y episodios abiertos, distinguiendo restauraciones de episodios extra. El propio Appendix E exige esa distinción. No reinterpretar silenciosamente métricas históricas ni regenerar baselines.

**DA-3. La comparación decisiva enfrenta cantidades de conocimiento distintas y no diagnostica el fracaso de cargas del comparador.**

- **Localización:** main pp. 9–10, descripción de ExtraTrees, tablas 4–5; p. 11, interpretación; supplement pp. 6–7, entrenamiento agrupado.
- **Evidencia:** el banco dispone de DAE nominal, operadores de cada activo y mapa terminal. ExtraTrees recibe descriptores y etiquetas de familias/activos; sus dos variantes obtienen 15/324 y 30/324 cargas, mientras SHORT obtiene 322/324 líneas, exactamente como el banco físico. Se usan reglas de publicación congeladas distintas. La división agrupada y la separación de padres reducen fuga, pero no igualan conocimiento previo ni exposición al espacio de severidades/contextos.
- **Objeción:** la diferencia de cargas puede reflejar representación, cobertura de entrenamiento o publicación, además del razonamiento físico. El manuscrito ya lo reconoce, pero no muestra la descomposición necesaria para que el lector sepa cuál es la explicación más plausible. La cifra total 644 frente a 330 invita a una conclusión global más fuerte que el patrón por familia.
- **Cierre mínimo:** mantener la desagregación carga/línea en toda conclusión e incorporar, con predicciones ya selladas, una confusión causal por familia/fuente o un ledger equivalente que separe ausencia de alarma, familia errónea, fuente errónea y diagnóstico tardío. Informar cobertura de amplitud/contexto por fuente en entrenamiento frente a prueba. No basta la matriz histórica de transferencia: pertenece a otro estimador, ventana y catálogo. Comparar el algoritmo físico próximo es una prioridad mayor que acumular clasificadores nuevos.

**DA-4. La amplitud de la evidencia favorece fuertemente el entorno donde el modelo dispone de la estructura correcta.**

- **Localización:** main pp. 8–9, diseño; pp. 11–12, límites; supplement pp. 3, 5 y 7.
- **Evidencia:** generador e inferencia comparten familia F01 y mapa PMU. Las tres condiciones modifican R/X dentro de esa familia; no cambian ley de carga, controles, productor o instalación instrumental. La mezcla genera 68 extras fuera del banco frente a 10 de ExtraTrees en esa condición. El banco físico ni siquiera es admisible en RAW0001 bajo su contrato de arranque; el híbrido que pasa de 1/24 a 2/24 no es el banco físico.
- **Objeción:** 644/648 demuestra eficacia dentro del entorno simulado especificado, no robustez general de inferencia física ni transferencia desde la validación del hackathon. La alta exactitud no valida BUS5, BUS39 ni el generador por retroalimentación. Esta limitación está bien declarada, pero acota directamente la significación del resultado.
- **Cierre mínimo:** conservar esa frontera en título interpretativo, abstract y discusión; tratar el trabajo como estudio de método en simulador. Si se desea ampliar la conclusión, la validación relevante sería con discrepancia estructural o productor independiente, no simplemente más seeds ni nuevas versiones de buses. No considero una campaña de campo requisito automático para un artículo de simulación ni autorizo nuevas ejecuciones mediante esta revisión.

### MINOR

**DA-5. El orden narrativo dispersa la contribución más sólida.** Main pp. 7–10 dedica espacio central a tres componentes de cohortes diferentes y a una matriz histórica casi perfecta para el estimador físico previo. Aunque las leyendas son honestas, el lector debe reconstruir cuál resultado valida qué método. Priorizar la secuencia problema concreto → procedimiento → control físico cercano → C01 → límites; conservar los componentes como motivación cuantitativa secundaria. La figura protegida de eventos y el unifilar no necesitan eliminarse ni cambiarse.

**DA-6. La capa cyber/integridad añade integración, no evidencia nueva de ataque.** Main pp. 3, 11–12 y supplement pp. 4–7 distinguen explícitamente disponibilidad por reporte, bad-data por ventana y diagnóstico físico. Los 161379 reportes sin desacuerdo prueban composición; las cuatro notificaciones con demora cero usan flags ya observados; la mejora 1/24→2/24 corresponde a un híbrido retrospectivo. Es correcto mantenerlos, pero no deben figurar como pilares de novedad física ni como detección de intrusión. La causalidad instrumental no equivale a atribución maliciosa. No pido un detector cyber nuevo para un artículo cuyo alcance principal no lo incluye.

**DA-7. Título y trazabilidad del suplemento no coinciden plenamente con el artículo.** Main usa “Physics-Informed Bayesian Event Attribution From Sparse PMUs”; supplement conserva “Physics-Based Event Attribution From Sparse PMUs With Recovery Memory”. Corregir la identificación y referencias de archivos en el paquete final. El problema es menor por sí solo, pero refuerza la necesidad de revisar que el suplemento sea exactamente el prometido.

## Explicaciones alternativas que deben seguir abiertas

1. **Ventaja del catálogo físico:** disponer de los operadores y mapa que también utiliza el generador puede explicar la mayor parte de la mejora de cargas. No es fuga de etiquetas; es una diferencia real de conocimiento previo.
2. **Pérdida de información en los descriptores aprendidos:** los resúmenes causales pueden eliminar diferencias útiles entre cargas o confundir recuperación con normalidad. El entrenamiento asigna normal fuera del intervalo activo; recuperación no es clase propia. Es una hipótesis explicativa, no un error demostrado del código.
3. **Reglas de publicación y búsqueda:** el patrón de aciertos y extras puede depender tanto de admisión/confirmación como del score. Igual reloj de seis reportes no significa igual umbral estadístico, y el manuscrito lo señala.
4. **Ajuste de amplitud suficiente para localizar:** resultados de respuesta o severidad mejores sin mejora de fuente, como el experimento de contexto con 240/240 para ambos corregidos, son compatibles con que la aproximación adicional mejore fidelidad sin mejorar diagnóstico.
5. **Memoria como consistencia, no como nueva información:** retener el estado evita un error de modelado obvio después de OFF. No implica que un banco largo de historias sea superior a un estado bien estimado más un contraste físico simple en todos los casos.

## Voces ausentes, sin ampliar el alcance artificialmente

- Operador que debe valorar una fuente correcta frente a alarmas adicionales y cierres prematuros.
- Responsable de integración PMU que necesita saber cuándo el algoritmo queda no disponible por arranque, faltantes o mapa instrumental.
- Reproductor independiente que recibe los dos PDFs y necesita encontrar las tablas que éstos prometen.

## Observaciones que no son defectos

- No es requisito inventar una nueva regla de Bayes ni un nuevo tensor para producir una contribución de ingeniería.
- Mantener RAW0001 como retrospectivo, F01 como candidato y RAW0002 fuera del estudio es una frontera correcta, no un fallo a remediar abriendo datos nuevos.
- El resultado negativo de recuperación y la normalización histórica errónea preservada con su prior efectivo fortalecen la honestidad; no deben borrarse para mejorar el relato.
- No hay que prometer probabilidades calibradas, optimalidad secuencial ni tiempo real. El texto actual evita esos saltos.
- La misma secuencia de PMU y un split de padres correcto son fortalezas, aun cuando no igualen el conocimiento físico del que disponen las rutas.

## Comprobación externa limitada de los precedentes

No se realizó una revisión bibliográfica exhaustiva ni se infiere prioridad mundial. El precedente de [Boers y Driessen, Automatica 2005](https://www.sciencedirect.com/science/article/pii/S0005109804003243) describe filtros por historia de modos y gestión adaptativa de hipótesis; confirma que retener múltiples historias no puede ser la novedad general. El [preprint de Warner et al.](https://d197for5662m48.cloudfront.net/documents/publicationstatus/169966/preprint_pdf/fb88c972e89f2492099d5d5e00da2aac.pdf) presenta detección/identificación mediante simulaciones de transitorios con PMUs dispersas. Su tarea de fallas de línea no es idéntica a las cargas/líneas con restauración de este artículo. Ambos precedentes ya están reconocidos por los autores; la cuestión pendiente es la demostración del aporte específico, no una acusación de omisión de citas.

## Criterio de cierre para esta revisión

Mi recomendación no es abrir otra campaña indiscriminada. El mínimo documental antes de enviar es recuperar los resultados prometidos, integrar el control físico ya ejecutado con sus límites y explicar las fallas de cargas a partir de las salidas selladas. El mínimo argumental es que la contribución aplicada sea explícita y que ninguna frase convierta la mejora del procedimiento completo en una ganancia atribuible a Bayes, tensor o memoria.

Si los autores buscan una afirmación metodológica más fuerte que esa contribución aplicada, la falta de un contraste aislado es una brecha científica real y no se cierra con prosa. Bajo el alcance estrecho actual, no exijo una nueva versión de la red ni una capa cyber nueva; exijo que el lector pueda inspeccionar exactamente qué se comparó, qué mejoró y qué no se ha demostrado. **Readiness actual: no cerrado para envío; revisión mayor acotada y sin pronóstico de decisión editorial.**
