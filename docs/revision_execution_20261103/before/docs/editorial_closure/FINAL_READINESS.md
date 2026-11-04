# P07 — estado tras la auditoría científica, 3 de noviembre de 2026

**Borrador listo para revisión de coautores; revisión científica mayor antes del envío.**

## Cambios y alcance

El artículo tiene ocho secciones y 15 páginas. El suplemento de 42 páginas conserva los estudios auxiliares con sus cohortes y limitaciones; la página para David y Masoud usa exclusivamente resultados completos. La narrativa central separa predicción consistente durante la recuperación, el efecto posthoc de conservar el estado y la comparación independiente con los adaptadores aprendidos. El control continuo de un solo estado/GLR vuelve al texto principal como evidencia de desarrollo.

Las diferencias e intervalos de alarmas usan ahora tiempo monitorizado: 108 s por cada registro de 120 s. La conversión exacta por 120/108 está documentada; C01/A01, sus predicciones, asociaciones, umbrales y archivos originales permanecen intactos. No se incorporan resultados parciales de B01.

## Verificación de esta revisión

- C01 conserva 171 trayectorias físicas y 342 registros observados; A01 conserva 96/96 salidas y sus resultados favorables y nulos.
- Dieciséis hashes de figuras protegidas verificados: imagen de eventos byte por byte, visible en p. 4; unifilar de 39 buses y ocho PMU visible en p. 5.
- Artículo y suplemento compilados sin referencias indefinidas ni etiquetas duplicadas; todas sus páginas renderizadas y revisadas. La página de coautores también se revisó visualmente.
- ZIP de 133 entradas recompilado aisladamente: texto y paginación coinciden exactamente para ambos documentos. Es una prueba de reproducción documental, no una repetición independiente de las campañas científicas.
- Paquete de coautores con hashes verificados y sin datos PMU crudos ni archivos privados. El manifiesto actual está en `FINAL_MANIFEST.json`.

## Pendientes científicos y editoriales

1. Validación independiente, con información equiparada, del control continuo/GLR frente al banco de historias para la afirmación fuerte sobre la necesidad de recuperación explícita.
2. Comparación con umbrales seleccionados previamente en validación y presupuestos de alarmas comparables; no elegirlos con C01/A01.
3. Transferencia a un modelo/planta independiente y calibración de las masas para afirmaciones más amplias de generalización e incertidumbre.
4. Revisión científica de coautores, permisos/declaraciones, comprobación bibliográfica final y confirmación del código/dependencias a entregar.

La [respuesta completa a la auditoría](../SCIENTIFIC_AUDIT_RESPONSE_20261103.md) distingue correcciones ejecutadas de evidencia aún faltante. No se promete aceptación ni se envía el manuscrito a autores o revista. B01 continúa separado; RAW0002 sigue cerrado.

## Trabajo activo para fortalecer la contribución

B01 prueba calibración y verosimilitud aprendida desde SIM. C02 prepara una comparación independiente con las 18 fuentes en entrenamiento, un observador físico continuo, banco nominal y calibración previa del presupuesto de alarmas. Ya tiene 102 escenarios sellados y 24 pruebas aprobadas; la implementación completa continúa antes de iniciar simulaciones. El resumen y la conclusión presentan primero las capacidades medidas; las condiciones de validez permanecen en la discusión. Véase `docs/P07_VALIDATION_ACTIONS.md`.
