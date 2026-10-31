# P07 — argumento y mapa de lectura revisados

Título de trabajo: *Physics-Informed Event Attribution From Sparse PMUs Under Model Uncertainty*. Autores, modelos y resultados conservados. Revisión narrativa del 30-oct-2026; no es una nueva versión de inferencia.

La pregunta es: con ocho PMU, ¿qué intervención explica mejor la historia observada, y cuándo puede distinguirse de las alternativas?

El texto sigue problema → predicción física → evidencia causal → M/ΔM → decisión → límite de resolución → comparación y fallos. La reconstrucción de estado y el banco batch son evidencia de apoyo con contratos propios; E_B/GH31 no se reemplaza por R11, ni E_J se presenta como terminado.

## Tres contribuciones acotadas

1. Mecanismo físico ejecutable: operadores DAE de carga/línea, medición terminal, estado estimado pasado, comparación causal y recuperación sin reset.
2. Interpretación de información: reconstruir un voltaje no equivale a separar fuentes; la geometría perfilada y el estudio batch explican la ambigüedad débil.
3. Evaluación trazable: desglose por familia y tiempo, nominal frente a mezcla, ablación negativa y confirmación independiente congelada. La novedad no se reclama por Bayes, Kalman o la palabra tensor.

## Lectura de las figuras

| Figura | Pregunta que responde |
|---|---|
| Arquitectura | ¿Dónde entran física, datos, hipótesis y decisiones? |
| Red IEEE-39 | ¿Qué medimos y qué fuentes admite el banco? |
| Señales | ¿Cómo se manifiestan dos intervenciones en las ocho PMU? |
| Resolución batch | ¿Detectar multiplicidad permite identificar las fuentes? |
| Secuencia y M/ΔM | ¿Cómo evoluciona la decisión y dónde llega tarde? |
| Compromiso de decisión | ¿Qué se gana y qué se pierde al reducir extras? |

El suplemento preserva pruebas, convenciones, estudios de estado y formulaciones propuestas. El texto anterior completo y su PDF están en `archive/narrative_before_20261030/`.

## C01 sigue intacta

No se miran resultados parciales para reescribir o ajustar el método. El ejecutor sigue congelado en SGSMA. Al completar la importación, `scripts/refresh_narrative_c01.py` integra sus resultados en esta estructura y conserva los gráficos detallados en el suplemento. La campaña no debe sobrescribir esta revisión con la estructura anterior.

Falta terminar C01, interpretar resultados completos y revisar afirmaciones/reproducibilidad/coautores para envío. No se exige ahora otra familia ni otra corrección por bus. No se abre RAW0002 ni se hace push.
