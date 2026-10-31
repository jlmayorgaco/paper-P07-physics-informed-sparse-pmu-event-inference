# Qué rescatamos de toda la conversación

Actualización ejecutada: el ensayo separado X02 verificó las firmas E_i en
IEEE-39 y mostró mejor respuesta e intensidad, sin más aciertos que recentrar.
Consultar [resultados y alcance](../ei-x02-results.md). Las ideas de incertidumbre
conjunta, simultaneidad y detección causal de DICE no se dan por resueltas.

## Objetivo y problema científico

El autor quiere un método explicativo y útil, más allá de volver a entrenar
ExtraTrees: con ocho PMU dispersas, inferir si ocurrió una intervención,
su familia y activo de origen, inicio, restauración y severidad. El simulador
debe permitir explorar escenarios nuevos sin proporcionar su verdad al método.
La contribución científica se juzga por mecanismo, evidencia y utilidad;
no por añadir un tensor, otra sigla o más ecuaciones.

Las peticiones sucesivas fijaron cinco requisitos que conservamos:

1. Simulaciones continuas: restaurar una carga o línea no reinicia máquinas.
2. Medición física explícita: corrientes terminales orientadas, bases,
   referencias y filtro PMU forman parte del modelo, no son detalles del CSV.
3. Inferencia causal: onset, origen, intensidad y agenda verdaderos no entran.
4. Métodos intercambiables y evaluación independiente: verdad reservada,
   escenarios padre, semillas, fallos y exposición normal quedan registrados.
5. Cierre finito: R11/nominal están congelados; no seguir creando versiones
   para arreglar cada bus del examen. C01 debe responder qué ganamos y perdemos.

## Cómo se conectan los avances

| Etapa discutida | Aporte que conservamos | Límite que no debemos olvidar |
|---|---|---|
| Recuperar R5C.2 y F01 | Un contrato de simulación y medición con procedencia, estado continuo y terminales explícitos | No es una reconstrucción única del productor de RAW0001; BUS5 sigue provisional y BUS39 tiene fase parcial |
| Detectar, clasificar y localizar | Separar alarma, familia, fuente, tiempo y restauración | Un acierto eventual puede llegar después del OFF y fallar operacionalmente |
| Estado estático y dinámico | Distinguir recuperar voltajes de identificar qué intervención los produjo | Baja HVRE no certifica identidad de fuente ni incertidumbre calibrada |
| M y ΔM | Resumir historias físicas y separar actividad, causa y reponderación de red | Guardar masas en un tensor no proporciona por sí solo una mejora algorítmica |
| Ventana retrospectiva de 10 s | Proponer un onset anterior a la alarma desde un estado pasado estimado | No repetir la evidencia de ventanas solapadas ni arrancar siempre del nominal |
| Eventos sucesivos | Conservar recuperación como explicación frente a una nueva intervención | Una línea recerrada puede seguir oscilando; esa oscilación no prueba otro evento |
| R/X inciertos pero constantes | Comparar trayectorias bajo hipótesis de red fijas | Un banco discreto no identifica una posterior continua de todas las impedancias |
| R11 y nominal | Referencias concretas para medir exactitud, extras y demora | Ninguna domina todas las métricas de desarrollo |
| C01 | Confirmación preespecificada con ambos ExtraTrees y Chen elegible | Hasta el cierre no hay resultados confirmatorios que adelantar |
| DICE / X01 | Pregunta nueva: que el contexto cambie la firma del evento y su incertidumbre | Sus controles algebraicos no demuestran mejora física en IEEE-39 |

Los nombres y cifras de pilotos mencionados por el autor en el chat no se
convierten en resultados ejecutados sin artefactos correspondientes. Este
corpus no reconstruye puntuaciones de V1–V9 o R01–R10 de memoria. Conserva la
trayectoria intelectual, pero usa los CSV congelados para las cifras.

## Mejores aportes actuales

### A. El objeto inferido es una historia física

El método compara lo que observarían las PMU bajo distintas intervenciones,
desde estados estimados y con memoria instrumental. Es **inferencia basada
en un modelo físico**, con filtrado y evidencia probabilística aproximada.
No es una PINN ni un componente de ML físico aprendido ya validado.

La distinción operativa central es conservar la causa después de OFF para
que recuperación y evento nuevo compitan. Esa construcción está implementada.
Su beneficio causal completo no queda aislado por la ablación de admisión
existente; la novedad diferencial debe discutirse frente a los precedentes.

### B. M comunica la inferencia sin inventar información

M acumula masa de historias activas por familia/activo. Γ retiene la causa
incluyendo historias restauradas. ΔM distingue evidencia dentro de cada
modelo y cambios de peso entre modelos de red. Esto explica una decisión
mejor que una sola etiqueta, pero es una identidad de agregación, no una
nueva factorización tensorial o garantía óptima.

### C. Detectabilidad, localización y confianza son tareas diferentes

Una señal puede diferir claramente del estado normal y seguir siendo
compatible con varios orígenes. El banco histórico de 137 soportes muestra
esa dificultad, pero no prueba que sus errores sean un límite físico:
también intervienen aproximación, priors y un defecto de normalización
verificado en su código. La corrección aislada no tiene replay físico aún.

### D. Comparación operacional y fallos visibles

En desarrollo, nominal obtiene más decisiones a tiempo y más extras que
la mezcla. Una admisión más estricta elimina extras pero pierde un evento
real. Ese resultado negativo ayuda a evitar la falsa solución de suprimir
alarmas indiscriminadamente. C01 mantiene las decisiones y mide esos costes
con más exposición normal y unidades parentales para los intervalos.

### E. Una plataforma que permite refutar las afirmaciones

El valor reutilizable incluye contratos de observación, generador con verdad
separada, manifiestos, semillas y evaluación. No se ofrece solo una colección
de CSV; se conserva la relación entre física, método, escenario y resultado.
La publicación o liberación pública de los artefactos sigue pendiente de
revisión de reproducibilidad y autorización; no se ha hecho push.

## Qué mejora realmente respecto de la hackathon

La mejora demostrada hoy es una capacidad investigable: hipótesis físicas,
onset desconocido, estado conservado, explicación de recuperación y métricas
de episodios continuos. Hay ventaja de carga en H04 frente a los dos
adaptadores ExtraTrees probados. No demuestra todavía ganar el score oficial
de todas las familias ni generalizar a cualquier bus de IEEE-39.

Las puntuaciones históricas de la jerarquía supervisada corresponden a
otro contrato. Su evaluación de fuentes excluidas también requiere reconocer
si el clasificador puede emitir identidades ausentes del entrenamiento.
No se atribuye su fracaso a todo ML. RAW0001 es una referencia retrospectiva
conocida; RAW0002 permanece cerrado.

## Mejores ideas para una continuación

1. **Firmas condicionadas por contexto:** recentrar la trayectoria nominal
   no equivale a recalcular cómo responde a un evento. Las sensibilidades
   mixtas E_i plantean una prueba física específica y falsable.
2. **Incertidumbre propia de cada hipótesis:** integrar el estado previo
   incierto modifica media/covarianza; conservar logdet y comprobar que no
   se absorben las direcciones que distinguen cargas.
3. **Referencia de respuesta no lineal:** separar error por poca información,
   surrogate, prior y cálculo antes de llamar inevitable a una confusión.
4. **Decisión con ambigüedad:** devolver alternativas o esperar solo después
   de validar cobertura, riesgo y costes, sin modificar retrospectivamente C01.
5. **Cómputo verificable:** equivalencia completa de evidencias y momentos,
   coste p50/p95/p99 y extremo a extremo antes de prometer 30 fps o comprar GPU.

Esas ideas no son nuevos requisitos para terminar el paper causal actual.
P07 conserva una sola tesis; la campaña de un sucesor será independiente.

## Qué no incorporamos como resultados

- El Top-1 de un prototipo sintético externo no es exactitud IEEE-39.
- Su latencia de 1.54 ms no es tiempo de nuestro estimador R11 ni del pipeline.
- Qij y E_i no están presentes en el predictor causal R11 como si ya fuese
  el banco simultáneo completo de DICE.
- P/Q, Clarke y espectro de fasores son transformaciones posibles con sus
  supuestos; no son evidencia nueva independiente de los canales originales.
- THD exige los armónicos u ondas necesarias. Tres fasores por trama no
  equivalen a la onda instantánea de cada fase a frecuencia de muestreo alta.
- No se declara solución general de E0–E8, todos los 39 buses, PMU faltantes,
  generación/falla, campo, transferencia entre simuladores o despliegue industrial.
- No se descartan resultados negativos, censuras ni trayectorias fallidas.

## Punto de llegada

Cerrar C01, actualizar y leer el artículo completo, contrastar la diferencia
metodológica con coautores y comprobar referencias, artefactos y metadatos.
La aprobación de envío y la aceptación editorial son decisiones distintas.
La imagen de los eventos se conserva exactamente; la evidencia nueva no
justifica rehacer esa ilustración aprobada.
