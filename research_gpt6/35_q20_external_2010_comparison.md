# 35. Q20 — comparación externa con Pelling (2010)

Fecha: 2026-10-07
Estado: comparación histórica exploratoria, no validación confirmatoria.

Nick Pelling propuso en 2010, de forma tentativa, un núcleo Q20 con orden de bifolios equivalente a:

`105|114 → 106|113 → 107|112 → 108|111 → 104|115`

El candidato derivado en nuestra rama, restringido al mismo núcleo de cinco bifolios, es:

`105|114 → 106|113 → 107|112 → 104|115 → 108|111`

El orden físico actual del mismo núcleo es:

`104|115 → 105|114 → 106|113 → 107|112 → 108|111`

## Comparación

Contra la propuesta de Pelling:

- nuestro candidato: distancia Kendall = **1/10** inversiones posibles;
- orden físico actual: distancia Kendall = **4/10**;
- ambos comparten 3/4 adyacencias no dirigidas con Pelling, por lo que el solapamiento de aristas por sí solo no discrimina;
- la diferencia informativa es el orden dirigido: nuestro candidato es una sola transposición adyacente del núcleo de Pelling.

Entre las 120 permutaciones dirigidas de cinco unidades, sólo 5 tienen distancia Kendall <= 1 respecto de Pelling (5/120 = 0.0417). Este valor es **descriptivo y post-hoc**, no un p-value confirmatorio, porque la comparación externa se examinó después de obtener nuestro candidato.

Pelling además trató `103|116` como bifolio estructuralmente distinto / posiblemente añadido por fuera, mientras nuestro modelo lo ubica como cierre. Por tanto la convergencia es parcial, no una réplica exacta.
