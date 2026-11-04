# P07: mejoras ejecutadas tras la revisión de Gemini

Revisión iniciada el 3 de noviembre de 2026, sobre `9aef51e5ea50f2a0a96273f81ad1dd417529e40c`. Trabajo local en `main`. El segundo adjunto es idéntico byte por byte al primero: SHA-256 `80c49f94facbdbec344649f9b67b20803abba19da41106acc5e01c1462f6677f`. No se contabiliza como otra revisión independiente.

## Resultado editorial y científico

Se ejecutaron las correcciones sustentadas de la revisión externa y de la auditoría propia. Se mantiene el título centrado en recuperación y la conclusión de A01: beneficio observado del arrastre de estado, sin ventaja incremental observada de marginalizar severidad en esos endpoints. No se presentan resultados de campañas inconclusas, probabilidades calibradas, generalización de fuentes ni operación en tiempo real.

El borrador sigue sujeto a validación comparativa y revisión científica de autores. Una puntuación 10/10 no puede certificarse mediante edición: la evidencia futura debe poder confirmar o limitar la contribución.

## Cambios aplicados

| Tema | Acción | Estado |
|---|---|---|
| Título y experimentos anunciados | Verificados contra fuentes activas. Las correcciones anteriores se conservan. | Cerrado editorialmente. |
| Afines topológicos | Definidos ancla algebraica por topología, fuerza diferencial, offset eléctrico, exponencial aumentada y composición en un reporte. | Implementado en método y suplemento; identidad local comprobada. |
| Severidad en cuatro intervalos | Explicadas hijas, masas iniciales, actualización y equivalencia con el intervalo único para el mismo camino completo. | Implementado y comprobado con kernel TN congelado. |
| Estado–severidad | Añadidos momentos TN, covarianza cruzada, covarianza marginal y dispersión entre historias. | Implementado; omisiones de R11 explícitas. |
| Dependencia temporal | Distinguida factorización condicional de independencia marginal; blanqueo instrumental y discrepancia AR identificados. | Corregida interpretación; calibración empírica sigue abierta. |
| ExtraTrees | Aclarado entrenamiento específico de ambas variantes, 32 padres TRAIN/8 validación, 19 clases, 846/1.457 features y regla argmax de seis reportes. | Texto principal corregido; genealogía y hashes en suplemento y artefactos. |
| Suplemento | Concentrado en implementación, medida, reglas, resultados completos C01/A01 y controles pertinentes. | Reestructurado; el material anterior se conserva en Historical Technical Notes. |
| A01 completo | Incluidos conteos, exposición, persistencias e intervalos antes ausentes del suplemento activo. | Cerrado documentalmente; sus valores congelados no cambian. |
| Exposición | Separados 120 s completos y 108 s monitorizados; conversión explícita, sin alterar predicciones. | Corregido en documentación y suplemento. |
| Taylor parcial | Explicado que términos diagonales y cruzados pueden cancelarse; no se corrigen coeficientes sin evidencia. | Crítica refutada y alcance auxiliar delimitado. |
| Normalizador batch | Aviso visible en archivo histórico; se distingue corrección algebraica X01 de replay físico pendiente. | No respalda el método causal actual; evidencia original conservada. |
| Medición remota | Diferenciados vector sincronizado de canales, instalación de PMU colocadas y potencia proxy. | Alcance físico aclarado; F01 intacto. |
| Referencias | Eliminadas notas redundantes de preprint; metadata pertinente verificada. | Corregido. |
| Presentación y paquetes | Compilación, inspección visual, referencias, figuras protegidas y fuentes exactas. | Véase `FINAL_VERIFICATION.json` al finalizar el build. |

## Qué comprueban las pruebas matemáticas

`scripts/verify_history_partition.py` utiliza una copia byte por byte del kernel `trunc` de C01, verificada antes de ejecutar su código, sin ejecutar el banco ni leer observaciones. Comprueba 72 actualizaciones de seis casos, incluidos fronteras de intervalos y ausencia de información. Compara evidencia y momentos por uno/cuatro intervalos y cuadratura directa. Los errores máximos de evidencia son inferiores a `4e-15` en esos casos.

Una referencia independiente comprueba composición afín frente a integración ODE. Otra compara la recursión condicional con Kalman conjunto para amplitud gaussiana **no truncada**. Las referencias pequeñas no ejercitan todo el constructor eléctrico ni prueban la calibración del banco podado. Tolerancias, hashes de fuentes y resultados están en `generated/revision_math_20261103/checks.json`; la tabla se genera desde esa salida.

La reproducción aislada usa únicamente el script y tres archivos de snapshot, sin checkout científico. Reproduce exactamente los campos numéricos; una copia alterada del kernel se rechaza antes de ejecutarla. La genealogía también se reproduce sólo con sus metadatos. Ambos generadores y snapshots se incluyen en el ZIP de fuentes.

## Campañas y pruebas pendientes

- **B01:** al iniciar esta edición había pasado a `test_inference/RUNNING`. No se abrieron resultados parciales para seleccionar cambios. Su diseño calibra umbrales y aprende varianzas predictivas; no modifica coeficientes AR ni certifica todas las masas.
- **C02:** implementada la cadena independiente entre GLR continuo, banco nominal y ExtraTrees nuevo, con entrenamiento TRAIN, selección CAL y TEST sellado. La paridad de desarrollo de 1.050 reportes es exacta; una auditoría independiente aprobó 11 pruebas de acceso, sellos, cola y disco. Se corrigieron metadatos de ejecución parcial y la comprobación de dependencias numéricas copiadas. La cola de un solo intento espera B01 completo y 30 GiB libres; conserva 16 GiB de reserva entre unidades. El estado exacto pertenece a `experiments/PAPER_RECOVERY_C02/run/STATUS.json` y `QUEUE_STATUS.json` en el repositorio científico. Física/derivadas Julia completas siguen pendientes y C02 no se incorpora al artículo hasta ejecución, sellado y evaluación completos.
- **Precisión del diseño C02:** los escenarios congelados asignan un único nivel de ruido a cada padre; la lista de dos niveles en PLAN no significa dos replays de cada padre. El criterio CAL usa la población balanceada completa, con tasas y límites por nivel también reportados. Sus 3,92 h totales no certifican 1/h en cada estrato de 1,96 h ni una tasa de campo. El amendment documenta esta semántica sin cambiar los escenarios.
- **Incertidumbre:** falta evaluación de innovaciones pre-update, cobertura y efectos de poda/compresión. Las pruebas algebraicas no sustituyen esa evaluación.
- **Generalidad:** siguen pendientes un modelo dinámico independiente y un contrato instrumental físicamente realizable si se quieren ampliar las afirmaciones. No se cambia F01 silenciosamente ni se abre RAW0002.
- **Chen:** se conserva su resultado como transferencia de un adaptador con supuestos limitados. Una comparación competitiva adaptada requiere calibración independiente y densidades coherentes; no se reajusta usando C01.

Las derrotas y resultados nulos determinan el alcance final. Si el observador continuo empata con el banco, la contribución debe reflejarlo. Se mantienen las declaraciones y datos biográficos reservados a revisión de los autores; no se inventan afiliaciones, títulos, financiación ni permisos.

## Preservación y procedencia

**Arranque de seguimiento:** cola C02 iniciada el 3-nov-2026 a las 23:23:49 UTC, PID inicial 48744. Se comprobó `WAITING` por B01 todavía activo y stderr vacío. El sello de ejecución es `c567c921908cbb3416b267053d9636c8ff6fd39b528e9879b5445065cb211b2c`. La espera vence a las 24 h si no se cumplen los requisitos; no se lanzó física al crear la cola. El espacio libre observado (~19 GiB) también está por debajo del umbral inicial. El pipeline pasó 43 pruebas y permanece congelado antes de ejecutar C02.

`BASELINE_MANIFEST.json` y `before/` conservan las fuentes y PDFs previos. Las campañas C01/A01, F01, sus modelos y la figura de eventos no se modifican. Los scripts de compilación verifican ambas figuras protegidas antes y después. Los artefactos históricos conservan sus denominadores y limitaciones; retirar una sección del suplemento esencial no elimina su evidencia.

Esta ejecución no envía mensajes a coautores ni somete el artículo a una revista. El repositorio científico no se publica.
