# Confirmación de episodios en MET_BAYES_GRAFO

La revisión `44697db` fijó dos reglas de publicación antes de simular la prueba. Se ajustaron los coeficientes con 192 trayectorias y se seleccionaron los umbrales con otras 96. El examen nuevo contiene 96 trayectorias, 104 intervenciones, cuatro familias físicas y ocho PMU. Hay 32 pares en los que ambas ramas presentan exactamente las mismas mediciones hasta el segundo inicio. Los activos de prueba se excluyeron del entrenamiento y de la selección de la confirmación. Ya figuraban en el conjunto reservado del estudio anterior. El simulador comparte la familia de dinámica y ruido usada en desarrollo. [Protocolo](PROTOCOL.md)

| Método | Detectados | Familia correcta | Familia y activo exactos | Macro-F1 | Extras | Extras tras restauración | Latencia mediana de detección |
|---|---:|---:|---:|---:|---:|---:|---:|
| Grafo original | 96 | 93 | 91 | 0,6103 | 159 | 154 | 0,00 s |
| Propuestas del grafo con el tiempo de confirmación | 97 | 92 | 91 | 0,6072 | 154 | 150 | 0,20 s |
| Confirmación que prioriza diagnósticos exactos en desarrollo | 93 | 91 | 90 | 0,7715 | 41 | 40 | 0,20 s |
| Confirmación que prioriza macro-F1 en desarrollo | 92 | 91 | 90 | 0,8879 | 9 | 8 | 0,20 s |
| MET_PMU_FIRMAS_ETREE | 93 | 93 | 87 | 0,9381 | 1 | 0 | 1,17 s |

El denominador en las tres primeras columnas es 104 y el plazo es 1,5 s. Los extras son avisos sin episodio emparejado. Todos ocurrieron en registros con eventos. La exposición en registros enteramente normales fue de 9,2 minutos. Una confirmación demora la publicación y puede cambiar qué episodio recibe un aviso por la regla común de emparejamiento. La fila de propuestas evalúa ese efecto antes de aplicar la decisión aprendida. [Resultados](scores.json) · [Punto de macro-F1](f1_scores.json)

Con el punto orientado a F1, la ganancia de macro-F1 frente al grafo original fue 0,278, con intervalo bootstrap pareado del 95 % de 0,195 a 0,342. La diferencia observada frente al supervisado fue −0,050, con intervalo de −0,118 a +0,006. Los tres aciertos conjuntos adicionales frente al supervisado equivalen a 2,9 puntos porcentuales, con intervalo de −7,1 a +12,4. Se remuestrearon grupos completos de trayectorias. La primera prueba del grafo había dado 0,7284 y 66 extras en otro conjunto. Ambas pruebas conservan sus propios modelos sellados, datos y puntuaciones.

## Qué ocurre con el segundo evento

En cada par, una rama solo se recupera. En la otra llega una segunda intervención. En el control se cuenta cualquier aviso extra desde la restauración hasta el final. En la rama intervenida se exige familia y activo correctos dentro del plazo. El primer evento es idéntico hasta que las dos trayectorias se bifurcan.

| Método | Controles sin extra posrestauración / 32 | Segundas intervenciones exactas / 32 | Cumple ambas condiciones en el mismo par / 32 |
|---|---:|---:|---:|
| Grafo original | 21 | 21 | 19 |
| Confirmación que prioriza diagnósticos exactos | 24 | 20 | 19 |
| Confirmación que prioriza macro-F1 | 31 | 20 | 20 |
| MET_PMU_FIRMAS_ETREE | 32 | 19 | 19 |

La variante orientada a F1 identifica 70/72 primeros episodios y 20/32 segundos. Tras despejar una falla acierta 1/8 segundos episodios. Tras recerrar una línea acierta 4/8, tras restituir generación 7/8 y tras restituir carga 8/8. Entre los doce segundos episodios sin diagnóstico exacto, en cinco no llegó una propuesta a tiempo, en cinco la propuesta tenía la familia equivocada, en uno tenía el activo equivocado y en uno la confirmación rechazó una propuesta correcta. Estos grupos se obtienen comparando la variante con sus mismas propuestas antes de filtrar. Cada subgrupo por familia precedente contiene solo ocho pares. El bajo rendimiento después de fallas ya es visible en el grafo original, con 2/8.

El contraste actual extrapola la tendencia anterior y compara el residuo con firmas de intervención y restitución. El siguiente cambio que merece probarse afecta al generador de propuestas. Tras un despeje, propagar la incertidumbre de ángulos y velocidades de las máquinas bajo recuperación y bajo cada segunda intervención. Así el monitor puede proponer el segundo inicio incluso cuando la red sigue oscilando. El beneficio debe medirse en nuevos pares, conservando los controles de recuperación y el plazo de 1,5 s.

## Reproducción

Desde la raíz, `python -B experiments/graph_recursive/episode_confirmation/audit.py` comprueba las huellas de datos y decisiones, reproduce los resultados por episodio con NumPy y desglosa los pares por primer evento. La auditoría compacta usa las predicciones selladas y las etiquetas publicadas en este directorio. Se verificó también que las mediciones de cada par coincidían muestra a muestra antes de la bifurcación y que la ejecución reporte a reporte reproducía los avisos sellados en cuatro trayectorias, para ambos ajustes.

Para consumir lecturas en línea, se crea un `F1Monitor` de `episode_precision.py` por trayectoria y se llama a `step(report)` a 30 Hz. El formato de los canales y el prefijo tranquilo son los del observador polar. La lista devuelta contiene exclusivamente avisos publicables en ese reporte. [Monitor](../episode_precision.py) · [Firmas y confirmación](../episode_gate.py)
