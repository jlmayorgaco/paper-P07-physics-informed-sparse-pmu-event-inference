# Auditoría exigente de P07 — 2 de noviembre de 2026

## Dictamen ejecutivo

**No enviaría esta instantánea a la revista. Sí la usaría para una revisión
técnica con coautores, acompañada de este informe.** Hay ciencia y resultados
reales; la dificultad está en aislar el aporte, cerrar el estudio pendiente y
presentar comparaciones que soporten exactamente la conclusión anunciada.

Dictamen simulado compatible con IEEE Access: **Reject — updates required
before resubmission**. En preparación interna significa revisión mayor antes
de enviar, no abandonar el trabajo. No es una decisión real de la revista ni
una predicción de aceptación. IEEE Access pide solidez y avance identificable;
no exige que todo artículo invente una teoría general nueva.

Se auditó el PDF principal de 16 páginas, el suplemento de 15 páginas, las
fuentes activas, partes del código físico/estadístico y los artefactos de C01.
La instantánea y sus hashes están en `AUDITED_SNAPSHOT.json`. El manuscrito no
se modificó. No se abrió RAW0002, no se reajustó ningún método y no se miraron
resultados parciales de A01 para seleccionar cambios.

Se completaron cinco lecturas independientes: física/matemática, estadística/ML,
objeción adversarial, criterio editorial y claridad/uso operativo. Coinciden
en que no procede aceptar esta instantánea. La lectura de claridad no rechaza
el resultado central por faltar la ablación; pide cerrar inequívocamente su
estado. Las revisiones técnica y editorial sí la consideran importante para
la afirmación mecanística fuerte. La síntesis conserva esa diferencia: el
resultado del paquete es válido, pero no aísla todavía sus ingredientes.

## 1. Qué contribución sí puede defenderse

Una formulación prudente de la aportación es:

> Un procedimiento de atribución continua para cambios de carga y apertura de
> línea con PMU dispersas, que compara intervenciones con la recuperación que
> predice el estado estimado de la red, integra incertidumbre local de severidad
> y distingue actividad de la intervención y persistencia de su causa.

La pregunta útil es si una nueva variación medida requiere otra intervención
o puede explicarse por la recuperación anterior. Tiene relevancia operativa:
abrir, mantener y cerrar episodios sin confundir respuesta residual con un
evento nuevo. La formulación está implementada para un catálogo concreto.

Lo que todavía **no** queda demostrado es que esa combinación sea superior en
general a ML o a filtros de historias existentes, ni cuánto del resultado
principal se debe a la integración marginal y a la transferencia de estado.
El estudio controlado ya iniciado es el contraste adecuado para parte de esa
pregunta. Un efecto nulo también debe conservarse: obligaría a estrechar la
contribución, no a buscar otra versión que produzca el titular deseado.

| Pregunta | Resultado de la auditoría |
|---|---|
| ¿La física es real? | Sí: DAE, eliminación algebraica, mapas de corriente orientada y dinámica producen las predicciones. |
| ¿Es realmente bayesiano? | El integral local de amplitud sí; el banco completo es aproximado por sustitución de contexto, covarianzas compartidas, selección y poda. |
| ¿Es un filtro óptimo general? | No está demostrado; el artículo actual ya lo reconoce. |
| ¿M y ΔM aportan una teoría tensorial nueva? | No: son agregaciones y una identidad temporal. ΔM es diagnóstico, no una ley nueva necesaria para decidir. |
| ¿Usar GPU cambiaría ese dictamen? | No. Una aceleración medida sería útil, pero no prueba novedad de estimación ni mayor exactitud. |
| ¿Hay un defecto fatal confirmado en las ecuaciones auditadas? | No se encontró. Esto no certifica formalmente todo el modelo ni cada ruta de código. |
| ¿Es una solución completa validada de la hackathon? | No: el ensayo continuo cubre nueve cargas y nueve líneas; integridad y otras familias son componentes separados. |

## 2. Resultados que sí se verificaron

Los agregados C01 son coherentes con los CSV inspeccionados:

| Procedimiento | Familia/origen correctos antes de OFF /648 | Alarmas extra |
|---|---:|---:|
| Banco físico de cinco modelos | 644 | 72 |
| Banco físico nominal | 643 | 92 |
| ExtraTrees causal de referencia | 330 | 29 |
| ExtraTrees causal corto | 352 | 16 |

Son **108 intervenciones en 18 calendarios, repetidas bajo seis condiciones**,
no 648 eventos independientes. Hay mejor cobertura oportuna frente a esos
artefactos y mayor carga de alarmas extra. Todos los diagnósticos emparejados
que llegaron a tiempo acertaron familia/origen: la diferencia principal no es
una mejor clasificación condicional de los casos ya diagnosticados, sino
cuáles llegan a diagnosticarse a tiempo.

La comparación con la hackathon tiene otro contrato: el ZIP original usa
ventanas de 30 s, más etiquetas y otro dominio de entrenamiento. No se puede
restar su score al 644/648 ni decir que mejoró el leaderboard. La transferencia
histórica revela una limitación de dominio de la entrega, no una nueva nota
oficial de competición.

### Un resultado valioso que estaba mal explicado: restauración

La auditoría releyó `EVENTS.csv` sin cambiar asociaciones ni métricas C01.
Como criterio descriptivo de esta revisión se tomó cierre adelantado más de
un reporte: `off_delay_s < -1/30 s`.

| Procedimiento | Restauraciones asociadas disponibles | Cierres prematuros entre ellas | Eventos sin restauración asociada /648 |
|---|---:|---:|---:|
| Físico de cinco modelos | 644 | 0 | 4 |
| Nominal | 643 | 0 | 5 |
| ExtraTrees referencia | 330 | 52 | 318 |
| ExtraTrees corto | 352 | 26 | 296 |

La última columna incluye omisiones; no equivale al número de episodios abiertos.
Esta es evidencia **posthoc descriptiva**, con replays dependientes y cobertura
distinta, no un endpoint confirmatorio nuevo ni una prueba del efecto causal
de la memoria. El código y hashes están en `R2_CHECKS.py/json`.

La tabla suplementaria `c01_operational.tex` llama **False OFF** a otra cosa:
restauraciones de episodios no emparejados, con 58/68/29/16. El texto explica
su significado, pero el encabezado puede inducir a confundirlo con cierres
prematuros. Conservar ambos conteos con nombres y denominadores distintos
mostraría una utilidad concreta que hoy se pierde.

## 3. Objeciones que impiden recomendar el envío actual

### A. El resultado del componente central está pendiente

En p. 12, sección IX.A, se lee “in progress”. El 2×2 compara puntuación marginal
frente a perfilada, y transferencia de 114 desviaciones físicas al cierre
frente a su anulación. No elimina toda inferencia bayesiana ni toda memoria.
Tampoco está diseñado para explicar por sí solo las extras con R/X fuera del
banco: usa los padres matched con ruido original ya conocidos.

**Cierre exigible:** completar el estudio fijado, informar los cuatro brazos,
intervalos por padre y resultados nulos/negativos; reemplazar el estado pendiente
solo después de revisar las salidas completas. No cambiar C01 ni umbrales.

### B. El comparador ML principal es débil justamente en la familia que produce la ventaja

El protocolo principal, líneas 46–55, informa que los árboles ya lograban solo
0/72 y 4/72 cargas a tiempo en validación previa. Congelarlos protege contra
ajuste al examen, pero no demuestra que sean alternativas competitivas de carga.
En línea, el árbol corto y el físico empatan en 322/324.

**Cierre exigible:** mantener junto al titular esta condición y formular la
ventaja frente a esos comparadores concretos. Si el artículo quiere afirmar
superioridad general frente a ML/SOTA, sí falta un competidor competente
seleccionado fuera de C01. Añadir una GNN por nombre no resuelve el problema.
Para un artículo más estrecho de mecanismo/recuperación, la ablación y un
contraste físico compatible pueden ser más relevantes.

### C. La contribución no queda diferenciada con suficiente precisión de bancos de historias y trayectorias anteriores

Warner, IMM/M3H y detección física de aperturas ya cubren ingredientes centrales.
La literatura debe señalar la operación o capacidad que se adapta o incorpora,
no atribuir novedad al vocabulario “física + Bayes + tensor”. El informe
adversarial también identifica el antecedente PF/DAE con PMU parciales de
Yang, Chen y Zhai (2021), ausente en la bibliografía actual. Eso requiere
discusión de su contrato, no automáticamente otro benchmark.

**Cierre exigible:** una comparación de mecanismos: heredado, adaptación
eléctrica, diferencia de esta implementación y evidencia que la verifica.
No es necesario inventar un teorema para que una contribución de ingeniería
sea publicable. Chen debe conservarse como adaptación de alcance limitado:
funciona en su ley de prueba, pero su fracaso en F01 no demuestra inferioridad
general del método publicado.

### D. El paper aún obliga al lector a reconstruir demasiados métodos distintos

Sección V/Fig. 5 mezcla reconstrucción de voltajes, features históricas,
sensibilidades de dos cargas y selección de soporte. Esos componentes no
entran todos en el algoritmo continuo. La tabla histórica de soporte conserva
además un prior efectivo distinto del declarado por un factor 2π. Reconocerlo
es correcto; usarlo como validación del filtro actual no lo sería.

**Cierre exigible:** conservar los resultados y su procedencia, pero jerarquizar
qué entra en el método principal, qué solo lo motiva y qué pertenece al historial.
Puede reducirse o trasladarse material a notas/suplemento sin desperdiciarlo.
La columna vertebral debe ser problema → algoritmo ejecutado → contraste →
beneficio y coste → límite.

### E. Reproducción y utilidad operativa incompletamente presentadas

El método tiene pseudocódigo, pero el comportamiento también depende del
publicador: pantalla de fuente, regla temprana de línea, dos relojes OFF y
reemplazo de episodios. Los archivos heredados contienen opciones inactivas.
Un revisor externo necesita el contrato activo, no reconstruir la genealogía.
Falta asimismo un coste de ejecución integral comparable con ExtraTrees;
30 reportes/s es la cuadrícula de entrada, no throughput demostrado.

**Cierre exigible:** receta activa verificable, tabla del mapa completo de
terminales, dependencias y punto de entrada del paquete científico. Presentar
inicialización, inferencia y memoria por separado usando registros existentes
cuando sean comparables. Un microbenchmark tensorial no sustituye esa medición.
El ZIP LaTeX reproducible acredita el documento, no toda la ciencia.

Además, el cuerpo principal define L y luego introduce las masas de historia
pi sin mostrar de forma compacta su transición y normalización. Ese puente es
central para entender el título bayesiano; puede explicitarse sin introducir
ecuaciones nuevas ajenas al código. El protocolo necesita rangos archivados
de duración, severidad, perturbación R/X y exposición: «antes de OFF» no se
interpreta igual para un evento de 0.2 s que para uno de 10 s. No estimar esos
rangos a ojo desde las figuras.

## 4. Riesgos técnicos que deben delimitarse, sin inventar fallos

- La eliminación de Schur es local y supone una carta regular. No prueba
  comportamiento ante singularidad ni ante una falla severa fuera del catálogo.
- El integral acotado de severidad y la actualización condicional m+d a son
  coherentes con el código revisado. La covarianza compartida y la pérdida de
  dispersión entre historias al cerrar no están validadas como incertidumbre
  calibrada. Si se anuncian intervalos de estado/severidad, requieren cobertura
  o deben quedar como estimaciones no calibradas.
- La búsqueda efectiva de nacimientos usa 0–18 lags, no todos los 300 reportes
  almacenados. El alcance demostrado son acciones abruptas del catálogo;
  no vigilancia universal de cambios lentos o fuentes invisibles.
- Generador y predictor comparten familia de ecuaciones y mapa instrumental.
  Perturbar R/X no es una validación con otro control, ley de carga o productor.
  No se identificó fuga de etiquetas por ese hecho; es validación dentro del
  modelo, con un límite claro de transferencia.
- BUS5 sigue provisional; BUS39 pierde el ángulo de corriente; V e I de algunas
  parejas no están colocadas en el mismo terminal. El paper ya lo reconoce.
  Falta centralizar el contrato, no recalibrarlo después del examen.
- RAW0001 es retrospectivo y el filtro físico lo rechaza bajo su contrato de
  ruido ROCOF. No hay validación externa del filtro. Integridad/missing y el
  clasificador heredado no equivalen a inferencia conjunta de ataques.
- Los intervalos bootstrap conservan padres y pares. Algunos endpoints incluyen
  normales con denominador cero, por lo que el número de padres de evento varía
  por réplica. Hay que documentarlo; no es una invalidez global ni autorización
  para reemplazar los intervalos originales silenciosamente.

## 5. Escritura y comunicación visual

La lectura visual cubrió las 16 páginas. Fig. 1 explica ahora el flujo, Fig. 2
es clara y debe conservarse intacta, Fig. 3 mantiene el unifilar. Fig. 8 muestra
un fallo concreto y Fig. 9 comunica bien ganancia y coste. No recomendaría una
reconstrucción visual general.

Los problemas son de foco. La contribución 1 reúne demasiados experimentos
distintos; la sección metodológica necesita hacer más visible el puente entre
likelihood, transición de historias y pesos; el procedimiento de publicación
no puede quedar resumido únicamente como “aplicar reglas fijas”. Fig. 4 muestra
datos, pero una comparación de observado/predicho y una hipótesis incorrecta
ayudaría a entender qué está evaluando la física si esas trazas ya existen.
No es un pedido de generar curvas ficticias.

Antes de referencias, el texto extraído contiene 22 usos de “frozen”, 12 de
“sealed” y 13 de “archived”. No prueba autoría automática: muestra una narrativa
demasiado centrada en procedencia y defensas. Hay que concentrar la trazabilidad
en el protocolo y dedicar el espacio a mecanismo y resultado. No aparecieron
R11, C01 ni “gate” en ese texto principal: esa objeción anterior ya fue resuelta.

La última página contiene solo una biografía y mucho espacio blanco. Es un
detalle editorial menor. Las fotos faltantes de dos autores no tienen el peso
científico de las objeciones anteriores. No se puede certificar origen humano
de un texto por estilo, ni prometer que ningún revisor cuestionará el artículo.

## 6. Ruta finita de cierre

1. **Cerrar A01 ya iniciado**, sin seleccionar otro método por el resultado.
   Si no aporta efecto aislado, ajustar la afirmación y conservar el resultado.
2. **Aclarar resultados existentes:** cobertura frente a clasificación,
   cierres prematuros frente a OFF de episodios no emparejados, omisiones y
   costes. Estos cambios de presentación no requieren corregir buses.
3. **Fijar una contribución y su alcance:** recuperación/atribución dentro del
   catálogo; comparar intelectualmente con trayectorias y bancos de historias.
   Si se mantiene una afirmación amplia de superioridad ML, queda abierta una
   validación adicional contra un comparador de carga competente.
4. **Concentrar el artículo:** mecanismo y pesos explícitos, mapa instrumental
   autocontenido, separar evidencia histórica y agregar disponibilidad/coste.
5. **Revisión de coautores y requisitos de envío:** bibliografía completa,
   permisos/procedencia de imágenes, autoría/afiliaciones, paquete de revisión
   y declaraciones que correspondan. La declaración de asistencia quedó
   pendiente por decisión del autor; debe resolverse antes del envío según
   la política IEEE aplicable, no confundirse con una certificación de ausencia.

No es imprescindible añadir GPU, una GNN, otra red, todas las familias, datos de
campo ni un filtro óptimo universal para un artículo de alcance acotado. Esas
ampliaciones sí serían necesarias si se reivindicaran sus capacidades. Esta
auditoría no autoriza nuevas campañas ni modifica las congeladas.

## 7. Verificaciones, alcance y fuentes

- Totales y nuevos conteos descriptivos: `R2_CHECKS.py/json`.
- Instantánea exacta: `AUDITED_SNAPSHOT.json`; verificaciones: `ROOT_VERIFICATIONS.json`.
- Ejemplo de integral frente a cuadratura: error 5.55e-17; es una prueba local
  de álgebra, no una certificación de todas las colas numéricas o la campaña.
- 16 hashes de figuras protegidas verificados; eventos en p. 4 y unifilar en
  p. 5. No hubo cambios del manuscrito durante la revisión.
- Se verificaron fuentes primarias cercanas, pero esta tarea no es una auditoría
  exhaustiva de cada referencia bibliográfica ni una prueba formal de todo el código.

Informes separados: `REVIEWER_1_PHYSICS.md`, `REVIEWER_2_STATISTICS.md`,
`DEVILS_ADVOCATE.md`, `EDITOR_INDEPENDIENTE.md`, `REVIEWER_3_CLARITY_IMPACT.md`.
La síntesis distingue objeciones confirmadas, limitaciones declaradas y pruebas
que solo harían falta si se amplía la afirmación.

Fuentes institucionales consultadas:

- [Criterios y decisiones de IEEE Access](https://ieeeaccess.ieee.org/reviewers/reviewer-guidelines/).
- [Preparación del artículo y política de contenido asistido por IA](https://ieeeaccess.ieee.org/authors/preparing-your-article/).
- [Reproducibilidad y requisitos del artefacto](https://ieeeaccess.ieee.org/authors/reproducibility/).

**Balance:** el paper no es vacío ni está listo. La mejor oportunidad es una
contribución precisa sobre atribución y manejo de episodios, con la física
como predictor verificable y resultados que expongan tanto cobertura como
alarmas y restauración. Más etiquetas de Bayes, tensores o GPU no reemplazan
esa demostración.
