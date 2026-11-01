# Propuesta de comparación SIM → RAW para un candidato sucesor

Estado: **diseño propuesto, no ejecutado**. No sustituye C01 ni autoriza a reutilizar sus resultados como desarrollo. No supone que R11 vaya a superar a los comparadores.

## Preguntas y brazos

| Pregunta | Comparación que la responde |
|---|---|
| ¿Hace falta el banco de historias? | R11 frente a predictor causal de estado físico/instrumental retenido con prueba residual de intervenciones, mismo modelo y publicación. |
| ¿Aporta la mezcla de redes? | Una frente a cinco redes, misma lógica de admisión/publicación; separar este contraste del anterior. |
| ¿Aporta respecto a ML con acceso comparable? | ExtraTrees reentrenado con los mismos padres y presupuesto declarado de ajuste, más las referencias ET ya congeladas. |
| ¿Mejora el artefacto de la hackathon? | Artefacto histórico congelado y candidato sobre un mismo replay y contrato de métricas, sin trasladar el resultado al leaderboard. |

Mantener separados el carril de aperturas persistentes de Chen y el carril continuo con cargas/OFF. Un método sin operador de cierre no debe recibir artificialmente restauraciones oracle ni ser penalizado como si prometiera esa función.

## Unidad de partición

El grupo es `physical_parent_id`: una trayectoria generada por una historia de intervenciones, punto de operación y estado inicial. Sus condiciones pareadas, realizaciones de ruido, PMU, ventanas, recortes temporales y características heredan el mismo grupo. Si una misma secuencia física se repite con variaciones para un contraste pareado, agrupar toda la familia de secuencias. Registrar también la genealogía respecto a campañas anteriores.

Para un banco nuevo, asignar aproximadamente 70% de grupos a desarrollo y 30% a test antes de observar resultados. Dentro del 70%, usar validación agrupada o una partición interna 80/20: en ese ejemplo el total es 56% ajuste, 14% selección y 30% test. Si hay pocos grupos, priorizar una validación agrupada con tamaño adecuado por estrato antes que imponer porcentajes exactos.

Estratificar por familia, activo, severidad, separación ON/OFF, recuperación y condición de red, cuando el tamaño lo permita. No redistribuir después de ver qué método falla. Publicar conteos de padres y eventos, no sólo número de ventanas.

SIM0001–SIM0019 ya usados en diseño pueden aportar desarrollo y regresiones retrospectivas; no se vuelven vírgenes al cambiar su semilla de split. Crear padres nuevos en una carpeta sucesora. Conservar F01, R1, R1.1, R5C.2 y todos los candidatos previos. Ejecutar desde las configuraciones congeladas, sin `prepare.py` históricos sobre baselines.

## Qué significa ajustar cada método

R11 no tiene una cabeza supervisada de fuentes. Documentar por parámetro si se fija por física, se estima del prefijo causal o se selecciona con desarrollo: diccionario, prior de severidad, covarianza/ruido, banco R/X, tamaño del beam, horizontes, umbrales y reglas de publicación. No utilizar información posterior del registro para la normalización ni la verdad para recortar ventanas.

Para ML, ajustar modelos, selección de características y umbrales sólo dentro de desarrollo. Usar el mismo catálogo, canales causales, prefijo y cronología de emisión; conservar la diferencia entre modelo histórico, modelo reentrenado y nuevas variantes. Registrar el número de configuraciones intentadas en ambos enfoques. No exigir que tengan idéntico número de parámetros: la igualdad relevante es acceso a datos y oportunidad de selección.

F01 sigue siendo `FROZEN_RESEARCH_CANDIDATE`, no simulador oficial validado. BUS5 5–6 es provisional. Las hipótesis alternativas, si se ensayan, pertenecen a candidatos nuevos y quedan trazadas. Las pruebas con mismo modelo y punto F01 miden interpolación dentro de esa familia; para afirmar robustez hacen falta cambios de estado operativo, historia previa, ley de carga/regulación e instrumentación fuera del banco, definidos antes del test.

## Congelación y controles de independencia

Antes de abrir test, archivar hashes de código, diccionario, modelos ajustados, configuración, mapeo PMU, métricas y manifiesto de padres. Separar observaciones de verdad reservada. Sellar predicciones antes de puntuar. Registrar todos los rechazos físicos y fallos de inferencia; no reemplazar silenciosamente los casos fallidos ni calcular sólo sobre ejecuciones exitosas.

Verificar que dos ventanas con el mismo padre no crucen particiones y que ningún prefijo del test haya servido para elegir la configuración global. La adaptación causal del prefijo del registro es admisible sólo si pertenece al método previamente definido y todos los competidores tienen un contrato comparable. No abrir RAW0002.

## Métricas mínimas y reparaciones propuestas

- Detección, familia/fuente correctas y atribución **antes del OFF**, con denominadores separados.
- Tiempo de alarma y tiempo del primer diagnóstico de fuente. Informar «fuente correcta al primer stop» sólo si se conoce la fuente en ese instante; un diagnóstico posterior tiene otra métrica. Tratar omisiones y censura sin descartarlas.
- Alarmas no emparejadas por hora, falsas alarmas en normales y fracción de registros normales con alguna alarma. Publicar exposición efectiva y planificada.
- Restauraciones sin evento emparejado **y** restauraciones prematuras de eventos emparejados. Informar adelanto, tiempo activo perdido, retraso después de OFF y episodios abiertos al final. La tolerancia temporal debe fijarse antes de ver el test.
- Disponibilidad, abstenciones, errores por datos ausentes y comportamiento en clases fuera del catálogo.
- Coste computacional, memoria y retraso de procesamiento en el hardware declarado; no confundir tiempo físico de detección con tiempo de cómputo.

Hacer contrastes pareados con remuestreo por padre físico, manteniendo juntos sus condiciones y ruido. La poca cantidad de padres limita incluso el bootstrap; mostrar distribución por padre y por activo. Las cotas Poisson para cero alarmas deben declararse condicionales a ese modelo, no tratarlas como garantías bajo dependencia arbitraria.

La auditoría del evaluador C01 va en un sucesor transparente. Preservar el evaluador y reporte originales. Establecer las reglas corregidas sin consultar predicciones parciales; después mostrar ambos resultados con una explicación de las diferencias. No usar esta reparación para cambiar el detector ni elegir umbrales sobre C01.

## Criterio de interpretación

Elegir una variable primaria antes del test —por ejemplo atribución oportuna— y declarar las restricciones operacionales de alarmas, latencia y disponibilidad. No ocultar un deterioro de otra variable detrás de una precisión agregada. Una diferencia puntual favorable no basta para afirmar superioridad; informar el intervalo pareado y los compromisos. Si se necesita una noción de equivalencia práctica, fijar su margen con requisitos operacionales antes del test, no después de observar diferencias.

El falsificador del banco es un predictor sencillo que logra resultados equivalentes dentro de ese margen con menor coste. El falsificador de la transferencia es la degradación causal en RAW bajo el contrato congelado. Ambos resultados son publicables si delimitan con precisión cuándo basta una representación sencilla.

## Replay RAW0001

RAW0001 ya influyó en la calibración de F01. Rotular todo resultado como **transferencia retrospectiva sobre datos previamente utilizados**, incluso si el detector nuevo no vio directamente sus etiquetas durante ajuste.

Antes del replay, crear un adaptador sucesor de entrada e integridad. La guardia RAW del runner congelado no se elimina. Validar unidades, terminales, timestamps, esquema, disponibilidad y tratamiento causal de faltantes. No completar datos usando futuro, reiniciar desde la verdad ni saltar segmentos difíciles. La abstención es una salida medible, no un éxito.

Producir dos tablas: (a) evaluación de las familias/fuentes admitidas, con reglas previas de elegibilidad; (b) cobertura y comportamiento durante todo el registro, incluyendo fallas, generación, integridad y ausencias. No presentar (a) como precisión del sistema completo. Cualquier ajuste después del replay inicia una nueva ronda de desarrollo y debe declararse.

Comparar el artefacto histórico y el candidato con los mismos tiempos de observación, anotaciones y política de puntuación. Si la anotación oficial requerida no está disponible, declarar la convención local. Un score de RAW0001 no es el score oficial de la hackathon.
