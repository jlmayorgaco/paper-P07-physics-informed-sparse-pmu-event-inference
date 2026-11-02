# P07: aporte, evidencia acumulada y alcance

**Dictamen actualizado:** ver [auditoría completa del 2 de noviembre](review_20261102/AUDITORIA_COMPLETA_P07.md). La revisión distingue cobertura oportuna de exactitud condicional, incorpora persistencia y tablas confirmatorias omitidas y declara el solapamiento de dos grupos normales en la validación interna del ET original. El borrador es para revisión de coautores, no se certifica como listo para envío.

Actualización editorial: 2 de noviembre de 2026. No se entrenó ni modificó
ningún estimador; no se cambió C01, sus casos o resultados. No se abrió RAW0002.

## La pregunta que organiza el artículo

Con ocho PMU, ¿cómo recuperar información sobre una perturbación y atribuirla
a una causa física, aunque su origen no esté instrumentado y la red todavía
se esté recuperando de una intervención anterior?

La propuesta compara lo observado con respuestas de causas candidatas construidas
con la DAE, Ybus, operadores de carga/línea y corrientes terminales orientadas.
Integra la intensidad local y conserva historias de inicio/restauración y
estado. M resume atribución activa; Gamma conserva la causa que explica la
respuesta; Delta M permite seguir cómo cambia esa explicación. ExtraTrees
con features eléctricas es una alternativa ejecutada, y una fuente de resultados
útiles, no un antecedente que deba ocultarse.

El aporte defendible es el procedimiento causal especificado, su comparación y
el análisis de qué información aporta cada representación. Ni Bayes, ni un
tensor por sí solo, ni el uso de ecuaciones físicas constituyen una novedad.
No se ha aislado una ganancia final causada específicamente por «Bayes + tensor».

## Lo que recuperamos para el cuerpo del artículo

| Resultado | Dato ejecutado | Lo que demuestra / límite |
|---|---|---|
| Reconstrucción de voltajes no medidos | Error relativo medio 0.3402% nominal, 0.00990% WLS, 0.00963% Kalman; 100 trayectorias | La red condicionada a las PMU recupera información bajo el modelo nominal. No prueba identificación única de todas las fuentes. |
| Features del localizador histórico | Top-1 medio 49.6% base, 54.8% con graph-temporal, 59.0% completo; tres semillas, 7,915 muestras físicas por semilla | Ablación de una familia histórica 136–448 features; no confundir con el ZIP final de 45,162 ni con los ET causales. |
| Sensibilidades tensoriales | Error blanqueado mediano 0.205 con D, 0.469 con autocurvatura, 0.00307 incluyendo términos mixtos; 32 respuestas | Los términos de interacción mejoran esa aproximación local de dos cargas. No fueron insertados retrospectivamente en C01. |
| Banco Bayes de 137 soportes | Top-1 conjunto 100%, 98.82%, 66.25%, 24.38% según régimen | Onset/contexto/familia conocidos; replays dependientes. Se conserva la advertencia del prior efectivo por el normalizador de una fuente. No acredita calibración ni replay corregido. |
| ZIP realmente entregado frente al estimador físico temprano | 124 ventanas comunes; 96 eventos. Familia+fuente 0/96 frente a 96/96 | Transferencia histórica de desarrollo, dominios e información previa distintos; no score oficial ni prueba final. Se muestran matrices de confusión de familia verificadas. |
| Comparación causal confirmatoria | Banco 644/648 y 72 extras; ET referencia 330/648 y 29; ET corto 352/648 y 16 | Ganancia sobre todo en carga, coste de alarmas bajo R/X externo. 108 intervenciones, repetidas seis veces, no 648 independientes. |
| Transferencia retrospectiva e integridad | Híbrido aprendido 1/24 a 2/24; composición consistente de 180 ventanas | Se mantiene el resultado negativo de transferencia amplia. El banco físico no supera sus condiciones de arranque en RAW0001. No es validación de campo. |

Las cifras nuevas de figuras y tabla de soportes se calculan con
`scripts/build_evidence_bridge.py` a partir de CSV verificados contra sus
manifiestos. `generated/EVIDENCE_BRIDGE_PROVENANCE.json` registra los 11
archivos usados. El ensayo histórico contra el ZIP se importó byte por byte
en `generated/frozen/historical_submission_comparison_20261102/`, comprobando
su manifiesto original. No se reconstruyeron matrices desde porcentajes.

## Qué significa physics-informed en cada ruta

- ExtraTrees usa una representación informada por señales y relaciones
  eléctricas. Sus etiquetas no tienen que satisfacer la DAE.
- El banco físico usa la DAE y el mapa instrumental para construir una
  predicción de cada intervención; su evidencia integra una intensidad
  desconocida y compara causas, con aproximaciones explícitas.
- D/Q/Qij son coeficientes de respuesta por canal, fuente y tiempo.
  M/Gamma/Delta M son resúmenes de inferencia por causa y tiempo. Son objetos
  diferentes. No atribuimos aceleración o novedad a una forma de almacenamiento.
- Las ecuaciones de potencia usan corrientes del terminal correspondiente.
  No equivalen automáticamente a inyección nodal. Los fasores fundamentales
  no permiten reconstruir THD sin información armónica adicional.

## Relación con la literatura y próximos pasos

Los estimadores DAE de Katanic y colaboradores ya reconstruyen estados con
modelos incompletos; Warner ya compara trayectorias para fallas; los bancos
de modelos y la evidencia marginal son precedentes. Li y colaboradores usan
restricciones físicas en una red espaciotemporal de grafos. P07 no presenta
estos ingredientes como inventos nuevos ni atribuye resultados no ejecutados
a una GNN. La diferencia que se explica es la atribución causal mediante
historias de intervención y recuperación, con fuentes, intensidades y clocks
separados, y evidencia empírica de las ventajas y errores de ese procedimiento.

El futuro metodológico se limita a preguntas medibles: evidencia integrada
frente a residual perfilado con el mismo diccionario; memoria frente a ausencia
de memoria con reglas y presupuesto de alarmas iguales; contexto/estado
inciertos conjuntamente; calibración de probabilidades; y prueba con fuentes
excluidas del aprendizaje frente a un modelo de grafos o corrección aprendida.
Estas propuestas no se anuncian como experimentos ya realizados ni autorizan
reajustar C01.

## Entrega actual

El manuscrito incorpora las ecuaciones, pseudocódigo, diagrama por cuatro
regiones, comparación de métodos, figura de componentes, matrices de confusión,
resultados confirmatorios y limitaciones. La figura de eventos permanece
intacta. Es un borrador para revisión científica de David y Masoud: la fuerza
de la contribución debe juzgarse como procedimiento completo y estudio
comparativo; una afirmación causal sobre componentes requiere las ablaciones
que todavía no existen. No se declara aceptación ni superioridad universal.
