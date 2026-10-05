# 03 — Gramática posicional

**Estado: PASS parcial** para la asociación entre glifo y posición; **NOT_RUN** para CLAVIS CODICIS o gramática de cinco slots.

La MI entre identidad del glifo y posición inicio/medio/final es 0.657811 bits. El resultado resiste dos alternativas de tratamiento de palabras singleton y excede el nulo de permutaciones dentro de palabra (999 permutaciones, seed 20261005; p empírico unilateral 0.001). Consulte `results/position_reproduction.json`.

Este test solo muestra que los glifos no se distribuyen al azar dentro de las palabras observadas. No comprueba la asignación DOMINIUM → GENUS → SPECIES → CORPUS → FINIS. Para contrastar esa propuesta haría falta congelar la codificación, comparar 2–8+ slots con penalización de complejidad y validación por folios completos reservados, e incluir modelos sin slots y controles generativos equivalentes. Eso no se ejecutó.
