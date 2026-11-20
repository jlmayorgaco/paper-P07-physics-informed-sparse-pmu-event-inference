# MET_BAYES_GRAFO con estimación conjunta desde PMU

El monitor congelado en `555057c` detectó, clasificó y ubicó **480/480 eventos físicos** en una prueba prospectiva simulada en la IEEE-39. Su macro-F1 de cuatro familias fue **1,0000** y emitió **cero avisos extra**. Acertó los 16 pulsos de generación y los 16 aumentos de carga en segunda posición después de una falla o apertura. El resultado cumple los criterios registrados de este ensayo. [Protocolo](PROTOCOL.md) · [Modelo y huellas](results/freeze.json)

## Comparación ciega sobre las mismas señales

Se simularon 416 registros independientes de 24 s con ocho PMU, 192 de ellos enteramente normales. Cada episodio se cuenta una sola vez. Las nueve barras y ocho ramas del examen son distintas de las de las dos pruebas ciegas precedentes. Se excluyeron globalmente sus etiquetas del nuevo entrenamiento y desarrollo, incluso entre familias que comparten barras. Los archivos históricos del grafo y de los árboles habían tenido acceso a ejemplos de algunos de estos activos. La réplica de los árboles se ajustó con los 1.591 registros históricos admisibles. [Activos y datos de prueba](results/test_manifest.json) · [Entrenamiento de la réplica](results/tree_fit.json)

| Monitor | Macro-F1 | Familia | Activo exacto | Extras | Segundos eventos objetivo, familia y activo | Terceros eventos, familia y activo |
|---|---:|---:|---:|---:|---:|---:|
| MET_BAYES_GRAFO conjunto | 1,0000 | 480/480 | 480/480 | 0 | 32/32 | 64/64 |
| Grafo anterior, pesos históricos congelados | 0,9163 | 430/480 | 423/480 | 8 | 31/32 | 30/64 |
| Grafo anterior, reajustado con la nueva partición | 0,9093 | 424/480 | 417/480 | 3 | 31/32 | 28/64 |
| MET_PMU_FIRMAS_ETREE histórico | 0,8120 | 353/480 | 326/480 | 4 | 6/32 | 1/64 |
| MET_PMU_FIRMAS_ETREE reajustado sin los activos reservados | 0,7563 | 324/480 | 288/480 | 3 | 3/32 | 1/64 |

El estimador conjunto acertó los 192 segundos eventos, considerando todas las familias. El tiempo entre inicio y publicación del diagnóstico fue de 0,20 s en la mediana, 0,30 s en el percentil 95 y 0,47 s en el peor caso, frente a un plazo de 1,5 s. Son tiempos en el reloj de los reportes de PMU. Los cinco monitores emitieron cero alarmas en los 73,6 minutos de reposo evaluables después de la inicialización. Todos los extras de los comparadores ocurrieron en registros con eventos. Las predicciones de los cinco se sellaron en `5506e60` antes de abrir las etiquetas. [Predicciones](results/predictions.json) · [Matriz de confusión e intervalos pareados](results/scores.json)

El aumento de macro-F1 frente a los árboles históricos fue de 0,1880 (IC pareado del 95 % de 0,1578 a 0,2234). La ubicación exacta aumentó 32,08 puntos porcentuales (IC de 28,47 a 35,79). Los intervalos se calcularon remuestreando registros completos. En métricas con acierto perfecto, el bootstrap del método aislado devuelve un intervalo degenerado porque todas las observaciones disponibles son aciertos. Los 32 aciertos objetivo proceden de solo 16 ejemplos de cada familia.

Después de abrir las etiquetas se ejecutó un control adicional con el estimador congelado. Se retiró el último evento de los 32 registros objetivo y de los 64 triples. Cada simulación conservó la planta, el ruido y todos los eventos anteriores. Se verificó que los bytes de las PMU y los avisos anteriores al instante de la intervención retirada coincidían en ambas ramas. El monitor encontró y ubicó los 160 eventos que seguían presentes en esos 96 controles, con cero avisos extra. Este control complementa el examen ciego y se puntúa por separado. [Control contrafactual](results/counterfactual.json) · [Repetición](results/counterfactual.py)

## Qué estima el monitor

Cada nueva perturbación se aplica sobre los ángulos y velocidades de las máquinas y los estados de reguladores dejados por los episodios anteriores. Así se predicen el transitorio y el retorno de voltajes y corrientes con una sola trayectoria eléctrica. La evidencia del banco y los cambios de escala de las innovaciones proponen instantes para examinar. Antes de publicar, el monitor compara candidatos de todas las familias contra la continuación física que ya predice las PMU. Estima intensidad, inicio y posibles despejes con las mediciones recibidas. Después del anuncio utiliza las PMU posteriores para ajustar los multiplicadores de inercia y amortiguamiento y las intensidades de los eventos confirmados. Mantiene fijos los diagnósticos de familia y activo ya publicados. [Modelo de red y máquinas](joint_physics.py) · [Decisión reporte a reporte](joint_observer.py)

Entrenamiento ajustó la transformación de las mediciones y las distribuciones temporales. Desarrollo condujo a dos cambios, la segunda vía de propuesta y la comparación física entre familias con ajuste de amplitud. En los 240 episodios de desarrollo los cinco umbrales del algoritmo final empataron con cero extras. El desempate predefinido seleccionó 15. El estimador usa el catálogo eléctrico completo y las ubicaciones de los sensores. En inferencia recibe únicamente el flujo de PMU. [Selección de desarrollo](results/development.json)

## Alcance y reproducción

El simulador y el estimador comparten la topología nominal y las leyes de máquina, red y regulador. La simulación usó 120 Hz, el predictor 60 Hz y los sensores 30 Hz. En cada registro variaron el ruido y los parámetros mecánicos, con multiplicadores comunes a las máquinas. Los eventos fueron sucesivos, con separación temporal, y todos los canales estuvieron disponibles. El ensayo demuestra generalización a los activos reservados bajo esas condiciones. Quedan por medir el efecto del error de topología, otros puntos de operación, eventos superpuestos y el desempeño en datos de campo.

Desde la raíz, `python experiments/joint_pmu/audit_joint.py` recalcula los resultados de los cinco métodos a partir de las predicciones y etiquetas publicadas. Con el archivo científico en `P07_SCIENCE_ARCHIVE` y `OPENBLAS_NUM_THREADS=1`, la opción `--regenerate` simula de nuevo los 416 registros, comprueba sus huellas y repite el monitor causal en 24 registros sorteados. Para procesar una trayectoria propia, `python experiments/joint_pmu/apply_joint.py registro.npy` emite las decisiones sobre una matriz de forma (reportes, 8 PMU, 5 campos). [Auditoría](audit_joint.py) · [Punto de entrada](apply_joint.py)

La repetición desde el simulador reprodujo la huella de las 416 trayectorias y cada alarma del monitor en los 24 registros recalculados por la vía de inferencia en línea.
