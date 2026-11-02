# Revisión adversarial independiente de P07

Fecha: 2 de noviembre de 2026. Perspectiva: novedad, fuerza de la inferencia científica y objeciones de un revisor exigente. Es una revisión simulada, no un dictamen emitido por IEEE.

Objeto: `main.pdf`, 16 páginas, SHA256 `3B098F6F0682EEDF39217C0AE28A73116BC2A8541CFE7AADDEDD3D88AB64B07F`, y sus fuentes incluidas. Revisé el texto completo principal y apartados suplementarios pertinentes. No leí otros informes de revisión ni resultados parciales de la ablación en curso. No modifiqué manuscrito, métodos, campañas ni figuras; RAW0002 no fue abierto.

## Dictamen

**Dictamen simulado: Reject, updates required before resubmission; no enviaría esta instantánea.** En términos de preparación interna, requiere revisión mayor antes de envío; no es una predicción de la decisión real. Hay un procedimiento físico real y resultados empíricos relevantes. El problema no es que todo sea decorativo. El problema es que el beneficio de la parte distintiva todavía no está separado suficientemente de la ventaja de disponer del modelo del generador, del publicador de episodios y de comparadores débiles para carga. La sección IX.A declara además una investigación en ejecución. Eso impide presentar esta versión como un estudio terminado.

No recomiendo otra cadena de correcciones por bus. Recomiendo terminar el contraste de componentes ya autorizado, cerrar una afirmación central verificable y ajustar el peso de las comparaciones a lo que realmente identifican.

## Lo que sí resiste una lectura escéptica

- El método usa ecuaciones DAE, observación de terminales orientados, respuestas dinámicas e integración de amplitud. Es legítimo denominarlo inferencia informada por física. No es necesario que sea una red neuronal para ello.
- El manuscrito diferencia correctamente magnitud/fase de fasores y THD, corriente terminal e inyección nodal, restauración física y estado dinámico, frecuencia de bus y velocidad de máquina.
- La descripción actual no presenta M ni ΔM como una nueva descomposición tensorial. Explica que son agregaciones y una identidad temporal; los coeficientes de interacción de segundo orden pertenecen a otro experimento. Esa honestidad es una fortaleza.
- Las limitaciones de Bayes están expresadas: evidencia local exacta bajo su modelo condicional, pero banco global aproximado por poda, selección, estimación de contexto por sustitución y covarianzas compartidas.
- El artículo conserva los fallos: alarmas extra bajo R/X fuera del banco, rechazo instrumental de RAW0001, ausencia de validación de todas las familias y falta de ventaja general de latencia.
- Se distingue el ZIP de la hackathon de los clasificadores causales posteriores. Esa separación evita una comparación numérica engañosa de métricas distintas.

## Objeciones mayores

### DA-1. La diferencia respecto de métodos establecidos todavía parece una configuración específica, no una contribución algorítmica aislada

**Evidencia:** introducción, líneas 31–56; `sections/article_related.tex:15–40`; método, líneas 165–205. El propio texto reconoce trayectorias físicas, búsqueda de inicio, filtros multimodelo y bancos de historias como antecedentes. La restauración que no reinicia estados es física correcta, pero no una ley descubierta aquí. La identidad de ΔM tampoco establece un nuevo estimador.

**Precedente verificado:** Boers y Driessen (2005) ya mantienen hipótesis de historias de modos, con un filtro condicional por hipótesis y poda/fusión adaptativa. Por tanto, “conservar historias y competir según likelihood” no basta para establecer novedad. [Artículo original](https://www.sciencedirect.com/science/article/pii/S0005109804003243).

**Pregunta del revisor:** ¿qué operación, capacidad o contrato técnico preciso no queda ya cubierto por aplicar un banco de modos/historias a la DAE? La respuesta defendible puede ser una formulación concreta de diagnóstico continuo carga/línea con recuperación e integración de severidad, acompañada de evidencia de utilidad. No hace falta inventar un nuevo Bayes ni un teorema general.

**Remedio mínimo:** una comparación explícita de operaciones con el antecedente de trayectorias y con IMM/M3H; separar “ingrediente heredado”, “adaptación eléctrica”, “decisión nueva” y “evidencia”. Si la novedad es de sistema/ingeniería, declararla así. No prometer superioridad de filtro óptimo ni agregar GPU como sustituto de novedad.

### DA-2. El mecanismo distintivo no tiene todavía un efecto aislado demostrado

**Evidencia:** `sections/article_controlled_ablation.tex:1–3` (p. 12) dice que el estudio está en curso. `sections/article_method.tex:224–228` reconoce que nominal y mezcla tienen distintas rutas de publicación. `sections/narrative_results.tex`, última subsección, reconoce que el GLR difiere en búsqueda, amplitud y semántica de puntuaciones. `sections/article_interpretation.tex:5–13` reconoce que el control con historia conocida no mejora de media la identificación binaria.

Estos resultados no contradicen la utilidad de retener recuperación, pero tampoco identifican su contribución al 644/648. Es posible que buena parte del beneficio provenga de las firmas correctas, el catálogo y las reglas de publicación. Esa explicación alternativa permanece abierta.

**Remedio mínimo:** terminar el 2×2 ya fijado y reportar efectos por padre sobre cobertura, extras y cierre, incluido cualquier resultado nulo. Limitar la conclusión a “integración marginal de amplitud” y “transferencia de 114 desviaciones físicas al cierre”: el perfil conserva estimadores condicionales bayesianos y el reset conserva otra memoria. No es una ablación de todo Bayes ni de toda memoria. No retocar C01 ni seleccionar después otro experimento por un resultado incómodo.

### DA-3. La comparación principal no demuestra ventaja frente a una alternativa supervisada competente para carga

**Evidencia:** `sections/narrative_protocol.tex:46–55` informa 0/72 y 4/72 atribuciones oportunas de carga en la validación previa de los dos clasificadores. La Tabla 5 y Fig. 9 (pp. 11 y 13) muestran que casi toda la diferencia total proviene de carga, mientras las líneas ya se resuelven bien con ambos enfoques. `sections/08c_c01_confirmatory.tex:39–46` añade que todos los diagnósticos emparejados a tiempo son correctos: la diferencia es cobertura o retraso, no precisión condicional de clase/origen.

Congelar un comparador débil evita ajustar al examen; no lo convierte en una referencia fuerte. El resultado sigue siendo válido para esos clasificadores, pero no sostiene “Bayes supera ML” ni “necesitamos este método porque ExtraTrees no puede resolverlo”. La información privilegiada también difiere: el banco conoce ecuaciones y operadores del generador; los árboles disponen de un conjunto finito de entrenamiento.

**Remedio mínimo:** mantener la afirmación estrecha y explicar el fallo de detección/cierre de los árboles, con cobertura y alarmas. Para una reivindicación competitiva más amplia sí se necesita un comparador de carga competente, elegido/calibrado con desarrollo separado antes de evaluarlo; no reajustar los árboles sobre C01. No es obligatorio usar GNN por moda: un detector físico más simple o un clasificador temporal bien validado puede ser más informativo.

### DA-4. Chen2016 es una prueba de incompatibilidad del adaptador, no evidencia suficiente de superioridad ante el antecedente físico más cercano

**Evidencia:** pp. 11 y 13; `sections/08c_c01_confirmatory.tex:68–84`: 74/162 primeras decisiones correctas, 66 anticipadas y 72/72 normales con parada. El texto advierte el supuesto de inyección blanca y las exposiciones desiguales.

**Fuente primaria:** Chen et al. modelan cambios incrementales de inyección y voltaje y formulan detección rápida con control del tiempo medio hasta falsa alarma. El hecho de que el adaptador falle en todas las normales hace especialmente importante verificar que el experimento está probando esa distribución y calibración, no únicamente un traslado fuera de soporte. [PDF de los autores](https://people.ece.ubc.ca/~chen/papers/journal/07041234.pdf).

Warner et al. es un antecedente más cercano para respuestas transitorias simuladas y PMU dispersas; el propio P07 confirma que no fue ejecutado aquí. Su existencia y enfoque se verificaron en el [preprint original indexado](https://d197for5662m48.cloudfront.net/documents/publicationstatus/169966/preprint_pdf/fb88c972e89f2492099d5d5e00da2aac.pdf); el acceso directo falló durante esta revisión, por lo que no certifico aquí una comprobación completa de todas sus ecuaciones.

**Remedio mínimo:** conservar Chen como contraste limitado de contrato y no como prueba de superar el estado del arte. Especificar el control que verificó su adaptador en un escenario compatible. Si la tesis central requiere superioridad frente a métodos de trayectorias, faltaría una comparación común adecuada; no es válido suplirla con su mal resultado de Chen.

### DA-5. Falta un antecedente muy cercano a “usar física dinámica para recuperar información con PMU parciales”

No encontré en `references.bib` ni en el texto principal a Yang, Nan Chen y Zhai, *Dynamic Power Systems Line Outage Detection Using Particle Filter and Partially Observed States* (2021). Su [texto original](https://arxiv.org/html/2107.06754v3) combina estados dinámicos de generadores, balance eléctrico, filtro de partículas y monitoreo de residuos en IEEE-39 con PMU parciales. Es detección de apertura, no el mismo contrato de atribución sucesiva carga/línea con restauración. Además requiere condiciones específicas de disponibilidad de vecinos/mediciones; no asumir equivalencia de sensores.

**Remedio mínimo:** incorporarlo al mapa de capacidades y explicar la diferencia de problema, observaciones y mecanismo. Su omisión debilita la tesis de que aprovechar estados no medidos mediante física sea en sí una novedad. No implica automáticamente que deba implementarse como otro comparador.

### DA-6. La evidencia componente ocupa demasiado peso causal en una narrativa que intenta defender un único método

**Evidencia:** sección V, pp. 8–9, Fig. 5 y Tabla 3. Se reúnen reconstrucción de voltajes, modelos de 136–448 features, sensibilidad mixta y un estimador de cardinalidad con inicio/contexto conocidos. Esos algoritmos no son el observador continuo. La tabla de cardinalidad además conserva un prior efectivo distinto del declarado: `(0.20,0.50/(2*pi),0.30)` (`article_evidence_bridge.tex:120–128`). La honestidad del aviso no vuelve limpio ese resultado como validación del método actual.

El lector debe recordar demasiados contratos para seguir una prueba central. La bajada de error de 0.205 a 0.00307 de las firmas mixtas impresiona, pero no demuestra una mejora del banco continuo que no usa esos términos. Es un riesgo de halo visual, no una acusación de datos falsos.

**Remedio mínimo:** preservar todos los archivos y resultados históricos, pero distinguir con mayor jerarquía visual los mecanismos que entran en el algoritmo actual. Trasladar detalles de cardinalidad defectuosa y modelos no usados a las notas históricas, o reducirlos a una motivación explícitamente secundaria. La contribución principal no debe depender de esa tabla. No modificar la figura de eventos protegida.

### DA-7. La validación solo mide una vecindad del mismo productor físico e instrumental

**Evidencia:** `sections/article_interpretation.tex:60–81`: generador y predictores comparten familia F01 y mapa PMU; perturbaciones R/X, BUS5 provisional, ángulo de BUS39 omitido, ruido entre familias incompleto y frecuencia/ROCOF con ruido separado. RAW0001 es conocido y el filtro no lo admite por ruido ROCOF.

Es una limitación sustantiva del alcance, no prueba de que la simulación sea inválida. Las cifras altas son perfectamente posibles en un catálogo cerrado con modelo conocido. Sin embargo no sostienen aún transferencia a una instalación PMU ni recuperación de toda la información física de una red desconocida. Las hipótesis de sensor y productor pueden dominar el resultado.

**Remedio mínimo:** mantener el artículo como estudio metodológico controlado dentro de este modelo y presentar la admisión/rechazo como parte del resultado. Si se desea afirmar robustez operacional o transferencia, falta evidencia con otro productor/ley de carga/control/mapa instrumental, definida antes de examinar resultados. No es obligatorio abrir RAW0002 ni añadir más buses para sostener el alcance limitado actual.

## Claridad y objeciones menores

1. El método tiene pseudocódigo real (Algoritmo 1), pero “aplicar las reglas fijas” oculta una parte decisiva: dos relojes OFF, pantalla de fuente de carga, regla temprana de línea y reemplazo. El resumen principal necesita mostrar cómo se conectan; el suplemento puede conservar constantes. No sugiero más ecuaciones genéricas, sino que las decisiones ejecutadas sean visibles.
2. “Sealed/frozen/archived” aparece repetidamente. La trazabilidad importa, pero no debe sustituir la explicación de mecanismo. Una declaración de protocolo y referencias al suplemento bastan en varios lugares. La abundancia de advertencias de contratos puede parecer un inventario de campaña, aunque no permite inferir autoría humana o automática.
3. M y ΔM están correctamente acotados en la versión actual. No recuperar el reclamo tensorial por haber escrito `einsum` o por un microbenchmark. Una aceleración futura debe medirse de extremo a extremo; no corrige la falta de aislamiento del mecanismo.
4. La imagen de eventos está contextualizada como RAW retrospectivo y familias fuera de alcance; no la cambiaría. La mejora necesaria está en el vínculo entre Fig. 1, algoritmo y los resultados de cobertura/alarma, no en añadir más fenómenos visuales.

## Cierre que pediría, sin seguir creando versiones

1. Terminar y revisar A01; eliminar el estado pendiente únicamente cuando existan resultados completos.
2. Reescribir la contribución en términos de la operación que A01 realmente pueda respaldar, preservando resultados nulos y el coste en extras.
3. Cerrar la comparación intelectual con M3H, Warner y el precedente PF/PMU parcial; no afirmar originalidad del vocabulario.
4. Definir si el paper reclama una demostración dentro del catálogo o superioridad competitiva más general. La primera puede sostenerse con evidencia estrecha y limitaciones claras; la segunda necesita una referencia competente y un contraste de alarmas comparable, no más prosa.
5. Reducir la dependencia narrativa de componentes históricos ajenos al algoritmo final y de la tabla con prior incorrecto.

**Conclusión:** sí hay material científico aprovechable y física auténtica. La instantánea actual todavía no demuestra que su combinación sea una mejora metodológica general ni que el mecanismo anunciado cause la ganancia principal. Un paper de ingeniería bien delimitado puede ser valioso; prometer que ningún revisor tendrá objeciones sería engañoso.
