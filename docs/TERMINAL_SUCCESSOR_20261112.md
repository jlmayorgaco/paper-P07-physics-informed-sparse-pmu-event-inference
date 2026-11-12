# Terminal successor 2026-11-12

## Scope

Successor aislado del prototipo estático externo, para corregir únicamente la orientación de las corrientes terminales y recomputar sus salidas estáticas. No forma parte de P07 como resultado, no usa SGSMA/F01, no cambia el modelo público, C03 ni su TEST. Se conserva el supuesto de MATPOWER case39, las 8 barras PMU, 18 hipótesis y la selección determinista de la primera rama incidente declarada en el script. ZIP fuente conservado en Downloads; SHA-256: `c19f7ed78d3b60bf05e50c6319ba6d196a6b1a43f9141c43b0a6188d1288f048`.

## Correcciones implementadas

- Para cada canal se conserva la rama física elegida en el caso base y se registra si la PMU está en FROM o TO. En las 7/8 PMU en TO se calcula la corriente local en ese extremo. Se usa el circuito pi completo: `I_f=((y+jB/2)/a²)V_f-(y/a)V_t`; `I_t=-(y/a)V_f+(y+jB/2)V_t`.
- Al abrir una rama se conserva su canal/índice, con corriente cero en esa rama; no se desplazan índices para que otro circuito ocupe accidentalmente ese canal.
- H de rango usa las filas de tensión PMU y las filas terminales correctas. Su rango complejo continúa siendo 14/39 en esta idealización. Esto no implica observabilidad dinámica ni un déficit del estimador P07.
- La desviación base hipotética de corriente se vuelve a calcular como `max(0.002, 0.002*abs(I_base_correcta))`. Es un supuesto sintético, no calibración de sensores PMU reales.

## Validación

`validate_successor.py` contrasta ambos sellos de cada una de las 46 ramas con fórmulas escalares independientes, incluyendo transformadores con tap y carga shunt; error máximo absoluto `5.69e-14`. También valida KCL en los 39 buses, selección en el bus local, los 7 terminales TO, y abre individualmente las 8 ramas seleccionadas: los canales afectados dan cero y los demás coinciden con la fórmula local independiente. El ZIP y la igualdad de matrices de ruido con seed 261112 se comprueban programáticamente. Valida además el ensamblado/rango de H y la escala de ruido recalculada.

Los dos prototipos se ejecutaron con el mismo generador y matriz de ruido (seed 261112, 18x150x32). El script original escribe en `original_results/`; el corregido, en `results/`. El archivo `results/validation_comparison.json` contiene la comparación numérica. Exactitud V permanece 89.96%, 68.44%, 40.15%. Exactitud V+I pasa de 95.63%, 85.56%, 64.85% a 95.67%, 85.67%, 64.44% para escalas 1, 5 y 20. Mediana del coseno más cercano V+I: 0.81281 a 0.80587; máximo: 0.98810 a 0.98799. El cambio en este experimento acotado es pequeño; no justifica atribuciones amplias ni afirmaciones sobre rendimiento físico.

## Reproducción

Desde esta carpeta y con NumPy/Matplotlib/SciPy disponibles:

```powershell
python -B run_original.py
python -B run_corrected.py
python -B validate_successor.py
```

Los tres comandos se ejecutan en secuencia, sin mover salidas. `run_original.py` solo difiere del código fuente extraído en la ruta local de salida (`original_results/`); el manifiesto registra ese cambio explícito. La validación importa el script corregido y reproduce su cómputo antes de las aserciones. `manifest.json` registra SHA-256 de entradas, código y resultados.
