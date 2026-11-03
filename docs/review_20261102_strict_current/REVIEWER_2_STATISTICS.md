# Revisor 2 — experimento, estadística, ML y reproducibilidad

**Dictamen simulado: revisión mayor; esta versión todavía no está lista para enviar.**

Revisión independiente del manuscrito actual del 2-nov-2026. No se consultaron
dictámenes anteriores ni los de otros revisores. Se leyeron las secciones
incluidas en `main.tex`, los apéndices pertinentes, el protocolo y código de
evaluación C01 y sus tablas completas. No se modificó el manuscrito, ningún
método ni C01; no se inspeccionaron resultados parciales A01 ni RAW0002.
Los hashes del PDF y archivos numéricos auditados constan en `R2_CHECKS.json`.
Las rutas de secciones son relativas a P07; las de experimentos, al repositorio
SGSMA26-Physics-Informed-AD.

## Qué sí está respaldado

El trabajo no es una demostración vacía de etiquetas físicas. Hay un procedimiento
ejecutado, predicciones selladas antes del evaluador, un catálogo explícito y
comparaciones sobre la misma señal causal. La separación entre alarmar,
diagnosticar, restaurar y mantener recuperación es científicamente útil.

Recalculé los totales desde `run/results/SUMMARY.csv` de C01:

| Procedimiento | Atribución oportuna /648 | Correcta eventualmente /648 | Alarmas extra |
|---|---:|---:|---:|
| Banco físico cinco modelos | 644 | 645 | 72 |
| Banco nominal | 643 | 645 | 92 |
| ExtraTrees referencia | 330 | 330 | 29 |
| ExtraTrees corto | 352 | 352 | 16 |

Son 108 intervenciones en 18 calendarios, repetidas seis veces, no 648
intervenciones independientes. El texto lo reconoce. El registro de evaluación
contabiliza los 342 registros por método, sin rechazos físicos ni fallos de
inferencia. La asociación temporal se hace antes de mirar familia/origen
(`execution/metrics.py:20–33`): no encontré un emparejamiento oportunista por
etiqueta. Los resultados negativos, las alarmas fuera del banco y la
indisponibilidad sobre RAW0001 permanecen visibles. Es una mejora importante
de rigor frente a presentar únicamente porcentajes cercanos al 100 %.

## Objeciones mayores

### R2-1. La diferencia con ExtraTrees es real, pero aún no demuestra una ventaja frente a un competidor fuerte de carga

**Confirmado.** `sections/narrative_protocol.tex:46–55` declara que los dos
comparadores ya tenían 0/72 y 4/72 atribuciones oportunas de carga en su propia
validación de desarrollo. El titular de C01 se apoya principalmente en carga;
para línea, el adaptador corto ya alcanza 322/324, igual que el banco físico.
Por tanto, el experimento confirma una diferencia entre los procedimientos
congelados, pero deja abierta la alternativa de un clasificador mal adaptado
al objetivo de detección oportuna de carga. Dar a todos los mismos canales
no iguala la información: el físico recibe la DAE y operadores de cada activo;
los árboles reciben ejemplos y resúmenes temporales.

**Remedio mínimo:** conservar íntegro C01 y mostrar esta limitación junto al
resultado principal, no solo al final del protocolo. Separar explícitamente
el beneficio frente a estos dos artefactos de una superioridad general sobre
ML. Para afirmar esta última sí haría falta un comparador competente, escogido
en desarrollo independiente y evaluado con reglas declaradas; no es necesario
añadir una GNN por moda, ni arreglar sus umbrales usando C01. La comparación
histórica con la entrega no satisface esta carencia porque cambia de dominio,
ventanas, catálogo y estimador físico.

### R2-2. El mecanismo central aún no tiene su contraste terminado

**Bloqueo objetivo de la versión actual.** `sections/article_controlled_ablation.tex:2`
dice que el estudio está en ejecución. Las contribuciones del artículo destacan
recuperación y evidencia condicional, pero C01 compara procedimientos completos.
Incluso nominal frente a mezcla tiene diferentes publicadores
(`sections/narrative_protocol.tex:84–86`; `article_method.tex:224–228`). Las
comparaciones de tensores, reconstrucción y soporte de la sección V son otros
experimentos, varios con tiempo o familia conocidos.

**Remedio mínimo:** terminar el contraste ya autorizado y presentar los cuatro
brazos, incluyendo efectos negativos e intervalos por padre. No hace falta una
nueva sucesión de versiones por bus. Interpretar su alcance con precisión:
el perfil conserva estimación condicional bayesiana y priors de intervalos;
el reset elimina 114 desviaciones físicas al cierre, no toda memoria. Igualar
umbrales numéricos no iguala falsas alarmas. Los 18 padres son conocidos y solo
de red matched/ruido original, por lo que no explican automáticamente las 68
extras fuera del banco. Todo ello está bien anticipado en el diseño actual,
pero una sección de resultados pendiente no es material terminado de envío.

### R2-3. La evaluación de restauración no muestra bien una ventaja relevante que ya existe

**Problema confirmado de semántica y presentación, no de modificación del detector.**
La tabla `tables/generated/c01_operational.tex:5–9` llama **False OFF** a
58/68/29/16. En `execution/evaluate.py:48`, esa variable cuenta restauraciones
de episodios NO emparejados con un evento, no cierres prematuros de un evento
real. El suplemento explica la distinción, pero el encabezado induce a la
lectura equivocada. Además, una mediana de retraso OFF no revela colas negativas
ni eventos que nunca tuvieron un cierre asociado.

Relectura descriptiva nueva de `EVENTS.csv`, sin rematching ni cambios de C01:
criterio de cierre prematuro `off_delay_s < -1/30 s`, elegido para esta auditoría.

| Método | Alarmas asociadas /648 | Restauraciones asociadas disponibles | Prematuras entre esas restauraciones | Sin restauración asociada /648 | Mínimo retraso firmado |
|---|---:|---:|---:|---:|---:|
| Físico cinco modelos | 647 | 644 | 0/644 | 4 | +0.167 s |
| Nominal | 648 | 643 | 0/643 | 5 | +0.167 s |
| ExtraTrees | 330 | 330 | 52/330 | 318 | −4.310 s |
| ExtraTrees corto | 352 | 352 | 26/352 | 296 | −2.986 s |

«Sin restauración asociada» incluye los eventos omitidos; no equivale a un
episodio abierto. Los conteos contienen replays dependientes. No son un nuevo
endpoint confirmatorio ni una prueba de significación. `R2_CHECKS.py` permite
reproducirlos a partir de los CSV sellados.

**Remedio mínimo:** renombrar la columna existente a «restauraciones de episodios
no asociados», conservarla, y añadir cobertura/cola negativa de OFF como auditoría
descriptiva claramente identificada. Una ECDF de retraso firmado con denominador
y una categoría de falta de cierre cuentan la historia mejor que añadir otro
porcentaje global. Esto apoya una utilidad concreta de retener recuperación sin
inventar una mejora del score de hackathon.

### R2-4. El comparador publicado funciona en su ley, pero la adaptación al ensayo no constituye una competencia fuerte

**Limitación explícita, no acusación de implementación falsa.** Chen produce
74/162 primeras identificaciones correctas y alarmas en 72/72 normales. Su
prueba independiente en la ley gaussiana de tres buses registra 299/300
identificaciones correctas tras cambio y 0/100 alarmas normales durante el
horizonte (`comparator/MATCHED_SUMMARY.csv`). Así, el código no parece un mero
comparador roto. Sin embargo, su adaptación usa inyecciones blancas isotrópicas,
DC y una referencia angular no observada, frente a ruido coloreado y una planta
dinámica. El README reconoce ya el fallo 3/3 normales en desarrollo.

**Remedio mínimo:** mantener la comparación como límite de transferencia de ese
adaptador, nunca como inferioridad general de Chen o del estado del arte. Para
el alcance de procedimiento práctico con recuperación, un control físico simple
compatible con la misma observación es más informativo; el GLR histórico ayuda,
pero no comparte C01 y cambia varias operaciones a la vez. La ablación controlada
de R2-2 puede resolver parte de este déficit sin añadir modelos por nombre.

### R2-5. Falta coste computacional medido en el artículo

**Confirmado por lectura.** `article_method.tex:236–260` ofrece orden causal y
declara correctamente que no hay operación en tiempo real demostrada. No se
presenta una tabla de coste total, memoria ni distribución de latencia por
reporte. «30 fps» describe la entrada, no el throughput. El protocolo C01
incluye runtime/peak memory como secundarios, pero su conclusión de utilidad
no informa del coste frente a ExtraTrees.

**Remedio mínimo:** usar tiempos ya registrados donde sean comparables y
explicar inicialización/reconstrucción de banco, inferencia y hardware/hilos
por separado. Si faltan latencias, medir un replay aislado sin alterar método
ni casos y declarar que es un benchmark computacional, no otra selección
científica. No insertar la prueba tensorial de kernels como si midiera todo
el detector. Una GPU no es requisito de publicación; una descripción honesta
del coste sí mejora mucho la evaluación de utilidad.

### R2-6. El mapa entre resultados de componentes y contribución principal sigue disperso

**Riesgo de argumento, no resultados falsos.** La sección V reúne reconstrucción
Kalman, features de modelos históricos, respuestas de dos cargas y selección
bayesiana de soporte. Son datos útiles, pero el filtro continuo no incorpora
todos esos algoritmos. El prior efectivo del soporte archivado difiere del
declarado por un factor 2π (`article_evidence_bridge.tex:120–128`). La honestidad
de advertirlo es correcta; usar esa tabla como evidencia causal de superioridad
de Bayes en el filtro actual sería incorrecto.

**Remedio mínimo:** un cuadro compacto «componente ejecutado / entra en el método
actual / pregunta que prueba / condición oracular» y una afirmación central que
se cierre con el contraste controlado. No borrar resultados históricos, pero
no exigir al lector reconstruir cinco contratos para entender qué se evaluó.
No se necesita reforzar el vocabulario tensorial: el texto actual reconoce
correctamente que la forma de M no demuestra una ventaja.

## Observaciones menores y precisiones estadísticas

1. **Bootstrap no estratificado con normales de denominador cero.**
   `execution/evaluate.py:66–69` arma 30 padres (18 eventos +12 normales) para
   timely_fraction y 39 (27+12) para first_correct_fraction. Los normales tienen
   cero numerador y denominador en esos endpoints, por lo que el número efectivo
   de padres de evento fluctúa en cada réplica. Extras usa18. Esto NO rompe el
   emparejamiento ni trata frames como independientes; no lo califico como
   invalidez global. Pero el lector debe conocer este diseño, distinto de
   remuestrear siempre18/27 padres de evento. Conservar los intervalos congelados;
   si se desea sensibilidad con estratos fijos, declararla posthoc, no reemplazar
   silenciosamente los originales.
2. **Primera alarma versus primera identificación.** `metrics.py:35–38` toma
   la etiqueta del diagnóstico asociado a la primera alarma, aunque ese
   diagnóstico llegue después. Para Chen ambos tiempos coinciden. La explicación
   suplementaria existe; el encabezado «first source» debe distinguir ambos
   instantes también en la tabla. No atribuir al físico una localización ya
   disponible en el instante de una alarma todavía sin etiqueta.
3. **Comparación a distinta tasa de alarma.** El texto ya admite el problema.
   Mantener «644 frente a330, con72 frente a29 extras» unido en abstract y
   conclusiones. No convertirlo en «mejor detector» sin una función de coste
   declarada o curvas obtenidas con calibración separada. Las cotas Poisson para
   cero alarmas, si se usan, deben conservar su hipótesis de proceso; 72 replays
   no son72 padres independientes.
4. **Entrega reproducible.** Hay código, hashes y procedimientos internos
   sólidos, pero el manuscrito/suplemento actual remite a rutas de un repositorio
   sin una localización pública versionada verificable. Antes de envío, añadir
   declaración de disponibilidad, dependencias/versiones y un punto de entrada
   reproducible que un revisor externo pueda usar, o explicar restricciones.
   Compilar el ZIP LaTeX no equivale a reproducir la inferencia.
5. **Transferencia y ciber.** RAW0001 fue usado para calibración y el filtro
   físico lo rechaza por ruido ROCOF del prefijo; no existe validación externa
   de ese filtro. Missing/bad-data son una interfaz/clasificador heredados,
   no atribución conjunta de ataques. Esto está declarado; mantenerlo así.
   No exigiría por principio todas las familias o datos de campo para un paper
   de simulación bien acotado, pero tampoco permitiría presentarlo como solución
   completa demostrada de la hackathon.

## Qué pediría en una respuesta de autores

Una respuesta satisfactoria debe cerrar el contraste ya iniciado, clarificar
el endpoint de restauración, mostrar el coste y fijar el alcance de la
comparación. Puede preservar todos los métodos y resultados congelados.
Si el alcance se mantiene en «procedimiento de catálogo con recuperación en
un simulador conocido», la falta de GNN, calibración universal, eventos de
generación/falla o validación de campo no es automáticamente fatal. Si se
reclama superar ML/estado del arte o una contribución tensorial necesaria,
la evidencia actual es insuficiente.

**Conclusión del revisor:** hay un resultado real y útil sobre cobertura
oportuna y mantenimiento de episodios. El principal problema actual no es
una tabla inventada: es que la ventaja mecanística aún está pendiente y la
comparación principal enfrenta clasificadores ya débiles en carga. El paper
puede fortalecerse mostrando esos mecanismos y los cierres que ya están en
los artefactos, sin otra ronda de correcciones específicas por bus.
