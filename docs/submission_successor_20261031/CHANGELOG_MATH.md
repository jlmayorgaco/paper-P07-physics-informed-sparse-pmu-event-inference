# Corrección técnica M1–M7 — sucesor de envío 31 octubre 2026

## Contrato científico de esta corrección

1. **Problema:** los apéndices mezclaban algunas condiciones matemáticas insuficientes con una descripción del estimador por lotes que no reconciliaba su normalización histórica.
2. **Brecha:** las pruebas ilustrativas previas no cubrían conos degenerados, fibras con covarianza variable, dominios unilaterales o matrices anchas.
3. **Idea:** conservar las fórmulas que son válidas y delimitar exactamente sus hipótesis, sin atribuir al R11 causal defectos del estimador histórico o garantías de un diseño no ejecutado.
4. **Prueba falsadora:** contrastar los enunciados reparados con proyecciones, integración numérica independiente y casos límite que violaban la redacción anterior.
5. **Consecuencia:** el texto puede defender las identidades bajo su contrato explícito; estos cambios no producen nuevas métricas físicas, calibración, resultados cyber ni transferencia a RAW.

Se aplicó `C:/Users/walla/.codex/skills/ieee-access-academic-quality/SKILL.md`, con su estándar de revisión técnica independiente. El alcance de edición fue únicamente `supplement/appendix_d_theory.tex` y `supplement/appendix_e_estimator.tex`, además de este registro y los checks nuevos. Se preservaron las cifras históricas, las figuras y las configuraciones congeladas. No se leyeron outputs/truth C01 ni RAW0002; no se ejecutó simulador ni se hizo push.

## Cambios

| Hallazgo | Archivo y comienzo actual | Reparación |
|---|---|---|
| M1 | `supplement/appendix_d_theory.tex:660` | Se declara simétrica la separación mínima entre conos. Se añade demostración breve mediante la optimización de escala no negativa y el máximo producto interior entre sus secciones unitarias. Se conserva el identificador LaTeX de la ecuación para no romper referencias. |
| M2 | `supplement/appendix_e_estimator.tex:419` | Cone–Laplace exige interior no vacío del cono en las coordenadas declaradas, convergencia casi en todas partes de indicadores, envolvente integrable de los integrandos reescalados y contribución distante pequeña respecto a la escala explícita. La prueba justifica que el coeficiente es positivo antes de escribir la equivalencia multiplicativa. Se excluyen expresamente los conos de masa gaussiana cero. |
| M3 | `supplement/appendix_e_estimator.tex:503` | La reducción por fibras requiere invariancia de la **ley condicional completa**. En el caso gaussiano se especifican media y covarianza; la prueba de Fubini permanece válida bajo esa condición. |
| M4 | `supplement/appendix_e_estimator.tex:531` | La evidencia mixta define su integral, dato centrado, dominio bilateral interior, dimensión regular, rango de la matriz y condiciones de localización. Se advierte que datos desplazados o una amplitud unilateral cambian la constante. La tasa y constante originales se conservan en el dominio donde fueron demostradas. |
| M5 | `supplement/appendix_e_estimator.tex:135,165,258,326,413,675` | Se distinguen modelo normalizado, implementación histórica y sucesor corregido sin nueva evaluación física. La prior efectiva y el factor histórico aparecen junto a la prior y la regla de cuadratura. Se distingue la integral exacta `Z_S` de su aproximación normalizada `widehat Z_S` y del score histórico `widetilde Z_S`. La tabla de algoritmo y el cierre no atribuyen a resultados antiguos la prior corregida. |
| M6 | `supplement/appendix_d_theory.tex:773` | El margen restringido se define con la raíz del autovalor mínimo de `H_U^T H_U`, equivalente al ínfimo sobre coeficientes unitarios, por lo que cuenta núcleos de matrices anchas. La cota de estabilidad requiere explícitamente margen positivo. |
| M7 | `supplement/appendix_d_theory.tex:308,333,352,703` | Se exige precisión nuisance total positiva definida en coordenadas comunes, e información/tangente no nula antes de dividir. El estadístico matched se declara para su experimento gaussiano centrado. Se especifica el uso de cociente identificable o geometría por proyección cuando proceda. La frase sobre onset distingue el banco histórico de onset conocido del banco causal R11. |

No se añadieron teoremas nuevos ni se cambiaron valores empíricos. Las reparaciones restringen el alcance de resultados existentes y corrigen una afirmación de simetría. Los cambios de interpretación histórica no reparan retroactivamente el código ni las cifras de su evaluación.

## Verificación independiente

Comando ejecutado:

```powershell
python docs/submission_successor_20261031/checks/math_corrected_claims.py
```

Resultado: todas las assertions pasaron. El JSON guarda hashes SHA-256 de los dos apéndices y del script correspondiente a la ejecución.

- **M1:** 15 comparaciones de conos, resolviendo cada dirección por minimización/proyección NNLS independiente; discrepancia máxima `3.89e-16`.
- **M2:** tres scores gaussianos en semirrecta con prior propia y cuatro escalas; error relativo asintótico decreciente, máximo final `3.65e-4`. El contraejemplo cusp conserva su ley `epsilon^3` y queda correctamente excluido porque su cono tiene dimensión uno en una carta de dimensión dos.
- **M3:** integral bidimensional con prior correlacionada frente a integral reducida; error `1.11e-16`. El caso de media constante pero varianza variable sigue rechazando la eliminación indebida de la fibra.
- **M4:** integrales finitas con prior propia para órdenes `k=1,2,3`; discrepancia máxima de constante `1.23e-15`. Se comprueba por separado que un residuo observado cambia la constante y que el dominio unilateral aporta la mitad a igual densidad local.
- **M5:** 20 vectores de evidencia sobre los 137 soportes; equivalencia entre factor histórico y prior efectiva con error máximo `3.00e-15`. El control de respuesta cero devuelve la prior efectiva histórica, no la prior originalmente declarada.
- **M6:** el mapa ancho `[1 1]` tiene margen cero; la cota corregida se cumple en 30 pares sparse de un mapa con margen positivo.
- **M7:** 30 comparaciones de información nuisance positiva definida satisfacen la monotonía; los ejemplos singular y de tangente nula quedan fuera de las fórmulas de división.

También pasó `git diff --check` para los dos apéndices. Los avisos de conversión LF/CRLF de Git no son errores de contenido.

Archivos nuevos:

- `docs/submission_successor_20261031/checks/math_corrected_claims.py`
- `docs/submission_successor_20261031/checks/math_corrected_claims.json`
- `docs/submission_successor_20261031/CHANGELOG_MATH.md`

Los checks son algebraicos y adimensionales. No son pruebas de rendimiento físico ni validan globalmente un teorema por muestreo; las demostraciones y condiciones se repararon en el texto y los ejemplos se usan como regresión adversarial.

## Revisión técnica final y vetos

**M1–M7 quedan cerrados para el alcance matemático reparado. No permanece un veto matemático derivado de esos siete hallazgos.** La integral truncada y el estado condicional de R11 ya habían sobrevivido a la revisión adversarial previa y no se modificaron.

La interpretación del estimador histórico queda condicionada a su prior efectiva. No hay autorización científica para llamar a sus cifras «resultados de la prior corregida» sin una nueva evaluación física. Tampoco la teoría suplementaria acredita por sí sola garantías globales del R11, probabilidad calibrada, superioridad cyber o transferencia externa a RAW. Estas fronteras ya constan en el texto y no constituyen nuevas exigencias para su contribución limitada.

La compilación conjunta, revisión visual final y verificación de figuras protegidas están delegadas al agente principal, que integra el envío. **Este informe no certifica por sí solo que el conjunto esté submit-ready**: cubre la corrección matemática asignada, y la aprobación final requiere esa integración y las revisiones independientes restantes. No se ejecutó build desde este subtrabajo para evitar interferir con la compilación central.
