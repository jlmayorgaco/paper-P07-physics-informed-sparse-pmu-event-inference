# Segunda planta: transferencia fuera del simulador del banco (protocolo congelado)

Pregunta: ¿cuánto se degrada cada método cuando los registros se generan con una física que no es la suya?

Datos: las 12 secuencias de eventos del TEST de B01 (mismas fuentes, instantes y amplitudes) re-simuladas con una planta independiente (máquinas clásicas con regulador de estatismo, cargas de impedancia constante, red del `.raw`; sin AVR ni excitación) más 4 registros normales de 120 s. Pasan por el mismo operador PMU y el mismo ruido instrumental, con las mismas semillas. Nada de esto se usa para ajustar umbrales.

Métodos, todos congelados antes de leer estos registros:
- Atribuidor estático (v2, catálogo del banco).
- ML y FIS (ExtraTrees), ajustados en TRAIN de B01 con umbral fijado en CAL (como en el estudio de líneas base).
- ML+ y FIS+: los mismos modelos con TRAIN re-ruidoso (20 realizaciones nuevas de ruido instrumental por cada padre de TRAIN, a partir de sus respuestas físicas sin ruido). Umbral fijado en CAL de B01.
- El banco dinámico: no se ejecuta aquí (necesita bancos de partículas por registro, construidos con Julia); queda preparado el conjunto exportado con el formato de entrada del banco.

Medidas: detectados, familia, Top-1 y Top-3, extras, alarmas en registros normales, registros con las seis fuentes bien (exacto de Clopper–Pearson). Se compara cada método con su propio resultado en el TEST original de B01. Un resultado en contra no se corrige después.

Enmienda de recursos (6-nov-2026), antes de leer ningún resultado: una primera ejecución fue detenida por falta de memoria y no produjo resultados. Para caber en la memoria libre (1,5 GB) los modelos con datos re-ruidosos usan 4 realizaciones de ruido por padre (96 registros), 60 árboles y relación de negativos 5:1. Los modelos pequeños no cambian.
