# Secuencia de cierre de P07

La pregunta del artículo es cuánto ayuda conservar alternativas de
recuperación para atribuir una intervención nueva. El resultado contra GLR
compara procedimientos completos. La estimación de covarianza responde a
otra pregunta: si el modelo del instrumento explica parte de las omisiones
bajo ruido independiente. El resultado de relinealización corresponde a
predicción física con el evento conocido.

| Orden | Trabajo y resultado exigido |
|---|---|
| 1. C03 | Verificar manifiestos, bloqueo final y denominadores de ambas plantas. Estimar historia–fusión y fusión–reset con remuestreo por padre. Verificar presupuesto en ambas y ajustar la tesis al contraste que se sostenga. |
| 2. Ruido independiente | Ejecutar el banco con ley añadida conocida, varianza por familia, Ledoit–Wolf y estimación estructurada de la escala por PMU. Usar padres CAL y TEST separados. Para cada brazo, seleccionar umbral en CAL con el mismo presupuesto y reportar cobertura, extras, exposición, cota de FAR y diferencias por padre en TEST. |
| 3. Robustez del resultado de ruido | El replay B01 es retrospectivo y tiene exposición normal pequeña. Si el oráculo mejora, comprobar si el estimador de prefijo recupera esa mejora en nuevos padres y ruido físico, conservando los demás módulos. Si el oráculo empata o empeora, auditar el modelo de base, admisión, sesgo, severidad y separabilidad antes de atribuir el fallo a la covarianza. |
| 4. Memoria | Si C03 deja ambigua la contribución, comparar media, momentos y mezcla a iguales operadores y propuestas. Conservar modos y variables de transición. Registrar qué historias existen al siguiente ON y cuándo se comprimen. Incluir un IMM o mezcla equivalente solo si su contrato de observación, publicación y costo es comparable. |
| 5. Predictor sucesor | Condicionado a desarrollar un banco nuevo, propagar incertidumbre con el predictor relinealizado y validar la integración de severidad. Comparar con el predictor fijo bajo búsqueda de fuente y onset desconocidos, sin reutilizar C03 para ajustar. |
| 6. Entrega | Regenerar cifras, compilar en aislamiento y verificar el mismo paquete en Overleaf. Revisar física, reproducibilidad, inglés, unidades, autores, financiación, conflictos y divulgación. Preparar la carta y disponibilidad de datos/código con coautores. Separar el paquete local de reproducción del paquete editorial y comprobar el límite de 40 MB por archivo en la [guía vigente de IEEE Access](https://ieeeaccess.ieee.org/authors/submission-guidelines/). |

## Decisiones del adjunto

Las derivadas de conmutación están comprobadas para ajustes dentro de
intervalos conocidos. Su utilidad bajo búsqueda de intervalos y ruido
sigue abierta. La corrección de información por variables molestas ya
tiene un diagnóstico nominal de amplitud anterior. Un siguiente contraste
puede estimar sensibilidades a parámetros de red en las mismas trayectorias
y verificar si los pares difíciles se predicen en una cohorte independiente.
La garantía secuencial requiere un nulo condicional válido y un presupuesto
explícito de reinicios. El ejemplo de sesgo del apéndice V muestra por qué
la cota no se transfiere automáticamente a las alarmas por hora de P07.

La reducción Hamiltoniana, las wavelets, el IEKF y la adaptación online
se justifican por una ablación de costo o decisión. El cierre del artículo
actual depende de C03, de una exposición explícita del límite instrumental
y de la revisión de coautores. Las extensiones que requieren una nueva
inferencia tienen su propio contrato de evidencia.

## Paquete editorial comprobado

`python -B scripts/package_ieee_editorial_sources.py` genera el ZIP de
LaTeX usado para revisión editorial. La versión actual contiene 174
entradas y ocupa 7.774.180 bytes. Una extracción aislada compiló el
artículo de 19 páginas y el suplemento de 40 con texto y paginación
idénticos. Quedan por verificar el mismo paquete en Overleaf y las
declaraciones finales con los coautores.
