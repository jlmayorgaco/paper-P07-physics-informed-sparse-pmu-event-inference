# Revisión narrativa y científica de P07

## Diagnóstico

El borrador reunía estudios válidos pero distintos como si fueran una sola cadena terminada: estado oculto, banco batch de cargas, propuesta conjunta y componente causal. La lista de contratos, versiones, ecuaciones y gráficos dejaba la contribución sin un centro. Esta revisión conserva los hechos y cambia el orden: problema operativo, mecanismo físico, decisión causal, evidencia y límite.

## Cinco pasadas de claridad

1. **Clutter — major.** Antes: varias secciones extendían propuestas y diagnósticos antes de explicar la ruta ejecutada. Ahora: el cuerpo principal sigue un método restringido y una pregunta; pruebas y estudios extensos están en el suplemento. El original completo queda archivado.
2. **Actores y verbos — major.** Antes: formulaciones como «el framework separa preguntas» no decían qué hace el programa. Ahora: la DAE predice, el filtro condiciona, el banco compara, M mezcla y la publicación emite decisiones. Cada verbo tiene una entrada y un resultado.
3. **Arquitectura de frases — major.** Antes: «el componente separado» llegaba después de varias páginas de formulación general. Ahora: la apertura plantea una carga no medida, su restauración y un evento durante recuperación. El lector encuentra el problema antes de la notación.
4. **Términos — critical.** Antes: la proximidad de reconstrucción, inferencia batch y propuesta conjunta facilitaba confundir validación de componentes con solución completa. Ahora: estado, atribución eventual, atribución antes de OFF, recuperación, masas aproximadas y probabilidades calibradas son objetos distintos. E_B/GH31 se preserva; E_J sigue propuesto.
5. **Números — critical.** Antes: el agregado de aciertos ocultaba el origen de la mejora. Ahora: una tabla genera detección, cargas, líneas, extras y alarmas normales desde CSV sellados. Un caso muestra diagnóstico correcto pero tardío; la ablación muestra cero extras a costa de un evento real. No se resta el score de la hackathon al de H04.

## Qué cuenta cada figura

- Arquitectura: dónde entra el modelo y dónde se compara su predicción con datos; la verdad queda fuera de inferencia.
- Topología: ocho PMU frente al catálogo real de nueve cargas y nueve líneas; no se promete localizar cualquier evento en cualquier bus.
- Señales: dos intervenciones de un padre fijado muestran las cuatro familias medidas en las ocho PMU. No se venden como patrones universales de clase.
- Resolución: el banco batch distingue número de fuentes e identidad del soporte; ilustra la limitación por intensidad sin atribuir esos resultados a R11.
- Evolución: intervenciones, matriz M y cambio descompuesto, con el fallo temporal BUS31 visible.
- Compromiso: nominal, mezcla y admisión estricta no dominan todas las métricas; se conserva la pérdida BUS16.

## Aporte real y límite

La parte física consiste en construir las trayectorias candidatas con DAE, red, terminales y operadores correctos; condicionar el estado inicial y conservar la recuperación; y evaluar explicaciones con incertidumbre. No se afirma una nueva ley de Kalman/Bayes, una novedad por el nombre tensor ni una solución de todas las familias. La posible contribución es ese mecanismo ejecutable y su interpretación, respaldados por comparaciones bajo un contrato explícito. La confirmación final depende de C01 completa y de la revisión de literatura/afirmaciones.

## Preservación e integración futura

No se modifican planta, método, umbrales, semillas, métricas ni baselines. Las ilustraciones nuevas leen solo el H04 ya abierto: padre H002, par MATCH/OUT, primera carga/primera línea y BUS31 para el fallo declarado. La selección se registra en un manifiesto, sin usar resultados parciales C01.

El build genera tablas, macros y figuras desde copias con hash. Cuando el ejecutor congelado importe C01, un adaptador editorial en P07 preservará esta narrativa y colocará sus resultados principales y el detalle suplementario. Esa adaptación no cambia el ejecutor ni la evaluación. La revisión es del mismo agente integrador, no un peer review independiente.
