# Contexto para revisar P07 — 30 de octubre de 2026

Adjunto la versión actual **Recovery-Aware Physical Event Attribution From
Sparse PMUs**, artículo principal de 13 páginas, sin suplemento anexado.
Revisa este PDF de nuevo; no supongas que coincide con la versión anterior
de 19 páginas titulada Physics-Informed State Reconstruction and Event-Source
Inference. La revisión anterior se conserva y sus observaciones valiosas
se contrastaron con el método y la evidencia disponibles.

## Qué cambió

- El hilo central es R11: atribución causal de cambios de carga y línea con
  ocho PMU, onset desconocido y recuperación conservada después de OFF.
- Se describe el predictor local derivado de la DAE, la memoria instrumental,
  la discrepancia estadística, las masas activa/causa y un algoritmo por reporte.
- El banco E_B de 137 soportes, con onset conocido y 32 coordenadas, es un
  estudio auxiliar distinto. Se califican su prior efectivo y la diferencia
  entre Top-1 conjunto y Top-3 condicionado a conocer dos fuentes.
- DICE-PMU (firmas dependientes del contexto y su incertidumbre) es un candidato
  separado. Hay pruebas algebraicas/sintéticas de sus núcleos; no se afirma
  validación física ni superioridad de ese método completo.
- El esquema IEEE-39 es un unifilar eléctrico. La imagen de tipos de eventos
  de RAW0001 y el diagrama de bloques aprobado se preservaron.

## Estado de la evidencia

C01 sigue ejecutándose con métodos, casos, umbrales y métricas congelados.
Los resultados H04, incluido 53/54, son desarrollo; no son confirmación ni
un nuevo score oficial de la hackathon. C01 comparará R11, nominal y ambos
ExtraTrees en secuencias continuas; Chen2016 solo en aperturas persistentes.
RAW0001 es evidencia retrospectiva. RAW0002 no se ha abierto.

El banco batch histórico tiene una discrepancia de normalización de las
hipótesis de una fuente, verificada en su commit original. Su corrección
existe en un candidato, sin cambiar los resultados archivados. El artículo
lo explica: no transfieras ese defecto a R11 ni des por recalculadas las
métricas físicas del E_B. Faltan sus arrays originales para ese replay.

## Revisión que solicito

Actúa como revisor técnico independiente y escéptico. No asumas que las
conclusiones anteriores o estas explicaciones son correctas: contrástalas
con lo que realmente contiene este PDF.

1. Resume en tres frases el problema, el método ejecutado y su contribución
   diferencial frente a los trabajos más cercanos. Si la novedad no alcanza,
   explica exactamente qué componente tiene un precedente equivalente.
2. Señala errores concretos por sección, ecuación o figura; distingue un error
   demostrable de algo que no puedes verificar sin código o datos adicionales.
3. Construye una tabla afirmación → evidencia visible → limitación → corrección
   mínima. Separa detección, clasificación, fuente, restauración y calibración.
4. Indica qué cerrará C01 y qué no puede demostrar, evitando interpretar
   resultados aún pendientes como ejecutados o proponer reajustar el examen.
5. Evalúa si la narrativa se entiende y si cada figura ayuda. **No propongas
   cambiar la imagen de tipos de eventos:** es una restricción del autor;
   puedes señalar cualquier limitación científica en su interpretación.
6. Termina con una lista corta y priorizada de cambios imprescindibles para
   circular a coautores y para enviar a IEEE Access. Distingue una corrección
   del artículo actual de una investigación futura DICE o multifamilia.

No busco aprobación automática ni otra lista genérica de algoritmos. Quiero
un dictamen concreto sobre este manuscrito, conservando los resultados útiles
y sin presentar nuevas propuestas como capacidades ya demostradas.
