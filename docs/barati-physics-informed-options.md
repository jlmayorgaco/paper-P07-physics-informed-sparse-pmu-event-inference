# Qué aprender de la trayectoria de Masoud Barati para cerrar P07

Se revisó al investigador de **ingeniería eléctrica de University of Pittsburgh**, no al homónimo de informática de Carleton. Fuentes institucionales: [Pitt Engineering](https://www.engineering.pitt.edu/people/faculty/masoud-barati/) y [Pittsburgh Quantum Institute](https://www.pqi.org/people/masoud-barati). Esto identifica líneas de investigación; no presume sus preferencias editoriales ni aprobación del manuscrito.

## Trayectoria relevante, no un inventario de prestigio

| Línea/documento | Qué está verificado | Lección concreta para P07 |
|---|---|---|
| Localización de fallas de distribución mediante CNN, Zhao/Barati, TIA 2021, DOI 10.1109/TIA.2021.3083645 | Registro institucional y tarea; no se hizo auditoría completa del texto | La localización aprendida ya es una línea madura. Cambiar ExtraTrees por una red más grande no distingue nuestro aporte. |
| Kernel estocástico, Barati/Ensaf/Hosseini KPEC 2023, DOI 10.1109/KPEC58008.2023.10215450; Ensaf/Barati arXiv:2309.10200 | Texto completo del segundo: SDE, inferencia de drift/difusión y regresión kernel, Sections II-III | La incertidumbre debe tener un origen físico y una tarea concreta. Estimar estados y atribuir eventos siguen siendo problemas distintos. |
| ACPF con NR/GD/grafos computacionales, arXiv:2406.10390; registro TIA 2025 DOI 10.1109/TIA.2025.3571862 | Texto completo arXiv; registro institucional de la publicación posterior. No se supone identidad entre versiones | Hacer explícitas las restricciones AC y las derivadas ayuda a dar sentido físico al estimador. R11 ya usa sensibilidad DAE; no hay motivo para sustituir el solver durante C01. |
| Inercia con GAT-LSTM, Albeladi/Basulaiman/Barati, TIA 2026, DOI 10.1109/TIA.2025.3618779 | Registro institucional y resumen primario del preprint; no auditoría completa de ecuaciones | Frecuencia/ROCOF y estructura espacial importan, pero inferir inercia no equivale a detectar el bus de una intervención. No se justifica añadir GAT a P07 sin ensayo propio. |

El hilo útil es **formulación matemática + estructura de la red + incertidumbre con propósito + comparación que pruebe una capacidad**. La teoría de categorías, computación cuántica o una arquitectura neural no se incorporan por asociación con la trayectoria de un coautor.

## Recomendación para el paper que queremos terminar

La mejora inmediata de la parte physics-informed es explicar con precisión lo que el código ya hace: las ecuaciones DAE generan la respuesta; el operador de línea modifica topología y corrientes de terminal; la carga modifica P/Q; el estado persiste después de OFF; el filtro y las hipótesis comparan esa recuperación con nuevos eventos. Se añadió esa explicación al método y se citan sus precedentes.

No recomiendo cambiar ahora R11 por PINN/GNN/GP. Crearía un método sin la evidencia confirmatoria que estamos terminando y desplazaría de nuevo el cierre. Esta decisión no equivale a afirmar que esas familias sean inferiores.

## Extensión más coherente si después decidimos hacer otro estudio

Sería una **incertidumbre de predicción derivada de física**, condicionada a cada historia, que distinga parámetros constantes, forzamientos ambientales e instrumento. Tiene antecedentes en GPR físico y en inferencia DAE; no sería novedosa por añadir un kernel.

Para ilustrar el requisito matemático, en una linealización local el residuo puede expresarse como

\[
r_W=s_h(a,\tau,\kappa)+J_{\theta,W}\delta\theta+G_Ww+\epsilon_W.
\]

Si los términos son Gaussianos, independientes bajo las hipótesis declaradas y con covarianzas conocidas, la covarianza marginal estándar sería

\[
\Sigma_W=R_{\mathrm{instr},W}
 +J_{\theta,W}P_\theta J_{\theta,W}^{\top}
 +G_WQG_W^{\top}.
\]

Un parámetro R/X constante crea correlación entre tiempos: no se reemplaza por ruido blanco nuevo en cada trama. Un forzamiento ambiente de carga puede parecerse al evento que se intenta reconocer; una covarianza arbitrariamente grande puede ocultarlo. Serían necesarias identificabilidad, restricciones físicas y validación de cobertura/tasa de falsas alarmas, no solo menor RMSE.

Esta expresión es una marginalización Gaussiana conocida, **no código nuevo, no un aporte ya demostrado y no un cambio en C01**. R11 conserva su mezcla finita y sus estimaciones startup por sustitución. La extensión queda fuera de las contribuciones del artículo actual.

Referentes primarios: [Ensaf/Barati](https://arxiv.org/abs/2309.10200), [Tartakovsky et al.](https://doi.org/10.1016/j.ijforecast.2022.03.007) y [Alalem Albustami et al.](https://arxiv.org/abs/2604.15686). La presencia de esos antecedentes obliga a formular una diferencia específica, no a vender "Bayes + física" como nuevo.

## Decisión final

Cerrar el artículo de **atribución con recuperación** con R11/nominal y C01. Usar esta revisión para afinar la contribución y discutir sus límites. No añadir otra versión de método ni otra campaña para corregir fuentes concretas.
