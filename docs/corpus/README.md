# Corpus científico de P07

Este es el punto de entrada para continuar el proyecto sin reconstruir sus
decisiones desde el chat. Separa lo que deseamos resolver, lo implementado,
lo medido y lo propuesto. No reemplaza los snapshots ni los protocolos.

Actualización: [X02 completó la prueba física E_i en IEEE-39](../ei-x02-results.md).
Mejora la predicción e intensidad en ese contrato; no añade aciertos de
localización al recentrado. Familia y ON/OFF son conocidos. La incertidumbre
conjunta y su beneficio dentro de R11 siguen sin demostrarse.

## La decisión vigente

El artículo actual estudia **atribución física de cargas y líneas sucesivas
con ocho PMU**, incluyendo la respuesta que persiste después de restaurar
una intervención. Su método es R11, con nominal como correferencia.
C01 es su evaluación confirmatoria, todavía en ejecución al integrar este
corpus. No se cambia por resultados parciales o por sugerencias de otro chat.

El objetivo de largo plazo sigue siendo detectar, clasificar y localizar
eventos de la hackathon, estimar sus tiempos y severidades y generar datos
físicos útiles. Ese objetivo completo no es la capacidad demostrada hoy.

## Leer en este orden

Actualización 31-oct: [nuevo chat, ZIP reproducido y decisiones de
integración](REVIEW_6ae64dc7.md). El piloto externo clásico, la comprobación
física F01 X04 y C01 tienen contratos separados.

1. [Síntesis de objetivos, decisiones y aportes](CONVERSATION_SYNTHESIS.md).
2. [Resultados rastreables](RESULTS.md): generados desde los CSV/JSON, con
   contrato e interpretación; [CSV](RESULTS.csv) para reutilizarlos.
3. [Ecuaciones y estado de implementación](EQUATIONS_AND_STATUS.md).
4. [Ideas y decisiones](IDEAS.csv): qué entra en P07, qué queda condicionado
   y qué no debe presentarse como resultado.
5. [Nueva revisión compartida](REVIEW_6ae55d7c.md), nueve respuestas leídas,
   con correcciones respecto del borrador antiguo.
6. [Qué incorporar y qué experimento lo justificaría](EXPERIMENT_DECISIONS.md).

`MANIFEST.json` conserva hashes de las fuentes numéricas y comprobaciones de
integridad. `review_source.json` identifica el enlace y los 18 mensajes de la
revisión. No contiene una supuesta auditoría de su ZIP: sus descargas no
estuvieron disponibles como archivos verificables en esta sesión.

## Reproducir la tabla de resultados

Desde la raíz de P07:

```powershell
C:/Users/walla/anaconda3/python.exe scripts/build_research_corpus.py
```

El generador lee fuentes archivadas y verificadas. No lee predicciones
parciales de C01, no simula, no reajusta y no modifica los métodos.
`RESULTS.md` y `RESULTS.csv` son salidas generadas; no editar sus cifras a mano.

## Continuidad hacia los repositorios de origen

- Cierre causal: `SGSMA26-Physics-Informed-AD/PAPER_CLOSURE_START_HERE.md`.
- C01: `experiments/PAPER_CONFIRMATORY_C01/RUN_CONTINUITY.md` en ese repo.
- Simulador: `SIM0001_START_HERE.md` y `SIM0001_CURRENT.json`; F01 sigue siendo
  candidato de investigación con terminal BUS5 provisional y limitaciones.
- Extensión DICE: `experiments/PAPER_METHOD_DICE_X01/METHOD_AND_EXPERIMENTS.md`.
- El corpus no autoriza abrir RAW0002, publicar, hacer push ni tocar baselines.

La imagen original de los eventos es inmutable. El diagrama aprobado y el
unifilar eléctrico se conservan. La próxima incorporación principal será
la comparación completa de C01, con sus fallos y denominadores.
