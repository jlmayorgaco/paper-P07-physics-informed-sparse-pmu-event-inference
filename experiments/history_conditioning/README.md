# ¿Condicionar por la historia mejora la atribución de fuente? Estudio en una planta reducida de IEEE-39

Código y resultados del estudio que responde a la segunda revisión externa (reducción de historias, firmas de segundo orden, marginalización de la incertidumbre previa).

- `PLAN.md`: protocolo congelado con hash antes de la cohorte de prueba (`results/TEST_FREEZE.sha`).
- `dynamics.py`: planta reducida (máquinas clásicas, regulador con estatismo, cargas de impedancia constante, red del `.raw`).
- `exp1_history.py`: seis predictores sobre las mismas observaciones. `analyze.py`: intervalos bootstrap pareados.
- `raw_cache.py`, `exp2_raw.py`: validación de solo lectura contra RAW0001 (el caché de RAW se regenera, no se versiona).
- `results/`: filas por escenario de las ocho celdas y los resúmenes.

Requiere el repositorio científico `SGSMA26-Physics-Informed-AD` junto a este (red, topología y RAW0001). Ejecución: `python raw_cache.py`; `python exp1_history.py 1000 1200 <ventana> <ruido> <historia> <desajuste> <etiqueta>` (se escribe en `results/<etiqueta>`).

Resultado: ningún predictor condicionado por la historia mejora la decisión de fuente respecto de la firma nominal recentrada en ninguna de las ocho celdas; ver `PLAN.md` para el criterio y `results/TEST_RESULTS.json`.
