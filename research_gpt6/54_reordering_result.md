# 54. Reordenación digital parcial: Q13 y núcleo de Q20

Fecha: 26-10-2026. Rama: `experiment/kraken-voynich`.

Se construyó una copia de lectura con una secuencia experimental por bifolios. **La comprobación textual no validó el orden seleccionado. No es una reconstrucción demostrada del manuscrito ni una traducción.** El PDF conserva el identificador de cada folio, la posición de origen, marcadores de navegación y un índice completo para revertir la propuesta.

## Protocolo y selección

El [protocolo 53](53_reordering_protocol.md) y el [plan](data/reordering_plan.json) se fijaron antes de medir los resultados en `f35af8057b36c9ed2cedef979db1ed492b5c50bf`. La implementación del análisis se publicó en `b8a6c1b80b89a9b70239505fc72cfb4eadff686f`.

Se mantuvo la orientación interna `ar, av, br, bv` de cada bifolio. Las líneas de cada página se dividieron por alternancia entre selección y comprobación. El IDF y el vocabulario se aprendieron en 77 hojas externas a Q13/Q20, con 4.139 formas literales. No se suministraron al IDF las hojas de los grupos que se reordenaron.

Se agotaron las 120 permutaciones de los cinco bifolios de Q13 y las 24 del núcleo de cuatro bifolios de Q20. La elección maximiza el coseno TF-IDF entre el final de un bloque y el inicio del siguiente en las líneas de selección. Se comprobó después esa misma elección en las otras líneas; no se cambió por una alternativa con mejor puntuación de comprobación.

El corpus y las páginas ya habían sido explorados. Las dos mitades de una página son dependientes, por lo que esta división no equivale a una validación histórica externa. Los [resultados anteriores](28_resultado_singulion_q13.md) y los controles [44](44_q13_matching_control.md) y [45](45_conjoint_leaf_replication.md) se conservan y no quedan sustituidos por este experimento.

## Secuencias de la copia

La notación `78|81` identifica las dos hojas de un bifolio; en la copia se leen sus cuatro caras `78r, 78v, 81r, 81v`.

| Ámbito | Secuencia seleccionada en la mitad de selección |
|---|---|
| Q13 | `78|81 → 79|80 → 75|84 → 76|83 → 77|82` |
| Núcleo Q20 | `108|111 → 106|113 → 107|112 → 105|114` |

En Q20 los bifolios de borde `103|116` y `104|115` mantienen sus posiciones. No se afirma haber reconstruido el orden de todo Q20. Las demás secciones, cubiertas y desplegables mantienen su lugar en el inventario fotográfico. Los desplegables se conservan como capturas completas, sin dividir sus paneles.

## Comprobación: la elección no resulta excepcional

| Grupo | Coseno en los límites de bloque | Rango en comprobación | Cola exacta inclusiva | Decisión |
|---|---:|---:|---:|---|
| Q13 | 0,498227 | 32 / 120 | 0,2667 | NOT_SUPPORTED_IN_LINE_SPLIT |
| Núcleo Q20 | 0,341054 | 6 / 24 | 0,2500 | DESCRIPTIVE_ONLY |

La sensibilidad por trigramas de caracteres sitúa la misma elección de Q13 en el rango 91/120 y la de Q20 en 2/24. No se eligió Q20 por esa sensibilidad: su elección primaria sigue siendo la del TF-IDF de selección. La cola exacta por trigramas de Q20 es 0,0833, tampoco una validación histórica.

El promedio de todas las adyacencias de las páginas pasa de 0,485903 a 0,505627 en Q13 y de 0,377575 a 0,377704 en el núcleo Q20. Esa mejora descriptiva no basta: dentro del espacio de órdenes permitidos, muchas alternativas también obtienen puntuaciones iguales o mayores en la comprobación. La similitud de vocabulario no establece continuidad de significado.

Como referencia previa, el orden Q13 atribuido a Layfield-Davis queda en el rango 59/120 en esta partición concreta. Este número no debe confundirse con el 39/120 del ensayo anterior, que empleaba otra representación/partición. No hemos refutado por ello toda su hipótesis codicológica.

## Copia fotográfica y alcance material

El inventario congelado contiene **213 posiciones**. Se mantuvieron todas sus identidades una sola vez. Cambian **32 posiciones**: 20 en Q13 y 12 en el núcleo Q20. Cuatro imágenes del núcleo Q20 coinciden con su posición de origen, aunque formen parte de los bloques evaluados. Ninguna posición fuera de los dos ámbitos se modificó.

Se recuperaron **211 fotografías**. Yale respondió HTTP 403 para `[Head]` y `[Tail]`, dos fotografías no textuales de los cantos de la encuadernación. Sus dos posiciones contienen avisos explícitos. Todas las imágenes de los grupos reordenados están disponibles. La adquisición detectó esos fallos y no se etiquetó como una recuperación íntegra de 213 fotografías.

El PDF tiene **219 páginas**: portada, guía, 213 posiciones de lectura y cuatro páginas de índice. Contiene 211 fotografías y dos avisos. Es una copia de consulta con imágenes remuestreadas y comprimidas, sin recorte ni giro. Se conserva el contenido completo de cada captura disponible. Las hojas históricamente perdidas no se recrean.

Nombre del archivo: `Voynich_Lectura_Experimental_2026-10-26.pdf`. El archivo descargable se entrega en la conversación; el repositorio publica los índices, el análisis y el código necesario para regenerarlo, sin duplicar todo el PDF y su caché de fotografías.

El orden de origen corresponde al inventario publicado y congelado de 213 capturas, no a un nuevo manifiesto canónico recuperado de Yale durante este ensayo. Sólo se utilizan sus identificadores de folio, canvas y servicio de imagen; no se adoptan las etiquetas semánticas del repositorio externo.

## Verificación

- Ocho controles del código: cadena sintética, empates sin evidencia, número de alternativas, orientación, separación de líneas, IDF externo, integridad de imágenes y objetivos ausentes/duplicados.
- [Auditoría de 2.133 comprobaciones](results/reordering/audit.json), sin discrepancias: rangos, elección, identificadores, posiciones originales y datos del PDF.
- Los bytes JPEG de las **211 imágenes incrustadas** coinciden con los activos de lectura registrados. Las dos posiciones sin fotografía contienen el aviso requerido y ninguna imagen inventada.
- Revisión visual de portada, guía, una página de Q13, un desplegable, un aviso de acceso no disponible y el índice. No se detectaron recortes de texto, solapamientos ni omisiones en esas muestras.

La ejecución fue local en Python, no una nueva ejecución de reconocimiento en GitHub Actions. Las verificaciones acreditan el proceso y la integridad de la copia; no acreditan la secuencia histórica.

## Archivos y reproducción

[Resultado completo y todas las permutaciones](results/reordering/reordering_result.json), [índice propuesto](results/reordering/reading_manifest.json), [orden CSV](results/reordering/reading_order.csv), [correspondencias con páginas PDF](results/reordering/reading_order_with_pdf.csv), [recibos públicos de imágenes](results/reordering/image_receipts_public.json), [procedencia de la copia](results/reordering/reader_provenance.json) y [portada](results/reordering/reader_cover.jpg).

Código: [análisis](code/reorder_bifolio_reading.py), [adquisición de imágenes](code/acquire_reading_scans.py), [preparación de consulta](code/prepare_reading_assets.py), [generador PDF](code/build_reordered_reading_pdf.py) y [auditoría](code/audit_reordered_reading.py).

Fuentes fijadas: corpus ZL EVA v3b del commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278` de `cesarjz/Voynich`, SHA-256 `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`; inventario literal de imágenes del commit `d4b31a245ba8133b727dc4255278b5e8349bbe39` de `xenoglyph-ai/voynich-public`; fotografías públicas IIIF de Yale, Beinecke MS 408. Referencia codicológica: [Layfield y Davis, 2026](https://doi.org/10.4000/16k0a).

## Decisión

Se entrega la reordenación como herramienta para inspeccionar una hipótesis, manteniendo su resultado negativo. No se utilizará esta secuencia como si hubiera quedado demostrada para traducir el texto. Para avanzar en el orden histórico se necesita evidencia adicional e independiente, especialmente del soporte físico, la continuidad de ilustraciones y las marcas materiales.

Orden histórico: **UNRESOLVED**. Traducción: **NOT_RUN**.
