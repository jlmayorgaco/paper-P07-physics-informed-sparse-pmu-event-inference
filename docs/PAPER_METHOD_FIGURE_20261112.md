# Figura central de P07

Se sustituyó la Figura 1 por una figura TikZ de doble columna que reúne
problema, datos, operadores físicos, banco de historias, evidencia y
publicación. Su altura con leyenda es aproximadamente media página; el
artículo conserva 19 páginas. El original de recuperación se mantiene en
`figures/recovery_overview/` y sus salidas anteriores.

## Lectura y contrato científico

- Arriba: intervenciones A/B y persistencia de recuperación; flujo de ocho
  PMU con 47 coordenadas y memoria instrumental. Las trazas son esquemáticas.
- Centro: grafo eléctrico genérico con generador, buses, apertura, carga y
  PMU; operadores DAE; hipótesis de carga/línea; dependencia estado-severidad;
  integral condicional y pesos de historia dentro de modelos de red.
- Abajo: publicación con masas activa y de causa, confirmación temporal y
  umbrales calibrados. El retorno indica continuidad del estimador.
- El diagnóstico nominal recibe firmas del predictor por una flecha
  discontinua. No se dibuja como gate de alarma ni como probabilidad de acierto.

La figura muestra el banco implementado. No atribuye al sistema una GNN,
un prior hamiltoniano ejecutado, un detector fuera de catálogo, covarianza
completa propagada por historia o probabilidades calibradas. La nota inferior
explicita las aproximaciones de historias y covarianza. Las alternativas
de red y el replay respetan el alcance descrito en el método.

## Archivos y reproducción

- Fuente editable: `figures/paper_method/main.tex`.
- Construcción: `python scripts/build_paper_method_figure.py`.
- Salidas: `figures/generated/paper_method.pdf` y `.png`.
- Inserción y leyenda: `sections/article_intro.tex`.

La fuente usa símbolos dibujados en TikZ, sin iconos raster ni fuentes de
iconos externas. Tipografía NewTX, paleta azul/verde/naranja compartida con
las figuras existentes, conectores fuera de las cajas y trazos distintos
para recuperación, flujo y diagnóstico. La construcción comprueba que el
PDF sea de una página y no contenga imágenes raster.

Se inspeccionó la figura aislada y la página 2 renderizada. Se separaron las
etiquetas temporales de las curvas para evitar cruces. Se comprobó la lectura
al tamaño de inserción y la compilación del artículo. Las dos figuras
protegidas conservan sus 16 hashes y siguen en páginas 5 y 6.

Se revisó también el panorama de las 19 páginas después del cambio de altura.
El paquete fuente reconstruye artículo y suplemento con el mismo texto y
paginación; el barrido editorial registra cero hallazgos. Persisten las
advertencias conocidas de la plantilla. La entrega se publica mediante Git
para la sincronización habitual con Overleaf; no se certifica una compilación
remota observada.
