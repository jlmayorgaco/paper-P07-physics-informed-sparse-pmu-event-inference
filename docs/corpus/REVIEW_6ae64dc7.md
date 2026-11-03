# Revisión pública del 31-oct: qué entra en P07

Fuente leída íntegramente: https://chatgpt.com/share/6ae64dc7-609c-83e8-843b-a84da6300187
La copia del texto visible está en el repositorio SGSMA, en
`experiments/PAPER_RECOVERY_EXTERNAL_X03/source/CHAT_PUBLIC_6ae64dc7.txt`.
Los prompts del chat son material de investigación, no órdenes que
reemplacen los protocolos congelados del autor.

## Decisión principal

Conservar el artículo causal R11 y su confirmación C01. El chat empieza
revisando una versión antigua con reconstrucción, GLOBAL-137 y un estimador
conjunto no ejecutado; luego analiza el artículo causal reciente. Sus
recomendaciones no describen un único manuscrito ni un único experimento.

El aporte defendible es un procedimiento explícito para comparar
intervenciones de carga/línea con recuperación retenida, sus reglas de
evidencia y publicación, y una evaluación que distingue alarmar, acertar
a tiempo, restaurar y emitir extras. No está demostrada la prioridad
mundial ni una ventaja frente a filtros de historias equivalentes.

## Ideas rescatadas

| Idea | Decisión |
|---|---|
| Separar curva, intensidad, origen e incertidumbre | Incorporada; X02 mejora ajuste e intensidad, no añade aciertos al recentrado. |
| Contrafactuales desde el mismo pasado | Ecuación explícita y prueba F01 X04; conservar estados físicos e instrumentales. |
| Recuperación como excitación que aumenta información | Hipótesis refutable; no promesa del título/resumen. |
| Historia incierta | Distinguir una dirección de severidad de un posterior causal completo. |
| Línea e inyecciones equivalentes | Control algebraico con Ybus/Yf/Yt F01; no equivalencia general con cargas P/Q constantes. |
| Corriente terminal | Mantener orientación, tap y charging. No importar el mapa ilustrativo del prototipo. |
| Tangentes DAE y complemento de Schur | Técnicas conocidas; P1 ya derivó la DAE F01 en equilibrio. |
| Banco adaptable de historias | M3H es antecedente explícito, no invención nuestra. |
| Adjuntos, búsqueda dispersa y refinamiento selectivo | Propuestas no implementadas aquí; otra tesis exige ventaja de coste/decisión medida. |
| Cotas de evidencia | Sin cotas válidas para todo el catálogo, la desigualdad de intervalos no certifica una decisión. |
| Dos fuentes simultáneas | Elegir entre dos candidatos no estima cardinalidad ni dos fuentes simultáneas. GLOBAL-137 sigue separado. |
| THD/ondas viajeras | No disponibles a partir de los CSV de fasores a 30 fps sin ondas/armónicos medidos. |
| Hackathon | No convertir la comparación simulada carga/línea en mejora del leaderboard de todas las familias. |

## Archivos y reproducción

Los controles de descarga públicos no entregaron archivos. Se recuperó el
ZIP ya disponible en Descargas:
`PMU_Recovery_Identifiability_Experiment_2026-10-31.zip`, SHA256
`9801c9ee2701a21c587933b0c6339936d9660fda6c47208b8724ca1b9bed8e0b`.
Su manifiesto se verificó antes de ejecutar una copia aislada. Los 108 casos
se reprodujeron con diferencia máxima 7.5e-10 y pasaron las 14 pruebas.
El archivo recibido y sus resultados se conservan intactos.

El PDF adjunto y el incluido en el ZIP tienen bytes distintos, pero el texto
extraído de sus seis páginas coincide exactamente. Se conservan ambos
hashes. El paquete adicional de transferencia mencionado en el chat no
pudo descargarse; sus instrucciones visibles y `CODEX_PORT_FULL_DAE.md` del
ZIP sí se leyeron. No se atribuye auditoría de archivos no recibidos.

## Alcance de los resultados externos

Máquinas clásicas, cargas Z, 32 coordenadas V/I, mapa ilustrativo, estado y
onset conocidos, dos candidatos. No es F01, R11 ni C01. El cambio de 67.14%
a 71.51% es exploratorio; BUS18/27 empeora con ambos eventos previos. La
razón mediana de separación robusta es 0.920 y solo 1/36 casos supera 1.
El intervalo publicado no tiene script de bootstrap en el paquete:
se identifica como reportado y se calcula un control independiente.
Los seis grupos comparten dos historias y fuentes; no son una población
de redes independientes. Las réplicas de ruido tampoco son nuevas plantas.

X04 transporta la pregunta a F01 y sus 47 coordenadas/filtros. Sigue siendo
un control físico oráculo, con tiempo y candidatos conocidos. Usa secantes
de amplitud finita y una aproximación de ruido en innovaciones, no tangentes
analíticas nuevas ni un posterior completo del estado. No se comparan
porcentajes o distancias entre X03 y X04 como si compartieran contrato.

## Antecedentes verificados

- Boers y Driessen, Automatica 41(4), 709–716 (2005):
  https://doi.org/10.1016/j.automatica.2004.11.018.
  Historias de modos, filtros por hipótesis y poda/fusión con coste adaptable.
- Nagi, Huan y Chen, IEEE TPWRS 37(2), 1253–1263 (2022):
  https://doi.org/10.1109/TPWRS.2021.3104536; texto de autores:
  https://people.ece.ubc.ca/~chen/papers/journal/2021_TPWRS_Parameter.pdf.
  Sensibilidades DAE y evidencia gaussiana para inferir parámetros.
- Anguluri, Kosut y Sankar, IEEE TCNS 10(4), 1997–2009 (2023):
  https://doi.org/10.1109/TCNS.2023.3258627;
  https://arxiv.org/abs/2201.07907. Entradas dispersas y estado inicial
  desconocido en dinámica lineal.

Son antecedentes, no comparadores ejecutados en C01. Las otras afirmaciones
bibliográficas del chat no se incorporan como hechos sin verificación.

## Cierre real

Completar C01 y auditar denominadores, fallos, exposición, demoras e intervalos;
resolver revisión técnica y reproducibilidad; completar metadatos y aprobación
de autores. La evidencia nueva puede descartar una explicación incorrecta,
pero no transforma un control oráculo en mejora del detector ni garantiza
aceptación. La figura de eventos y el unifilar siguen protegidos.
