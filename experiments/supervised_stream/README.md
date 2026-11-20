# Monitor supervisado de eventos PMU

El modelo de la carpeta successor procesa un reporte sincronizado cada 1/30 s. Aprende a disparar una alarma, estimar el inicio, clasificar la intervención y ordenar sus posibles orígenes. La clasificación usa bosques ExtraTrees. El localizador compara los cambios temporales de los fasores con las firmas físicas de los activos y aprende de ejemplos etiquetados qué diferencias distinguen al activo correcto. Un registro normal puede terminar sin emitir ninguna alarma.

## Entrenamiento y prueba

El experimento final contiene 2100 simulaciones de entrenamiento (3303 eventos) y 900 simulaciones nuevas de prueba (1444 eventos). Cada registro dura 24 s. La unidad de partición es la trayectoria completa. Para calibrar los umbrales se reservaron internamente 420 de las 2100 trayectorias de entrenamiento y se reajustaron los estimadores con las 2100 antes de congelarlos. Las semillas, hashes de las señales, predicciones y etiquetas están en los manifiestos. El commit e9ff2d7 fijó el modelo antes de generar la prueba. La prueba fue ejecutada por el mismo operador, con las etiquetas fuera de la ruta de predicción.

El simulador resuelve las 39 tensiones y la dinámica de diez máquinas con reguladores a 120 pasos/s. El monitor observa únicamente ocho PMU a 30 reportes/s. Los orígenes comprenden 39 barras de falla/pulso, 35 líneas sin formación de islas, 10 generadores, 18 cargas y ocho instrumentos. Los sensores son 2, 5, 6, 10, 19, 22, 29 y 39. Las ubicaciones pueden repetirse entre entrenamiento y prueba. Varían secuencia, instante, intensidad, duración, parámetros dinámicos y ruido instrumental. La topología base, el punto inicial y el modelo instrumental son conocidos. Son intervenciones físicas y anomalías de medición simuladas con las etiquetas del estudio. Para los eventos compuestos se puntúa el origen físico. Los eventos objetivo empiezan al menos cuatro segundos uno después de otro; las familias compuestas sí incluyen componentes simultáneos.

| Medida de la segunda prueba | Resultado |
|---|---:|
| Alertas correctas en tiempo entre todas las emitidas | 1384/1386 |
| Eventos detectados dentro de 1,5 s | 1384/1444 |
| Familia correcta entre todos los eventos | 1377/1444 |
| Tiempo, familia y activo correctos | 1251/1444 |
| Macro-F1 de nueve clases | 0,9753 |
| Registros normales sin alarma | 168/168 |
| Registros completos sin ningún error | 735/900 |

Las dos alarmas sin correspondencia ocurrieron en registros con eventos. La exposición total fue de seis horas y los registros completamente normales sumaron 67,2 minutos. La latencia mediana de las detecciones emparejadas fue de 1,167 s y el percentil 95 fue de 1,200 s. Son tiempos de señal necesarios para publicar; no incluyen transporte ni un despliegue de campo. El intervalo bootstrap por registro del acierto conjunto es 84,79–88,45 %. El intervalo para la familia es 94,22–96,42 %. El macro-F1 incluye los eventos omitidos, alarmas adicionales y una unidad negativa por segundo sin intervención ni publicación. Por eso difiere del macro-F1 por ventanas de la competición. En la matriz de confusión, los conteos aparecen dentro de las celdas y el color representa la fracción de cada fila; los verdaderos negativos de la clase 0 son segundos elegibles.

El primer experimento (700/300) queda archivado en esta carpeta, fuera de successor. Su prueba contenía 473 eventos y alcanzó 374 aciertos conjuntos. En un diagnóstico posterior, un predictor lineal de recuperación entrenado con la cohorte de 2100 y evaluado en 210 registros nuevos ganó cinco aciertos y perdió cinco. Se conservó el modelo congelado. Este diagnóstico no participa en las métricas de las 900 trayectorias.

## Usar el modelo entrenado

Desde la raíz del repositorio, ejecutar:

    python experiments/supervised_stream/online.py experiments/supervised_stream/successor/controls/two_fault_locations.npy

El monitor devuelve las alarmas a medida que recibe cada reporte. La matriz de entrada NumPy contiene [reportes, 8 PMU, 5 campos]. Los campos son log-magnitud de tensión relativa al punto de operación, ángulo relativo de tensión en radianes, magnitud de la corriente de terminal en amperios, ángulo de corriente relativo en grados y presencia (0/1). Necesita un segundo inicial tranquilo para establecer su referencia. La clase Monitor también acepta un reporte a la vez mediante step. El modelo queda en successor/model.joblib y se comprueba su hash antes de cargarlo. Para emplearlo con otra fuente hay que validar el orden, orientación, referencia de fase, unidades y ruido de los canales. La asignación verificada es la del simulador B01.

## Reproducir el estudio final

Usar la versión de scikit-learn 1.6.1 con la que se guardaron los bosques. Para regenerar la física, apuntar P07_SCIENCE_ARCHIVE al archivo científico SGSMA y fijar OPENBLAS_NUM_THREADS=1. Desde esta carpeta:

    python larger.py generate_train
    python larger.py train
    python larger.py generate_test
    python larger.py predict
    python larger.py score
    python breakdown.py
    python examples.py

Los controles incluyen normalidad, una falla, dos fallas en la misma barra y dos en barras distintas. Modificar todos los reportes futuros no cambió las publicaciones anteriores al punto de corte en esos cuatro casos. Se comprobó la coincidencia del monitor incremental con la inferencia por lotes en registros adicionales. El integrador coincidió con el RK4 de referencia en una perturbación de carga. El artículo principal no fue modificado en este experimento.
