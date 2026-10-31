# Reglas del usuario para P07

1. **Todo en `main`.** Trabajar, hacer commit y publicar directamente en `main`.
   No crear ramas, worktrees con ramas ni PR salvo nueva orden explícita del usuario.
2. **No borrar ni quitar del artículo las dos figuras protegidas:** la imagen de
   eventos (Figura 2, `fig:reference-event-types`) y el unifilar IEEE-39 con PMU
   (`fig:narrative-topology`). Deben seguir incluidas y visibles en el PDF principal.
3. La imagen de eventos se conserva byte por byte. El unifilar conserva sus 39
   barras, 46 ramas, 12 transformadores, 10 generadores y PMU
   `{2,5,6,10,19,22,29,39}`. No reemplazarlo por un grafo de nodos.
4. Las copias de `figures/frozen/` son de recuperación, no destinos de generación.
   No borrar, sobrescribir ni regenerar los archivos fijados en
   `figures/frozen/PROTECTED_FIGURES.json`; no cambiar sus hashes para ocultar un fallo.
   Consultar `docs/PROTECTED_FIGURES.md` antes de editar estos elementos.
5. La orden del 31-oct-2026 autoriza compactar el unifilar a una columna y mejorar
   el diagrama del método por fases. No autoriza cambiar conexiones, PMU, datos de
   eventos ni resultados científicos. Futuros cambios sustanciales requieren una
   nueva orden explícita y una copia sucesora, conservando las anteriores.
6. Después de cualquier edición del artículo: compilar, revisar visualmente las
   figuras en su tamaño final y ejecutar `python scripts/verify_protected_figures.py
   --pdf main.pdf`. La compilación por sí sola no demuestra que siguen presentes.

Estas reglas aplican por igual a Codex, Claude y otros agentes. No convierten en
resultados ejecutados los módulos que el manuscrito describe como propuestos.
