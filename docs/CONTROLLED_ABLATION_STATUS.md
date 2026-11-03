# Cierre del estudio controlado de puntuación y arrastre físico

## Estado

El estudio factorial congelado está completo. Incluye 24 registros en cada
uno de cuatro brazos: 18 secuencias continuas, tres controles normales y tres
aperturas persistentes. El evaluador contabiliza las 96 salidas previstas:
96 disponibles, cero fallos. La predicción se selló antes de evaluar, los
métodos comparadores no se reajustaron y la campaña original no cambió.

El control de copia igualó 3,601 reportes con la predicción de referencia;
los campos comparados tuvieron error máximo cero y los eventos fueron
idénticos.

## Resultados continuos

| Variante descriptiva | A tiempo | Alarmas extra | Restoraciones no asociadas | Sin diagnóstico oportuno | Demora mediana* |
|---|---:|---:|---:|---:|---:|
| Puntaje marginal, con arrastre físico | 108/108 | 1 | 1 | 0/108 | 0.267 s |
| Puntaje de perfil acotado, con arrastre físico | 108/108 | 1 | 1 | 0/108 | 0.267 s |
| Puntaje marginal, reinicio al cierre inferido | 75/108 | 166 | 130 | 33/108 | 0.337 s |
| Puntaje de perfil acotado, reinicio al cierre inferido | 75/108 | 166 | 130 | 33/108 | 0.337 s |

\* La demora se calcula solo para diagnósticos emitidos y asociados; debe
leerse junto al conteo de eventos sin diagnóstico oportuno.

Los controles normales tuvieron cero falsas alarmas en 1,764 segundos de
exposición evaluada (588 s por registro; tres registros de 600 s con 12 s de
inicio excluidos). En los tres controles de línea persistente por brazo, los
tres eventos se diagnosticaron a tiempo y los tres quedaron abiertos al final
del registro.

## Contrastes y límites

El puntaje marginal y el puntaje perfilado empatan en estos endpoints. El
brazo de perfil conserva medias y varianzas de estado bayesianas condicionales,
pesos previos y hazards fijos; solo reemplaza el incremento de la integral de
amplitud por un puntaje perfilado penalizado, también durante la reproducción
retrospectiva del nacimiento del evento. No es un posterior ni un GLR puro.

El reinicio elimina los primeros 114 desvíos estimados del estado físico solo
al cierre inferido. Conserva la memoria instrumental, covarianzas, pesos,
umbrales y relojes; nunca reinicia la planta simulada. Las diferencias
emparejadas por 18 padres son descriptivas y posthoc: el arrastre aporta
0.306 de fracción oportuna (IC 95% 0.241-0.380) y reduce 275 alarmas extra
por hora de registro de eventos (IC 95% -325 a -223.333), frente al reinicio.
No se hizo ajuste por multiplicidad ni se midió superioridad con falsas
alarmas igualadas. El resultado respalda el arrastre físico al cierre inferido
en esta cohorte; no establece que toda la inferencia bayesiana sea necesaria
ni la elimina.

Es un análisis posthoc de datos existentes, no una confirmación independiente.
La evidencia fuente, las predicciones selladas y las tablas están en
`generated/frozen/ablation_a01_20261102/`; no se abrió RAW0002.
