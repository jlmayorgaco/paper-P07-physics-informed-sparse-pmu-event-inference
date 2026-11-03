# P07: revisión para lectura científica (2 noviembre 2026)

Esta primera revisión redujo el artículo principal de 17 a 12 páginas;
la revisión posterior de lectura lo dejó en 11 páginas (véase
`P07_READER_PASS_2026-11-02.md`). Los métodos, escenarios,
umbrales, predicciones, métricas y resultados C01 permanecen intactos. El
PDF previo y sus cuatro figuras reemplazadas están en
`output/frozen/2026-11-02-pre-reader-revision/`. Las figuras aprobadas de
eventos y del unifilar no se regeneraron ni modificaron.

| Antes | Ahora | Pregunta que permite responder |
|---|---|---|
| Fig. 4: ocho PMU superpuestas en ocho paneles | Dos PMU fijas, corriente y ROCOF, ON/OFF visibles | ¿Qué sigue moviéndose después de restaurar una carga o línea? |
| Fig. 6: dos mapas de 18 filas y una identidad de masas | Cronología de seis eventos, diagnósticos correctos, alarma extra y diagnóstico tardío, con masa de bus 31 | ¿Qué falla exactamente bajo R/X fuera del banco? |
| Fig. 7: seis barras casi repetidas | Aciertos por carga/línea y extras por condición en la misma figura | ¿Dónde gana la física y cuál es su costo? |
| Fig. 8: doce intervalos dispersos en un eje | Seis estratos, dos ejes compactos para aciertos y extras con intervalos | ¿El compromiso persiste al remuestrear padres físicos? |

Las cuatro figuras nuevas se generan desde manifiestos sellados mediante
`scripts/build_reader_figures.py` y no alteran las figuras originales.
El inventario `branch.csv` del ejemplo de desarrollo tiene conversión
CRLF de checkout Windows; el script verifica sus bytes normalizados LF
contra el hash original sin escribir en el archivo congelado.

La narración principal usa nombres de método (`physical bank`, `nominal
bank`, `ExtraTrees`) y condiciones interpretables (`matched`, `R/X in bank`,
`R/X outside bank`). Los códigos internos de método y campaña quedan en el
suplemento y en los manifiestos. La tabla de diseños laterales y la sección
larga sobre entrenamiento grupal/RAW salieron del artículo principal; sus
resultados permanecen documentados en el suplemento y los expedientes.
El artículo ahora sigue problema → observaciones → predictor → decisiones
sucesivas → comparación confirmatoria → límites.

La figura del método y el Algoritmo 1 ya existían. El algoritmo aún debe
pasar de una enumeración explicativa a pseudocódigo plenamente ejecutable
con complejidad y coste por reporte si se quiere una garantía de
reproducibilidad a partir del artículo sin acudir al suplemento.

Esta revisión mejora la lectura; no resuelve el principal riesgo científico
de la auditoría previa: C01 compara procedimientos completos y no aísla la
ganancia causada por la memoria de recuperación. Tampoco iguala los
presupuestos de falsas alarmas de los comparadores.
