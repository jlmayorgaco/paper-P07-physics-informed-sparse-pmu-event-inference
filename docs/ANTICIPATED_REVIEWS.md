# Revisores previstos (IEEE Access / Transactions) y estado de la respuesta

Cada punto indica dónde responde hoy el paper y qué queda abierto. «Cerrado» = respuesta con evidencia en el texto o el suplemento; «Declarado» = límite reconocido sin evidencia nueva; «Abierto» = requiere trabajo.

## Revisor 1 (sistemas de potencia)

| Pregunta probable | Estado | Dónde / qué falta |
|---|---|---|
| ¿Es realista la planta? Cargas de impedancia constante, un solo simulador | Declarado + parcial | Suplemento «Transferencia a una planta distinta»: otro modelo de planta, los aprendices pierden fuentes, el estático no; **el banco no se corrió allí (Abierto)**. |
| ¿Datos reales? | Declarado | RAW0001 es validación con iteraciones registradas; el banco no arranca en ese registro. Amenazas a la validez (suplemento). |
| ¿Por qué no se compara con Yang, Chen y Zhai (GLR AC dinámico, filtro de partículas)? | Declarado | Citados y situados en trabajo relacionado y en la tabla; **no ejecutados (Abierto)**. Ambos tratan cortes persistentes con 10 PMU, sin restauración ni cargas. Opción: implementar el GLR en Python. |
| Con 8 PMU, ¿qué pasa si falta alguno? | Cerrado | Sección de integridad; la banca física pierde atribución con valores retenidos. |
| ¿Ruido realista? | Declarado | El ruido independiente por PMU de 0,05 % TVE lo derrota; hace falta estimar la covarianza entre PMU. |
| ¿Fallas, generación y otros tipos? | Declarado | El banco es de carga y línea; el atribuidor estático cubre los doce eventos de RAW; campaña de todas las familias pendiente. |
| ¿Tiempo real? | Cerrado | Banco nominal 26,4 ms por informe; el banco de cinco modelos es reproducción fuera de línea. |
| ¿Errores de modelo de red? | Cerrado | 68 de 72 extras ocurren fuera del banco de R/X; fallos oportunos solo ahí. |

## Revisor 2 (métodos y estadística)

| Pregunta probable | Estado | Dónde / qué falta |
|---|---|---|
| ¿Cuántas unidades independientes? | Cerrado | 18 padres (C01) y 12 registros (B01); réplicas no independientes; cota inferior 74 % con 12/12; intervalos por padre. Tabla de afirmaciones. |
| ¿TEST reutilizado, RAW iterado? | Cerrado | Amenazas a la validez: quién abrió qué y cuántas veces. |
| ¿Baselines justos? | Parcial | Aprendices reentrenados con datos del banco, umbral en CAL, una pasada. **Falta** el GLR de un estado (C02) y un aprendiz con mucha más variedad física. |
| ¿Hiperparámetros ajustados con TEST? | Cerrado | Umbral en CAL; protocolos con hash. |
| ¿Ninguna falsa alarma? | Cerrado | 11,8 h, cota 95 % de unas 0,25 por hora; sin afirmar tasa operativa. |
| ¿Son probabilidades las masas? | Declarado | La discusión indica que no lo son. |
| ¿Reproducibilidad? | Abierto (decisión del autor) | Repositorio científico privado; plan: depositar en Zenodo `experiments/` del paper. |
| ¿La teoría predice los experimentos? | Cerrado | Predicción 1–3 contrastadas; información predice amplitud de detección (ρ = −0,794); la confusión entre pares queda inconclusa. |
| ¿Resultados negativos? | Cerrado | Condicionar por la historia no ayuda (10 celdas, hash previo); el reset sí daña. |
