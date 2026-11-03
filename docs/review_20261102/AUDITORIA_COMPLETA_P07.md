# P07: dictamen de preparación para envío

2 de noviembre de 2026. Revisión editorial, eléctrica/matemática, estadística/ML, cyber/impacto y abogado del diablo. Los cinco informes son perspectivas independientes de revisión asistida; no representan a IEEE, David Celeita ni Masoud Barati. Se conservó el manuscrito recibido en `submitted_snapshot/`. Se revisaron fuentes, PDF, código y artefactos; no se repitieron las simulaciones completas ni se certificó cada dependencia externa.

## Dictamen

**Todavía no lo enviaría al journal. Sí lo enviaría a David y Masoud como borrador científico para decidir el alcance final.** Hay un procedimiento físico-bayesiano real y resultados medidos valiosos. No se ha demostrado que la ganancia provenga específicamente de Bayes, de memoria o de una operación tensorial. Tampoco hay evidencia de superioridad general frente al estado del arte ni transferencia independiente a datos reales.

No encontré fundamento para llamarlo un trabajo ficticio. Tampoco sería honesto certificarlo como «a prueba de revisores». La limitación principal es la atribución de la mejora y el alcance de la comparación, además de varias omisiones de presentación ya reparadas.

## Aporte que sí podemos defender

**Un procedimiento causal de atribución de cambios de carga y apertura de línea con PMU dispersas, que compara historias físicas de intervención y recuperación, integra incertidumbre local de intensidad y publica por separado alarma, diagnóstico y restauración.** El estudio muestra su cobertura de diagnóstico oportuno y su comportamiento durante eventos persistentes, y cuantifica el coste en falsas alarmas cuando la red se aparta del banco de modelos.

La física aporta predicciones de candidatos no instrumentados mediante DAE, topología, eliminación algebraica y corrientes orientadas. La evidencia bayesiana compara esas predicciones con mediciones, condicionada al contexto estimado y a las aproximaciones declaradas. Esta combinación describe el procedimiento ejecutado; **no prueba por sí misma prioridad científica** frente a bancos de hipótesis existentes.

La diferencia a explicar frente a Warner, filtros de múltiples hipótesis y estimadores DAE es el contrato específico de eventos sucesivos, recuperación y mensajes públicos bajo incertidumbre de red. La búsqueda de trayectorias, Bayes y la estimación de estados tienen precedentes. Un claim de novedad algorítmica fuerte necesita una separación más precisa de esos precedentes y evidencia controlada de la parte nueva.

## Respuestas a las preguntas del autor

| Pregunta | Evidencia real | Dictamen y límite |
|---|---|---|
| ¿Contribución clara? | Procedimiento causal, comparación congelada, mantenimiento de episodios y análisis de fallos. | Es defendible con ese alcance. «Bayes + tensor mejora muchísimo» atribuye una causa no aislada. |
| ¿Physics-informed? | DAE ensamblada de 114 estados diferenciales y 78 algebraicos, 38 entradas, Schur, mapa de medición, operadores ON/OFF y sensibilidades. | Sí, sustantivo. El predictor es local y comparte familia de modelo/mapa con el generador. No equivale a validación en campo. |
| ¿Matemática correcta? | Integral marginal local de intensidad, propagación de estado y reglas explícitas. Se verificaron convenciones y código. | No se identificó un error algebraico fatal nuevo. Posterior global aproximado: contexto plug-in, covarianzas compartidas, propuestas y poda. No hay garantía de optimalidad ni probabilidades calibradas. |
| ¿Tensor necesario? | M/Gamma/DeltaM agregan pesos; D/Q/Qij modelan interacciones en otro experimento. | M es una representación útil, no un algoritmo tensorial que por sí solo gane exactitud/coste. Qij no se utilizó en el predictor causal final. No confundir ambos resultados. |
| ¿Bayes necesario? | La marginalización está implementada; no es una etiqueta añadida a ExtraTrees. | Su ventaja frente a perfilar intensidad con el mismo banco y publicación no está aislada. |
| ¿Cyber implementado? | Disponibilidad, missing y clasificación heredada de datos corruptos; composición de mensajes verificada. | Sí como módulo de integridad separado. No como atribución conjunta físico-cyber, detección de intención maliciosa ni resistencia demostrada a ataques. |
| ¿Pseudocódigo? | Algoritmo por reporte, diagrama y desarrollo suplementario. | Sí. Se añadieron reglas exactas de soporte, confirmación, diagnóstico, reemplazo y cierre para eliminar ambigüedades. |
| ¿Análisis ML completo? | Features, ablaciones históricas, confusiones, dos ET causales, resultados por fuente y condiciones. | Útil pero no completo para un claim amplio: falta aislar componentes y un competidor fuerte con información y presupuesto de alarmas comparables. |
| ¿70/30 SIM y después RAW? | El ET de C01 usa 32/8 IDs físicos locales; el sucesor agrupado usa 31 fitting + 8 validación + 17 test. | Son modelos distintos. El aproximadamente 70/30 corresponde al segundo. Dos grupos normales se comparten en la validación interna original, sin demostrar fuga en C01. RAW0001 ya calibró el simulador: es retrospectivo, no test externo. |
| ¿Otros métodos? | Dos ET, Chen2016 para primera parada y GLR físico en un control secundario. | Sí. Warner/GNN son literatura, no comparadores ejecutados. Una GNN no es obligatoria por nombre; una comparación adecuada sí importa para sostener el claim. |
| ¿Ventajas y desventajas claras? | Más diagnósticos oportunos de carga y mejor persistencia; más extras fuera del banco, alcance limitado y arranque condicionado. | Se incluyen ambos lados. No afirmar superioridad universal ni reducción general de latencia. |

## Resultados que sostienen el aporte

C01 finalizó **171 trayectorias físicas y 342 registros observados**, sin rechazo físico ni fallo de inferencia. En continuo hay 108 intervenciones reproducidas bajo seis condiciones; los 648 casos no son 648 realizaciones físicas independientes. Los intervalos congelados remuestrean por padre.

| Procedimiento continuo | Familia y origen correctos antes de OFF /648 | Extras | Cargas /324 | Líneas /324 |
|---|---:|---:|---:|---:|
| Banco físico, cinco modelos | 644 | 72 | 322 | 322 |
| Banco físico nominal | 643 | 92 | 322 | 321 |
| ExtraTrees referencia | 330 | 29 | 15 | 315 |
| ExtraTrees corto | 352 | 16 | 30 | 322 |

La descomposición post hoc de **432 archivos de predicción sellados** encuentra que todos los diagnósticos emparejados emitidos antes de OFF aciertan familia y fuente. Por tanto, la ventaja principal es cobertura oportuna; no una mejora demostrada de exactitud condicional entre decisiones emitidas. Los eventos omitidos y tardíos permanecen en el denominador. Las extras se contabilizan aparte.

En las 162 aperturas persistentes, los cuatro procedimientos anteriores aciertan la primera decisión. Después, ambos bancos físicos producen **0 extras y mantienen 162 episodios abiertos al final**, lo esperable sin recierre; ET referencia/corto producen **164/179 extras** y conservan **16/61** abiertos. Esta lectura es un análisis descriptivo secundario de los artefactos congelados, no un nuevo endpoint confirmatorio. Las restauraciones de episodios no emparejados son 164/178; no representan todas las restauraciones falsas posibles.

Chen obtiene 74/162 primeras paradas correctas, 66 antes del evento y 22 con origen incorrecto después. Detiene los 72 registros normales. Tiene hipótesis y exposición distintas; no se convierte ese fracaso en una prueba de superioridad frente a todo método físico publicado.

La comparación histórica del ZIP de la hackathon conserva 0/96 atribuciones conjuntas frente a 96/96 del estimador físico temprano en la transferencia simulada examinada. **No es una mejora del score oficial**: distinta campaña, dominio y conocimiento previo. El ET causal del estudio final no es ese ZIP de ventanas de 30 segundos.

## Hallazgos que no debemos esconder

1. Los ET causales ya tenían cobertura de carga muy baja en validación: 0/72 y 4/72. El gap no demuestra una insuficiencia intrínseca del ML ni la necesidad exclusiva de Bayes.
2. Con R/X fuera del banco, el procedimiento físico acumula 68 extras en continuo. No existe aquí una comparación de todos los métodos al mismo presupuesto de falsas alarmas.
3. Nominal y mezcla difieren también en reglas de publicación; su comparación no es una ablación pura de incertidumbre de red.
4. El generador estima frecuencia/ROCOF con ajuste cuadrático robusto ponderado; el predictor usa uno fijo sin esos pesos. Las diferencias están documentadas. Las perturbaciones de frecuencia/ROCOF añadidas después no son la derivada exacta del ángulo exportado ruidoso.
5. El mapa tiene terminales no coincidentes de V/I en BUS2 y BUS10; su producto es un proxy, no potencia terminal medida exactamente. BUS5 sigue provisional y BUS39 tiene limitaciones.
6. El banco histórico GH31 conserva un problema conocido de normalización y un prior efectivo distinto. Sus cifras no prueban calibración ni un replay corregido; se preservan E_B/GH31.
7. Missing logra 14/14 ventanas positivas; datos corruptos 1/2, con 2 FP y 1 FN. La igualdad de composición en 180 ventanas no significa 180 ciberataques detectados.
8. El filtro físico no admite RAW0001 por el soporte del ruido ROCOF de arranque. El híbrido aprendido source-only mejora 1/24 a 2/24. No hay examen independiente «SIM entrenado, RAW aprobado».

## Reparaciones efectuadas en esta revisión

- Se hizo obligatorio el capítulo C01 del suplemento: antes un `IfFileExists` omitía silenciosamente tablas prometidas. Ahora incluye estratos, fuentes, intervalos por padre, fallos, demoras, restauraciones, censuras y primera parada.
- Se incorporó el GLR físico ya ejecutado: 37/54 y 37 extras, frente a 44/54 y 6 nominales, y 51/54 y 3 del banco, bajo su campaña secundaria. No se presenta como comparación a igual tasa de falsas alarmas.
- Se añadieron confusiones causales y persistencia con procedencia y hashes; no se cambió el emparejamiento ni se volvió a inferir.
- Se precisaron la ley ZIP constante-impedancia con P/Q firmados, el convenio temporal del observador, la condición LTI de aditividad, la medición de potencia y el operador de frecuencia/ROCOF.
- Se corrigieron el split ML, el alcance de RAW/cyber y los denominadores. Se separaron resultados históricos, confirmatorios y diagnósticos post hoc.
- Se conserva la figura de eventos y el unifilar protegidos. No se reajustaron métodos, planta, semillas ni umbrales; no se abrió RAW0002 ni se hizo push.

## Cierre mínimo, sin seguir creando versiones para buses

**1. Cerrar el claim con los coautores.** El borrador actual sustenta el procedimiento completo y su trade-off. Si se quiere afirmar que Bayes/memoria/tensores causan la mejora, hace falta una comparación predeclarada con igual banco, observaciones y publicación; integrar frente a perfilar intensidad y memoria frente a su ablación. No puede obtenerse esa conclusión retocando el texto o C01. No es necesario desarrollar otro detector para cada bus.

**2. Asegurar una comparación convincente para ese claim.** El GLR secundario ayuda, pero no iguala información, cohortes y presupuesto de falsas alarmas del resultado principal. Una campaña comparativa de cierre, si se mantiene el claim fuerte, debe fijarse antes de observar sus resultados. Warner o una GNN relevante son opciones según el problema y disponibilidad; no añadir una GNN solo para decorar. No he lanzado entrenamiento ni pruebas nuevas en esta auditoría.

**3. Cerrar reproducibilidad y envío.** El ZIP de fuentes reproduce los PDF, no toda la campaña científica desde un entorno limpio. Falta empaquetar/identificar públicamente código, modelos y datos permitidos con instrucciones verificadas, resolver las referencias y derechos/metadatos de autores con ellos y revisar la versión final. Si cyber conjunto o transferencia externa permanecen fuera del claim, no hay que abrir nuevas campañas para sostener afirmaciones que el artículo no hace.

Las reglas oficiales de IEEE Access no exigen una partición 70/30 ni una GNN específica. Exigen una contribución original y una presentación verificable, además de requisitos de formato y declaraciones: https://ieeeaccess.ieee.org/authors/submission-guidelines/ . Ningún informe permite prometer aceptación.

## Evidencia de la auditoría

Informes originales: `editorial.md`, `electrical_math.md`, `methodology.md`, `cyber_impact.md`, `devils_advocate.md`. Sus observaciones se refieren al snapshot previo; las reparaciones anteriores explican las diferencias con el PDF actualizado.

Datos derivados: `generated/review_diagnostics_20261102/PROVENANCE.json`, matrices CSV, `persistent_monitoring.csv`; generadores `scripts/build_review_diagnostics.py` y `scripts/build_complete_confirmation_tables.py`. Datos primarios: importación congelada C01 y sus manifiestos. Los reportes independientes no sustituyen los datos ni constituyen cinco validaciones experimentales nuevas.
