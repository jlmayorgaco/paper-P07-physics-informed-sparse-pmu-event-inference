# Figuras que deben permanecer en P07

Por orden expresa del usuario del 31 de octubre de 2026, **la Figura 2 de eventos
y el unifilar IEEE-39 con las ocho PMU no se borran ni se quitan del artículo**.
La protección incluye su presencia en el PDF, no solo conservar un archivo sin usar.

| Figura | Etiqueta estable | Archivo activo | Copia de recuperación |
|---|---|---|---|
| Eventos, Figura 2 | `fig:reference-event-types` | `figures/generated/event_signatures.pdf` y `.png` | `figures/frozen/event-signatures-approved/` |
| IEEE-39 con PMU | `fig:narrative-topology` | `figures/ieee39_single_line.tex` y `figures/generated/narrative_topology.pdf` | `figures/frozen/ieee39-approved-20261031/` |

La copia aprobada del unifilar contiene el TikZ completo copiado literalmente,
un `main.tex` independiente, PDF, PNG, generador y auditoría. Es la versión amplia
aprobada antes de compactar. No depende de que una futura edición conserve el
archivo activo. Para recuperarla, copiar su TikZ al archivo activo y compilar;
para recuperar también la regeneración, restaurar su script en `scripts/`.
Nunca ejecutar el generador dentro de la carpeta congelada.

La versión compacta de una columna también se conserva completa en
`figures/frozen/ieee39-compact-20261031/`. Su carpeta no reemplaza la versión
amplia aprobada. Ambas permiten recuperar el código y la imagen de forma independiente.

La presente revisión puede acercar elementos y ajustar tipografía para usar una
columna. Debe conservar toda la conectividad, dispositivos y PMU. La figura de
eventos no se redibuja, recorta ni regenera. Las copias y sus hashes son inmutables;
una futura revisión autorizada se conserva en otra carpeta, sin reemplazarlas.

`scripts/verify_protected_figures.py` comprueba hashes, la inclusión alcanzable
desde `main.tex`, las etiquetas y la presencia de ambas figuras en el PDF. Los
scripts de compilación llaman este control antes y después del build. Un fallo
se investiga: **no se resuelve borrando el control o actualizando el hash**.

```powershell
python scripts/verify_protected_figures.py
python scripts/verify_protected_figures.py --pdf main.pdf
```

El historial de Git constituye una segunda vía de recuperación. Estas copias
evitan depender solo del historial y dejan la instrucción visible a otros agentes.
