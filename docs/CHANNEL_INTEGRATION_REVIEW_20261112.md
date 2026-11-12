# Integración de terminales, canales y separación

## Cambios validados

- Sucesor del prototipo externo: terminal local FROM/TO, identidad de rama
  persistente al abrir, filas de observación y escala sintética de ruido
  corregidas. Comprobaciones independientes de las 46 ramas, KCL y apertura
  de cada una de las ocho ramas instrumentadas.
- Predictor nominal P07: mapa ya consistente con F01; BUS5 5–6 sigue
  provisional. No se trasladó al predictor la elección de ramas del prototipo.
- Diagnóstico de canales: instantánea compacta con procedencia y hashes,
  covarianza de reportes brutos con correlación temporal, medias de amplitud
  fija y descomposición condicional V / I dado V. Auditoría Luna independiente
  sin bloqueos matemáticos. No se reutilizan innovaciones de todos los canales
  como si provinieran de un observador que solo midiera tensión.

## Integración y lectura visual

El artículo incorpora únicamente el cociente de separación nominal; no
modifica resumen, resultados C02 ni afirmaciones de desempeño. El suplemento
contiene método, figura y controles. Figura 6 principal: marcadores abiertos
y llenos, escala logarítmica, familias con colores coherentes y referencia de
amplitud expresamente bajo el modelo. Figura nueva: separación V/V+I junto
con el porcentaje condicional calculado para una misma pareja.

Se inspeccionaron las páginas renderizadas del artículo 11 y del suplemento
18–19, además de la vista general de los documentos. No se encontraron
solapamientos en las figuras nuevas. La referencia ideal de score no se
etiqueta como umbral operativo de detección. El artículo conserva 19 páginas;
el suplemento pasa a 30. Las dos figuras protegidas siguen en páginas 5 y 6.

El paquete aislado recompila ambos documentos con texto y paginación
idénticos. El cálculo de canales también se repitió desde su instantánea
dentro de la extracción aislada, con un hilo BLAS: todos los controles
pasaron. Las diferencias de redondeo por BLAS no cambian los competidores
seleccionados ni las cifras publicadas. Persisten advertencias conocidas de
la plantilla sobre fuentes, colores y cajas de salida; no se presenta el
log como libre de advertencias.

## Límites y siguiente prueba

C03 permanece en ejecución: 55/72 CAL a las 17:59 del 12 de noviembre,
sin selección final ni evaluación TEST. Se leyó solo un banco CAL terminado
para extraer operadores nominales; sus hashes antes y después coinciden.
No se cambió configuración, ejecución, datos ni resultados de C03.

La idea común es distinguir un evento nuevo durante recuperación mediante
una representación suficiente de incertidumbre y mediciones eléctricas
complementarias. No se ha demostrado su interacción. El siguiente contraste
debe cruzar canales con controles de distribución, conservar la misma
política de propuestas y usar una nueva calibración y un TEST independiente.
El prototipo corregido y la identidad gaussiana no sustituyen esa prueba.
