# 03 — Gramática posicional

**Estado: PASS parcial** para la asociación entre glifo y posición y para predicción posicional fuera de muestra; **NOT_RUN** para CLAVIS CODICIS o la gramática semántica propuesta de cinco slots.

La MI entre identidad del glifo y posición inicio/medio/final es 0.657811 bits. El resultado resiste dos alternativas de tratamiento de palabras singleton y excede el nulo de permutaciones dentro de palabra (999 permutaciones, seed 20261005; p empírico unilateral 0.001). Consulte `results/position_reproduction.json`.

Este test solo muestra que los glifos no se distribuyen al azar dentro de las palabras observadas. No comprueba la asignación DOMINIUM → GENUS → SPECIES → CORPUS → FINIS. Para contrastar esa propuesta haría falta congelar la codificación, comparar 2–8+ slots con penalización de complejidad y validación por folios completos reservados, e incluir modelos sin slots y controles generativos equivalentes. Eso no se ejecutó.

## Predicción en folios reservados

`results/heldout_prediction.json` evalúa modelos fijados de antemano en cinco pliegues por folio (semilla 20261005), con suavizado jerárquico Dirichlet (`alpha=1`). El modelo de dos glifos previos alcanzó 3.0051 bits/glifo, frente a 4.1488 para unigramas; ganancia de 1.1437 bits/glifo (IC bootstrap por folio 95%: 1.1030–1.1826). El modelo que usa solo la clase de posición (inicio/medio/final/singleton) alcanzó 3.4981 bits/glifo. Esto confirma que cierta estructura de secuencia y posición se generaliza a folios retenidos. No identifica palabras, referentes, idioma ni sistema de cifrado; los límites de palabra provienen de la transcripción STA1.
