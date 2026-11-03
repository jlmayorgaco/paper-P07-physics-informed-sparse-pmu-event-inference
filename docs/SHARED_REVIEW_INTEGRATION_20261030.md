# Integración de la revisión compartida — 30-oct-2026

## Fuente y decisión

Se leyeron los 14 mensajes/siete respuestas de [la conversación de revisión](https://chatgpt.com/share/6ae4eff8-00c4-83ea-812f-d5afe8c2f774).
La revisión analizaba un borrador anterior de 19 páginas principales y 24
suplementarias. El artículo causal actual tenía 12 páginas y ya había separado
la reconstrucción B0/B1/B2, el banco batch E_B y la propuesta conjunta E_J.
No se reintroducen como etapas de un único algoritmo validado.

La revisión tiene dos aportaciones distintas: mejorar la presentación de lo
ejecutado y proponer un estimador nuevo (DICE-PMU). P07 conserva R11/C01 como
historia principal. DICE se desarrolla como candidato separado, con ecuaciones,
código de los núcleos, controles y protocolo. No se atribuyen sus posibilidades
a los resultados congelados de R11.

## Qué se incorporó

| Idea de la revisión | Acción y estado |
|---|---|
| Explicar problema, algoritmo y ventaja en una secuencia clara | Se conserva la arquitectura causal; se añade un algoritmo numerado por reporte, con entradas, estado previo, propuestas, densidad predictiva, actualización y publicación. |
| Physics-based Bayesian inference es más preciso que PINN/PI-ML | Se explicita que las ecuaciones construyen predicciones y evidencia; no se declara una red neuronal ni un componente aprendido inexistente. |
| Eventos visibles no equivalen a fuentes identificadas | La figura auxiliar distingue decisión conjunta y rango condicionado a dos fuentes; no certifica un límite informacional. |
| Comparación con Group LASSO y Bayes bajo estado incierto | Se verificó la referencia Anguluri–Kosut–Sankar 2023 en la fuente institucional y se completó su DOI. Se cita como precedente, no como comparador ejecutado de C01. Zhao 2014 ya estaba citado. |
| Estadísticas suficientes antes de comprar GPU | El código histórico **ya usa Gram por soporte**. Se implementaron caché global compartida e integración GH31 por lotes, verificadas contra las funciones originales. |
| La incertidumbre debe depender de fuente y amplitud | Se derivó la extensión evento–contexto y su covarianza con determinante conservado; se probó el núcleo algebraico denso/bajo rango. Las sensibilidades físicas E_i no están aún validadas. |
| Latencia, observación y transporte son distintos | El artículo evita llamar tiempo real a la causalidad. El microbenchmark nuevo es sintético y no incluye observador/onsets/adquisición; no valida 30 fps. |
| No sumar ocho figuras a todas las anteriores | Se sustituyó solo la figura auxiliar de resolución por dos paneles con contratos claros. El gráfico técnico del candidato queda fuera de la historia principal. |

La imagen de tipos de eventos permanece **exactamente igual**, tanto PDF como
PNG. El build comprueba sus hashes antes y después de compilar y falla si cambian.
También se preservan el diagrama de bloques aprobado y el unifilar eléctrico.

## Hallazgos que cambian la interpretación

### 1. Normalización del banco batch de 137 soportes

En el commit histórico `5189fa16a1e39e31595ed5786f2ccc4487db24d3`, las
funciones numéricas coinciden con las disponibles localmente. Si todas las
firmas son cero, una evidencia correctamente normalizada debe ser idéntica
en H0, una fuente y dos fuentes. El código devuelve:

- una fuente: log Z − log Z0 = −log(2π);
- dos fuentes: log Z − log Z0 aproximadamente cero.

Así, el prior declarado (0.20,0.50,0.30) se realiza como un prior efectivo
proporcional a (0.20,0.50/(2π),0.30), aproximadamente
(0.34508,0.13730,0.51762). Que el posterior sume uno no basta para preservar
el modelo de evidencia declarado. La corrección del candidato añade log(2π)
a las 16 evidencias de una fuente y recupera el prior en ese control.

No se modificaron E_B, GH31, sus CSV históricos ni sus figuras originales
archivadas. El modo legacy del candidato reproduce su aritmética; el modo
normalizado es un sucesor explícito. No se puede calcular la exactitud física
corregida reescalando medias agregadas. Hace falta el replay por registro.
El artículo ahora califica esos resultados como archivados y no los utiliza
para certificar la calibración del posterior o un límite físico inevitable.

Este hallazgo **no cambia R11 ni C01**. El integral local R11 sigue otro
código y sus expresiones se verificaron por cuadratura independiente.

### 2. Top-1 y Top-3 no usan la misma decisión

El Top-1 de GLOBAL-137 exige K=2 y soporte correcto en la decisión conjunta.
Su Top-3 es el rango del par verdadero solo entre las 120 parejas. El panel
nuevo declara que K=2 se suministra en esa segunda tarea. No se presenta
como una mejora del mismo localizador devolviendo simplemente más etiquetas.

### 3. La curva de severidad no es una curva de exactitud por severidad

`weak_weak_transition.csv` asigna el mismo Top-1 global de parejas débiles a
cada grupo de amplitud. La repetición está en `supplemental()` del código,
no demuestra una exactitud constante por severidad. No se usa esa columna
para construir una curva nueva. La tabla se conserva sin modificaciones.

### 4. Datos disponibles y límite de reproducción

Existen resúmenes, manifiestos importados y código de E_B; no están sus
arrays originales D/Q/Qij ni las trayectorias completas en esta copia.
La búsqueda incluyó las rutas de proyecto y tres paquetes de revisión.
No se regeneró un baseline mediante scripts antiguos ni se sustituyó por
otro diccionario. X01 informa `IEEE39_physical_replay_executed=false`.
La campaña R11/C01 mantiene sus propios artefactos completos.

## Lo nuevo que sí se ejecutó

`experiments/PAPER_METHOD_DICE_X01` contiene una implementación aislada de:

1. proyecciones y Gram compartidos entre los 137 soportes;
2. GH31 vectorizada sobre las 120 parejas, con las mismas propuestas Newton,
   nodos, pesos, normalizadores legacy y momentos;
3. corrección explícita de normalización, activable independientemente;
4. densidad gaussiana con incertidumbre de contexto de bajo rango;
5. factor de Bayes condicionado, contrastado con cuadratura;
6. estadísticas de prefijo blanqueadas y control de independencia del futuro.

Se evaluaron seis fixtures sintéticos de 960 dimensiones/152 bases con todos
los 137 soportes. Se comprobaron evidencias, masas completas, momentos y
Top-1/Top-3; los errores están en el JSON, no son cifras de clasificación de
IEEE-39. El benchmark usa 30 repeticiones intercaladas por variante, Float64
y un hilo BLAS en el equipo local compartido. No se copian los tiempos
1.54/2.28/3.43 ms del otro chat como resultados nuestros.

El snapshot de entradas, código y resultados está en
`generated/frozen/shared_review_x01_20261030/`. El generador verifica hashes y
produce `review_kernel_audit` y la tabla del control de normalización.
El control lineal adicional de los 136 soportes está en
`generated/frozen/shared_review_x01_normalization_20261030/`. Esa tabla y
el gráfico técnico quedan en el expediente de revisión; el artículo conserva
una explicación breve del prior efectivo y no se convierte en un informe
extenso de auditorías.

## Giro científico y validación organizada

La extensión propuesta cambia la respuesta D_i con el contexto η mediante
E_i = ∂D_i/∂η. Después integra esa incertidumbre con una covarianza dependiente
de hipótesis/severidad y sus normalizadores. Es más que recentrar la media.
La prueba decisiva compara nominal, recentrado solo y firmas condicionadas,
con los mismos datos, priors, observaciones y presupuesto temporal.

El método completo, las aproximaciones, la actualización causal sin doble
conteo y los experimentos X01–X05 están desarrollados en
`experiments/PAPER_METHOD_DICE_X01/METHOD_AND_EXPERIMENTS.md` del repositorio
SGSMA, copiado al snapshot de este paper. Las mejoras algorítmicas no se
consideran demostradas porque se haya derivado una ecuación. Su validación
requiere recuperar el replay, verificar E_i con la DAE y usar trayectorias
nuevas para comparación, cobertura y riesgo selectivo.

## Cierre de P07

C01 sigue sin reajustes y continúa siendo la confirmación del método causal.
Al completar integra R11, nominal y ambos ExtraTrees; Chen solo en aperturas
persistentes. No se añaden métodos a ese examen después de iniciarlo.

Antes del envío deben concordar conclusiones, resultados completos y archivos
reproducibles. Si se conserva E_B como resultado probabilístico principal,
su replay y la discrepancia de normalización deben cerrarse; puede quedar
como contexto histórico calificado sin sostener el aporte causal central.
El nuevo candidato no se venderá como resultado multifamilia, calibrado,
industrial o superior a R11 antes de sus pruebas.

Fuentes bibliográficas verificadas: [Anguluri et al.](https://asu.elsevierpure.com/en/publications/localization-and-estimation-of-unknown-forced-inputs-a-group-lass/)
y [Zhao et al.](https://collaborate.princeton.edu/en/publications/identification-of-outages-in-power-systems-with-uncertain-states-/).
