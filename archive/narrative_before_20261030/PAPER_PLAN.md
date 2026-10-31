# P07 — cierre del manuscrito, 29-oct-2026

Estado: borrador revisado con evidencia ejecutada; C01 preparada, no ejecutada.
No cambia el título, los autores, la planta F01 ni los estimadores archivados.

## Contrato científico en cinco frases

1. Problema: ocho PMU deben distinguir recuperación de estado y atribución de una intervención, con información incompleta y error de modelo.
2. Gap que se contrasta: una reconstrucción precisa no garantiza separación entre fuentes; un buen score en fuentes conocidas tampoco prueba transferencia ni vigilancia causal.
3. Idea: medir separación después de permitir amplitud y nuisance físicos, y conservar hipótesis de intervención/estado en lugar de aprender exclusivamente etiquetas de bus.
4. Prueba falsable: geometría frente a errores de soporte en el banco batch; método causal y referencias congeladas frente a líneas persistentes, restauraciones, R/X y ruido, con todos los fallos incluidos.
5. Consecuencia: decidir qué puede inferirse, qué permanece ambiguo y cuánto cuesta esperar; el resultado negativo también limita las afirmaciones del artículo.

## Lo que se preserva

- B0–B3: reconstrucción de voltajes y recentrado físico, con sus denominadores.
- E_B: banco batch 137 hipótesis, GH31 y W2. Sin sustitución por R11.
- E_J: formulación conjunta propuesta, aún no validada en su totalidad.
- ANDES/ExtraTrees históricos: referencia separada; no se mezcla el leaderboard con H04.

## Lo que se añade ahora

- R11 y nominal: componente causal carga/línea, estados continuos, inicio desconocido, 47 coordenadas y catálogo 9+9 conocido.
- Ecuaciones ejecutadas del intercepto fijo, peso prequential y descomposición exacta de ΔM. Son mecanismos, no tres teoremas nuevos.
- Tabla y figura H04 generadas desde CSV importados con SHA256. R12 queda como ablación negativa.
- Comparador publicado Chen2016: núcleo reproducido, adaptación F01 declarada; carril propio de apertura persistente, sin atribuirle clasificación de carga/OFF.
- C01: métodos y protocolo sellados; nuevas solicitudes de simulación preparadas. Ninguna métrica confirmatoria inventada.

## Orden fijo hasta cerrar

1. Ejecutar C01 sin modificar R11, nominal, ExtraTrees, umbrales ni evaluador. Conservar los rechazos y censuras.
2. Generar comparaciones pareadas por padre, intervalos, exposición normal y figuras; escribir Results a partir de esos artefactos, incluso si no hay superioridad.
3. Revisar contribuciones frente a la literatura y a los fallos, compactar el borrador y verificar referencias, derivaciones, reproducibilidad y consistencia de claims.

No se crea R13 para arreglar otro bus. Una modificación posterior sería otra investigación, no reparación de este examen.

## Afirmaciones bloqueadas

No se afirma: estimador global óptimo, probabilidades calibradas, novedad por llamar tensor a M, mejora del score oficial de la hackathon, generalización causal a fuentes excluidas, validación de 39 orígenes, faltas/generación/integridad, cambio de PMU, transferencia de campo o reproducción exacta de RAW0001. No se abre RAW0002.

La novedad defendible debe apoyarse en la distinción información de estado/separación de fuentes y su prueba empírica, no en una lista de Kalman+Bayes+tensor. Las recursiones de filtrado, la mezcla finita y CUSUM tienen precedentes. La contribución causal queda condicionada a C01 y a la comparación con esos precedentes.

## Fuentes del borrador y comandos

- Métodos: `sections/05b_causal_component.tex`.
- Resultados nuevos: `sections/08b_continuous_evidence.tex`.
- Evidencia: `generated/frozen/continuous_20261029/MANIFEST.json`.
- Auditoría de escritura y alcance: `docs/paper-closure-2026-10-29.md`.
- Regenerar: `python -B scripts/generate_continuous_evidence.py`.
- Compilar artículo y suplemento: `powershell -File scripts/build_manuscript_bundle.ps1`.

El PDF es un borrador de investigación, no una versión autorizada para enviar.
