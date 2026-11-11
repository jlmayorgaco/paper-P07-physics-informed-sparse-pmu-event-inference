# P07 — revisión ejecutada, 3 de noviembre de 2026

**Registro historico.** B01 y C02 ya cerraron. Ver el [cierre actual](../P07_CLOSURE_CURRENT.md).

**Borrador fortalecido para revisión de coautores; validación científica adicional pendiente antes del envío.**

## Cambios comprobados

El artículo tiene 16 páginas y el suplemento esencial 19. El material auxiliar anterior sigue disponible en Historical Technical Notes. El método explicita los offsets afines por topología, la integración de severidad por intervalos, la dependencia estado–severidad y las aproximaciones de covarianza y compresión. Las pruebas pequeñas reproducen las identidades locales; no certifican el banco no lineal ni sus probabilidades.

La genealogía de ambos ExtraTrees identifica el entrenamiento con 32 padres y la validación con ocho, sus 19 clases, 846/1.457 características, 400 árboles, hashes y regla de publicación. El suplemento incluye ahora los resultados completos de A01, incluidos sus resultados nulos, junto con C01. Los denominadores de 120 s completos y 108 s monitorizados se distinguen sin modificar los resultados congelados.

## Verificación documental

- Artículo y suplemento compilados sin referencias indefinidas ni etiquetas duplicadas; sus 35 páginas fueron renderizadas y revisadas. Se corrigieron los solapamientos de texto detectados en el suplemento.
- Dieciséis hashes de figuras protegidas comprobados. La imagen de eventos permanece byte por byte en la página 4; el unifilar IEEE-39 con ocho PMU permanece en la página 5.
- El ZIP de fuentes fue recompilado en un directorio aislado: texto y paginación coinciden exactamente para ambos documentos. El manifiesto de esta ejecución es `../../output/source/SOURCE_PACKAGE_VALIDATION.json`.
- Las pruebas matemáticas y el generador de genealogía se reproducen desde snapshots mínimos, sin el repositorio científico ni datos de campañas. Las pruebas matemáticas requieren NumPy/SciPy.
- C01/A01 y sus archivos congelados no se editaron. No se incorporaron resultados parciales de B01 ni resultados inexistentes de C02.

El registro verificable de esta revisión está en `../revision_execution_20261103/FINAL_VERIFICATION.json`; la respuesta punto por punto está en `../revision_execution_20261103/RESPONSE_AND_STATUS.md`.

## Evidencia que aún determina la contribución

1. Terminar B01 y evaluar su calibración independiente sin seleccionar cambios con TEST.
2. Ejecutar C02: banco nominal, GLR continuo y ExtraTrees nuevo, con selección de umbrales sólo en CAL y un presupuesto de alarmas declarado. La selección usa la población balanceada completa; no certifica cada estrato de ruido por separado.
3. Evaluar innovaciones pre-update, cobertura y efectos de poda/compresión para sostener afirmaciones de incertidumbre.
4. Probar un modelo dinámico independiente y un contrato instrumental físicamente realizable si se pretende ampliar la generalización.
5. Cerrar revisión de autores, declaraciones y permisos antes de una eventual presentación.

La implementación y el estado operativo de C02 se documentan en `../P07_VALIDATION_ACTIONS.md` y en su directorio del repositorio científico. Una campaña implementada o en cola todavía no constituye evidencia ejecutada. No se promete una calificación perfecta ni aceptación. RAW0002 permanece cerrado; no se enviaron mensajes a autores ni a la revista.
