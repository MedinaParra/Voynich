# Actualización del estado del arte: evidencia nueva de 2026

**Corte: 6 de octubre de 2026.** Esta nota complementa [el estado del arte general](11_estado_del_arte.md). Distingue artículos revisados, preprints y propuestas independientes; un resultado estadístico no constituye por sí mismo una lectura del manuscrito.

## 1. Unidad de análisis: glifos, grupos y espacios

Rozanova y Temerev, [*A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space*](https://arxiv.org/abs/2608.17096), preprint arXiv presentado el 17 de agosto de 2026, prueban las suposiciones habituales sobre glifo, palabra y espacio con prosa, cifrados y pseudo-textos de control, además de remuestreo por cuaderno. Informan que la identidad de un grupo separado por espacios predice menos del 1% de su entropía en la posición siguiente, mientras la asociación entre glifos en bordes de grupo es más marcada; también encuentran separadores de anchura física distinta.

**Lectura crítica:** estos son resultados del preprint, aún pendientes de una reproducción independiente con el mismo corpus, tokenizador, controles y unidades físicas. El número de MI depende de cómo se normalicen transliteraciones, alternativas editoriales, espacios y casos raros. Una baja dependencia entre grupos no descarta estructura dentro de grupos ni informa por sí sola si el texto tiene significado.

Esto no contradice directamente la prueba de esta rama que predice glifos con una n-grama: esa prueba mide predictibilidad de secuencias de glifos en la transcripción fijada. No prueba que un glifo sea letra, que un grupo sea palabra o que el texto sea lenguaje. El resultado nuevo sí exige ampliar el análisis: comparar secuencias de glifos, grupos convencionales, bordes y espacios físicos con particiones reservadas por cuaderno.

## 2. Nueva cuantificación de Currier A/B

Parisel, [*A Quantitative Confirmation of the Currier Language Distinction*](https://arxiv.org/abs/2604.25979), preprint v2 de mayo de 2026, informa que una mezcla beta-binomial selecciona dos grupos sin recibir las etiquetas Currier y predice etiquetas retenidas al 89%. El artículo propone además un conmutador binario por folio relacionado con la vocal que sigue a los dígrafos ch y sh, y un sistema de plantillas con contextos fijos y variables.

El artículo presenta código para verificación independiente, pero el resumen y la fuente arXiv no proporcionan un resultado de reproducción de esta rama. A/B sigue siendo una distinción estadística; el modelo de conmutador es una explicación propuesta, no una traducción ni una identificación de dos idiomas. La réplica debe congelar la transcripción, reconstruir la asignación de folios, y separar selección de variables y evaluación fuera de muestra.

## 3. Rectificación de una lectura latina

Matthew Owens actualizó en julio de 2026 su preprint [*Voynichese Has Natural-Language-Range Character Entropy but Anomalous Order-Scaling*](https://doi.org/10.17613/asz1z-nax02). La versión 2 retira la afirmación de desciframiento en latín abreviado: el resultado χ²=41.56 comparaba con un nulo uniforme inadecuado; al usar los conteos reales, informa aproximadamente 358, que no respalda la lectura latina. Es una corrección del propio autor en un preprint, no una retractación editorial de un artículo revisado.

**Implicación:** los cribados deben comparar contra distribuciones nulas que preserven las frecuencias observadas y deben penalizar la búsqueda entre alfabetos, segmentaciones y convenciones. Una coincidencia contra un nulo artificialmente simple no cuenta como evidencia de desciframiento.

## 4. Revisión de la señal zodiacal publicada por Averyanov

En su [estudio de las etiquetas zodiacales](https://voynich.site/paper-2-labels?lang=en), Averyanov mantiene que un vector de atributos codificado a ciegas se asocia con el sexo asignado a grados zodiacales bajo un desplazamiento 23 (52/78; p=0.0088, segunda ronda). La página actual del mismo investigador matiza la lectura: la señal puede representar una partición gruesa de 15 + 15 figuras (60/78; p=0.024); la prueba no selecciona de forma única la tabla de al-Biruni, y la versión latina medieval candidata rinde peor. La interpretación actual es una partición clara/oscura, no una identificación demostrada de nombres por grado.

Es una propuesta independiente autocorregida y no revisada por pares. No es réplica de nuestra prueba hebreo/aramea: se usan atributos visuales, alineamiento circular y una fuente externa diferentes. La coincidencia no descifra las etiquetas ni el texto corrido.

## Estado y siguiente prueba

Estos trabajos refinan las restricciones estadísticas, pero ninguno ofrece una lectura integral reproducida de forma independiente. El resultado más sólido de este repositorio sigue siendo predictivo: la secuencia de glifos contiene regularidad que generaliza a folios y cuadernos reservados. Su significado continúa abierto.

La siguiente réplica de esta rama debe:

1. Fijar corpus, revisión de transliteración, identificadores de líneas, manos y cuadernos.
2. Medir por separado dependencia de glifos, de grupos entre espacios, de bordes de grupo y de espacios físicos.
3. Comparar el orden observado con permutaciones dentro de línea que mantengan frecuencias, y reportar entropía/MI normalizadas, intervalos por cuaderno y todos los controles.
4. Repetir con una segunda transcripción pública y un conjunto de controles emparejados antes de interpretar unidades.
5. Evaluar cualquier clave semántica nueva en folios y etiquetas no usados para proponerla, incluyendo corrección por todas las alineaciones o candidatos probados.

Hasta completar estas pruebas, no se debe promover ninguna de estas hipótesis a «desciframiento».
