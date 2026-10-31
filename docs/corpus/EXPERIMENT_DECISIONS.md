# Qué incorporamos ahora y qué necesitaría una campaña propia

## Artículo actual: cerrar, no reiniciar

La pregunta central es si conservar historias de recuperación permite una
atribución oportuna de eventos sucesivos con una carga de alarmas aceptable.
El valor de P07 depende de una diferencia concreta respecto a precedentes y
de resultados completos. No se declara resuelto porque un piloto tenga
96/96, porque el banco sea físico o porque una tabla se llame tensor.

| Decisión | Acción actual | Evidencia que corresponde |
|---|---|---|
| Método principal | Mantener R11 y nominal congelados | Código/sellos y resultados H04; C01 al cerrar |
| Comparación profesional | Ambos ExtraTrees en continuo; Chen en aperturas persistentes y normales | Mismos registros elegibles, fallos, exposición, censuras e intervalos parentales |
| Aporte físico | Explicar predictor, estados, terminales y recuperación | Ecuaciones del artículo y contrato de implementación |
| Mejoras frente a hackathon | Mostrar capacidades y diferencias bajo contratos comunes | No extrapolar el score H04 al leaderboard oficial |
| Figuras | Una pregunta por figura; conservar las aprobadas | Señales y M/ΔM ya provienen de H04; C01 aportará resultados completos |
| Imagen de eventos | No cambiar PDF ni PNG | Verificación de hashes antes/después |
| Banco simultáneo E_B | Mantener como evidencia auxiliar calificada | Prior efectivo y Top-3 condicionado explícitos; no promover al centro del paper |
| Material antiguo valioso | Conservarlo en corpus y suplemento independiente | No sumar todas las historias al artículo principal |

## Continuación DICE: pruebas discriminantes, no promesas

Estas decisiones organizan X01–X05 ya formuladas. No autorizan cambiar C01
ni lanzar silenciosamente una campaña nueva mientras ocupa el equipo.

| Pregunta | Comparación mínima | Lo que falsaría el beneficio | Estado |
|---|---|---|---|
| ¿La aceleración conserva el cálculo? | Legacy GH31 vs caché/lotes, evidencias y momentos completos | Cambiar posterior/ranking fuera de tolerancia | PASS en seis fixtures; replay físico pendiente |
| ¿Solo faltaba un normalizador? | Legacy y normalizado con igual prior declarado/efectivo bien documentado | Atribuir el cambio de cardinalidad a mejor física | Control analítico PASS; exactitud física corregida desconocida |
| ¿El contexto cambia la firma? | Nominal vs recentrado solo vs recentrado + E_i, mismo horizonte/datos | E_i no mejora frente al recentrado dentro de su error numérico | Derivadas mixtas DAE y trayectorias nuevas pendientes |
| ¿Integrar contexto aporta información útil? | Punto estimado vs incertidumbre calibrada, con logdet | Covarianza absorbe fuentes o empeora cobertura/log-loss | Núcleo algebraico verificado, prueba física pendiente |
| ¿Ayuda más horizonte o un mejor algoritmo? | 1/2/4/10 s para controles equivalentes | Atribuir a E_i una mejora obtenida solo al observar más datos | Requiere respuestas físicas para cada horizonte |
| ¿La confusión es informacional? | Respuestas no lineales de competidores frente al surrogate | Declarar inevitable un error que desaparece con mejor modelo | Control de alta fidelidad pendiente; no cota global automática |
| ¿La confianza es útil? | Riesgo/cobertura, log-loss y tamaño/cobertura de conjuntos | Masa alta con errores frecuentes o conjuntos enormes | Protocolo separado; no recalibrar en C01 |
| ¿Puede usarse a 30 fps? | Tiempo de adquisición/cola/cómputo y decisión, p50/p95/p99 | Atraso acumulado, descartes o posterior alterado por optimización | No demostrado; kernel local p99 supera 33.3 ms |

Antes de una afirmación nueva sobre E_B corregido se requieren sus arrays
originales D/Q/Qij o una campaña sucesora explícita, que ya no sería replay
del baseline. Antes de simultaneidad en el generador F01 se valida el operador
correspondiente: el contrato de una intervención activa no se elimina por texto.

## Ideas para después, sin convertirlas en bloqueos del envío actual

- Atlas predictivo de confusiones, cantidad/ubicación de PMU y sensores caídos.
- Group LASSO adaptado al mismo problema de entradas, estados y canales.
- Transferencia PowerDynamics/ANDES con operadores y mediciones armonizados.
- Generación, fallas e integridad con pruebas propias; E8 sigue desconocido.
- Residuo aprendido sin etiquetas de fuente, solo si aporta valor en un
  experimento distinto de física pura y evita memorizar identidades.
- Refinamiento DAE selectivo con control de masa omitida y normalizadores.
- GPU o precisión mixta después de localizar y medir el cuello de botella.

## Criterio de incorporación de una idea al paper

Entra en **método** si está en el código evaluado; en **resultados** si tiene
salida ejecutada y denominador; en **discusión** si explica un resultado con
sus límites; en **trabajo futuro** si necesita operadores o pruebas nuevas.
Queda en este corpus si añade ambición pero no claridad al argumento central.

Ninguna idea nueva reescribe las condiciones del examen C01. Una derrota
se informa y limita las afirmaciones; no dispara otra corrección por bus.
