# Lectura y adjudicación de la segunda revisión compartida

Fuente: https://chatgpt.com/share/6ae55d7c-8024-83e8-8820-cce9ad9ed3e3

Se leyeron **18 mensajes y nueve respuestas** mediante el contenido renderizado
del chat. No se envió ningún mensaje, archivo ni datos al chat. El contenido
se trata como crítica y propuesta, no como orden de alterar protocolos ni
como una publicación científica revisada por pares.

## Qué versión se revisó

La primera respuesta nombra el manuscrito anterior *Physics-Informed State
Reconstruction and Event-Source Inference From Sparse PMUs Under Limited
Observability*, con 19 páginas principales y 24 suplementarias. P07 ya usa
*Recovery-Aware Physical Event Attribution From Sparse PMUs*, con R11 como
historia central y el suplemento separado. C01 está corriendo, no ausente.
No trasladar la numeración de figuras ni el dictamen de aquel borrador a
esta versión sin verificarlo.

## Las nueve respuestas y su uso

| Respuesta | Idea central | Adjudicación para P07 |
|---|---|---|
| 1. Revisión científica | Cuatro líneas mezcladas; falta comparación equivalente y claridad de contribución | Aceptar el diagnóstico editorial; el artículo actual ya separa B2, E_B, E_J y R11. C01 aborda la confirmación causal |
| 2. Contribución original | Interacciones físicas, soporte y cardinalidad no equivalen a localizar cualquier evento | Incorporar la distinción; no cambiar el centro del paper por un resultado auxiliar con replay pendiente |
| 3. Physics-informed | Physics-based Bayesian inference describe mejor el mecanismo que PINN o PI-ML | Aceptar y explicitar dónde entran ecuaciones y dónde entra estadística |
| 4. Tiempo real | Gram y estadísticas suficientes antes de GPU; separar evidencia física y tiempo de cómputo | Ya existe Gram por soporte. X01 verifica caché/lotes localmente; no adoptar la cifra externa de 1.54 ms |
| 5. Figuras y despliegue | Una pregunta por figura; predicción, residuo y decisión; adquisición separada de inferencia | Conservar eventos y diagrama aprobados; no dibujar como implementada una arquitectura industrial propuesta |
| 6. Valor científico | Atlas de dificultad, respuesta-oráculo, riesgo selectivo y fairness | Registrar como pruebas de continuación. La asociación retrospectiva actual no es un atlas predictivo validado |
| 7. Giro algorítmico | Qij, E_i, contexto incierto, evidencia causal y refinamiento selectivo | Integrar en la formulación X01 existente. No renombrar R11 ni adjudicarle simultaneidad y E_i inexistentes |
| 8. Prototipo DICE | Declara pruebas sintéticas y AC de tres buses, propone ZIP y manuscrito nuevos | Evidencia externa reportada, no reproducida aquí; no importarla como resultados IEEE-39 |
| 9. Rectificación | Sí hay miles de simulaciones históricas, pero faltan arrays para nuevo replay | Coincide con el inventario: resultados y scripts existen; D/Q/Qij originales de E_B siguen ausentes en esta copia |

## Resultados externos que no se adoptan como mediciones locales

La revisión reporta un piloto sintético con Top-1 15/22/49%, log-loss
7.59/2.81/1.58 y una mejora de 34 puntos con intervalo 23–45. También
reporta un ejemplo AC estático de tres buses, pruebas 12/12 y un
microbenchmark con mediana 1.54 ms en un Xeon virtualizado.

Estos valores pueden motivar hipótesis, pero no se incluyen en las tablas
de resultados de P07: aquí no se descargaron ni ejecutaron sus fuentes,
se desconoce la correspondencia exacta entre el piloto de 100 casos y los
200 casos que menciona después, y los archivos ofrecidos no estaban
disponibles como enlaces descargables verificables. No se requiere subirlos
para cerrar C01; serían necesarios antes de reproducir ese prototipo exacto.

El paquete local X01 es otro artefacto, con hashes propios. Sus seis
fixtures verifican equivalencia algebraica y tienen tiempos distintos.
No se mezclan los resultados de ambos entornos ni los dos programas.

## Correcciones científicas importantes

1. La reducción mediante Gram no es una nueva identidad ni una operación
   ausente del código antiguo. El progreso local es compartir y vectorizar.
2. Preservar el posterior legacy y corregir su prior efectivo son contratos
   diferentes. La condición R0 debe nombrar cuál se desea reproducir.
3. Exactitud 24.4% no certifica un límite físico; el normalizador histórico,
   el surrogate y el prior también afectan el resultado.
4. Qij mejora la fidelidad de respuesta en el diagnóstico T120; no hay una
   ablación pareada de exactitud que pruebe el mismo beneficio de localización.
5. Mejor HVRE tras recentrar no demuestra una posterior conjunta calibrada
   ni identifica de forma única el punto de operación completo.
6. Un clasificador cerrado puede no emitir un bus excluido de entrenamiento.
   Esa limitación no prueba imposibilidad de generalización de otros métodos ML.
7. 30 fps es el contrato de entrada, no un rendimiento extremo a extremo
   demostrado. Los tiempos científicos de alarma y el tiempo de CPU se separan.
8. La literatura citada por el chat no se importa ciegamente. Los precedentes
   ya verificados siguen en la matriz de capacidades; las sugerencias nuevas
   necesitan comprobación primaria antes de añadirlas a la bibliografía.

## Cambios realizados al integrar

Se crea este corpus, con registro de ideas y resultados derivados de archivos.
El método del artículo distingue explícitamente modelo físico y discrepancia
estadística. La discusión concreta qué comparación permitiría atribuir una
mejora a E_i, frente a usar más horizonte o simplemente recentrar.
La guía de construcción corrige la descripción obsoleta de un PDF combinado.
No se alteran métodos, casos, umbrales, semillas, métricas o resultados de C01.

## Decisión para cerrar

No reemplazar ahora P07 por el manuscrito DICE de siete páginas descrito en
el otro chat. Tampoco añadir todos sus experimentos como condiciones de envío.
Conservar R11/C01 para el cierre y la propuesta condicionada como continuación
con controles explícitos. Si la confirmación no respalda una afirmación,
se reduce esa afirmación; no se corrige otro bus sobre el examen.
