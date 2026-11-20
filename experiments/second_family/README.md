# ¿Qué permite clasificar el segundo evento de carga o línea?

Los métodos comparten los instantes de alarma del monitor del artículo. La tarea es identificar la familia del segundo evento antes de su despeje. El protocolo y los pesos se congelaron en `070a569` antes de generar los pares. Los registros duran 40 s y contienen dos intervenciones que no se superponen. Los rotores pueden seguir en movimiento cuando comienza la segunda. El banco de ecuaciones de red y máquinas se construyó con la planta de referencia y se aplicó a la segunda planta del manuscrito. La CNN se entrenó específicamente con simulaciones de esta segunda planta. [Protocolo](PROTOCOL.md) · [Huellas](results/freeze.json)

## Resultados de la prueba ciega

Las predicciones quedaron selladas en `90bbccd` antes de abrir las etiquetas. Cada denominador incluye los eventos que el detector perdió o para los que el estimador se abstuvo. [Predicciones por trayectoria](results/predictions.json) · [Recuento e intervalos pareados](results/scores.json)

| Familia correcta antes del despeje | Carga | Línea | Total |
|---|---:|---:|---:|
| Banco del PDF | 12/18 | 16/18 | 28/36 |
| Estimador de familia con retardo fijo | 12/18 | 16/18 | 28/36 |
| CNN-F adaptada, con o sin sustracción | 8/18 | 16/18 | 24/36 |
| Historias fusionadas, estado físico conservado | 10/18 | 16/18 | 26/36 |
| Historias fusionadas, estado físico reiniciado | 7/18 | 10/18 | 17/36 |

El banco recuperó cuatro cargas que la CNN clasificó como líneas. La diferencia fue de 11,1 puntos porcentuales (intervalo bootstrap pareado del 95 % de 2,8 a 19,4 puntos). Con cuatro discordancias, la prueba exacta bilateral dio *p* = 0,125. El estimador de retardo fijo coincidió con el banco original en los 28 segundos eventos con alarma. Dentro del par de bancos fusionados, conservar el estado físico ganó diez diagnósticos y perdió uno respecto al reinicio, un saldo de 25,0 puntos (intervalo de 11,1 a 38,9 puntos, *p* exacta = 0,0117).

El detector común perdió seis cargas y dos líneas. Emitió cero alarmas en 5,88 horas de reposo ciego (límite superior unilateral del 95 % de 0,51/h, presupuesto de 1/h) y 58 alarmas sin correspondencia en las 36 trayectorias con perturbaciones. El criterio de acierto evalúa la familia del segundo evento y su plazo. La localización exacta del activo requiere otra comparación.

## Comparadores

* **Decisión publicada en el PDF.** Se ejecutó el código congelado del banco de historias con sus 18 fuentes, las ocho PMU y el umbral original. Se retuvo la familia del activo elegido al dispararse la alarma. Para la comparación principal se cobró el mismo retraso a todos. El informe también incluye el resultado en el instante original de publicación.
* **CNN-F de Li y Wang, adaptada.** La red recibe las partes reales de los autovalores DMD de magnitud de tensión, frecuencia y potencia activa aproximada, y los valores singulares de tensión y frecuencia. Disponemos de siete pares utilizables de ángulos de corriente y tensión. Se centra cada señal en el prefijo de reposo. Para la segunda alarma se extrapola la respuesta anterior desde el tramo disponible, se resta y se extraen los modos de los 30 reportes siguientes, contando el reporte de alarma. Se usa la regla de rango de la ec. (4) de Li y Wang, orden por parte real decreciente y relleno a nueve posiciones. Se emplean dos ramas convolucionales con filtros 2×1, agrupación inicial 2×1, cuatro y ocho mapas de salida y 16 unidades por rama. Las magnitudes y la normalización se adaptan al instrumental local. Se emplean estadísticas de entrenamiento fijas en inferencia, normalización por canal y dos clases. La validación seleccionó una de tres inicializaciones, con 104/108 aciertos en eventos aislados. El archivo de pesos, la selección y las semillas son públicos. Se probó la misma red sin restar el primer evento. [Fuente y cuadernos originales](https://github.com/Wendy0601/Identifying-Overlapping-Successive-Events-Using-a-Shallow-Convolutional-Neural-Network/tree/f0e6ea244de74c23392e10202bd30049d5d2faa9) · [Entrenamiento](results/training.json)
* **Estimador de familia con retardo fijo.** Usa las probabilidades aproximadas que el banco asigna a las historias en el reporte 30 de la ventana. Conserva las historias cuyo último evento empezó después de la alarma anterior y estaba activo en la alarma evaluada. Suma sus pesos por familia. Elegir la familia con mayor masa minimiza el riesgo de clasificación 0–1 condicionado a ese conjunto de historias. Con masa nula se abstiene. El cálculo depende de la poda y del modelo eléctrico. El umbral y la decisión de cuándo alarmar se evalúan empíricamente.
* **Control físico.** Dos copias del banco reciben las mismas mediciones y los mismos instantes de restauración publicados por el banco original. Ambas fusionan las historias ya despejadas. Una conserva la media física y la otra pone a cero sus 114 desviaciones físicas. La lectura de familia y los instantes de decisión son iguales. Esta intervención permite atribuir a la continuidad del estado la diferencia observada dentro del par.

## Control del comparador publicado

Se aplicaron los pesos originales de tres clases del modelo A a las características públicas de un segundo de separación en IEEE-68. Con sustracción se obtuvieron 292/309 aciertos (94,5 %), el valor que imprime el cuaderno de los autores. Sin sustracción se obtuvieron 248/309 (80,3 %). Este control comprueba la evaluación de los pesos publicados sobre características ya extraídas. La comparación ciega en IEEE-39 incluye extracción y extrapolación desde los reportes de PMU y usa pesos para carga y línea. [Control externo y huellas de entrada](results/upstream_control.json)

## Reproducir

Después de instalar las dependencias científicas del repositorio, el recuento de las predicciones publicadas se ejecuta con:

```powershell
python experiments/second_family/validation/audit.py
```

Para repetir la simulación y la inferencia causal de dos trayectorias de prueba, configure `P07_SCIENCE_ARCHIVE` con la raíz del archivo científico SGSMA. Use un hilo BLAS por proceso para repetir también las huellas de los archivos de PMU. La comprobación verifica los ajustes eléctricos del prefijo contra los archivos congelados:

```powershell
$env:OPENBLAS_NUM_THREADS = '1'
$env:OMP_NUM_THREADS = '1'
$env:MKL_NUM_THREADS = '1'
python experiments/second_family/validation/audit.py --replay
```

Para el control IEEE-68, `python experiments/second_family/validation/upstream.py` descarga la revisión fijada y lee el checkpoint con TensorFlow. Alternativamente, `--converted` admite un NPZ con los mismos tensores y nombres exportados del checkpoint original. Los datos y pesos de los autores se guardan solo en la caché local.
