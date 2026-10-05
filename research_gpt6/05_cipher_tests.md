# 05 — Criptoanálisis

**Estado: PASS parcial** para auditar los resultados guardados de una búsqueda de anclas zodiacales; **NOT_RUN** para rerun independiente, descifrado fuera de muestra y ataques criptográficos completos.

El notebook fuente `28_zodiac_cribs.ipynb` guarda tres búsquedas de nombres zodiacales hebreos/arameos. Reporta p Monte Carlo de **0.6103**, **0.8066** y **0.7713**; ninguna supera su nulo. El mejor ajuste hallado mapea cinco signos y 17 glifos, pero se selecciona entre muchos candidatos de las mismas páginas, así que no es una traducción validada.

La comparación posterior de bigramas hebreos guarda 9.581/9.582 válidos y z=1.54, null=75.3% ±16.1%, percentile=0.1%. La celda calcula el porcentaje como `mean([1 for x in null_rates if observed > x]) / N * 100`: para cualquier cantidad positiva de permutaciones bajo lo observado, `mean(...)` vale 1 y el resultado queda fijo en 0.1% con N=1000. Por tanto el percentil guardado no es válido. La aproximación normal de z=1.54 ubica la observación cerca del percentil 93.8 (cola superior ~6.2%), pero **no sustituye** el percentil empírico ni corrige la selección de la clave, la dependencia entre pares o el nulo aleatorio simple.

Auditoría reproducible de fuente y aritmética: `code/audit_zodiac_crib.py`; salida: `results/zodiac_crib_audit.json`. Lee outputs guardados y revisa el código; no vuelve a ejecutar el análisis hebreo/Torá.

También se probó el crib directamente fuera de muestra. En cada pliegue se reservaron todas las etiquetas de un signo; una correspondencia glifo→letra se ajustó con las etiquetas de los otros nueve signos y se congeló antes de buscar el nombre hebreo/arameo esperado en las etiquetas reservadas. Resultado: **0 aciertos exactos en 10 signos**; solo 29.3% de las etiquetas reservadas se podían descifrar completas con la clave entrenada. En 1,000 permutaciones de la asignación signo-página, el promedio fue 0.002 aciertos por signo y el máximo 1; p de cola para el resultado observado de cero = 1.0. Este test acota la hipótesis de un nombre zodiacal literal bajo sustitución homofónica 1-glifo→1-letra; no excluye nombres en texto circular, otra ortografía o un código distinto. Código: `code/zodiac_crib_holdout.py`; salida: `results/zodiac_crib_holdout.json`.

Pendiente comparar sustitución simple, homofónica, polialfabética, transposición, nomenclátor, códigos silábicos/morfémicos, abreviaturas, escritura consonántica/fonética, cifrado verbose, código posicional y sistemas combinatorios. Para cada familia se congelarán modelo, presupuesto de búsqueda, semillas y métrica; la evaluación será en folios completos que no participaron en selección ni entrenamiento.

La documentación del repo dice que sus controles Caesar/Vigenère difieren de ciertas métricas Voynich; incluso si se reproduce, ello solo evalúa esas implementaciones y fuentes concretas.
