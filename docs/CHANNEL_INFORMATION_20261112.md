# Diagnóstico nominal de información de canales P07

Fecha: 2026-11-12. Estado: cálculo exploratorio reproducido e integrado como diagnóstico nominal; separado de la evaluación del detector.

## Pregunta y alcance

¿Cuánto cambia la separación nominal de firmas del banco P07 al pasar de tensiones a tensiones más corrientes, y luego a las 47 coordenadas PMU? Este cálculo compara medias deterministas de los 18 operadores de fuente de R11 bajo una sola covarianza gaussiana nominal. No ejecuta filtros de decisión, no calibra umbrales y no mide detección, localización o desempeño.

La fuente de operadores es la copia CAL nominal `C03_a1adb9f9adcf_nominal`, con 300 reportes de prefijo y sin verdad leída según su `READY.json`. Se leyó y copió solo el banco CAL y su registro `READY`; no se ejecutó código de C03, no se leyó TEST ni se modificó ningún archivo de C03. Para evitar incluir el banco fuente de 43 MB, `prepare_snapshot.py` guardó una instantánea compacta de 11,330,109 bytes con los operadores y la covarianza necesarios. El hash del banco fuente antes y después de extraerla fue idéntico.

El mapa de terminales F01 y el mapa R11 usado en el runtime tienen el mismo SHA-256 (`74c1ba…bd9be`) y son byte por byte idénticos. BUS5 se conserva como la hipótesis histórica provisional 5–6, terminal 5; este resultado no confirma la identidad del CT productor. Las coordenadas se ordenaron siguiendo el runtime R11: `Vmag[8], Vangle[8], Imag[8], Iangle[7], f[8], ROCOF[8]`. Así, V contiene 16 coordenadas, V+I contiene 31 y el contrato completo contiene 47.

## Diseño fijado

- Fuentes: los nueve buses de carga y nueve líneas del `assets.json` R11, en el orden congelado del runtime.
- Intervenciones: carga con severidad fija `0.10` para cada firma; línea con el operador discreto de apertura completa, sin parámetro continuo de severidad. No se ajusta ni perfila una nuisance; las medias son condicionales a esos valores.
- Historia: desviación inicial del estado igual a cero; muestra de onset seguida por el operador stay. Horizontes de 3, 15 y 30 reportes (0.1, 0.5 y 1.0 s a 30 fps).
- Covarianza: una misma covarianza quiet/null de 47 dimensiones, aplicada a reportes brutos apilados. Se incluyen correlaciones entre canales y entre reportes bajo el observador nominal.
- Métrica: `D² = dᵀΣ⁻¹d`, distancia de Mahalanobis cuadrática entre cada par dirigido de medias fijas. No es una tasa, log-verosimilitud completa ni score de decisión.

La covarianza se reconstruye desde la representación de innovaciones completa del filtro nulo, `m[k+1]=T m[k]+K e[k]`, `y[k]=J m[k]+e[k]`, con `e[k]~N(0,S)`. El resultado es la covarianza de la secuencia de reportes brutos. Para cada contrato de canales se extrae la submatriz marginal de esa covarianza y se factoriza por Cholesky tras escalar por desviación estándar. No se ponen señales a cero y no se reutilizan innovaciones que dependan de canales omitidos.

## Resultados del cálculo

Hay 306 pares dirigidos por horizonte y 918 filas en total. Las corrientes añaden separación condicional positiva en los 306 pares de cada horizonte. La mediana de `(D²_VI−D²_V)/D²_V` sobre todos los pares es 27.3% a 3 reportes, 17.4% a 15 y 18.1% a 30. En 11 de los 54 casos fuente-horizonte cambió el competidor más cercano al pasar de V a V+I. Añadir frecuencia y ROCOF no cambió ningún competidor más cercano en este conjunto finito, aunque su término condicional fue no negativo.

Estos porcentajes describen solo las firmas y la covarianza nominales fijadas aquí. No demuestran que las corrientes mejoren un detector en línea ni que predigan errores o se generalicen a otros estados, severidades o plantas. La comparación tampoco resuelve la hipótesis de instrumentación provisional BUS5.

## Controles matemáticos

Los controles se evalúan antes de escribir los CSV:

- La identidad `S⁻¹S=I` tiene error absoluto máximo `8.88e-16`; S pasa Cholesky.
- Los cinco operadores de cada una de las nueve líneas tienen `u=v=0` exactamente; por tanto, la línea queda como un cambio de operador discreto y no como severidad continua.
- La covarianza temporal recursiva coincide con una transformación explícita de innovaciones en 3 reportes con error relativo máximo `5.95e-16`.
- Para todos los pares y horizontes, `dᵀΣ⁻¹d` en reportes completos coincide con la suma de innovaciones nulas blanqueadas; error relativo máximo `3.06e-15`.
- La descomposición de Schur V más I|V y VI más resto|VI coincide con el cálculo directo; error relativo máximo `1.35e-11` (error absoluto máximo `1.43e-6` en D² grandes).
- El menor incremento condicional calculado es `5.49`; las distancias de los canales anidados son monótonas en los 918 pares-horizonte.

## Artefactos y procedencia

- Código: [`run_channel_diagnostic.py`](../experiments/channel_information_20261112/run_channel_diagnostic.py), [`prepare_snapshot.py`](../experiments/channel_information_20261112/prepare_snapshot.py).
- Salidas: [`diagnostic_summary.json`](../experiments/channel_information_20261112/diagnostic_summary.json), [`pairwise_separation.csv`](../experiments/channel_information_20261112/pairwise_separation.csv), [`nearest_competitor.csv`](../experiments/channel_information_20261112/nearest_competitor.csv).
- Instantánea compacta y metadatos de extracción: `experiments/channel_information_20261112/input_snapshot.npz` y `snapshot_metadata.json`.
- SHA-256 del banco CAL fuente: `6457dd91e8332044854d7a2745b44b11b4af4b7d50a0acef0d6501b047310cd7`.
- SHA-256 de la instantánea compacta: `6102a7a39ee22c0080b4ec0820ef4cf50ece9f77910bd551189fbf9b03fc8140`.
- La identidad de los hashes y el registro de no lectura de verdad están en `diagnostic_summary.json` y `snapshot_metadata.json`.

La integración usa `scripts/build_channel_information_figure.py`, que verifica
los hashes de los CSV y genera la figura y las macros numéricas. El artículo
resume el cociente de separaciones mínimas a un segundo (mediana 1,35; rango
1,03–8,41), que difiere del resumen de todos los pares anterior. El suplemento
documenta la derivación, las amplitudes fijas y los controles. Para el competidor
elegido con V+I, la fracción condicional de corrientes tiene mediana 18,0%
y rango 2,6%–76,6%. Es un cálculo por fuente, no un intervalo poblacional.
