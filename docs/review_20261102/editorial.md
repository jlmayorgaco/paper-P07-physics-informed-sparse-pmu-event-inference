# Evaluación editorial independiente

Revisor: perspectiva editorial de ingeniería de potencia / inferencia estadística.
Fecha: 2 noviembre2026. Revisión del snapshot de14p, suplemento11p. No es una decisión de IEEE ni representa a sus editores.

## Contrato científico en cinco frases

Problema: atribuir intervenciones sucesivas de carga/línea a partir de ocho PMU, conservando la dinámica de recuperación.
Gap candidato: comparar historias nuevas y recuperación bajo incertidumbre de intensidad/contexto, con separación de mensajes de detección, diagnóstico y restauración.
Insight: una restauración cambia el operador pero no borra el estado; la historia física condiciona la predicción que compite por la siguiente observación.
Test falsador: un competidor que conserve estados, use el mismo diccionario/observaciones y tenga iguales reglas de publicación/presupuesto de falsas alarmas podría explicar la misma ganancia sin la maquinaria propuesta.
Consecuencia: identificar dónde el modelo físico ayuda a localizar cargas y dónde el error de modelo provoca alarmas; no afirmar superioridad universal.

## Veredicto

No listo para envío. Apto para revisión crítica por coautores. Existe trabajo ejecutado y reproducible, pero el argumento de novedad reúne componentes de varias campañas sin una ablación causal de la parte central; un resultado alto en simulación compartida no demuestra necesidad de Bayes ni ventaja tensorial del método causal.

## Fortalezas

- Ecuaciones DAE, corrientes orientadas, incertidumbre local de intensidad y estados conservados tienen especificación técnica; no se limita a apilar features.
- Comparación cerrada de procedimientos con fallos y alarmas, unidad de remuestreo por padre y un resultado de carga considerable.
- Se preservan contribuciones de features y el ZIP entregado sin llamarlo artificialmente el ET causal.
- Se declaran falta de calibración, mapaBUS5 provisional, alcance de nueve cargas/nueve líneas y fracaso de transferencia directa.

## Objeciones principales

1. **Novedad no aislada.** Bayes, historia multimodelo y firmas físicas son precedentes. M/DeltaM resumen pesos; el tensor mixto de dos cargas pertenece a otro estimador. La contribución debe formularse como procedimiento/comparación específica; la necesidad de sus componentes exige una ablación bajo un contrato común.
2. **Competidores de distinta fuerza y alcance.** Chen es un detector de primera parada bajo hipótesis no satisfechas; Warner y la GNN física de Li son relacionados pero no comparadores ejecutados. Una GNN no es requisito editorial universal, pero no cabe atribuir superioridad frente al estado del arte general.
3. **La historia científica se dispersa.** Reconstrucción,features,tensor de segundo orden,bancoGH31,causal,cyber pertenecen a distintas configuraciones. Un mapa de evidencia compacto debe mostrar la conexión y marcar las partes no conectadas experimentalmente. Las cifras100% del archivo con normalización errada no deben anclar la novedad.
4. **Transferencia limitada.** Generador e inferencia comparten familiaF01/mapa. RAW0001 es retrospectivo y conocido; no un examen externo. No se puede convertir un split70/30 de otra campaña en test del métodoC01.
5. **Reproducibilidad de entrega.** El ZIP del artículo reproduce LaTeX; no equivale a un entorno autónomo capaz de regenerar toda la inferencia. Distinguir reproducción editorial y científica.

## Literatura y requisitos comprobados

- Katanic/Lygeros/Hug: estimación recursiva con DAE incompleta; https://arxiv.org/abs/2305.10065. Es precedente de reconstrucción, no el mismo problema de eventos sucesivos.
- Li etal.,2024: STGCN de voltajes y restricciones tipo-topología/coste; https://doi.org/10.1049/gtd2.13331. Representa una ruta física+ML real y relevante; no se ejecutó aquí. El artículo no puede convertir una diferencia de arquitectura en superioridad empírica.
- Warner: la referencia DOI10.36227/techrxiv.23264519.v1 está presente; el acceso web al PDF falló en esta revisión. No certifico una lectura nueva completa ni prioridad exclusiva frente a él.
- IEEE Access permite artículo original de desarrollo/investigación; pide formato fuente+PDF, referencias pertinentes, biografías y disclosureAI. No prescribe70/30 ni unaGNN concreta. https://ieeeaccess.ieee.org/authors/submission-guidelines/

## Cierre mínimo

Completar la entrega de resultados prometidos, precisar splits y cyber, comprobar trazabilidad matemática y limitar el claim. Para sostener el claim fuerte «Bayes/tensor causan la mejora», una comparación controlada nueva sería necesaria; no se repara con redacción. La selección de ese experimento debe hacerse antes de abrir otra prueba, sin ajustarC01.
