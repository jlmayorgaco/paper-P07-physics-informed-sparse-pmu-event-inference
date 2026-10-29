# Revisión P07 y cierre finito

## Cambio de alcance explícito

Las guías iniciales describían un sistema híbrido aprendido, fuentes excluidas y PMU cambiantes. Esas metas no se convierten en resultados porque R11 mejore sobre ExtraTrees. El manuscrito revisado mantiene la formulación completa como propuesta y presenta tres componentes con contratos distintos: reconstrucción de estado, E_B batch y el componente causal R11. Esta revisión acota las afirmaciones al trabajo ejecutado; no marca como terminadas las campañas A–D originales.

## Contratos que no se mezclan

| Ruta | Qué está ejecutado | Qué no acredita |
|---|---|---|
| B0–B3 | Voltaje oculto; sensibilidad a punto operativo y recentrado AC | Identidad de un evento o covarianza conjunta fiable |
| E_B | Soportes de carga hasta dos fuentes, onset conocido, GH31/W2 | Vigilancia causal multi-familia |
| R11 / nominal | Inicio desconocido, carga/línea sucesivas, 47 canales, catálogo 9+9, estados conservados | 39 buses, fuentes excluidas, aprendizaje de discrepancia ni E_J completo |
| R12 | Ablación de admisión, cero extras pero regresión BUS16 | Mejora uniforme o nuevo método seleccionado |
| Chen2016 | Núcleo QCD persistente verificado y adaptador PMU-only | Clasificación de carga, restauración ni ARL garantizado en F01 |
| C01 | Configuración y solicitudes nuevas preparadas | Resultado confirmatorio: aún no existe |

## Diferencia frente a la hackathon

El resultado histórico ANDES tiene más familias y su propio split. H04 compara causalmente dos adaptaciones ExtraTrees congeladas con R11 bajo otro contrato restringido. Los porcentajes de esos dos experimentos no se restan para afirmar una mejora del leaderboard. La ventaja local de atribución frente a ExtraTrees es evidencia secundaria de la utilidad de hipótesis físicas; falta su confirmación con más padres y condiciones.

## Diagnóstico de novedad

Las formulaciones DAE, el filtro condicional, la mezcla finita, la búsqueda de cambio y la actualización Bayes no son nuevas por separado. La identidad ΔM es contabilidad exacta de evidencia y reponderación, no una nueva ley física. El argumento del artículo es que la recuperación de estado y la separación de intervenciones son objetos distintos, y que la geometría perfilada predice fallos que una cifra global oculta. La extensión causal debe demostrar utilidad frente a un detector publicado bajo un contrato compatible, sin borrar sus propias falsas alarmas o latencias.

No se declara prioridad mundial ni aceptación editorial. Los resultados pueden sostener una contribución acotada aunque una variante no gane todas las métricas.

## Tres bloques pendientes para envío

1. **Evidencia confirmatoria:** ejecutar C01, sellar predicciones antes de verdad, intervalos por padre, exposición normal, latencias y fallos completos. No retocar métodos tras mirar el resultado.
2. **Comparación y alcance:** escribir la comparación Chen/R11 en aperturas persistentes y la comparación R11/ML en secuencias; revisar literatura, igualdad de información, cadencia y coste. No extrapolar a fuentes no vistas.
3. **Cierre editorial y reproducibilidad:** auditoría final ecuación-código, referencias/figuras, afirmaciones/artefactos, compactación del artículo y revisión de coautores. El suplemento preserva teoría y contratos detallados.

Faltas, generación, PMU perdida y aprender una discrepancia más compleja son extensiones posteriores. No son requisitos escondidos para declarar cerrado el contrato restringido actual.

## Trazabilidad

`generated/frozen/continuous_20261029/MANIFEST.json` lista las copias de fuentes y sus hashes. H03/H04 son ahora desarrollo; ninguna fila se llama confirmatoria. Los CSV y macros se regeneran con scripts. El repositorio SGSMA conserva `experiments/PAPER_CONFIRMATORY_C01/references/R11_FREEZE.json`, el protocolo sellado y los requests nuevos.

Esta es una revisión técnica del mismo agente que integra el borrador, no un peer review independiente. Las limitaciones previas y los números de E_B no se sobrescriben.
