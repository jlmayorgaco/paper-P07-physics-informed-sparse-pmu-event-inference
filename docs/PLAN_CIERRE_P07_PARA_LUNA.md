# Plan de cierre de P07 para GPT Luna

Fecha de preparación: 2 de noviembre de 2026, America/Bogota.
Este archivo es un plan de ejecución posterior, no una certificación de envío.

## 0. Misión, alcance y definición de terminado

Tu tarea es cerrar **el artículo existente** como borrador científico riguroso
para David y Masoud, con resultados completos, método comprensible y paquete
reproducible. Después debes señalar si satisface los requisitos técnicos de
envío o qué decisión de autores queda pendiente. No puedes garantizar aceptación,
ausencia de objeciones o prioridad científica universal.

No inventes un método nuevo, no arregles buses, no busques una variante que gane.
La ruta elegida es un **artículo metodológico de ingeniería, de alcance acotado**:
atribución continua de cambios de carga y aperturas de línea, en el catálogo
simulado conocido, que distingue intervenciones nuevas de recuperación previa.
No se reclama superar todo ML, resolver toda la hackathon o validar campo.

La orden de ejecutar este plan autoriza edición editorial, generación de
tablas/figuras desde resultados existentes, verificaciones y empaquetado local.
No autoriza envío a coautores/revista, publicación, push, nuevos entrenamientos,
ni una campaña científica adicional. No hagas commit salvo orden posterior.

**Producto final:** manuscrito principal claro y autosuficiente en su argumento;
suplemento para detalles reproducibles; una página para coautores; fuentes y
artefactos de revisión; matriz de respuesta a los cinco informes; lista breve
de limitaciones y declaraciones de autores pendientes. Los resultados negativos
forman parte del producto terminado. No se exige que A01 salga positivo.

## 1. Directorios y fuentes de verdad

En este documento, las rutas relativas de artículo parten de PAPER; las de
experimentos parten de SCIENCE. No inventes rutas si falta un archivo.

```powershell
$paperRoot = 'C:/Users/walla/Documents/Github/paper-P07-physics-informed-sparse-pmu-event-inference'
$scienceRoot = 'C:/Users/walla/Documents/Github/SGSMA26-Physics-Informed-AD'
$closurePython = 'C:/Users/walla/anaconda3/python.exe'
$closureRoot = Join-Path $paperRoot 'docs/closure_luna'
$ablationRoot = Join-Path $scienceRoot 'experiments/PAPER_ABLATION_A01'
```

Lee en este orden, sin explorar todo el historial del repositorio:

1. `PAPER/AGENTS.md`, `PAPER/docs/PROTECTED_FIGURES.md`.
2. `SCIENCE/PAPER_CLOSURE_START_HERE.md`, **solo su estado vigente primero**.
3. `PAPER/docs/review_20261102_strict_current/AUDITORIA_P07.md`.
4. Los cinco informes de esa carpeta: `REVIEWER_1_PHYSICS.md`,
   `REVIEWER_2_STATISTICS.md`, `DEVILS_ADVOCATE.md`,
   `EDITOR_INDEPENDIENTE.md`, `REVIEWER_3_CLARITY_IMPACT.md`.
5. `SCIENCE/experiments/PAPER_ABLATION_A01/README.md`, `PLAN.json`,
   `FREEZE.json`, `amendments/*.json` y los estados de `run/`.
6. `PAPER/main.tex` y todos sus inputs activos; después los apéndices pertinentes.
7. Para el mapa instrumental/modelo: `SCIENCE/SIM0001_START_HERE.md`,
   `SCIENCE/SIM0001_CURRENT.json` y el contrato indicado por ese JSON.

Precedencia documental: archivos/resultados sellados y comprobados > código
activo > informe fechado reciente > README histórico > recuerdos del chat.
Algunos README todavía dicen que C01 no se ejecutó: **son texto histórico**.
`experiments/PAPER_CONFIRMATORY_C01/run/COMPLETE.json` confirma que terminó.
No interpretes un README desactualizado como orden de repetirla.

## 2. Restricciones que no se negocian

- No abrir RAW0002 ni buscar ejemplos dentro de él.
- No modificar C01, sus semillas, métricas, casos, métodos ni predicciones.
- No modificar F01, R1, R1.1, R5C.2 ni otros baselines.
- No modificar la ciencia de A01 ni analizar parciales para tomar decisiones.
- No instalar paquetes en el entorno que ejecuta A01; no activar GPU/TensorFlow.
- No añadir otra versión para BUS31 u otro activo. No GNN ni entrenamiento nuevo.
- No ejecutar `prepare.py` de experimentos o baselines.
- No redibujar, recortar, recolorear o regenerar la **Figura 2 de eventos**;
  conservar sus bytes y presencia en el PDF como Figura 2.
- Conservar el unifilar IEEE-39, conectividad, dispositivos y las ocho PMU.
- No editar `figures/frozen/` ni `generated/frozen/`; las importaciones finales
  de A01 las realiza su ejecutor. Tus nuevos derivados van en otra carpeta.
- No borrar resultados desfavorables, cambiar denominadores ni renombrar scores
  como probabilidades calibradas.
- No generar con IA curvas, resultados, diagramas eléctricos o fotos científicas.
- Trabajar en la rama existente `main`; sin worktrees, ramas o PR nuevos.
- No enviar mensajes a autores, no someter el artículo y no hacer push.

## 3. Orden de trabajo y regla para no bloquearte

La secuencia es P0 → P1/P2/P3 preparados en paralelo con la espera → P4 → P5 →
P6 → P7. “En paralelo” significa avanzar tareas independientes; no lanzar
simulaciones duplicadas ni procesos pesados simultáneos. Un único editor integra
el manuscrito. No necesitas agentes adicionales.

Si A01 sigue corriendo, prepara cambios en `docs/closure_luna/staging/`.
No sobrescribas archivos activos que A01 va a importar/compilar. Puedes crear
informes, scripts NUEVOS de análisis descriptivo y fuentes revisadas en staging.
No compiles ni cambies scripts activos del build mientras el importador final
de A01 pueda estar usando esos mismos archivos.

En cada tarea registra: entrada, salida, comprobación, estado y siguiente acción
en `docs/closure_luna/PROGRESS.md`. Al retomar otra sesión lee ese archivo y
`STATUS.json`; no vuelvas a empezar. Una decisión razonable ya indicada aquí no
requiere volver a preguntar al usuario.

Si un detalle opcional requiere más de 20 minutos de búsqueda infructuosa,
usa la alternativa indicada y continúa. Un fallo de integridad, datos faltantes
imprescindibles o una fórmula contradictoria no se resuelve por tiempo: registra
el bloqueo real y no marques la entrega completa. Continúa con lo independiente.

## P0 — Asegurar la instantánea y seguir A01 sin interferencia

### P0.1. Preparar continuidad

Crear `docs/closure_luna/` con:

- `PROGRESS.md`: tareas, archivos cambiados y siguiente paso.
- `STATUS.json`: campos `phase`, `ablation_state`, `paper_state`,
  `last_verified_local_time`, `open_blockers`, `next_action`.
- `BEFORE_MANIFEST.json`: SHA256 de fuentes activas, scripts que vayas a editar,
  PDF principal/suplemento y archivos de figuras protegidas.
- `backups/`: copias de los archivos editables antes de cambiarlos; no de todo
  el repositorio ni de cientos de gigabytes de simulación.
- `RESPONSE_TO_REVIEWERS.md`: una fila por comentario de los cinco informes,
  con estado `pending / addressed / narrowed-claim / author-decision`.

Ejecutar controles de figuras y guardar su salida en esa carpeta:

```powershell
& $closurePython -B "$paperRoot/scripts/verify_protected_figures.py" --pdf "$paperRoot/main.pdf"
& $closurePython -B "$paperRoot/scripts/verify_protected_event_figure.py"
```

Si fallan ya al inicio, no cambies hashes de referencia. Identifica qué archivo
difiere de la copia aprobada y deja el fallo documentado. No reemplaces cambios
ajenos del usuario sin comparar la procedencia. Puedes preparar el texto aparte.

### P0.2. Estado real de A01

Al preparar este plan, A01 estaba en tarea **18/72**, controlador PID 36740.
Esto es solo una instantánea: **no reutilices ese PID sin verificarlo**.

Lee `run/PROGRESS.json`, `LAUNCH.json`, `BLOCKER.json` si existe,
`COMPLETE.json`, `PAPER_UPDATED.json` y el log señalado por PROGRESS.
Consulta la línea de comandos, no solo existencia del PID:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -match 'PAPER_ABLATION_A01' } |
  Select-Object ProcessId,ParentProcessId,CommandLine
```

Decisiones exactas:

| Situación | Acción |
|---|---|
| Controlador correcto vivo y log/reportes avanzan | No reiniciar, no duplicar; avanzar P1–P3 en staging. |
| Log quieto brevemente | Comparar CPU/log/progreso en dos muestras; una sola ausencia de líneas no es bloqueo. Algunas reconstrucciones tardan. |
| Controlador ausente, hijo A01 vivo | No reanudar aún: esperar/verificar el hijo y conservar su salida. Trabajar lo independiente. |
| No quedan procesos A01, hay bloqueo de infraestructura | Leer traceback. Corregir solo infraestructura recuperable, conservar artefactos y registrar reparación. |
| No hay procesos, corrida interrumpida sin corrupción | Verificar cadena de hashes y reanudar el mismo `pipeline.py run`; no preparar otra campaña. |
| COMPLETE y PAPER_UPDATED, sin procesos de importación activos | Verificar denominadores/sellos y pasar a P4. |
| Algún brazo terminó con fallo científico/numérico | Mantenerlo en denominador y ledger; no cambiar método ni eliminarlo. No fabricar cuatro brazos exitosos. |

Verificación no destructiva:

```powershell
Push-Location $scienceRoot
try { & $closurePython -B experiments/PAPER_ABLATION_A01/pipeline.py verify }
finally { Pop-Location }
```

Solo si está autorizado por las condiciones anteriores, reanudar con Anaconda,
un proceso oculto y stdout/stderr NUEVOS identificados por hora. Usar
`Start-Process -WindowStyle Hidden -PassThru`, registrar su PID/comando y
conservar el LAUNCH anterior en el historial. No usar el Python de Microsoft
Store: produjo caches distintos y fue rechazado. No relajar igualdad de hashes.

Las reparaciones A01, si de verdad hacen falta, siguen el mecanismo de
`amendments/`: registrar hashes anterior/nuevo y motivo exclusivamente de
infraestructura. No editar `FREEZE.json` para aceptar una discrepancia. Si no
puedes justificar que no cambió la ciencia, detén esa reparación y reporta.

### P0.3. Evitar la carrera con la importación automática

Al terminar, A01 escribe/actualiza al menos:

- `generated/frozen/ablation_a01_20261102/`;
- `tables/generated/ablation_a01.tex`;
- `sections/article_controlled_ablation.tex`;
- `supplement/ablation_a01.tex`;
- gráficos del estudio, PDF, página y paquete de coautores.

No cambies `evaluate.py` para mejorar estilo durante la corrida. Después del
fin, revisa lo importado y aplica tus cambios editoriales; documenta el nuevo
PDF sin alterar el sello científico. El hash de PDF antiguo en PAPER_UPDATED
describe la importación original, no debes reescribirlo para ocultar la revisión.

**Salida P0:** continuidad creada, baseline verificado, estado real del trabajo.

## P1 — Fijar el argumento sin inventar una contribución

### P1.1. Enunciado elegido

Mantener el título existente por defecto. Estrechar abstract e introducción a:

> A recovery-aware physical hypothesis bank for continuous attribution of
> load and line interventions from sparse PMU reports, evaluated through
> timely attribution, unmatched alarms and episode restoration.

Esta frase es una guía de contenido, no una oración obligatoria a copiar.

El artículo debe responder tres preguntas, en este orden:

1. ¿Qué intervención explica las señales disponibles antes de su restauración?
2. ¿Qué aporta conservar recuperación e integrar severidad frente al mismo banco?
3. ¿Cuánto cuesta esa cobertura en falsas alarmas, cierres y cómputo?

No usar “Bayes beats ML”, “optimal estimator”, “tensor intelligence”, “digital
twin validated on real data”, “all 39 buses” ni “complete hackathon solution”.
M es una agregación de hipótesis; ΔM una diferencia interpretable. Los tensores
mixtos históricos y la prueba GPU no entran en el algoritmo final.

### P1.2. Registro de afirmaciones

Crear `docs/closure_luna/CLAIM_EVIDENCE.csv` con columnas:
`claim_id,statement,scope,evidence_file,table_or_figure,status,limitation`.

Filas mínimas:

- Física usada para producir predicciones: código DAE/mapa PMU, demostrado localmente.
- Integral marginal local: fórmula y control por cuadratura, demostrado bajo hipótesis.
- 644/648 frente a 330/648, con 72/29 extras: C01, procedimientos completos y catálogo conocido.
- Aporte aislado de severidad/memoria: pendiente de A01; nunca anticiparlo.
- Restauraciones prematuras: auditoría descriptiva posthoc de C01, no nuevo endpoint.
- Persistencia de líneas sostenidas: salida C01, distinguir primera parada y seguimiento.
- Comparación con entrega hackathon: histórica y de dominio diferente, no leaderboard.
- Robustez: perturbación R/X en la misma familia, no cambio de productor.
- Transferencia RAW: retrospectiva y filtro físico rechazado por prefijo ROCOF.
- Cyber: interfaz/clasificador heredado, no filtro conjunto de ataques.
- Tensor/GPU: no aporta al resultado causal actual; fuera del núcleo del artículo.

**Criterio P1:** cada afirmación del abstract y conclusión tiene una fila; ninguna
fila pendiente aparece como logro ejecutado.

## P2 — Recuperar y presentar bien evidencia existente

### P2.1. Datos autorizados y esquemas ya conocidos

C01: `SCIENCE/experiments/PAPER_CONFIRMATORY_C01/run/results/`.
Copias en PAPER: `generated/frozen/c01_20261029/`, protegidas por MANIFEST.

Usar `SUMMARY.csv`, `RECORDS.csv`, `EVENTS.csv`, `PAIRED_INTERVALS.csv` y
`EVALUATION_AUDIT.json`. No reevaluar ni rematchear C01.

Campos útiles reales:

- RECORDS: `method,record,parent,condition,noise,lane,duration_s,available,
  events,timely,joint,extras,normal_FA,normal_available_s,monitored_s,
  false_restorations,open_eof`.
- EVENTS: `event,family,source,onset_s,off_s,detected,joint,timely,alarm_s,
  emitted_s,diagnosis_delay_s,method,record,parent,condition,noise,lane,
  off_delay_s,available`.

Comprobaciones de referencia, no números para transcribir manualmente a LaTeX:

| ID | Nombre en artículo | Timely /648 | Extras |
|---|---|---:|---:|
| R11 | Physical history bank | 644 | 72 |
| R11_NOMINAL | Nominal physical bank | 643 | 92 |
| ET_REFERENCE | Causal ExtraTrees | 330 | 29 |
| ET_CANDIDATE | Short-window ExtraTrees | 352 | 16 |

Si no se reproducen esas sumas desde los CSV, investiga selección de lane y
duplicación de estratos; no “corrijas” los datos para que coincidan.

### P2.2. Restauración: resultado nuevo descriptivo, no nuevo experimento

Punto de partida ejecutado:
`docs/review_20261102_strict_current/R2_CHECKS.py/json`.

Crear `scripts/build_closure_evidence.py` NUEVO y sus derivados en
`generated/closure_analysis/`. Debe leer copias verificadas y generar:

1. CSV con cobertura de restauración y conteos de adelanto.
2. Tabla LaTeX `tables/generated/closure_restoration.tex`.
3. Figura vectorial `figures/generated/closure_restoration.pdf` más PNG.
4. JSON con hashes de entradas, criterio, unidades y estado posthoc.

Filtro: lane continuo y cada método separado. Adelanto =
`off_delay_s < -1/30`. El denominador del porcentaje de adelanto son las
restauraciones asociadas disponibles; informar además eventos sin restauración
asociada sobre648. Los NaN no son cero ni necesariamente episodio abierto.

Verificación esperada: físico 0/644 y 4 sin restauración; nominal 0/643 y 5;
ET 52/330 y 318; corto 26/352 y 296. Conserva los replays dependientes.

Figura: dos paneles compactos, misma paleta de Fig.9.

- A: ECDF del retraso OFF firmado para restauraciones disponibles, línea vertical
  en 0 y marca de -1/30; no ocultar la cola negativa. Leyenda con n.
- B: proporción/conteo sin restauración asociada del total 648. Escribir que
  incluye omisiones. No dibujar esos faltantes como un retraso infinito exacto.

Si la ECDF queda ilegible, usar panel de cuantiles firmados + conteo de adelantos;
no eliminar observaciones. No agregar significación estadística improvisada.

La etiqueta **False OFF** se genera en `scripts/c01_main_tables.py`, llamado
por `build_complete_confirmation_tables.py`. Después de A01, cambiar allí
encabezado/caption a **Unmatched-episode restorations** o abreviación definida.
Los valores 58/68/29/16 NO cambian. No editar solo la tabla generada: el build
volvería a crear el encabezado incorrecto.

### P2.3. Ficha de dominio evaluado

Generar desde los manifiestos de C01 y CSV, sin tocar verdad de RAW:

- Duración de registros y exposición monitorizada.
- Rango de duración OFF−ON de eventos finitos, por familia.
- Rango y definición de severidad de cargas desde solicitud/protocolo original.
- Perturbaciones R/X exactas y significado de ruido ×1/×2.
- Catálogo de 9 cargas + 9 líneas y 8 PMU; inicio supuesto quieto; 10 s de ajuste y 12 s de warmup.

Los archivos de casos se localizan bajo
`experiments/PAPER_CONFIRMATORY_C01/execution_request/` y `protocol/`.
Busca nombres con `rg --files` y lee el esquema antes de calcular. Si una
severidad no se conserva en EVENTS, no la infieras de amplitudes PMU: ve al
manifiesto generador. Si no existe fuente verificable, declara ese dato faltante
en el suplemento y la matriz de cierre; no inventes un rango “típico”.

Extras/hora: conservar el denominador original de C01, que incluye el registro
completo para extras de eventos. No intercambiarlo con exposición después del
warmup sin cambiar nombre y declarar cálculo descriptivo aparte.

### P2.4. Coste computacional: usar datos disponibles primero

Buscar en `SCIENCE/experiments/PAPER_CONFIRMATORY_C01/run/timings/`, logs y
predicciones selladas campos `wall_seconds`, `seconds`, hilos, memoria.
Separar simulación, reconstrucción del banco, inicialización e inferencia.
No confundir `bank_Sxxx.json` con tiempo de inferencia.

Producir `generated/closure_analysis/COMPUTE_COST.csv` e incluir una tabla
pequeña solo con magnitudes comparables. Un total de registro dividido por
reportes es **promedio amortizado**, no p95 ni latencia de cada reporte.
Registrar CPU/OS/entorno y concurrencia cuando se conozcan.

Alternativas predeterminadas:

- Si hay tiempos heterogéneos/no comparables: reportarlos como descriptivos,
  sin speedup ni afirmación real-time.
- Si faltan memoria o latencia por trama: escribir “not recorded”; no inventar.
- Si no hay ningún tiempo usable: declarar ese límite y dejar la medición como
  pendiente explícito para autores; **no lanzar un benchmark nuevo largo**.
- La prueba `PAPER_COMPUTE_TENSOR_X01` no sustituye coste completo y no entra en
  la tabla principal. No instalar aceleradores para cerrar este artículo.

### P2.5. Incertidumbre y bootstrap

No regenerar los intervalos confirmatorios. Explicar que algunos endpoints
remuestrean padres normales con denominador cero, según `execution/evaluate.py`,
conservando pares; no llamar a todos los intervalos “18 padres exactos”.
Separar los 18 calendarios/108 intervenciones de 648 realizaciones.

Las masas 0.99 no son probabilidades calibradas. Si existen innovaciones
pre-update archivadas, se pueden resumir descriptivamente por régimen sin
retune; si no, mantener calibración/cobertura pendiente. No fabricar NEES/NIS
usando residuos corregidos o posteriores a selección como si fueran predicciones.
Esta validación no es obligatoria si se retira toda afirmación de incertidumbre
calibrada; sí sería necesaria para vender intervalos fiables de estado/severidad.

**Salida P2:** derivados con hashes, definiciones exactas y regresiones numéricas
que garantizan que las tablas originales no cambiaron.

## P3 — Preparar método, literatura y nueva estructura en staging

### P3.1. Modelo eléctrico autocontenido

Preparar `supplement/measurement_contract.tex` con una tabla de los ocho canales:
PMU de tensión, terminal de corriente, orientación, unidades/bases, referencia,
ganancia/fase si corresponde y procedencia/estado provisional.

Tomar los valores SOLO del contrato F01 actual y archivos que señale. No
reconstruir terminales desde el chat, ni sustituir BUS5 para mejorar resultados.
Explicar parejas V/I no colocadas (BUS2/BUS10), exclusión de ángulo BUS39,
frecuencia de bus versus rotor, ventana de 21 reportes y diferencias ponderado/no
ponderado entre exportador y predictor. Explicar dónde se añade ruido y qué
dependencias entre familias no están modeladas.

No copiar todas las ecuaciones Sauer–Pai/AVR si no son necesarias. Mantener
DAE/reducción/mapa eléctrico como cadena central y citar modelo/software con
versión verificable. Si falta una versión, obtenerla del entorno/manifest, no
de la web actual. No presentar el simulador como reproducción perfecta de RAW.

### P3.2. Puente likelihood → masa → decisión

Editar en staging `sections/article_method.tex` y apéndices pertinentes.
Mantener las ecuaciones eléctricas correctas y la integral local. Añadir una
actualización compacta de pesos compatible con el código:

    masa predictiva de historia = masa del padre × probabilidad de transición
    masa no normalizada = likelihood local × masa predictiva
    normalización conjunta incluyendo hipótesis nula
    selección/poda y renormalización documentadas

La ecuación puede usar `tilde_pi_h,k = L_h,k * sum_j T_jh,k pi_j,k-1`, pero
debe marcar que expresa el flujo del conjunto admitido: nacimientos retrospectivos
reemplazan su likelihood de sufijo y la pantalla/poda no equivalen a enumeración
Bayes exacta de todas las historias. NO introducir una matriz de transición
completa que el código no ejecuta como si existiera materializada.

Comprobar contra `core_v6.py`, `retro_birth.py`, `static_rx.py` activos de C01,
sin cambiarlos. Diferenciar pesos de modelos R/X de pesos de historias. Indicar
prior medio cero junto a `b=mu/v` en el diseño de la ablación.

Mantener `M` y `Gamma` porque explican actividad y causa. ΔM puede permanecer
como diagnóstico con una frase; no dedicarle una contribución de novedad.

Pseudocódigo final: entrada/permisos → prefijo → predict → guardar densidad
predictiva → proponer/replay → score → corregir → normalizar/podar → agregar →
publicar/cerrar. Añadir fuente de hipótesis nula y distinción reloj interno/público.
Usar 19 retardos (0–18) de manera consistente. Seis reportes son 0.2 s de persistencia,
quince son 0.5 s; no equivalen a garantía de demora total.

### P3.3. Comparación intelectual limitada y verificable

Editar `sections/article_related.tex`, `references.bib` y el registro de afirmaciones.
Revisar fuentes primarias de Warner trayectorias, IMM/M3H, Chen/Rovatsos y
Yang–Chen–Zhai, *Dynamic Power Systems Line Outage Detection Using Particle
Filter and Partially Observed States*, preprint de 2021:
`https://arxiv.org/html/2107.06754v3`.

Tabla preferida de cuatro columnas:
`antecedente / mecanismo heredado / diferencia de tarea o implementación / prueba aquí`.
No equiparar automáticamente disponibilidad de sensores, eventos o tipo de
medición. No atribuirle a otro método incapacidad de recuperación solo porque
su artículo no la evaluó. No decir “first” o “novel” sin comparación específica.

Si el texto completo no abre: usar DOI/registro/editorial/repositorio de autores
para existencia y metadatos, restringir afirmaciones al contenido verificado,
marcar limitación interna y continuar. No inventar páginas o ecuaciones.
El paper puede declarar no haber ejecutado Warner y no comparar numéricamente
con él. No se autoriza implementar nuevos comparadores durante este cierre.

Chen: incluir brevemente su control compatible (299/300 identificaciones,
0/100 normales en horizonte) si se confirma desde `comparator/MATCHED_SUMMARY.csv`.
Sus resultados F01 son transferencia limitada, no superioridad universal propia.

### P3.4. Estructura final predeterminada

Mantener los nombres de archivos donde sirvan; no reorganizar el repositorio
completo. En `main.tex` el orden objetivo es:

1. Introducción: problema, hueco específico, método, evidencia y alcance.
2. Trabajos relacionados y diferencia operacional.
3. Problema/mediciones: conservar eventos como Figura 2 y unifilar.
4. Método físico y algoritmo: observado→predicción→evidencia→episodio.
5. Protocolo experimental con ficha de dominio y comparadores honestos.
6. Resultados principales C01: cobertura, alarmas, restauración, coste.
7. Ablación completa y ejemplo interpretativo de recuperación.
8. Evidencia auxiliar/hackathon, compacta y sin competir con el resultado principal.
9. Discusión y límites.
10. Conclusión.

La numeración de figuras posteriores puede cambiar; Figura 2 y etiquetas
protegidas se mantienen. Fig.1 sigue antes de la imagen de eventos.

`article_evidence_bridge.tex`: conservar versiones históricas en backup/notas;
compactar en el cuerpo la relación entre features y candidato físico. El bloque
de cardinalidad con prior efectivo incorrecto y su tabla van a las notas
históricas/suplemento, con el error visible. No usarlos para demostrar Bayes
del filtro actual. Tensor mixto y reconstrucción pueden quedar como evidencia
auxiliar separada, no como módulos ejecutados del filtro. No borrar datos.

`narrative_results.tex`: conservar el ejemplo continuo útil; mover controles
de desarrollo y Fig.7 al suplemento si distraen. La comparación histórica
hackathon y su confusión se conservan como subsección corta o suplemento,
siempre distinguiendo ventanas de 30 s del ensayo causal. No reinventar una matriz
de confusión uniendo poblaciones incompatibles.

### P3.5. Mapa de figuras

| Elemento | Decisión predeterminada |
|---|---|
| Figura 1 arquitectura | Conservar diseño por zonas; solo ajustar texto/flechas si no coincide con código. |
| Figura 2 eventos | Intacta byte por byte y visible como Figura 2. |
| Unifilar IEEE-39 | Conservar y visible; no redibujar topología. |
| Señales corriente/ROCOF | Conservar si explica recuperación; no añadir curvas de predicción inexistentes. |
| Fig.5 componentes | Reducir protagonismo/mover material auxiliar; no mezclar cohortes ni borrar historial. |
| Confusión hackathon | Conservar con dominio/ventana/estimador explícitos; no titularla C01. |
| Tradeoff de desarrollo | Suplemento por defecto; no competir con confirmación. |
| Historia BUS31 y recuperación | Conservar ejemplo de fallo, acercarlo a explicación; no corregir el caso. |
| C01 cobertura/extras | Resultado central, acercarlo a su sección y mantener ambos costos visibles. |
| Intervalos por padre | Conservar; no alterar sus cálculos. |
| Restauración nueva | Dos paneles compactos, posthoc explícito, denominadores y faltantes. |
| A01 | Cuatro brazos completos; estimación e intervalo, no solo barras de acierto. |

No pasar de aproximadamente 10 figuras principales salvo necesidad clara; es
una preferencia editorial, no causa para ocultar resultados. No imponer 20 páginas
ni añadir gráficos decorativos. Priorizar legibilidad en tamaño final de columna.

**Salida P3:** archivos revisados en staging, tabla de literatura verificable,
contrato de medición y mapa claro de qué evidencia va en cada lugar.

## P4 — Integrar A01 completo y decidir qué se puede afirmar

Requisito: no queda controlador/hijo importando, COMPLETE y PAPER_UPDATED
presentes, resultados y manifiesto íntegros. No confundir 24 registros × 4 brazos
con 96 eventos: hay 18 secuencias × 6 = 108 intervenciones por brazo, más controles.
Son 72 inferencias nuevas; 24 salidas de control se reutilizan tras paridad.

Verificar:

- `checks/BASELINE_PARITY.json`: 3.601 reportes y mensajes idénticos.
- 96 salidas contabilizadas, incluidos fallos explícitos.
- `run/PREDICTIONS_SEAL.json` precede evaluación.
- `run/results/SUMMARY.csv`, `PAIRED_INTERVALS.csv`, auditoría e interacción,
  si existen según esquema del evaluador.
- Manifiesto de la copia importada en PAPER coincide con los archivos fuente.
- Cada contraste usa la misma familia de banco/publicador y datos declarados.

Mostrar cuatro nombres legibles:

1. Marginal evidence + physical-state carry.
2. Profile score + physical-state carry.
3. Marginal evidence + physical-state reset at closure.
4. Profile score + physical-state reset at closure.

No llamar “non-Bayesian” al perfil: conserva estimación condicional y priors de
intervalos. No llamar “memoryless” al reset: conserva memoria instrumental y
otros estados. Mantener estas distinciones una vez en método/caption, no veinte.

### Tabla de decisión editorial: no inventar soluciones favorables

| Resultado | Qué escribir y qué NO hacer |
|---|---|
| Mejora cobertura y no aumenta extras/cierres bajo el contraste | Reportar magnitudes e intervalos; afirmar aporte en ese estudio posthoc, no universal. |
| Menos extras pero menor cobertura | Tradeoff explícito; no elegir una métrica para declarar ganador global. |
| Empate o intervalos compatibles con efectos de ambos signos | “No resolved benefit in this tested setting”; mantener la contribución del procedimiento completo, no necesidad del componente. |
| Regresión | Conservarla, explicar límite; no retocar umbrales ni correr otra variante. |
| Solo un factor ayuda | Atribuir evidencia a ese factor; retirar reclamo conjunto Bayes+memoria. |
| Interacción fuerte | Reportar efecto condicionado al otro factor; no sumar beneficios como si fueran independientes. |
| Fallos de ejecución | Mostrar todos los denominadores/ledger; si el contraste queda no interpretable, no declarar el efecto resuelto. |

Los intervalos son descriptivos por padre, sin confirmación nueva ni multiplicidad
corregida inventada. No inferir que A01 explica las 68 extras fuera del banco:
esa condición no está en su selección. No cambiar nombres o métricas C01.

Si A01 sigue en ejecución cuando todo lo demás está preparado: deja el staging
listo y estado `WAITING_FOR_COMPLETE_ABLATION`; no digas submit-ready ni detengas
la campaña. Si la ejecución está realmente bloqueada y no es reparable dentro
del contrato, entrega borrador de coautores con resultado pendiente claramente
delimitado; eso no cumple el cierre científico completo de este plan.

## P5 — Aplicar revisión y escribir con claridad

Después de P4, aplicar staging comparando archivo original y cambios que haya
hecho el importador A01. No sobrescribir ciegamente las secciones recién generadas.
Conservar todas las cifras desde macros/generadores.

### P5.1. Abstract e introducción

Abstract objetivo 180–220 palabras: problema concreto; mecanismo; alcance de 9 cargas + 9 líneas;
resultado C01 con cobertura Y extras; efecto de ablación solo si demostrado;
limitación principal. No enumerar cinco estudios auxiliares. No abrir con
“With the rapid development…”, “novel comprehensive framework” o promesas.

Introducción: dos o tres contribuciones precisas, cada una con evidencia. No
usar como contribución independiente la identidad ΔM o el uso de TensorFlow.
La distinción con ExtraTrees: se evalúan rutas congeladas diferentes, con
información diferente; las señales iguales no igualan conocimiento de modelo.
Reconocer cerca del titular que los árboles ya eran débiles en carga.

### P5.2. Método y resultados

Nombrar siempre el mismo procedimiento de forma consistente. En texto principal
no usar R11/R08/C01/A01 como nombres científicos; los identificadores pertenecen
al mapa de artefactos/reproducibilidad. Sí se pueden conservar en CSV y manifiestos.

Regla por párrafo: una afirmación → su mecanismo o evidencia → su alcance.
Evitar repetir en cada párrafo “no es X”. Un único apartado de límites resume
calibración, fuente no vista, ruido, productor, tiempo real y otras familias.
No eliminar cautelas sustantivas para parecer más contundente.

Resultados primero: pregunta, número y costo, explicación. Después controles
históricos. La conclusión no repite la historia de versiones ni anuncia
capacidades no validadas. No usar “significant” si no hay contraste que lo sostenga.

### P5.3. Estilo y declaración de asistencia

Revisar vaguedad, redundancia y frases que solo adornan. No usar detectores de IA
para fabricar un porcentaje humano ni ofrecer autoría certificada por estilo.

Por instrucción actual del autor, la declaración de asistencia sigue fuera del
borrador en `docs/SUBMISSION_DECLARATIONS_PENDING.md`. No insertarla silenciosamente
ni eliminar el registro de procedencia. En el checklist final dejar **pendiente
de autores antes de someter** conforme a la política IEEE aplicable. No declarar
el envío autorizado mientras esa decisión no esté resuelta. Mejorar estilo no
equivale a ocultar procedencia.

## P6 — Compilar y verificar sin regeneraciones peligrosas

No usar `-RefreshArtifacts`: incluye scripts históricos que sobrescriben secciones
y pueden reintroducir redacción obsoleta. Actualizar explícitamente solo el
generador relevante y revisar su diff. `build_evidence_bridge.py` y
`build_complete_confirmation_tables.py` se ejecutan incluso en el build normal:
si cambias etiquetas/tablas que generan, cambia el generador, no solo el output.

Preparar nuevos tests de integridad SOLO para errores reales de integración:

- sumas C01 inalteradas;
- conteos restauración reproducidos;
- sin cifras manuales que diverjan de macros;
- ausencia de referencia/cita sin resolver;
- figuras protegidas y manifiestos intactos;
- A01 completo o marcado pendiente sin afirmaciones de resultado.

Comandos base (Python explícito; build llama `python` por nombre):

```powershell
& $closurePython -B "$paperRoot/scripts/verify_supplement_examples.py"
& $closurePython -B "$paperRoot/scripts/build_closure_evidence.py"
$closureOldPath = $env:PATH
try {
    $env:PATH = 'C:/Users/walla/anaconda3;' + $closureOldPath
    & powershell -NoProfile -File "$paperRoot/scripts/build_manuscript_bundle.ps1"
    if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect its log.' }
} finally { $env:PATH = $closureOldPath }
& $closurePython -B "$paperRoot/scripts/verify_protected_figures.py" --pdf "$paperRoot/main.pdf"
& $closurePython -B "$paperRoot/scripts/verify_protected_event_figure.py"
& $closurePython -B "$paperRoot/scripts/verify_source_package.py"
```

Guardar stdout/stderr en logs de cierre y comprobar código de salida de cada
comando. No ignorar errores porque se produjo un PDF antiguo.

Renderizar todas las páginas con PyMuPDF/Poppler y leerlas en tamaño final.
Si Poppler no existe, PyMuPDF ya está disponible: no bloquearse instalando.
Comprobar específicamente:

- figuras 2/unifilar presentes, legibles y correctas;
- diagramas coherentes con pseudocódigo;
- unidades/ejes/denominadores/captions;
- histórico/posthoc/confirmatorio distinguibles;
- sin tablas cortadas, letras superpuestas, `??` o páginas de resultados vacías;
- figuras centrales cerca de su explicación;
- biografía aislada compactable sin tocar contenido científico;
- no encabezados “in progress” si se está entregando versión final.

Límite de iteraciones de estilo: una revisión estructural y una pasada visual
de corrección; repetir solo por un defecto concreto. No rediseñar Fig.1 sin
motivo de concordancia. No convertir esto en otra investigación de tipografía.

## P7 — Paquete final y dictamen honesto

Actualizar desde artefactos verificados:

- `scripts/prepare_coauthor_brief.py` y página/PDF de una página;
- `scripts/package_coauthor_review.py` y ZIP de coautores;
- `scripts/package_submission_sources.py` y prueba de compilación aislada;
- `docs/P07_CLOSURE_FOR_COAUTHORS.md` y el punto de continuidad científico
  solo en su sección vigente, sin reescribir archivos científicos congelados.

La página para David y Masoud debe tener: pregunta; aportación concreta; tabla
C01; efecto A01 real; resultado de restauración posthoc; limitaciones; decisiones
de autores pendientes. No una lista de versiones ni una declaración de triunfo.

Completar `RESPONSE_TO_REVIEWERS.md` con ubicación exacta de cada respuesta.
“Addressed” exige archivo/figura/comprobación; reconocer un límite puede responder
a una objeción si la afirmación se estrechó. No marcar como resuelta una validación
que solo se prometió. No convertir recomendaciones opcionales en nuevos bloqueos.

Entregar `docs/closure_luna/FINAL_READINESS.md` con tres estados separados:

1. `SCIENTIFIC_DRAFT_READY_FOR_COAUTHORS`: argumento y evidencia cerrados para revisión.
2. `TECHNICAL_PACKAGE_READY`: PDFs, fuentes, cifras y artefactos verificados.
3. `AUTHOR_SUBMISSION_DECISIONS_PENDING`: aprobación de autores, declaraciones,
   metadatos/disponibilidad o restricciones por resolver. No enviar nada.

Si hay un bloqueo científico material, los dos primeros estados no son
automáticamente verdaderos. Explica el bloqueo en una frase y la acción mínima.
Nunca declarar “perfecto”, “nadie podrá objetar” o “aceptación asegurada”.

## 8. Prioridades y presupuesto de trabajo

**Imprescindible:** integridad y estado A01; argumento y ecuaciones trazables;
comparaciones completas con fallos; figuras protegidas; PDF revisado; paquete
para coautores. Si el tiempo es limitado, termina esto antes de retoques de estilo.

**Acotado:** una figura nueva de restauración, una tabla instrumental, una tabla
de coste si hay datos y la figura de ablación ya generada. No producir una figura
por cada objeción del revisor. Reutilizar generadores y estilos existentes.

**Fuera de este cierre:** entrenamiento de un nuevo comparador, GNN, GPU,
TensorFlow, otras redes, otras familias de evento, nuevas variantes por bus,
calibración de probabilidades que exija nuevas corridas y nuevas campañas.
Registrarlas como límites o trabajo futuro según corresponda.

Estimación de organización, no promesa de duración: P0–P1, una sesión corta;
P2–P3, una o dos sesiones de análisis/editorial; P4 depende de que termine A01;
P5–P7, una o dos sesiones de integración y revisión. No confundir esta estimación
con el tiempo pendiente del proceso. Actualizar avance por entregables terminados.

## 9. Soluciones predeterminadas para errores habituales

| Problema | Solución dentro del guion |
|---|---|
| README contradice COMPLETE | Usar sellos/resultados recientes comprobados; registrar el texto histórico, no repetir experimento. |
| Figura protegida no coincide | No actualizar hash; investigar/recuperar de copia aprobada identificada. |
| Build repone una etiqueta vieja | Corregir el generador activo, no editar repetidamente su output. |
| A01 termina mientras editabas | Comparar staging y nueva importación; conservar datos importados y aplicar solo prosa/maquetación. |
| Falta dato de ruido o severidad | Buscar contrato/manifest exacto; no estimar desde gráfica. Si no existe, documentar ausencia. |
| A01 negativo o empate | Mantener resultado; estrechar contribución; no entrenar/cambiar umbrales. |
| Comparador ExtraTrees flojo | Declararlo junto al resultado; no retunear C01. Retirar afirmación de superioridad general. |
| No hay tiempos comparables | Reportar disponibles con límites o “not recorded”; no inventar speedup. |
| Cita no verificable | Buscar autor/editorial/arXiv/DOI; no inventar. Reescribir afirmación para depender solo de fuentes verificadas. |
| Matriz de confusión parece perfecta | Explicar que condiciona a diagnóstico a tiempo; mostrar faltantes y extras separadamente. |
| Piden THD con fasores | No añadirlo: no hay ondas/armónicos medidos en este contrato. |
| Nueva teoría sugerida por otro chat | Aparcarla en ideas futuras; no meterla como implementación ni desviar cierre. |
| Perfil score produce pesos | Llamarlos scores normalizados, no posterior calibrado. |
| Autoría/permiso requiere decisión humana | Preparar resultado concreto y lista pendiente; no inventar consentimiento, no bloquear tareas técnicas independientes. |
| Error de LaTeX | Reparar ruta/escape/entorno; no borrar sección científica para que compile. |
| Memoria insuficiente | No matar A01; posponer render/compilación pesados y seguir prosa/lectura. |
| Sospecha de discrepancia científica real | Documentar archivo/dato; no modificar método ni ocultarla. Esa parte queda bloqueada honestamente. |

## 10. Checklist binario de entrega

- [ ] A01 contabilizado completo, con resultados favorables/nulos/regresiones.
- [ ] C01 y baselines conservan resultados/sellos, RAW0002 no abierto.
- [ ] Afirmación central única, acotada y distinta de ingredientes heredados.
- [ ] Sin reivindicación tensorial/GPU no demostrada.
- [ ] Física, likelihood, pesos, poda y publicación conectados explícitamente.
- [ ] Tabla completa del contrato instrumental y limitaciones f/ROCOF.
- [ ] Baselines débiles y puntos de alarma desiguales declarados junto al resultado.
- [ ] Cobertura, extras, cierres, faltantes y costes presentados con denominadores.
- [ ] “False OFF” corregido semánticamente sin alterar valores originales.
- [ ] C01 confirmatorio, A01 posthoc e históricos claramente diferenciados.
- [ ] Literatura próxima contrastada; referencias comprobadas en alcance declarado.
- [ ] Fuente/paquete disponibles para revisión, sin depender de rutas personales sin explicación.
- [ ] Figuras2 y unifilar preservados; todo el PDF inspeccionado visualmente.
- [ ] Compilación aislada del ZIP pasa; cifras y tablas reproducibles.
- [ ] Página coautores y ZIP actualizados; response-to-reviewers con evidencia.
- [ ] Declaraciones/aprobaciones de autores pendientes separadas y explícitas.
- [ ] Resumen final breve: qué cambió, efecto observado, límites y lo pendiente.

**Regla final:** termina con la mejor afirmación que sostengan los datos, no con
la afirmación más impresionante que pueda redactarse. El cierre es evidencia
completa y comprensible; no una nueva ronda de versiones.
