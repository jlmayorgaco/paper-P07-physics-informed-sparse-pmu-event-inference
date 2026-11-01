# Recuperación del artículo y su complementario — 31 de octubre de 2026

## Diagnóstico comprobado

Las fuentes `main.tex` y `supplement.tex` estaban presentes en el checkout
`613ed39` y ambas compilaban con pdfLaTeX. El commit `fdcdb83` quitó de
`main.tex` la inclusión del PDF complementario: desde ese cambio, el documento
principal produce únicamente el artículo. No eliminó `supplement.tex` ni sus
apéndices. El README mezclaba instrucciones de la antigua salida conjunta
con instrucciones de las dos salidas independientes.

Hay además un fallo del entorno de compilación. La ejecución local de
`latexmk -version` informa que falta Perl. El compilador integrado de Codex
también informó acceso denegado al log de MiKTeX en ProgramData; su alternativa
Tectonic falló en `ieeeaccess.cls`, al encontrar el comando específico de
pdfTeX `\pdfobj` usado por el color directo. No se cambió la clase oficial ni
la instalación del sistema. La ruta comprobada usa pdfLaTeX y BibTeX directamente.
La previsualización automática del editor sigue dependiendo de ese entorno.

## Separación que queda implementada

| Documento | Contenido |
|---|---|
| `main.tex` | Problema, mecanismo físico, integral que define la evidencia, recuperación, algoritmo causal, protocolo, resultados decisivos y límites |
| `supplement.tex` | Explicación por reporte, configuración congelada, derivación de la integral, actualización condicional, ejemplos numéricos, escenarios y reproducción; después, teoría completa y estudios históricos preservados |
| `output/pdf/P07_Event_Attribution_Review_Bundle.pdf` | Los dos documentos completos, concatenados con marcadores de navegación |

El nuevo `supplement/appendix_causal_walkthrough.tex` abre el complementario
con tres apéndices: guía del método actual, cálculos y ejemplos, y escenarios
de simulación. La derivación de amplitud, la actualización de estado y los
detalles numéricos de configuración se trasladaron desde el método principal.
El artículo conserva la integral y las limitaciones de la aproximación.
La derivación duplicada del apéndice histórico se sustituyó por una referencia
a su ubicación completa.

Los ejemplos escalares son ilustraciones verificadas, no nuevos experimentos.
H03/H04, C01, E_i/X02, X04 y el banco histórico mantienen contratos distintos.
C01 no se convierte en un resultado terminado por compilar este documento.
F01 conserva su condición de candidato de investigación y la hipótesis
provisional BUS5 5–6. No se ejecutaron simulaciones ni se abrió RAW0002.

## Compilación y recuperación

Desde la raíz de P07:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_manuscript_bundle.ps1
```

El comando compila ambos documentos con bibliografía y referencias, verifica
las figuras protegidas, publica los PDF independientes y crea la copia conjunta.
Los dos nombres largos de entrega anteriores se mantienen como alias actualizados.
El comportamiento predeterminado ya no regenera artefactos científicos ni
importa resultados. `-RefreshArtifacts` conserva ese trabajo como operación
explícita y separada. Las instrucciones manuales están en el README.

Las fuentes previas siguen en Git, en `613ed39`; la copia de trabajo anterior
a esta edición también quedó en `build/recovery_documents_20261031/before/`.
No se revirtieron revisiones científicas posteriores a la antigua separación.

## Comprobaciones

- Compilación de ambos documentos con pdfLaTeX/BibTeX y revisión de referencias.
- Compilación adicional en una copia de fuentes sin auxiliares ni PDF raíz previos.
- Integración numérica independiente de la verosimilitud y la media truncada;
  comprobación de los ejemplos de recuperación y cambio de pesos.
- Hashes de las 16 copias protegidas y presencia de las dos figuras en el artículo.
- Igualdad del texto de cada página del PDF conjunto con su documento de origen.
- Revisión visual mediante páginas renderizadas; ajuste de saltos de línea y
  de espacios para no extender el artículo innecesariamente.
- Figuras, tablas, resultados congelados, bibliografía y autoría sin cambios.

Los logs, la copia de compilación limpia y el manifiesto de los PDF están bajo
`build/`. Los avisos de tipografía y cajas de la clase IEEE Access se distinguen
de errores o referencias sin resolver. Compilar no valida por sí mismo las
conclusiones científicas ni repara el compilador automático del editor.
