# Respuesta científica a la auditoría — 3 de noviembre de 2026

## Dictamen

**Borrador revisado para discusión con coautores; revisión científica mayor antes del envío.** La edición mejora la correspondencia entre afirmaciones y evidencia, pero no transforma controles de desarrollo en confirmación independiente. No se reajustaron métodos, casos, semillas, predicciones ni asociaciones de C01/A01. B01 sigue separado y sus resultados parciales no entran en P07.

## Contrato científico de esta revisión

- **Problema:** las PMU muestran simultáneamente la recuperación de una intervención anterior y una posible intervención nueva.
- **Brecha:** el diagnóstico necesita conservar una predicción físicamente consistente y distinguir presencia activa de causa originaria.
- **Mecanismo implementado:** historias de carga/línea derivadas de la DAE, estados iniciales estimados, memoria instrumental y pesos condicionales de evidencia.
- **Prueba que puede refutar la interpretación fuerte:** comparar con un observador físico continuo que conserve el mismo estado y reciba la misma información, con calibración previa y evaluación independiente. Ya existe un primer control GLR de desarrollo; no cumple por sí solo toda esa prueba.
- **Consecuencia demostrada:** conservar las desviaciones físicas al cierre mejora claramente los endpoints del control ejecutado. La necesidad de toda la arquitectura, la superioridad general de Bayes y la calibración de sus masas siguen sin demostrarse.

## Hallazgos contrastados con código y artefactos

| Objeción | Evidencia real | Acción y estado |
|---|---|---|
| Tasas con startup en el denominador | `RECORDS.csv` da 120 s completos y 108 s monitorizados por registro de evento. La auditoría proponía 80/68, correspondiente a desarrollo, no a esta figura confirmatoria. | Se generó una conversión exacta de diferencias e IC por **120/108 = 1,1111**, manteniendo originales intactos. Figura principal e intervalos suplementarios usan horas monitorizadas. |
| Bayes frente a perfil | A01: marginal/carry y perfil/carry empatan en 108/108 oportunos y una extra; ambos reset dan 75/108 y 166 extras. | El título, resumen, contribuciones y conclusión destacan recuperación consistente. No atribuyen la mejora a una necesidad demostrada de marginalización. |
| Falta total de control físico continuo | Existe un control de un estado comprometido con GLR, sin reset físico: 37/54 y 37 extras; banco nominal con reloj común 44/54 y 6; cinco modelos 51/54 y 3. | Incorporado al cuerpo principal y sus ecuaciones al suplemento. Es desarrollo con tres padres y diferentes semánticas de puntuación/búsqueda; no reemplaza una validación independiente equiparada. |
| Catálogo y conocimiento desigual | C01 fija nueve cargas y nueve líneas heredadas del desarrollo; no es una selección representativa de los 39 buses ni una prueba de fuentes no vistas. | Tabla explícita de fuentes y límite de información frente a los adaptadores aprendidos. No se explica toda la diferencia como efecto aislado de arquitectura. |
| Mejora frente a ExtraTrees | 644/648 y 72 extras frente a 330/648 y 29; la ventaja se concentra en cobertura oportuna de carga. Las líneas son comparables al adaptador de ventana corta. | Conteos preservados, comparación acotada y nueva distribución descriptiva de demora con todos los eventos en el denominador. No es una mejora de la puntuación oficial de la hackathon. |
| Memoria en observación | El generador calcula f/ROCOF desde una historia causal de fase. | La ecuación de observación incluye estado instrumental aumentado. La sección de medida explica fase A, rotaciones B/C sintéticas y las 47 coordenadas. |
| Terminales | Tabla existente, antes no incorporada al suplemento activo: tensión y corriente pueden estar en terminales distintos. | La tabla completa de orientación, ganancias y fases queda incluida. BUS5 5–6 sigue provisional; se excluye el ángulo I de BUS39. No se retocó la planta. |
| Novedad frente a IMM/M3H | Las historias de modo, filtros condicionales y poda son antecedentes directos. | Recursión estándar explícita y distinción entre operadores eléctricos, historia ON/OFF, causa y estado activo. No se presenta una nueva ley general de Bayes, propagación ni factorización tensorial. |
| Coste computacional | Tabla ya generada con mediana/rango de etapas, pero ausente del texto principal. | Incorporada. La tasa amortizada queda por debajo de 30 reportes/s. Latencia por trama y memoria máxima no están medidas: no se inventan. |
| Prior histórico defectuoso | El archivo auxiliar usa una normalización de cardinalidad distinta de la declarada. | Su tabla y análisis pasan al suplemento como evidencia histórica cualificada; dejan de respaldar el resultado principal. No se corrige retrospectivamente el resultado ejecutado. |
| Contribución de firmas/contexto sin tabla principal | Experimento conocido ON/OFF, separado del detector causal. | Retirado de las contribuciones centrales; diseño, tablas, severidad y resultados nulos de decisión conservados completos en el suplemento. |
| Resumen anuncia confusión histórica | El resultado referido no era parte del cuerpo principal. | Resumen reescrito alrededor del mecanismo y los dos experimentos pertinentes. No promete una figura ausente ni mezcla cohortes. |
| Lenguaje interno y fragmentación | Once secciones con estudios heterogéneos y códigos de desarrollo. | Ocho secciones, nombres científicos en el núcleo; resultados independientes primero. Historias de desarrollo y códigos quedan en reproducibilidad/suplemento. |

## Novedad defendible

El aporte es una **construcción eléctrica específica de atribución secuencial con predicción consistente durante la recuperación**, más su evaluación conjunta de cobertura oportuna, alarmas y cierre. Las ecuaciones de red definen qué cambios pueden producir las PMU remotas; la inferencia compara esas explicaciones con estado inicial y severidad inciertos. Eso es una contribución aplicada real, aunque sus ingredientes estadísticos tengan antecedentes.

No se ha demostrado que el tensor sea una innovación algorítmica: M organiza pesos y su incremento explica cambios de atribución. El tensor de interacciones de dos cargas pertenece a otro experimento y no se anuncia como parte del detector evaluado. La igualdad marginal/perfil es evidencia nula que se conserva.

## Literatura primaria consultada y papel en la comparación

- [Boers y Driessen, Automatica 2005](https://www.sciencedirect.com/science/article/pii/S0005109804003243): filtros condicionales sobre historias de modos y número adaptativo de hipótesis. Antecedente directo; no baseline ejecutado.
- [Warner et al., manuscrito de trayectorias de alta fidelidad](https://d197for5662m48.cloudfront.net/documents/publicationstatus/169966/preprint_pdf/fb88c972e89f2492099d5d5e00da2aac.pdf): candidatos de falla de línea y búsqueda de inicio con trayectorias PMU. No se afirma superioridad numérica sobre un método que no corrimos.
- [Anguluri et al., arXiv:2201.07907](https://arxiv.org/abs/2201.07907): recuperación de entradas dispersas y estado inicial desconocido en dinámica lineal. Antecedente de fuente desconocida; contrato diferente de episodios conmutados.
- [Pomarico et al., arXiv:2607.00116v1](https://arxiv.org/html/2607.00116v1): reconstrucción dinámica desde PMU escasas en IEEE-39. Es preprint y se cita como reconstrucción, no como atribución ON/OFF.
- [Dey et al., IEEE TSG 2026, página del laboratorio autor](https://salapakalab.ece.umn.edu/publications/dey-2026-topology-change-estimation-in-power-distribution-networks/): detección/localización de cambios topológicos de distribución con validación HIL. Se incorpora para acotar la novedad; no se inventa una comparación de accuracy entre tareas diferentes.

La lista focal no constituye una revisión sistemática exhaustiva ni demuestra prioridad mundial. No se agregaron cuaterniones, THD, GNN o teoremas sin implementación para aparentar novedad.

## Qué falta y qué no requiere otra versión para un bus

1. **Control independiente equiparado:** validar el observador continuo/GLR existente frente al banco, con los mismos operadores, fuentes, datos permitidos y protocolo de calibración. Registrar una comparación específica de continuidad frente a competencia explícita de recuperación; el reset extremo no la sustituye.
2. **Presupuesto de alarmas comparable:** seleccionar umbrales solo en entrenamiento/validación y evaluar una vez en un nuevo holdout. No reconstruir una frontera ROC confirmatoria escogiendo umbrales con C01. B01 estudia calibración en una campaña separada y no satisface automáticamente toda la comparación con ExtraTrees/M3H.
3. **Correspondencia de modelos:** una planta o implementación dinámica independiente pondría a prueba el riesgo de inverse crime; perturbar R/X de la misma familia no lo elimina.
4. **Incertidumbre y poda:** calibración de masas, masa descartada y sensibilidad al tamaño del banco. Un margen perfilado causal puede ser una hipótesis útil; no se ofrece como certificado de error hasta validarlo.
5. **Antes del envío:** revisión científica de coautores, permisos y declaraciones, comprobación bibliográfica final y paquete reproducible. El tiempo por trama y memoria deben medirse antes de cualquier afirmación de tiempo real.

Las prioridades 1–3 fortalecen el argumento científico; no se resuelven con una reescritura. Se evita lanzar otra campaña mientras B01 está en curso o modificar sus métodos. Para un artículo aplicado con afirmaciones más estrechas, los coautores deben decidir si el alcance actual es suficiente. Esta revisión no garantiza aceptación ni afirma puntuaciones 10/10.

## Archivos y verificación

- `scripts/monitored_exposure.py` verifica exposiciones iguales por padre antes de convertir tasas; `generated/monitored_exposure_audit.json` conserva hashes y factores.
- `scripts/build_scientific_revision.py` genera catálogo y CDF descriptiva desde CSV sellados; no produce inferencias nuevas.
- Las imágenes protegidas se verifican por hash y por presencia en el PDF. Se revisan referencias, etiquetas y todas las páginas renderizadas antes de actualizar el paquete.
- C01/A01 y los baselines se conservan; RAW0002 permanece cerrado. No se envía el borrador a autores ni revista.
