# 84 — Un adversario de fronteras, antes de elegir una explicación

3 de noviembre de2026. Base `1478edb3000b0f0d91babd1fda3cddf52d454f0c`. [Plan completo](data/boundary_adversary_plan.json).

La prueba elegida conserva las letras y deja variar todas las fronteras discutibles entre VT yZL. Se utilizarán los98loci de letras proyectadas iguales del informe81. La inspección de factibilidad, sin medir la señal, encontró49posiciones binarias y170segmentaciones locales. Las combinaciones globales son2^49. Esta familia híbrida es una prueba de estrés amplia; las fuentes no certifican que cada combinación sea una lectura correcta o equiprobable.

Se fijan fronteras compartidas y ciertas. Las restantes posiciones anotadas son opcionales. Para cada segmentación se calcula semejanza local de grupos vecinos por edición≤1, con longitud mínima3, quitando primero/último grupo. La señal se centra contra la media de todos los pares interiores: bajo permutación uniforme del multiconjunto interior, su esperanza es0. La suma por locus usa fracciones exactas.

Se calcularán mínimos y máximos exactos con presupuestos de0,1,2,4,8 ytodos los cambios de frontera respecto deVT, con segmentaciones testigo. El radio de fragilidad es el menor coste que permite una señal no positiva; siVTya no es positiva será0. No es una probabilidad paleográfica.

Se conservarán999permutaciones interiores paraVT y una envolvente que domina las colas simuladas de cualquier combinación fija. El máximo por locus se toma también en contra de nuestra conclusión. La fórmula más-uno evita colas de MonteCarlo iguales a0. Esta cota condicional no es un p-valor universal: el corpus y la familia de anotación se construyeron observando el mismo texto.

Antes se ejecutarán cuatro controles: copia/modificación y el mismo multiconjunto reordenado, con/sin una frontera interna opcional por cada dos líneas. Los umbrales y semillas quedan en el plan. Son ejemplos de calibración; no estiman potencia o error deTipoI en una población. Si fallan, no se promoverá una interpretación del manuscrito.

El repositorio ya estudió vecindad, comas y copia en17/19, y otros trabajos ya borran separadores. El aporte nuevo aquí es el certificado adversarial exacto y la perturbación mínima, no volver a descubrir semejanza local. Tampoco esta señal identifica una clave: se conservará su invariancia ante sustitución biyectiva y reversión. No se alteran etiquetas propuestas en83, ni se ejecutanOCR, entrenamiento o traducción.
