# C01 — ejecución iniciada el 29-oct-2026

## Comprobación del 31-oct-2026, 09:01 (Bogotá)

180 de 342 registros completados; S181 en ejecución. Controlador original y
trabajador comprobados por PID, creación y comando; CPU y logs activos.
Sin BLOCKER, COMPLETE ni PAPER_UPDATED. No se abrió ninguna predicción para
ajustar métodos o adelantar resultados científicos.

Restan 162 registros: 126 de 120 s y 36 de 600 s. Los últimos doce registros
completos de cada duración tardan, en promedio, 7.40 y 28.65 minutos incluyendo
banco, R11/nominal, ML y Chen. La proyección serial es 32.7 horas: alrededor
del 1-nov a las 17:46 en Bogotá para terminar inferencia. Evaluación,
integración y revisión editorial vienen después. Es una estimación condicionada
al ritmo actual; el registro en curso se cuenta completo.

Los once sellos del ejecutor y la imagen original de eventos se verificaron
sin cambios. Fuente: `run/operations/PROGRESS_ETA_CURRENT.json` en C01.
El seguimiento sigue activo y no se lanzó otra instancia.

## Contrato conservado

El ejecutor/evaluador se selló antes de simular y predecir. Se lanzaron las
171 trayectorias físicas y sus 342 observaciones previstas, conservando los
métodos. Esto es estado de ejecución, no una tabla de resultados.

Pruebas antes del examen: asociación temporal sin elegir por origen verdadero,
diagnóstico tardío penalizado, OFF nulo/censura, primera parada persistente,
omisiones por fallo, bootstrap por padre. Un fixture sintético cubrió 342
registros y 1710 combinaciones método/registro. Los cinco prefijos y ambos
ExtraTrees reprodujeron exactamente H04/S012 ya abierto. El fixture no usa
señales ni resultados C01.

La cadena de ejecución exportará señales, construirá bancos solo desde PMU,
ejecutará métodos congelados, sellará predicciones antes de evaluar, generará
intervalos/figuras e importará resultados aquí. No hay reajuste automático.

Seguimiento en el repositorio SGSMA:

- `experiments/PAPER_CONFIRMATORY_C01/run/PROGRESS.json`.
- `run/RECORD_PROGRESS.json`, `run/logs/`, `run/BLOCKER.json`.
- `run/results/SUMMARY.csv`, al terminar evaluación.
- `run/PAPER_UPDATED.json`, al terminar integración y compilación.

Para reanudar: `python -B -X utf8 experiments/PAPER_CONFIRMATORY_C01/execution/pipeline.py run`.
No lanzar una segunda instancia mientras siga activa la primera. Las fases
completas se preservan. Se conserva el catálogo conocido; no se presenta este
ensayo como un examen de fuentes excluidas o como RAW0002.
