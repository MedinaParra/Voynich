# 53. Copia de lectura por bifolios: protocolo

Fecha: 26-10-2026. Estado inicial: NOT_RUN.

El usuario solicita continuar la investigación y reordenar páginas. Se prepara una copia digital hipotética, no una restauración del orden histórico. Los ensayos previos [28](28_resultado_singulion_q13.md), [44](44_q13_matching_control.md) y [45](45_conjoint_leaf_replication.md) no validaron la secuencia publicada ni una coherencia residual robusta. Esos resultados no se borran.

Se consideran los cinco bifolios de Q13 y los cuatro bifolios del núcleo homogéneo de Q20 ya seleccionados por metadatos. Los dos bifolios de borde de Q20, las demás secciones, los desplegables y las cubiertas mantienen su posición. Cada bifolio seleccionado se lee en orientación fija `ar, av, br, bv`; no se inventan hojas perdidas ni se ensayan inversiones internas.

Para cada página se alternan loci de párrafo: mitad de selección y mitad de comprobación. El vocabulario y el IDF se aprenden por hoja física fuera de Q13 y Q20. Se elige una única permutación por coseno TF-IDF entre extremos de bloques, agotando 120 y 24 órdenes posibles. Los empates eligen el orden lexicográfico mínimo. Después se comprueba esa misma selección en las otras líneas y se informa sensibilidad por trigramas. No se cambia de candidato al ver la comprobación.

Q13 tiene un criterio diagnóstico de p exacto inclusivo <=0,05 y mejora del promedio de adyacencias frente al orden actual. Q20 es descriptivo. Las mitades proceden de páginas ya exploradas y no son evidencia codicológica independiente; incluso un resultado favorable no demuestra el orden original. La etiqueta de la copia será siempre `ORDEN EXPERIMENTAL - NO VALIDADO HISTÓRICAMENTE`.

La copia preserva las 213 imágenes del inventario congelado y cada identificador de folio. Sólo reemplaza los 20 lugares de Q13 y los 16 del núcleo Q20. Se guardan la lista original, la propuesta, los enlaces de imagen y las puntuaciones de todas las alternativas. Si falla un control de integridad no se entrega una copia como íntegra.

Fuentes: [Layfield y Davis, Digital Medievalist 2026](https://doi.org/10.4000/16k0a), corpus ZL congelado y metadatos físicos de nuestros ensayos anteriores. El inventario de imágenes externo sólo aporta identificadores y URLs, nunca sus etiquetas semánticas.

[Plan completo](data/reordering_plan.json). Traducción: NOT_RUN. Orden histórico: UNRESOLVED.
