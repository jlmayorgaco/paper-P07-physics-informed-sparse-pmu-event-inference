# Adaptación e inferencia histórica: decisiones de integración

## Contrato científico en cinco frases

1. **Problema:** una nueva intervención y la recuperación de otra pueden
   producir respuestas parecidas en las ocho PMU.
2. **Brecha:** el banco publicado conserva estados e historias, pero usa
   covarianzas de régimen compartidas y un modelo instrumental fijado al inicio;
   el ruido independiente y la compresión de incertidumbre son límites conocidos.
3. **Hipótesis:** propagar incertidumbre y adaptar una familia acotada de ruido
   bajo supervisión de las historias puede seguir cambios instrumentales sin
   convertir intervenciones persistentes en operación normal.
4. **Prueba que puede refutarla:** comparar covarianza fija, adaptación protegida
   y adaptación sin protección bajo ruido cambiante, cargas débiles persistentes
   y recuperación, con calibración independiente y el mismo presupuesto de alarmas.
5. **Consecuencia:** solo una mejora oportuna que sobreviva a esos controles
   justifica reclamar una contribución adaptativa; una arquitectura no la demuestra.

## Fuentes consultadas

- Adjunto del usuario: `5213d0a1-8755-4429-9f94-119080dd7272/Texto pegado.txt`.
- El enlace compartido `https://chatgpt.com/share/6af76062-a2b4-83e9-b391-086697c64bce`
  falló en dos intentos de lectura. No se atribuye al chat contenido no recuperado.
- Método activo `sections/article_method.tex`; `core_v6.py` y
  `amplitude_parent.py` de las dependencias congeladas de C03, solo lectura.
- README de `research/pmu_hybrid_dae_bayes`: describe un resultado desfavorable
  de recentrado Huber. El informe enlazado no estaba localmente disponible;
  no se importan sus cifras al artículo como evidencia auditada.
- Wang et al., IET GTD 2019, 13(12), 2455–2463,
  https://doi.org/10.1049/iet-gtd.2019.0031. Fuente primaria consultada:
  adaptación por innovaciones, filtro unscented H-infinito y evaluación IEEE-39.
  Es antecedente de estimación, no comparador ejecutado de atribución.

## Qué se incorpora y qué no se convierte en resultado

| Idea | Decisión | Evidencia / límite |
|---|---|---|
| DAE, Kirchhoff y propagación por la red | Explicar el mecanismo existente | Operadores físicos; no GNN ni nueva ley de propagación |
| Kalman condicionado por historia | Precisar la dependencia afín estado–severidad | Ya existe; no se vende como novedad nueva |
| Covarianza específica por historia | Derivación y verificaciones pequeñas para un sucesor | No implementada en el banco evaluado |
| Ruido común + local | Familia PSD acotada, bases fijas, ajuste estructurado | Hipótesis instrumental, no estimación arbitraria de toda R |
| Adaptar R, Q y parámetros simultáneamente | Rechazado como primer paso | Identificabilidad y absorción de severidad sin resolver |
| Adaptación por posterior normal | Gate operativo previsible, con pruebas adversariales | Las masas aproximadas pueden equivocarse; no garantía |
| Suavizado histórico | Frontera probabilística, versiones guardadas y reemplazo de evidencia | El replay actual no equivale a un suavizador conjunto exacto |
| Memoria adaptativa | Posponer hasta separar efecto de covarianza y replay | Medir pérdida de masa, ranking y coste; no solo tamaño del beam |
| Hamiltoniano / energía | Mantener como interpretación o diagnóstico existente | No añadir energía como likelihood independiente de los mismos datos |
| Cyber | Capa externa y salidas separadas | Integridad o residual físico no demuestra intención de ataque |

No se cambia título ni abstract para anunciar un estimador adaptativo no validado.
La contribución actual sigue centrada en atribución física durante recuperación.
La frase defendible del sucesor sería: **adaptar incertidumbre instrumental
sin absorber una intervención física**, si los controles lo demuestran.

## Correcciones a las ecuaciones propuestas

1. Con severidad incierta, conservar `xi | a,h = N(m + d*a, P)` y actualizar
   tanto `m` como `d`, además del prior truncado de `a`. Propagar solo su media
   pierde varianza y correlación estado–severidad.
2. La recursión predict–observe del suplemento asume ruidos independientes;
   la implementación utiliza operadores conjuntos de un reporte. Adaptarla
   exige comprobar índices y términos cruzados, no pegar fórmulas estándar.
3. La innovación usa incertidumbre predictiva, no únicamente R. Para mezclas,
   incluir varianza de severidad y dispersión entre medias de historias.
4. El covariance matching de una ventana finita es aproximado. Su gate puede
   sesgar la estimación: aceptar solo innovaciones pequeñas reduce la varianza
   incluso bajo el modelo correcto. También debe medirse el bloqueo de
   adaptación cuando aumenta el ruido normal y el gate deja de admitir datos.
5. Puntuar con R_k y actualizar a R_(k+1). Cambiar R implica cambiar ganancia,
   forma cuadrática y log determinante. Q, theta y centro quedan fijos al inicio.
6. Los datos ausentes se marginalizan sobre coordenadas presentes. No usar
   una submatriz de la precisión ni rellenar y contar valores como evidencia.
7. Cada replay reemplaza un sufijo con su distribución de entrada y versiones
   de parámetros guardadas. No reaprender ruido al releer el mismo reporte.
8. El objeto `p(h,x,theta,R | y)` sería un objetivo de inferencia más amplio;
   estimar theta y R por sustitución no calcula ese posterior conjunto.

## Orden de implementación y prueba

La cadena A–E del adjunto mezcla varios mecanismos. Se propone:

1. **E0:** referencia fija reproducida sin cambios en una copia independiente.
2. **E1:** covarianza por historia y transporte de la mezcla al cerrar OFF,
   con idéntica política de propuestas. Separar este control de C04, que
   estudia un incremento de covarianza del nulo bajo aproximaciones fijadas.
3. **E2:** E1 + adaptación de R sin gate físico (control adversarial).
4. **E3:** E1 + adaptación de R con gate físico. Comparar E3/E2 para aislar
   la protección y E3/E1 para medir el valor neto de adaptar.
5. **E4:** E3 + suavizado de ventana con ambos niveles de pesos coherentes.
6. **E5:** E4 + política de memoria adaptativa. Cambiar theta requiere un
   experimento adicional de identificabilidad, no se suma a esta cadena.

Antes de TEST, congelar código, semillas, padres, priors, ventana, gate,
recovery cooldown, cotas de R, tasa de aprendizaje y rejilla de umbrales.
Todos los brazos reciben los mismos reportes y nominales. No usar OFF real
ni rótulos de eventos para decidir elegibilidad. No reutilizar C03 TEST para
selección. No se modifica ni reinicia C03.

Diseñar CAL y TEST nuevos por planta, emparejados por padre; usar el objetivo
de 1 alarma normal/h ya establecido. Incluir normales estacionarios y con
incrementos/reducciones del ruido, intervenciones débiles largas, separaciones
cortas, cambios de R/X, pérdida/reconexión y eventos coincidentes con ruido.
Las condiciones de ruido 0,05 % y 0,1 % se expresarán como **RMS TVE añadido**;
si se implementan dos componentes polares independientes de igual varianza,
su desviación individual es TVE/sqrt(2) bajo la aproximación de pequeños errores.
Verificar el TVE realizado; no repetir la confusión de N01.

Informar cobertura conjunta antes de OFF, extras por hora de secuencia,
FAR y exposición normal, demoras con omisiones, log-score predictivo,
cobertura de incertidumbre, fracción de adaptación admitida y coste p50/p95.
Remuestreo pareado por padre, no por reportes. Un brazo sin umbral factible
no constituye una comparación a presupuesto igual. Ganar RMSE de estado
sin mejorar atribución o sin respetar alarmas no sostiene la tesis.

## Integración editorial y verificación

El artículo añade una distinción breve entre corrección de estado y aprendizaje
de parámetros, y un párrafo de discusión con el antecedente primario. El
suplemento contiene la arquitectura completa, derivación, sesgo de selección,
contrato causal y pruebas pendientes. Figura 1 y figuras protegidas permanecen
intactas; el diagrama nuevo es un vector TikZ separado.

`python scripts/verify_adaptive_extension.py` produce
`generated/adaptive_extension_checks.json`. Comprueba cuadratura de severidad,
media/covarianza del estado, forma de Joseph, marginalización de canales,
ajuste PSD estructurado, causalidad de prefijo y reemplazo de sufijos en un
modelo pequeño, además de dos contraejemplos. No corre el detector IEEE-39,
no aporta cifras de FAR/cobertura y no cierra la novedad empírica.

`python scripts/build_layered_architecture.py` regenera PDF y PNG del diagrama.
Los módulos propuestos se dibujan con bordes y flechas discontinuas. La capa
cyber no suministra un score adicional a la evidencia física. Su contrato
de disponibilidad es una interfaz futura que necesita validación independiente.

## Revisión adversarial de esta integración

- **Novedad:** se añadió el antecedente primario de adaptación en IEEE-39.
  Las ecuaciones de Kalman y covariance matching se presentan como componentes
  conocidos. La protección de atribución durante recuperación es una hipótesis
  pendiente, no una prioridad mundial demostrada por esta revisión acotada.
- **Causalidad:** el aprendiz de ruido actúa después de puntuar el reporte;
  replay no vuelve a entrenarlo. La prueba pequeña no certifica la ruta de
  ejecución del futuro detector completo.
- **Selección e identificabilidad:** el gate puede absorber eventos no
  detectados o bloquearse bajo ruido nuevo. Se exigen controles sin gate y
  normales con cambios de ruido; Q, centro y parámetros no se adaptan en E3.
- **Integridad y cyber:** la disponibilidad es un contrato de medida, no
  etiqueta de ataque. Los resultados actuales de integridad no se convierten
  en validación de un sistema ciberfísico integrado.
- **Presentación:** se corrigieron dos ecuaciones que excedían el ancho de
  columna y se separó la ruta discontinua de la flecha de memoria del núcleo.
  Se inspeccionaron las páginas finales del suplemento y la discusión.

Registro de afirmaciones: covarianza afín y contraejemplos = teoría local;
verificaciones numéricas = comprobación de implementación pequeña;
mejor atribución, robustez adaptativa y latencia viable = hipótesis sin
evidencia de campaña. No hay una nueva cifra empírica principal.

## Diagnósticos iniciales: retirados por error de OFF

Se ejecutó `experiments/adaptive_innovation_20261113`, con protocolo/código
sellados antes de generar datos y selección CAL sellada antes de TEST. El
README de esa carpeta conserva resultados, límites y reproducción. El control
rank-one respalda preservar covarianza a media fija, bajo el modelo correcto.
La adaptación continua mejora seguimiento de ruido pero no demuestra mejora
de atribución; el guardado por historia quieta casi impide aprender. Por tanto,
no se integra ese guardado en el banco ni se anuncia una nueva capacidad.
El siguiente desarrollo requiere datos nuevos y un control de covarianza en el
banco completo. Se mantiene el diagnóstico negativo sin ajuste tras TEST.
No se ejecutó ni modificó el protocolo C04 dependiente del cierre C03.

## Corrección posterior

El diagnóstico inicial usó OFF=4+5*celda, que era ON a medio reporte.
Su comprobación repetía el error. Se retiran esos resultados y se conservan
sellos y archivos originales. El sucesor `_corrected` usa OFF=3+5*celda,
comprobación independiente del orden del builder y nuevas semillas. Los
resultados vigentes están en su README. No cambian C01, C02 ni C03. La
adaptación no aporta cobertura y dos brazos superan la FAR objetivo en
TEST; no se retocaron umbrales tras observarlo.
