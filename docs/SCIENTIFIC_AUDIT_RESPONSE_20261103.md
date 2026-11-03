# Respuesta cientÃ­fica a la auditorÃ­a â€” 3 de noviembre de 2026

## Dictamen

**Borrador revisado para discusiÃ³n con coautores; revisiÃ³n cientÃ­fica mayor antes del envÃ­o.** La ediciÃ³n mejora la correspondencia entre afirmaciones y evidencia, pero no transforma controles de desarrollo en confirmaciÃ³n independiente. No se reajustaron mÃ©todos, casos, semillas, predicciones ni asociaciones de C01/A01. B01 sigue separado y sus resultados parciales no entran en P07.

## Contrato cientÃ­fico de esta revisiÃ³n

- **Problema:** las PMU muestran simultÃ¡neamente la recuperaciÃ³n de una intervenciÃ³n anterior y una posible intervenciÃ³n nueva.
- **Brecha:** el diagnÃ³stico necesita conservar una predicciÃ³n fÃ­sicamente consistente y distinguir presencia activa de causa originaria.
- **Mecanismo implementado:** historias de carga/lÃ­nea derivadas de la DAE, estados iniciales estimados, memoria instrumental y pesos condicionales de evidencia.
- **Prueba que puede refutar la interpretaciÃ³n fuerte:** comparar con un observador fÃ­sico continuo que conserve el mismo estado y reciba la misma informaciÃ³n, con calibraciÃ³n previa y evaluaciÃ³n independiente. Ya existe un primer control GLR de desarrollo; no cumple por sÃ­ solo toda esa prueba.
- **Consecuencia demostrada:** conservar las desviaciones fÃ­sicas al cierre mejora claramente los endpoints del control ejecutado. La necesidad de toda la arquitectura, la superioridad general de Bayes y la calibraciÃ³n de sus masas siguen sin demostrarse.

## Hallazgos contrastados con cÃ³digo y artefactos

| ObjeciÃ³n | Evidencia real | AcciÃ³n y estado |
|---|---|---|
| Tasas con startup en el denominador | `RECORDS.csv` da 120 s completos y 108 s monitorizados por registro de evento. La auditorÃ­a proponÃ­a 80/68, correspondiente a desarrollo, no a esta figura confirmatoria. | Se generÃ³ una conversiÃ³n exacta de diferencias e IC por **120/108 = 1,1111**, manteniendo originales intactos. Figura principal e intervalos suplementarios usan horas monitorizadas. |
| Bayes frente a perfil | A01: marginal/carry y perfil/carry empatan en 108/108 oportunos y una extra; ambos reset dan 75/108 y 166 extras. | El tÃ­tulo, resumen, contribuciones y conclusiÃ³n destacan recuperaciÃ³n consistente. No atribuyen la mejora a una necesidad demostrada de marginalizaciÃ³n. |
| Falta total de control fÃ­sico continuo | Existe un control de un estado comprometido con GLR, sin reset fÃ­sico: 37/54 y 37 extras; banco nominal con reloj comÃºn 44/54 y 6; cinco modelos 51/54 y 3. | Incorporado al cuerpo principal y sus ecuaciones al suplemento. Es desarrollo con tres padres y diferentes semÃ¡nticas de puntuaciÃ³n/bÃºsqueda; no reemplaza una validaciÃ³n independiente equiparada. |
| CatÃ¡logo y conocimiento desigual | C01 fija nueve cargas y nueve lÃ­neas heredadas del desarrollo; no es una selecciÃ³n representativa de los 39 buses ni una prueba de fuentes no vistas. | Tabla explÃ­cita de fuentes y lÃ­mite de informaciÃ³n frente a los adaptadores aprendidos. No se explica toda la diferencia como efecto aislado de arquitectura. |
| Mejora frente a ExtraTrees | 644/648 y 72 extras frente a 330/648 y 29; la ventaja se concentra en cobertura oportuna de carga. Las lÃ­neas son comparables al adaptador de ventana corta. | Conteos preservados, comparaciÃ³n acotada y nueva distribuciÃ³n descriptiva de demora con todos los eventos en el denominador. No es una mejora de la puntuaciÃ³n oficial de la hackathon. |
| Memoria en observaciÃ³n | El generador calcula f/ROCOF desde una historia causal de fase. | La ecuaciÃ³n de observaciÃ³n incluye estado instrumental aumentado. La secciÃ³n de medida explica fase A, rotaciones B/C sintÃ©ticas y las 47 coordenadas. |
| Terminales | Tabla existente, antes no incorporada al suplemento activo: tensiÃ³n y corriente pueden estar en terminales distintos. | La tabla completa de orientaciÃ³n, ganancias y fases queda incluida. BUS5 5â€“6 sigue provisional; se excluye el Ã¡ngulo I de BUS39. No se retocÃ³ la planta. |
| Novedad frente a IMM/M3H | Las historias de modo, filtros condicionales y poda son antecedentes directos. | RecursiÃ³n estÃ¡ndar explÃ­cita y distinciÃ³n entre operadores elÃ©ctricos, historia ON/OFF, causa y estado activo. No se presenta una nueva ley general de Bayes, propagaciÃ³n ni factorizaciÃ³n tensorial. |
| Coste computacional | Tabla ya generada con mediana/rango de etapas, pero ausente del texto principal. | Incorporada. La tasa amortizada queda por debajo de 30 reportes/s. Latencia por trama y memoria mÃ¡xima no estÃ¡n medidas: no se inventan. |
| Prior histÃ³rico defectuoso | El archivo auxiliar usa una normalizaciÃ³n de cardinalidad distinta de la declarada. | Su tabla y anÃ¡lisis pasan al suplemento como evidencia histÃ³rica cualificada; dejan de respaldar el resultado principal. No se corrige retrospectivamente el resultado ejecutado. |
| ContribuciÃ³n de firmas/contexto sin tabla principal | Experimento conocido ON/OFF, separado del detector causal. | Retirado de las contribuciones centrales; diseÃ±o, tablas, severidad y resultados nulos de decisiÃ³n conservados completos en el suplemento. |
| Resumen anuncia confusiÃ³n histÃ³rica | El resultado referido no era parte del cuerpo principal. | Resumen reescrito alrededor del mecanismo y los dos experimentos pertinentes. No promete una figura ausente ni mezcla cohortes. |
| Lenguaje interno y fragmentaciÃ³n | Once secciones con estudios heterogÃ©neos y cÃ³digos de desarrollo. | Ocho secciones, nombres cientÃ­ficos en el nÃºcleo; resultados independientes primero. Historias de desarrollo y cÃ³digos quedan en reproducibilidad/suplemento. |

## Novedad defendible

El aporte es una **construcciÃ³n elÃ©ctrica especÃ­fica de atribuciÃ³n secuencial con predicciÃ³n consistente durante la recuperaciÃ³n**, mÃ¡s su evaluaciÃ³n conjunta de cobertura oportuna, alarmas y cierre. Las ecuaciones de red definen quÃ© cambios pueden producir las PMU remotas; la inferencia compara esas explicaciones con estado inicial y severidad inciertos. Eso es una contribuciÃ³n aplicada real, aunque sus ingredientes estadÃ­sticos tengan antecedentes.

No se ha demostrado que el tensor sea una innovaciÃ³n algorÃ­tmica: M organiza pesos y su incremento explica cambios de atribuciÃ³n. El tensor de interacciones de dos cargas pertenece a otro experimento y no se anuncia como parte del detector evaluado. La igualdad marginal/perfil es evidencia nula que se conserva.

## Literatura primaria consultada y papel en la comparaciÃ³n

- [Boers y Driessen, Automatica 2005](https://www.sciencedirect.com/science/article/pii/S0005109804003243): filtros condicionales sobre historias de modos y nÃºmero adaptativo de hipÃ³tesis. Antecedente directo; no baseline ejecutado.
- [Warner et al., manuscrito de trayectorias de alta fidelidad](https://d197for5662m48.cloudfront.net/documents/publicationstatus/169966/preprint_pdf/fb88c972e89f2492099d5d5e00da2aac.pdf): candidatos de falla de lÃ­nea y bÃºsqueda de inicio con trayectorias PMU. No se afirma superioridad numÃ©rica sobre un mÃ©todo que no corrimos.
- [Anguluri et al., arXiv:2201.07907](https://arxiv.org/abs/2201.07907): recuperaciÃ³n de entradas dispersas y estado inicial desconocido en dinÃ¡mica lineal. Antecedente de fuente desconocida; contrato diferente de episodios conmutados.
- [Pomarico et al., arXiv:2607.00116v1](https://arxiv.org/html/2607.00116v1): reconstrucciÃ³n dinÃ¡mica desde PMU escasas en IEEE-39. Es preprint y se cita como reconstrucciÃ³n, no como atribuciÃ³n ON/OFF.
- [Dey et al., IEEE TSG 2026, pÃ¡gina del laboratorio autor](https://salapakalab.ece.umn.edu/publications/dey-2026-topology-change-estimation-in-power-distribution-networks/): detecciÃ³n/localizaciÃ³n de cambios topolÃ³gicos de distribuciÃ³n con validaciÃ³n HIL. Se incorpora para acotar la novedad; no se inventa una comparaciÃ³n de accuracy entre tareas diferentes.

La lista focal no constituye una revisiÃ³n sistemÃ¡tica exhaustiva ni demuestra prioridad mundial. No se agregaron cuaterniones, THD, GNN o teoremas sin implementaciÃ³n para aparentar novedad.

## QuÃ© falta y quÃ© no requiere otra versiÃ³n para un bus

1. **Control independiente equiparado:** validar el observador continuo/GLR existente frente al banco, con los mismos operadores, fuentes, datos permitidos y protocolo de calibraciÃ³n. Registrar una comparaciÃ³n especÃ­fica de continuidad frente a competencia explÃ­cita de recuperaciÃ³n; el reset extremo no la sustituye.
2. **Presupuesto de alarmas comparable:** seleccionar umbrales solo en entrenamiento/validaciÃ³n y evaluar una vez en un nuevo holdout. No reconstruir una frontera ROC confirmatoria escogiendo umbrales con C01. B01 estudia calibraciÃ³n en una campaÃ±a separada y no satisface automÃ¡ticamente toda la comparaciÃ³n con ExtraTrees/M3H.
3. **Correspondencia de modelos:** una planta o implementaciÃ³n dinÃ¡mica independiente pondrÃ­a a prueba el riesgo de inverse crime; perturbar R/X de la misma familia no lo elimina.
4. **Incertidumbre y poda:** calibraciÃ³n de masas, masa descartada y sensibilidad al tamaÃ±o del banco. Un margen perfilado causal puede ser una hipÃ³tesis Ãºtil; no se ofrece como certificado de error hasta validarlo.
5. **Antes del envÃ­o:** revisiÃ³n cientÃ­fica de coautores, permisos y declaraciones, comprobaciÃ³n bibliogrÃ¡fica final y paquete reproducible. El tiempo por trama y memoria deben medirse antes de cualquier afirmaciÃ³n de tiempo real.

Las prioridades 1â€“3 fortalecen el argumento cientÃ­fico; no se resuelven con una reescritura. Se evita lanzar otra campaÃ±a mientras B01 estÃ¡ en curso o modificar sus mÃ©todos. Para un artÃ­culo aplicado con afirmaciones mÃ¡s estrechas, los coautores deben decidir si el alcance actual es suficiente. Esta revisiÃ³n no garantiza aceptaciÃ³n ni afirma puntuaciones 10/10.

## Archivos y verificaciÃ³n

- `scripts/monitored_exposure.py` verifica exposiciones iguales por padre antes de convertir tasas; `generated/monitored_exposure_audit.json` conserva hashes y factores.
- `scripts/build_scientific_revision.py` genera catÃ¡logo y CDF descriptiva desde CSV sellados; no produce inferencias nuevas.
- Las imÃ¡genes protegidas se verifican por hash y por presencia en el PDF. Se revisan referencias, etiquetas y todas las pÃ¡ginas renderizadas antes de actualizar el paquete.
- C01/A01 y los baselines se conservan; RAW0002 permanece cerrado. No se envÃ­a el borrador a autores ni revista.
