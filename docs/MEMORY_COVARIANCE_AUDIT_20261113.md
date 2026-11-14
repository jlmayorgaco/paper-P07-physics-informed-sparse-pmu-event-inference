# Ablación de memoria y auditoría de covarianza

El plan maestro mantiene una pregunta principal para P07: atribuir la
siguiente intervención durante la recuperación. Se conserva la distinción
entre el banco probado, la relinealización con evento conocido y las notas
históricas de reconstrucción y múltiples fuentes. La validación de un
predictor abierto no da por sí sola una ventaja en atribución. La igualdad
de predicción tras cambiar coordenadas tampoco añade evidencia bayesiana.

## Memoria

Verifiqué los 15 hashes del ZIP, ejecuté los nueve tests, la demostración
recursiva y los cuatro escenarios con los tamaños y semillas del manifiesto.
La diferencia máxima entre resúmenes fue menor a 3e-13. Los intervalos
emparejados condicionan en los umbrales ya calibrados y no incluyen su
incertidumbre. Los brazos C y D comparten una misma rama de likelihood en
el código original. La igualdad resulta de la construcción y también se
verificó permutando etiquetas y comprobando el filtro recursivo contra la
integración por lotes. No debe interpretarse como una comparación de dos
implementaciones independientes. La identificación retrospectiva conserva
el mapa entre el índice de mezcla y su causa.

La mayor ganancia en estas ventanas viene de recuperar la covarianza.
El incremento de mezcla sobre Gaussiana está entre 0,49 y 1,89 puntos
porcentuales según el escenario. El diseño prescribe la recuperación
inicial y el instante de la nueva carga. La tasa por ventana no se
compara con alarmas por hora. El contrato sucesor conserva modo, duración
y priors en C y D y compara las historias presentes en el siguiente ON.
El cierre operativo, la poda, el presupuesto de alarmas y la transferencia
se miden en secuencias físicas independientes. C03 atiende continuidad y
conservación explícita, mientras la compresión gaussiana por momentos y la
mezcla sin etiquetas requieren brazos adicionales.

## Covarianza

T11 mezcla error absoluto de covarianza, error relativo de covarianza y TVE.
Escalar la observación cambia el error absoluto de covarianza por el
cuadrado de la escala. Por tanto la cifra de 40% no es una medida del
prefijo real. Concentración depende de la escala, el rango efectivo y la
ley de muestreo. El paso de una cota con dimensiones p y pr a una tasa que
solo depende de r carece de justificación cuando se estiman cargas y
varianzas desconocidas. [Koltchinskii y Lounici](https://arxiv.org/abs/1405.2468).

En el modelo espigado isotrópico clásico, el umbral de espiga poblacional
es 1+sqrt(p/N) y el borde superior del espectro muestral es su cuadrado,
ambos en unidades de la varianza base. Son objetos distintos y los
resultados asintóticos no proporcionan un criterio exacto para ruido
heterocedástico y correlacionado. [Paul](https://www3.stat.sinica.edu.tw/statistica/oldpdf/A17n418.pdf).

La desigualdad válida para una firma fija se obtiene acotando los
autovalores de la covarianza blanqueada. De ahí no se deduce que el umbral
adaptativo se conserve, ni que un bootstrap proporcione por sí solo el
error respecto de la covarianza verdadera. La ausencia de una espiga
tampoco impide estimar ruido independiente con estructura diagonal.
Para canales ausentes la marginal gaussiana usa la submatriz principal
observada. Un complemento de Schur da una covarianza condicional.

El piloto contrasta escala nominal, muestra y Ledoit–Wolf con verdad
conocida. Sus ocho celdas combinan 300/1.200 reportes, independencia/AR(1)
0,9 y perturbación diagonal nula/unitaria en unidades estandarizadas.
Cada celda tiene 128 prefijos independientes. La métrica es la KL marginal
verdadera a estimada. Al usar una ley proporcional o cercana al patrón
nominal, ese patrón aporta información previa a uno de los brazos.
Los resultados no identifican el origen del fallo de atribución con TVE.
Para identificarlo, el control decisivo mantiene búsqueda y publicación
fijas, compara primero con covarianza oráculo en el modelo de ruido físico,
y luego con estimadores de prefijo a igual presupuesto en nuevas cohortes.

## Reproducción y estado

Desde una copia aislada, en el directorio del experimento, ejecutar
`python -B covariance.py` y `python -B present.py`. Para reproducir
el ZIP entrar en `toy`, ejecutar `python -B test_experiment.py` y
`python -B run_study.py --n-test 3800 --n-cal 3000 --seed 20261113 --output reproduction`.
El manifiesto original refiere además a archivos del ZIP que no se
requieren para ejecutar esos comandos. El código, resultados y procedencia
de esta revisión están registrados en el repositorio.

Al corte de 19:34 Bogotá, C03 completó la inferencia nominal de los 72
registros TEST de F01. La evaluación sellada de ambas plantas sigue
pendiente. La comprobación solo consultó metadatos de progreso.
