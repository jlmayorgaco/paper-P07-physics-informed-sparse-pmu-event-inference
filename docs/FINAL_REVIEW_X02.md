# Cierre de la revisión X02 y del artículo

## Qué está terminado

El candidato independiente `PAPER_METHOD_EI_X02` completó 142 trayectorias
físicas y 255 registros observados. No modifica R11, C01, F01 ni los baselines.
Los 80 casos físicos con intervención se observan con tres semillas comunes;
no son 240 intervenciones independientes. Cinco controles producen 15 registros.

El artículo principal tiene 15 páginas y se compiló separado del suplemento.
Su argumento sigue observaciones, predicción física, competencia de historias,
evaluación causal, prueba controlada de firmas y límites. Los resultados
históricos y sus problemas de normalización siguen en el suplemento/corpus.
La imagen original de eventos y el diagrama causal aprobado no se modificaron.

## Resultado que se puede afirmar

El recentrado del prefijo y el término E_i empatan en presencia/origen: 240/240,
sin selecciones de evento en los 15 controles. E_i reduce el error mediano
incremental de 1.2513% a 0.0561% y el error relativo mediano de intensidad
de 1.2032% a 0.3288%. El ensayo suministra familia y ON/OFF, y prueba cuatro
fuentes y una dirección escalar de operación. No demuestra mejora del detector
causal, calibración probabilística ni superioridad sobre la hackathon.
La comparación donde adaptar la referencia nominal empeora la intensidad
permanece visible. El detalle y los intervalos condicionales a las semillas
están en [ei-x02-results.md](ei-x02-results.md).

## Verificación ejecutada

- 255 observaciones sin campos de verdad, 301 reportes y 47 coordenadas;
  timestamps uniformes y sincronizados.
- Continuidad de estados ON/OFF, inicialización y constancia de parámetros
  estructurales comprobadas en las 142 trayectorias.
- Integral de evidencia por estadísticos de Gram frente a cuadratura directa:
  discrepancia máxima 2.02e-16 en el control numérico independiente.
- Derivadas revisadas con semipasos; frontera de lectura y causalidad del
  prefijo verificadas. No se ajustó tras observar el test.
- Sellos de 86 archivos F01, 735 archivos R11 y 36 entradas X02 verificados;
  el corpus verifica además siete archivos del ejecutor C01 sin leer resultados.
- PDF completo renderizado, con inspección del contacto de todas las páginas
  y de las páginas de ecuaciones, arquitectura, tabla y señales nuevas.
  No hay referencias/citas indefinidas. Persisten avisos tipográficos de la
  clase IEEE Access en cabeceras/salida y palabras clave; no se afirma cero
  avisos TeX. La inspección no muestra recortes de contenido científico.
- ZIP verificado por hashes y corpus regenerado desde su extracción:
  89 filas de resultados y 32 ideas con alcance y procedencia.

Los JSON completos se encuentran en `build/ei_x02_layout_audit.json`,
`build/ei_x02_package_check.json` y, en el candidato científico,
`results/FINAL_CHECKS.json` y `results/BASELINE_INTEGRITY.json`.

## Qué sigue pendiente

C01 sigue en ejecución y no se interpreta parcialmente. Su comparación
completa debe integrarse con denominadores, fallos, falsas alarmas, demoras
e intervalos por padre. Después corresponde revisar afirmaciones finales,
bibliografía, metadatos y aprobación de coautores. Esta revisión no certifica
novedad mundial ni convierte el manuscrito en listo para envío.
