# P07: estado de cierre vigente

**Revisión de narrativa, 14-nov-2026.** El artículo plantea la
atribución antes de la restauración, presenta los tres procedimientos y
explica la calibración antes de mostrar sus resultados. Separa la
comparación principal, el control de continuidad y las pruebas de
sensibilidad. El suplemento conserva los detalles de las evaluaciones
secundarias. Artículo de 16 páginas y suplemento de 43. C03 sigue
pendiente de cierre, con 38/72 registros nominales de P2 en la consulta.

**14-nov-2026.** Se completó el contraste retrospectivo de covarianza al
0,05% y 0,10%. Ningún oráculo superó al estimador por familia y la exposición
normal fue de 0,3267 h por brazo. Se reprodujo una ablación sintética con
inicio desconocido y se ejecutó una segunda semilla. C03 no tiene todavía
el sello conjunto. Véase el [criterio de envío vigente](P07_SUBMISSION_GATE_20261114.md).

**13-nov-2026, 22:21 Bogotá.** El apéndice X integra el contraste
retrospectivo R11 al 0,05% por componente. Familia, estructura y oráculo
obtuvieron 11/12 cargas oportunas. Ledoit–Wolf obtuvo 10/12. Los cuatro
registraron cero alarmas normales en 0,3267 h por brazo. El resultado
del 0,10% permanece en ejecución. C03 tenía 68 registros P2 exportados
y el sello F01. La evaluación conjunta de C03 sigue pendiente.

**13-nov-2026, 21:30 Bogotá.** C03 selló las predicciones de F01 y
está exportando TEST de P2 (38 registros exportados en el último corte).
El cierre combinado aún está pendiente. La corrida de covarianza R11
lleva 23/48 replays CAL y pasa automáticamente a TEST tras fijar los
umbrales. La evidencia de esta versión incluye la validación numérica
del modelo de ruido añadido. Las conclusiones de atribución requieren
terminar TEST y auditar su exposición normal.

**13-nov-2026, 21:00 Bogotá.** C03 completó 72/72 registros nominales
de TEST de F01 y sigue en las pruebas de estrés F01. La evaluación
sellada de ambas plantas sigue pendiente. El contraste retrospectivo de
covarianza con B01 está en ejecución. Pasaron la comprobación del modelo
del ruido añadido y un replay oráculo del banco. El
[plan de cierre](P07_JOURNAL_CLOSURE_20261113.md) fija la secuencia
para usar los resultados y preparar el envío.

**13-nov-2026, 19:34 Bogotá.** C03 terminó los 72 registros nominales
TEST de F01. Sigue pendiente el cierre sellado de ambas plantas.
El suplemento incorpora la reproducción de la ablación controlada de
memoria y un piloto de estimación de covarianza con verdad conocida.
Véase [la auditoría](MEMORY_COVARIANCE_AUDIT_20261113.md).

**Revisión de las 18:58 Bogotá, 13-nov-2026.** El artículo conecta la
comparación de procedimientos con la geometría de recuperación y conserva
19 páginas. El suplemento de 40 páginas añade tres diagnósticos reproducibles:
separación bajo incertidumbre en la carga anterior, derivadas de conmutación
y cruces secuenciales bajo desajuste del modelo normal. Los resultados
respaldan afirmaciones de desarrollo en sus respectivos contratos.
La [revisión de los adjuntos](REORGANIZATION_AND_EXPERIMENTS_20261113.md)
documenta las decisiones y el protocolo. C03 lleva 69/72 registros de TEST
de F01 y queda pendiente la evaluación sellada de ambas plantas. Los
estados fechados a continuación corresponden a revisiones previas.

**Última actualización: 13-nov-2026, 17:00 Bogotá.** Se revisaron los once
adjuntos nuevos, siete textos distintos. Véase
[la auditoría de la segunda ola](IDEAS_SECOND_WAVE_AUDIT_20261113.md).
Apéndice U incorpora una cota condicional de error de score con media y
covarianza y distingue ganador de masa de publicación. La implementación
se comprobó en 2.000 perturbaciones gaussianas, sin violaciones observadas;
no es una prueba de atribución. Las A nativas no son Laplacianas y tienen
un modo numéricamente cercano a cero: no se certifica una regla de olvido
por decaimiento global. El refinamiento selectivo no está habilitado en
el banco. Artículo 19 páginas; suplemento 39. C03 intacto: 60/72 registros
F01 TEST completados, proceso 32480 activo y sin archivos finales de
resultado/bloqueo. La revisión fue solo operativa, sin métricas de TEST.
Los bloques fechados siguientes son historial de avances anteriores.

**Actualización vigente: 13-nov-2026, 16:36 Bogotá.** El sucesor
`experiments/relinearized_recovery_20261113` reduce el RMSE de fase en la
recuperación de la línea de referencia de 3,191 a 0,139 grados (95,7%).
Actualizar la dinámica local cada 0,1 s mejora los cuatro casos de línea;
el control que cambia solo la observación no resuelve el error. Pasan los
11 criterios predefinidos en siete trayectorias. Se conocen evento, tiempos
y estado inicial: no es una mejora demostrada de detección. Para integrar
en el banco faltan propagación de covarianza compatible, integración de
severidad y una comparación con eventos desconocidos bajo nuevo CAL/TEST.
Apéndice U, Tabla 29 y Figura 18; arquitectura actualizada en Figura 15.
Artículo: 19 páginas; suplemento: 38. Los párrafos siguientes conservan
resultados y tamaños de revisiones anteriores.

C03: proceso principal 32480 activo; el último registro de campaña muestra
58/72 registros F01 TEST completados. No existen `TEST_RESULTS.json` ni
`TEST_EVALUATION_LOCK.json`; no se leyeron resultados parciales. La campaña,
sus entradas y sus umbrales no se modificaron. No se puede cerrar todavía
el contraste de mecanismo ni la transferencia a la segunda planta.

Las ideas del chat compartido y los adjuntos se clasifican en
[SHARED_IDEAS_AUDIT_20261113.md](SHARED_IDEAS_AUDIT_20261113.md).
Los contraejemplos impiden incorporar las garantías propuestas de
submodularidad, KL de compresión, consistencia y poda futura. El criterio
de envío permanece abierto: evidencia C03 sellada, auditoría de ambas
plantas, coherencia final de afirmaciones y aprobación de coautores.

La derivación suministrada se comprobó en su ejemplo de tres barras y se
conectó con el punto de operación real de F01. El nuevo estudio
`experiments/descriptor_bridge_20261113` extrae 192 variables nativas
(114 diferenciales, 78 algebraicas), verifica A/B/C/D y ejecuta seis
trayectorias no lineales. Las derivadas y los terminales pasan; eso no implica
precisión global. En recuperación, el error de voltaje complejo es ~1,48%
para cargas de 1%, ~14,8% para cargas de 10% y 30,7% para la línea. La
observación polar de primer orden evita el cambio artificial de magnitud
inducido por convertir exactamente un fasor tangente, pero conserva ~3,19
grados de RMSE de fase en la recuperación de línea. No es una evaluación del
banco completo ni una mejora de atribución. Se añade el Apéndice T y Figura
17: artículo 19 páginas, suplemento 37. C03 no se leyó ni se modificó en
este diagnóstico. Sus estados fechados abajo son la última revisión previa,
no una nueva comprobación de progreso.

La revisión hamiltoniana añade cuatro trayectorias nuevas F01: normal,
aumento/reducción de carga y apertura/restauración de línea. Se verifican
balance cinético y potencias terminales con el modelo no lineal completo.
Se deriva un subsistema mecánico hamiltoniano, no una energía total de la DAE.
El cambio de coordenadas conserva predicciones y decisiones de fuente, sin
mostrar ganancia de inferencia. La tolerancia absoluta de log-likelihood de
1e-6 falla (máximo 1,907e-6); se informa sin relajar el criterio. No se ha
probado un prior energético ni una mejora del banco completo.

La auditoría detectó un OFF erróneo en el diagnóstico auxiliar anterior.
Se conservaron sus archivos y se retiraron sus conclusiones. El sucesor
corregido usa semillas nuevas y ningún otro ajuste: covarianza 279/360 frente
a 343/360 (+17,78 pp; IC 95% [13,89; 21,94]). Los tres brazos adaptativos
obtienen 20/72; fijo y continuo incumplen el presupuesto normal en TEST.
No se declara ventaja adaptativa. Véanse los README de
experiments/hamiltonian_f01_20261113 y
experiments/adaptive_innovation_20261113_corrected.

Artículo: 19 páginas; suplemento: 35. Arquitectura en Figura 15; el balance
físico añade Figura 16. Figuras protegidas intactas. El ZIP de fuentes se
conserva localmente pero ya no se versiona: superaba 50 MB y bloqueaba la
sincronización de Overleaf. Ningún archivo vigente de Git supera ese límite.
C03 no se modificó ni se reejecutó en estos estudios.

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
