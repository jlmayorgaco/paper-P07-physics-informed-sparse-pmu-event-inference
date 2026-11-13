# P07: estado de cierre vigente

La revisión del 13 de noviembre ejecuta dos diagnósticos independientes con
operadores nominales, sin cambiar C03. Con inicio, amplitud y media de recuperación
conocidos, conservar la covarianza mejora la fuente correcta de 281/360 a 338/360
(+15,83 pp; IC 95% [11,94; 19,72]). Es una prueba bajo el modelo gaussiano declarado,
no un resultado del banco completo ni de transferencia. La prueba causal de ruido
usa 36 normales CAL, 36 normales TEST y 36 padres TEST con dos cargas. Fijo,
continuo y con bloqueo obtienen 13/72, 15/72 y 13/72; no hay mejora concluyente de
atribución. El bloqueo admite solo el 8,13% de reportes normales monitorizados.
No se retocaron parámetros tras TEST. Los hashes, umbrales y publicaciones pasaron
un recuento independiente. Ver experiments/adaptive_innovation_20261113/README.md.

La arquitectura TikZ se redibujó con red eléctrica, fasores, recuperación,
trayectorias, matrices, incertidumbre y reloj de publicación. Núcleo implementado,
desarrollo adaptativo y capa ciber siguen separados. Artículo: 19 páginas;
suplemento: 34 páginas, Figura 15 en página 32. Las figuras protegidas conservan
sus hashes. Los nuevos resultados aparecen en el suplemento y sus límites en
la discusión; no se añaden promesas adaptativas al resumen.

**Estado: borrador para revisión científica.** El manuscrito incorpora la comparación C02 sellada. La prueba de mecanismo a presupuesto común y la transferencia dinámica a una segunda planta pertenecen a C03. Solo se incorporarán después de que terminen y se auditen.

| Evidencia | Qué respalda | Límite |
|---|---|---|
| C01 | Comparación de cobertura y alarmas en el catálogo de carga y línea | Réplicas correlacionadas por padre, simulación de la misma familia |
| A01 | El reset perjudica al control a umbrales fijos | Marginalización y perfilado empatan; no se igualaron tasas de alarma |
| B01 | Tres brazos empatan en 72/72, con siete extras cada uno | La selección previa eligió alpha = 0; la corrección aprendida fue nula |
| C02 | Banco 99/108 y 8 extras; GLR 72/108 y 85; ExtraTrees 22/108 y 0 | Presupuesto común en CAL, 18 padres con eventos, 24 normales; contraste de procedimientos |
| Segunda planta histórica | Exploración con comparadores estáticos | Primer reporte mal etiquetado; el banco dinámico no se ejecutó |
| C03 | Sucesor con separaciones cortas y dos plantas | El 13 de noviembre CAL y sus umbrales quedaron congelados a las 07:21 (Bogotá). TEST de F01 sigue ejecutándose; aún faltan resultados sellados de ambas plantas. Ver C03_PROGRESS_AUDIT_20261113.md. |
| Diagnóstico de canales | Con el predictor nominal, la separación mínima V+I/V a 1 s tiene mediana 1,35 y rango 1,03–8,41 | Medias y amplitudes fijas, una covarianza nula común; no cobertura, FAR ni ganancia del detector |
| Sucesor de separación con magnitud rival ajustable | Mediana V+I/V de 1,53; cuatro fuentes cambian de rival más cercano | Perfilado determinista en [-0,2;0,2], líneas sin reescalado; no evidencia marginal ni evaluación del detector |

Las cifras C02 se regeneran con **python scripts/build_recovery_comparison.py**, sin acceso a las corridas ni a la verdad de TEST. El agregado, sello y cierre de evaluación están en **generated/frozen/recovery_c02_20261105**. C02 se abrió una vez en el repositorio científico; la importación no evalúa de nuevo.

La versión de revisión separa diagnósticos de firma y probabilidad de detección; distingue el perfilado del promedio sobre el prior. RAW0001 es una referencia retrospectiva. La evidencia de integridad y la atribución de todas las familias están en el suplemento. Los documentos fechados de noviembre conservan el historial.

El sucesor se encuentra en **experiments/PAPER_RECOVERY_C03** del repositorio científico. El informe **run/TEST_RESULTS.json** solo se considera evidencia después de **run/TEST_EVALUATION_LOCK.json** con estado **COMPLETE_SINGLE_USE** y el hash de resultado correspondiente. Antes de incorporar resultados, revisar por separado el efecto de la fusión y el reset, el costo en alarmas y las fallas de admisión.

La validación preliminar de la segunda planta registra `valid: true`, residuo
máximo de Kirchhoff de aproximadamente $2.3\times10^{-13}$ pu y continuidad
en los cambios comprobados. Es una comprobación de generación, no un resultado
de atribución ni una evaluación de transferencia. El proceso principal y su
trabajador estaban activos durante la revisión; no se reinició la campaña.
El método ahora incluye pseudocódigo numerado que explicita el orden causal,
el reemplazo del sufijo y el uso de las densidades exteriores guardadas.

La revisión visual y narrativa del 12 de noviembre concentra la Figura 1 en
el problema y las historias competidoras. La Figura 4 se construye ahora en
TikZ: operadores físicos, continuidad en OFF y composición de los 47 canales.
Sus curvas son ilustrativas, no resultados de los experimentos. La Figura 7
añade las diferencias pareadas y sus intervalos desde el mismo resultado C02
sellado. La tabla de poblaciones incluye ahora C02. Se simplificaron la
introducción y la entrada al método; el costo computacional cierra los
resultados y la discusión distingue mecanismo, transferencia, medición y
aproximaciones. Véase [el registro de revisión](VISUAL_NARRATIVE_REVISION_20261112.md).
El artículo conserva 19 páginas y las figuras protegidas en las páginas 5 y 6.
Esta edición no reevalúa C03 ni verifica la compilación autenticada en Overleaf.

El acabado posterior de las figuras 1, 4 y 7 unifica el reloj y el flujo de
hipótesis en TikZ, explicita la formación de las medidas y añade el intervalo
pareado del costo en alarmas. La [inspección visual documentada](FIGURES_1_4_7_POLISH_20261112.md)
incluye los archivos vectoriales y las páginas finales 2, 7 y 13.

El [plan autónomo de cierre](P07_AUTONOMOUS_CLOSURE_PLAN.md) reúne decisiones,
responsables y criterios. La revisión adicional separa suficiencia del estado
ampliado, compresión de distribuciones y atribución histórica. El suplemento
incluye las identidades y contraejemplos; `scripts/verify_recovery_distribution.py`
comprueba ejemplos finitos, sin atribuirles validación empírica del detector.
El artículo distingue el presupuesto objetivo común de tasas de alarma reales
iguales, que no han sido demostradas.

La [auditoría de ejecución](C03_EXECUTION_AUDIT_20261112.md) estima unas 14–15 h
restantes de CAL y unas 19–20 h adicionales de inferencia TEST, más generación
y bancos, a partir de tiempos observados. Son estimaciones, no una garantía.
El [importador](C03_IMPORT_CONTRACT.md) rechaza resultados incompletos o sellos
inconsistentes. No se ha importado evidencia C03. El [protocolo C04 de desarrollo](C04_DISTRIBUTION_CONTROL_PROTOCOL.md)
delimita un control adicional de covarianza; está diseñado, no implementado ni
ejecutado, y no sustituye a un TEST independiente.

Para el envío siguen pendientes terminar y auditar C03, resolver las objeciones
que sus resultados dejen abiertas, aprobación de autores y
[declaraciones](SUBMISSION_DECLARATIONS_PENDING.md). Por instrucción del autor,
se trabaja en LaTeX local y Git; Overleaf se actualiza mediante la sincronización
existente. La reconstrucción local aislada no certifica una compilación remota
observada. Consultar la [matriz de comparadores](P07_RELATED_EVIDENCE.md) para el
alcance de la comparación con literatura.

La integración posterior del 12 de noviembre corrige los terminales del
prototipo externo en un sucesor aislado. El mapa nominal de nuestro modelo
ya coincide con F01: no se cambió, y BUS5 conserva su condición provisional.
El nuevo diagnóstico de canales usa una copia de operadores de un banco CAL
terminado, sin leer verdad ni TEST y sin modificar la campaña. Incluye
covarianza temporal, descomposición condicional de corrientes y auditoría
matemática independiente por Luna. El artículo resume el resultado; el
suplemento añade la derivación y una figura vectorial. La Figura 6 principal
ahora diferencia con claridad separación frente al nulo y al competidor.
Artículo: 19 páginas. Suplemento: 30 páginas. La interacción entre memoria de
recuperación e información de corrientes sigue siendo una hipótesis para un
sucesor, no una contribución empírica ya demostrada.

La [integración de las nuevas derivaciones](HBG_INTEGRATION_DECISIONS_20261112.md)
añade el perfilado de severidad rival y el vínculo teórico con incertidumbre
de recuperación. El ejemplo hamiltoniano de cuatro buses se reprodujo y
pasó controles numéricos adicionales; su alcance sigue siendo ilustrativo.
No se añade un término energético independiente a la likelihood ni se cambia
el prior del detector. La figura del suplemento compara ahora magnitudes
fijas y ajustadas sobre los mismos operadores. Esta versión conserva
19 páginas de artículo y tiene 31 de suplemento. C03 permanece intacto.

La [nueva figura central](PAPER_METHOD_FIGURE_20261112.md), editable en TikZ,
reúne el problema y el método implementado en aproximadamente media página.
Es la Figura 1 en la página 2; sustituye el esquema anterior, conservado en
sus archivos originales. La composición distingue la inferencia en línea
del diagnóstico nominal de separación. No añade capacidades nuevas al
estimador ni modifica campañas. Se mantiene la paginación de 19/31 páginas.

La [revisión del 13 de noviembre](P07_REVIEW_20261113.md) corrige la ganancia
determinista bajo carry, distingue ruido e innovación y elimina referencias
obsoletas a predicciones. N01 usaba 0,05 % por componente, equivalente a
aproximadamente 0,071 % RMS TVE añadido; se corrigieron etiquetas y prosa,
sin modificar resultados ni C03. Las propuestas PNG de las figuras protegidas
son documentos separados; sus archivos activos y congelados no cambiaron.
