# P07: plan autónomo de cierre científico

Fecha de apertura: 12 de noviembre de 2026. Estado: en ejecución; no listo para envío.

## Avance de esta ejecución

- Tres agentes Luna completaron auditorías de ejecución, matemática y revisión
  adversarial; coordinación revisó y corrigió sus entregas.
- Teoría de suficiencia predictiva y compresión incorporada al suplemento;
  ejemplos finitos verificados, sin nuevas afirmaciones empíricas.
- Resumen, introducción, discusión y conclusión ajustados al alcance de C02.
- Protocolo C04 delimitado y selección CAL fijada; implementación y ejecución
  pendientes, no es evidencia.
- Importador C03 preparado y probado con datos sintéticos: rechaza resultados
  alterados/incompletos y resúmenes inconsistentes; verifica sellos, compila sus
  macros/tablas y reconstruye el paquete compacto. Comprobación real: PENDING
  por ausencia de `CAL_SELECTION.json`; ninguna cifra C03 importada.
- Revisión visual de las 48 páginas; inspección ampliada de figuras 1/4/7,
  nueva teoría y tablas finales. Corregidos solapamiento de tabla y porcentaje
  sin escapar. Artículo 19 páginas y suplemento 29.
- ZIP de 176 archivos reconstruido en carpeta aislada: texto y paginación
  coinciden; figuras protegidas verificadas. Persisten avisos de clase/fuentes,
  sin referencias sin resolver ni errores fatales de compilación.
- C03 permanece en CAL a las 16:43 de Bogotá: 53/72 registros cerrados,
  siguiente activo. No hay selección CAL ni resultado/lock de evaluación TEST.
- Entrega científica definitiva pendiente de esa evidencia, revisión posterior
  y cierre de las objeciones; envío pendiente también de declaraciones/autores.

## Contrato científico

Problema: una intervención nueva puede comenzar durante la recuperación de otra.
Pregunta: qué pierde una representación comprimida de esa recuperación y cómo
afecta a la atribución oportuna con ocho PMU.
Mecanismo candidato: conservar alternativas sobre el estado y la causa, con sus
incertidumbres, frente a comprometerse con una representación reducida.
Prueba que lo puede refutar: controles de estado/fusión, presupuesto normal
común y transferencia del predictor congelado a otra planta.
Consecuencia: determinar cuándo merece la pena conservar alternativas y cuándo
la continuidad del estado basta. No se presupone un resultado favorable.

La distribución completa de un estado Markoviano adecuadamente aumentado es
suficiente para la predicción. Una comparación contra fusión de medias no
demuestra superioridad sobre todo observador de estados. Reconstruir variables
ocultas a partir de las mismas PMU tampoco crea mediciones independientes.

## Responsabilidades y orden

| Etapa | Responsable | Entrega | Condición de cierre |
|---|---|---|---|
| 1. C03 | Luna experimentos + coordinación | Auditoría de ejecución, sellos, controles y duración | CAL y TEST completos; cierre único y hashes válidos; fallos conservados |
| 2. Matemática | Luna teoría + revisión de coordinación | Suficiencia predictiva, covarianza de mezcla, verificación enumerable | Hipótesis explícitas, casos que contradigan simplificaciones, comprobaciones reproducibles |
| 3. Control adicional | Luna experimentos + teoría | Protocolo sucesor para media/covarianza/mezcla | Prueba pequeña antes de gastar en simulaciones; contrato y TEST nuevos cuando corresponda |
| 4. Integración | Coordinación | Importador sellado, tabla, contrastes, figuras y texto | No importar resultados parciales ni reabrir evaluación TEST |
| 5. Revisión adversarial | Luna reviewer + revisores por rotación | Registro de objeciones y correcciones | Cero objeciones graves no resueltas; límites explícitos |
| 6. Editorial y visual | Luna por rotación + coordinación | Prosa, pseudocódigo, leyendas y figuras coherentes | Inspección en PDF al tamaño final; figuras protegidas intactas; objetivo 19 páginas |
| 7. Reproducibilidad | Luna por rotación + coordinación | Paquete aislado y regeneración de cifras | Artículo y suplemento compilan desde el paquete; tablas trazables |
| 8. Entrega | Coordinación + autores | PDF, suplemento, fuente y Git actualizado | Evidencia cerrada y aprobación/declaraciones de autores; sincronización Overleaf vía Git |

Tres agentes Luna simultáneos como máximo. Cada agente posee archivos distintos.
La coordinación valida los cambios antes de integrarlos y publicar en main.
Los agentes no hacen push, no envían mensajes a coautores ni abren RAW0002.

## C03: preservar el experimento

- Mantener fuentes, configuración, datos y predicciones congelados. No editar
  dependencias usadas por el proceso activo ni lanzar un segundo supervisor.
- Reutilizar únicamente resultados con `COMPLETE_SINGLE_USE` y hash correcto.
- Auditar ambos contrastes por planta, 36 padres con eventos y 36 normales,
  144 eventos cortos primarios, seis intervenciones por padre y 5,88 h normales
  planificadas. La exposición realmente admitida se informa por separado.
- Verificar factibilidad de CAL por brazo y aplicación sin recalibración a P2.
- Conservar todos los fallos en cobertura; no transformar falta de exposición
  en cero falsas alarmas. Reportar omisiones junto a demoras condicionales.
- No confundir fusión de media con conservación de toda la distribución.
- El ensayo de dropout actual retiene el último reporte: describirlo como tal,
  sin atribuirle tratamiento correcto de ausencia mediante máscara.
- La aceleración de ejecución solo se admite si evita escrituras concurrentes,
  conserva predicciones y documenta condiciones de medición de tiempos.

## Decisiones vinculadas a la evidencia

1. Ventaja de historias en las dos plantas: exigir al menos +5 puntos observados,
   límite inferior pareado de 95 % mayor que cero y presupuesto normal cumplido
   por ambos brazos en cada planta. Informar costo de alarmas extra y cómputo.
2. Ventaja solo en F01: declarar límite de transferencia; no presentar ventaja
   general. Una ventaja exclusiva de P2 también se informa sin ocultarla.
3. Fusión supera reset pero historias no superan fusión: centrar el resultado
   en continuidad y costo de representación, conservando el resultado negativo.
4. Ninguna mejora material: detener la afirmación de superioridad y revisar la
   tesis. No cambiar umbrales después de TEST para obtener un resultado favorable.

## Ampliaciones con presupuesto científico acotado

**Primero:** problema enumerable para comparar distribución exacta, media,
media/covarianza y reset; distinguir predicción de atribución retrospectiva.
Si se necesita un nuevo brazo de planta, congelar un sucesor separado. No llamar
confirmatorio a un análisis elegido tras ver los resultados que pretende confirmar.

**Después, si resuelve una objeción central:** evaluar la reconstrucción causal
del impacto sobre buses no observados o una PMU retirada, con las mismas
condiciones iniciales para la trayectoria de recuperación y la de nueva
intervención. Verdad oculta solo para puntuar; informar incertidumbre, error de
fasores y efecto sobre atribución. No sumar su residuo como evidencia independiente.

**No ampliar por acumulación:** fallas desbalanceadas, inversores, eventos físicos
simultáneos, nuevas redes y fuente no catalogada requieren otros contratos. No
son capacidades del método actual ni requisitos para una afirmación estrecha.
Conservar los resultados negativos de B01 y de condicionamiento histórico.

## Arquitectura editorial

Introducción y antecedentes -> problema/medición -> método y pseudocódigo ->
análisis de continuidad y compresión -> protocolo -> resultados organizados por
mecanismo, comparación y transferencia -> límites -> conclusión.

C02 y C03 conservarán denominadores separados. Las figuras 1 y 4 explican el
problema y la física; la figura principal de resultados compara efectos e
incertidumbre. Añadir una figura empírica solo si explica una decisión o un fallo.
Preservar las figuras protegidas y enviar historia extensa al suplemento/notas.

## Comprobaciones de entrega

- Resumen y conclusión con cifras generadas y afirmaciones respaldadas.
- Teoría local separada de garantías operacionales; scores aproximados separados
  de probabilidades calibradas; causalidad separada de latencia de ejecución.
- Referencias pertinentes verificadas; no aumentar citas por autor o prestigio.
- Tablas desde artefactos sellados, manifiesto de código/entorno/configuración.
- Compilación aislada de artículo y suplemento; revisión visual; verificador de
  figuras protegidas; Git en main según AGENTS.md. No afirmar compilación remota
  observada cuando solo se verificó el paquete local.
- Autoría, aprobación de todos los autores, financiación, conflictos, permisos
  de datos/figuras y declaración real de asistencia de IA pendientes de autores.
  Preparar información concreta; no inventar aprobaciones.

La entrega final puede ser una versión científica cerrada para aprobación de
autores. Solo se denomina lista para envío cuando también se cierren sus
declaraciones. Ninguna etapa garantiza aceptación editorial.
