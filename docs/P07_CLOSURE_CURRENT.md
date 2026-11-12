# P07: estado de cierre vigente

**Estado: borrador para revisión científica.** El manuscrito incorpora la comparación C02 sellada. La prueba de mecanismo a presupuesto común y la transferencia dinámica a una segunda planta pertenecen a C03. Solo se incorporarán después de que terminen y se auditen.

| Evidencia | Qué respalda | Límite |
|---|---|---|
| C01 | Comparación de cobertura y alarmas en el catálogo de carga y línea | Réplicas correlacionadas por padre, simulación de la misma familia |
| A01 | El reset perjudica al control a umbrales fijos | Marginalización y perfilado empatan; no se igualaron tasas de alarma |
| B01 | Tres brazos empatan en 72/72, con siete extras cada uno | La selección previa eligió alpha = 0; la corrección aprendida fue nula |
| C02 | Banco 99/108 y 8 extras; GLR 72/108 y 85; ExtraTrees 22/108 y 0 | Presupuesto común en CAL, 18 padres con eventos, 24 normales; contraste de procedimientos |
| Segunda planta histórica | Exploración con comparadores estáticos | Primer reporte mal etiquetado; el banco dinámico no se ejecutó |
| C03 | Sucesor con separaciones cortas y dos plantas | La ejecución seguía activa el 11 de noviembre; aún no existe `TEST_RESULTS.json` ni `TEST_EVALUATION_LOCK.json` |

Las cifras C02 se regeneran con **python scripts/build_recovery_comparison.py**, sin acceso a las corridas ni a la verdad de TEST. El agregado, sello y cierre de evaluación están en **generated/frozen/recovery_c02_20261105**. C02 se abrió una vez en el repositorio científico; la importación no evalúa de nuevo.

La versión de revisión separa diagnósticos de firma y probabilidad de detección; distingue el perfilado del promedio sobre el prior. RAW0001 es una referencia retrospectiva. La evidencia de integridad y la atribución de todas las familias están en el suplemento. Los documentos fechados de noviembre conservan el historial.

El sucesor se encuentra en **experiments/PAPER_RECOVERY_C03** del repositorio científico. El informe **run/TEST_RESULTS.json** solo se considera evidencia después de **run/TEST_EVALUATION_LOCK.json** con estado **COMPLETE_SINGLE_USE** y el hash de resultado correspondiente. Antes de incorporar resultados, revisar por separado el efecto de la fusión y el reset, el costo en alarmas y las fallas de admisión.

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

Para el envío siguen pendientes la revisión posterior a C03, confirmación en el proyecto autenticado de Overleaf, aprobación de autores y [declaraciones](SUBMISSION_DECLARATIONS_PENDING.md). Consultar la [matriz de comparadores](P07_RELATED_EVIDENCE.md) para el alcance de la comparación con literatura.
