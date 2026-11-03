# Revisión independiente y cierre de la incorporación

Tres revisiones independientes requeridas por el flujo IEEE Access:

1. **Técnica:** no atribuir novedad a historia/IMM/M3H; no llamar ablación
   de incertidumbre a procedimientos con publicación distinta; explicitar
   evidencia predictiva antes del cribado, reglas del banco y condición de
   independencia en la ampliación de covarianza.
2. **Reproducibilidad:** fijar la dependencia instrumental X04; distinguir
   secantes/tangentes, 32/47 coordenadas, amplitud positiva perfilada/signed
   integrada, rango uno/posterior completo y draws/padres independientes.
   El intervalo bootstrap externo no incluía su generador.
3. **Lector experto:** poner alcance de severidad en resumen, anunciar X04
   en protocolo, aclarar prefijos pareados y retirar causalidad atribuida
   exclusivamente al banco incierto.

Las observaciones se incorporaron sin modificar métodos congelados. El
evaluador X04 ahora usa una copia exacta del puente X02 con referencias
locales selladas, antes de abrir sus resultados. La reproducción externa
no retoca ningún dato. Se agregó una enumeración independiente de las
46.656 remuestras de seis grupos: intervalo descriptivo [-0.750,9.125]
puntos, que incluye cero. No se presenta como inferencia poblacional.

El artículo incorpora M3H y sensibilidades bayesianas de Nagi/Huan/Chen
como antecedentes, la distinción entre historia e información y el
control F01 negativo. La mejora media de origen X04 es cero. No se ha
implementado un nuevo filtro óptimo ni una búsqueda adjunta certificada.

## Mapa ejecutable R11

Raíz SGSMA `experiments/PAPER_CONFIRMATORY_C01/run/runtime/`:
- `PROTOCOL.json`: riesgos birth/OFF, segmentos de amplitud, tamaño de haz,
  reglas de cribado, confirmación y aproximaciones declaradas.
- `core_v6.py`, `StreamTensor.transitions/process`: nacimiento,
  descendencia OFF conservando estados, integración, normalización y poda.
- `retro_birth.py`, `seed`: reconstrucción retrospectiva y reemplazo de sufijo.
- `continuous_bank.py`, `ContinuousBank.process`: propuestas desde el banco
  continuo; no implica evaluar exhaustivamente todos los inicios de 10 s.
- `confirmation_r08.py`, `SingleClockBoundaries`: publicación separada de
  los cambios físicos.

Raíz SGSMA `experiments/E5_VALIDATION_PAPER/M03_R11_FROZEN_DISCREPANCY/observer/`:
- `static_rx.py`, `predictive_log_density/Particle.attach/StaticRX.process`:
  evidencia externa guardada antes del cribado y actualización de pesos.
- `run.py`: ejecutor PMU-only con límites de lectura.

El sello de ejecución C01 fija estos insumos. Se consultó código y
configuración, nunca predicciones parciales para ajustar o elegir afirmaciones.

## Estado de envío

Versión preparada para revisión crítica de coautores después de compilar y
comprobar figuras. **Todavía no para envío:** C01 está ejecutándose; faltan
sus resultados completos, auditoría de denominadores/fallos/exposición,
comparación confirmatoria y la revisión final de autores y metadatos.
No existe prueba de superioridad frente al mejor IMM/M3H físico comparable.
Debe mantenerse una contribución de procedimiento y evaluación acotada,
o ejecutar esa comparación por separado antes de reivindicar superioridad.

Se conservan byte por byte la imagen de eventos y los snapshots protegidos
del unifilar. No se abre RAW0002, no se recalibra ni se hace push.

### Verificación editorial final
PDF principal de 15 páginas, nota de 4 páginas, inspección visual y 16 hashes de figuras protegidas verificados. Se retiró del cuerpo principal la ecuación de extensión futura de covarianza conjunta: permanece como idea del corpus, no como método ejecutado. Se corrigió una barrera de floats que creaba una página casi vacía. Los 90 archivos protegidos F01/C01 conservan sus hashes. C01 continúa en ejecución; aún no hay conclusión confirmatoria ni declaración de listo para envío.
