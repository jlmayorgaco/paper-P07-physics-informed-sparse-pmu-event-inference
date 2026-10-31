# P07 — la historia que debe entender el lector

**Pregunta:** con ocho PMU y un modelo imperfecto, ¿qué intervención física explica mejor la historia observada, dónde ocurrió y cuándo tenemos evidencia suficiente para decirlo?

## La idea en seis pasos

1. Recibimos V, I terminal, frecuencia y ROCOF de ocho PMU, sin etiquetas ni tiempos verdaderos.
2. El modelo de red, máquinas, controles y cargas predice cómo una intervención en cada activo candidato afectaría esas ocho PMU.
3. En cada instante preguntamos si una carga o línea cambió en algún momento de los últimos 10 s; la predicción parte del estado estimado entonces, no de cero.
4. Comparamos predicción y datos. El filtro maneja estado/ruido; la intensidad de carga se integra y las hipótesis físicas compiten. Cada reporte se cuenta una vez.
5. M resume la masa de las fuentes admisibles. ΔM distingue evolución dentro de los modelos y cambios en sus pesos. Esa identidad no es por sí sola una invención matemática.
6. Publicamos alarma y diagnóstico cuando lo permiten las reglas congeladas; seguimos los estados durante la restauración. OFF no significa que la oscilación terminó.

## Dónde entra la física

En las ecuaciones DAE, Kirchhoff, la ley P/Q de la carga, el cambio de topología de la línea, la corriente orientada de un terminal, y la evolución del estado de máquinas/controles. La física genera la predicción que se contrasta. R11 no usa un clasificador aprendido de etiquetas de bus ni promete un Kalman globalmente óptimo.

## Qué aporta este trabajo

El aporte que defendemos es un mecanismo ejecutable y trazable para comparar intervenciones y recuperación con PMU dispersas, acompañado por un análisis de cuándo sus respuestas son distinguibles. La evidencia separa reconstrucción de estado, resolución de fuentes y decisiones causales. No se reclama novedad solo por usar Bayes, Kalman o un tensor. La novedad diferencial y la fuerza final de la comparación deben revisarse con C01 completa.

## Qué muestran realmente los resultados ejecutados

La tabla siguiente se genera del H04 sellado, ya abierto como desarrollo. Cada columna de familia exige familia y fuente correctas emitidas antes de OFF.

| Método | Cargas a tiempo | Líneas a tiempo | Extras |
|---|---:|---:|---:|
| Physical bank (5 models) | 26/27 | 27/27 | 4 |
| Physical bank (nominal) | 27/27 | 27/27 | 7 |
| ExtraTrees reference | 0/27 | 27/27 | 3 |
| ExtraTrees short | 0/27 | 27/27 | 3 |
| Onset-witness ablation | 25/27 | 27/27 | 0 |

El resultado no es que la física gane en todo: aquí las líneas empatan. La ganancia frente a estos dos adaptadores ExtraTrees está en cargas. La mezcla reduce extras frente al nominal, pero llega tarde en BUS31. La admisión más estricta elimina extras, pero rechaza una carga verdadera en BUS16. Son 18 intervenciones repetidas en tres condiciones, no 54 eventos independientes, y no es el score oficial de la hackathon.

## Cómo leer las figuras

1. **Arquitectura:** datos → modelo → hipótesis → evidencia → M/ΔM → decisión. La verdad queda fuera de inferencia.
2. **Red:** qué PMU existen y qué nueve cargas/nueve líneas admite realmente el banco. No se promete cualquier familia en cualquier bus.
3. **Señales:** una carga y una línea del mismo padre muestran V/I/f/ROCOF en las ocho PMU. Son ejemplos físicos, no reglas universales de clasificación.
4. **Resolución:** el estudio batch muestra que fuentes débiles se confunden aunque las más intensas se resuelvan. No es el mismo estimador que R11.
5. **Evolución temporal:** verdad reservada, M y la descomposición de su cambio; el caso BUS31 permite ver por qué un acierto eventual puede llegar tarde.
6. **Compromiso:** los puntos muestran simultáneamente aciertos a tiempo y extras; no se esconde la pérdida del caso BUS16.

## Dónde quedaron las exploraciones

El suplemento conserva pruebas, estado oculto, errores de modelo, recentrado, banco de 137 soportes, propuestas conjuntas y pilotos. El texto anterior completo y su PDF están archivados. El artículo principal sigue una pregunta; no obliga al lector a reconstruir la historia de versiones.

## Qué sigue abierto

C01 continúa con R11, nominal, ExtraTrees y Chen2016 congelados. No usamos sus resultados parciales para elegir métodos ni para llenar este borrador con cifras inventadas. El build incorpora automáticamente la comparación al terminar, manteniendo esta narrativa. E_B/GH31, planta, baselines y RAW0002 se conservan. El siguiente paso es interpretar la confirmación y cerrar el envío, no arreglar otro bus.

**Archivos:** el artículo legible está en `output/pdf/P07_Event_Attribution_Article.pdf`; el suplemento y el paquete completo permanecen por separado.
