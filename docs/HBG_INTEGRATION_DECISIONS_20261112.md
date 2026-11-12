# Integración de las ideas Hamiltoniano–Bayes–grafos en P07

## Contrato científico

**Problema.** Atribuir una intervención nueva cuando la respuesta anterior
todavía persiste, con ocho PMU y un catálogo conocido.
**Vacío por resolver.** Separar el valor de la distribución de recuperación
del valor de conservar etiquetas históricas y del aporte de cada medición.
**Idea.** La ambigüedad depende tanto de las causas que producen respuestas
parecidas como de la incertidumbre del estado desde el que se predicen.
**Prueba que puede refutarla.** Controles de distribución con las mismas
propuestas, junto con V frente a V+I, recalibrados antes de un TEST nuevo.
**Consecuencia.** Si no mejora atribución o alarmas, conservar la geometría
como explicación de límites y retirar la afirmación de mejora del método.

## Qué aportan los documentos nuevos

Los dos textos pegados son idénticos. El Markdown independiente coincide con
el del ZIP. Se conservaron los originales en un directorio de desarrollo
separado y se reprodujo el ejemplo de cuatro buses. Sus resultados verifican
identidades y una simulación reducida, no la planta DAE de P07.

| Idea | Dictamen | Acción |
|---|---|---|
| Grafos, operadores DAE y respuestas de fuente | Ya sustentan el predictor actual | Explicitar procedencia; no presentar otro algoritmo por renombrarlo |
| Bayes factor gaussiano de rango uno | Correcto bajo el prior gaussiano indicado | Verificar integral y normalización truncada; no sustituir el prior existente |
| Estado de recuperación incierto | Conecta directamente con el control de covarianza | Añadir identidad explicativa y condición de no duplicar incertidumbre |
| Separación con magnitud rival ajustable | Extensión ejecutable del diagnóstico anterior | Ejecutada con los operadores reales y soporte [-0,2;0,2] |
| Hamiltoniano de oscilación | Válido para el modelo reducido declarado | Verificado; no se añade como energía de toda la DAE ni como segunda likelihood |
| Prior energético | Hipótesis de método nuevo | Exige Hessiano adecuado, referencia angular y calibración independiente |
| Generación, fallas y clase desconocida | Extensiones posibles | No incorporarlas como capacidades validadas del banco de 18 fuentes |
| Optimalidad global | No establecida para el banco conmutado | La solución cuadrática condicionada no demuestra optimalidad del sistema completo |

## Resultado nuevo con el predictor P07

El sucesor `experiments/channel_profile_20261112` conserva el experimento
nominal anterior y cambia únicamente la magnitud del rival de carga: ahora
se optimiza dentro del soporte total admitido por el banco. Las aperturas
de línea nunca se reescalan. Se fijan onset, estado inicial y carga verdadera
de +10%; se usan todos los pares de 18 fuentes a 3, 15 y 30 reportes.

A un segundo, la razón entre separaciones mínimas V+I/V tiene mediana 1,53
(1,03–7,82). El aporte nominal de corrientes persiste después de ajustar la
magnitud rival. Al mismo tiempo, cuatro fuentes cambian de rival más cercano.
BUS31 retiene solo 2,3% de su separación mínima anterior: el rival pasa de
BUS26 a BUS7. Estos cocientes comparan mínimos que pueden corresponder a
fuentes diferentes; no son tasas de éxito ni estimaciones poblacionales.

El resultado importante no es que todas las firmas sean muy grandes: una
fuente de otra magnitud puede imitarlas mucho mejor de lo que muestra una
comparación con magnitudes fijas. El artículo resume este hallazgo y el
suplemento desarrolla la geometría, la figura y sus límites.

## Dos errores evitados

1. La covarianza actual de reportes se construye desde innovaciones del
   predictor completo. No se le suma de nuevo `O P Oᵀ` del mismo filtro.
   La identidad `R+O P Oᵀ` se deriva por separado, con R sin ese término.
2. El perfil conjunto V+I usa una sola amplitud rival. No se suman mínimos
   de V e I obtenidos con amplitudes diferentes como si fueran evidencia
   conjunta. Se verifican monotonía y descomposición al mismo ajuste.

## Decisiones de maduración

1. Terminar C03 intacto y aplicar su contrato de auditoría. No usar sus
   resultados futuros para declarar confirmatorio el diagnóstico de hoy.
2. Implementar C04 en desarrollo para conservar media y covarianza con las
   mismas propuestas y reloj. Comprobar primero equivalencias gaussianas y
   sensibilidad a compresión; luego congelar un contraste independiente.
3. Si el mecanismo sigue siendo defendible, cruzar ese control con V/V+I,
   reconstruyendo cada observador y calibrando cada brazo al presupuesto
   común. Evaluar también ruido independiente y pares ambiguos; no seleccionar
   solo BUS31, BUS16 o BUS24 después de ver sus resultados.
4. Explorar un prior energético únicamente si el modelo completo permite
   definirlo y aporta algo que la incertidumbre ya disponible no representa.

No recomiendo cambiar el nombre a HBG-DAE ni extender ahora el resumen a
fallas, generación u optimalidad global. La combinación útil es una pregunta
física comprobable, no una lista de formalismos.

## Literatura y trazabilidad

Se verificó el registro primario de [Fiaz et al.](https://doi.org/10.1016/j.ejcon.2013.09.002),
que formula redes port-Hamiltonianas; se añadió esa referencia contextual al
suplemento. El [texto de los autores de Anguluri et al.](https://rajanguluri.github.io/assets/pdf/papers/RA-OK-LS-TCNS2022.pdf)
trata localización de entradas con estado inicial desconocido y Group LASSO;
ya estaba citado en P07. Esos antecedentes impiden atribuir novedad a
Hamiltoniano, propagación dinámica o inferencia con estado desconocido por
separado. No se hizo una búsqueda exhaustiva de novedad en esta integración.

Las auditorías matemáticas y de reproducción están en
`HBG_MATHEMATICAL_AUDIT_20261112.md` y `HBG_REPRODUCTION_AUDIT_20261112.md`.
El ejemplo original y trece controles adicionales pasan; los controles
nominales del sucesor también pasan una revisión Luna independiente.
No se abrió RAW0002 ni se modificó C03.

## Verificación de entrega

Artículo y suplemento recompilados: 19 y 31 páginas. El paquete extraído
reproduce texto y paginación de ambos documentos. Desde esa extracción se
ejecutaron también el sucesor de magnitud rival y los trece controles HBG,
sin acceso al repositorio científico. La revisión visual cubrió la nueva
figura a tamaño de página, sus ecuaciones y el panorama del suplemento;
se corrigió una ecuación que excedía la columna. Las dos figuras protegidas
siguen visibles en las páginas 5 y 6 y sus 16 hashes pasan. El barrido
editorial automatizado registra cero hallazgos. Persisten advertencias
conocidas de la plantilla, sin certificar un log vacío ni preparación para
envío. Se publica por Git según el flujo autorizado de sincronización con
Overleaf; no se observó una compilación remota.
