# Fuentes, formatos y límites

- Fotografías: Yale University Library, Beinecke MS 408. Las URL oficiales, identificadores de canvas y SHA-256 de f8r/f8v se conservan en el plan y los recibos de adquisición. Los recortes anteriores proceden de las fotografías ya preservadas en el repositorio.
- Textos y cajas: Voynichese Project. Los XML conservan el aviso Apache License 2.0; documentación de origen en https://github.com/voynichese/voynichese/blob/wiki/DataSets.md. No son nuevas lecturas paleográficas ni una referencia experta independiente.
- Código `runs/*/sources/kraken_augment.py`: copia sin cambios del módulo instalado de Kraken 7.1, con su aviso Apache 2.0. Texto de esa licencia disponible también en [el archivo ya conservado](../voynichese_registration/inputs/APACHE-2.0.txt).
- Código nuevo de intervención, entrenamiento, evaluación y auditoría: este proyecto. La intervención no importa glifos generados, glosas latinas o etiquetas de otros recursos reseñados.

Las máscaras seleccionadas de entrenamiento se conservan como **ZIP sin pérdida de los PNG originales**, con los hashes originales en `perturbation_records.json(.gz)` y un inventario del artefacto completo. La envoltura ZIP se creó después del ajuste; no cambió ninguna entrada de entrenamiento. Los ficheros marcados como `best` en el artefacto temporal no seleccionaron el resultado y sólo se conservan en el inventario; se preservan los checkpoints finales y sus modelos convertidos.

Las 884 imágenes derivadas por condición no se duplican en Git. Sus bytes y textos se reconstruyen a partir de fotografías, geometría, selección y receta fijadas; la auditoría verificó todos sus hashes. Los 265 recortes nuevos tampoco se duplican: sus fotografías, polígonos, máscaras reconstruibles y etiquetas completas sí están conservados. El helper de restauración requiere Pillow 12.3.0 para recuperar los mismos bytes PNG.

Los JSON grandes usan `.json.gz` y un inventario de hashes de los bytes originales. Los lectores de auditoría admiten ambos formatos. Los NPZ contienen matrices NumPy y se leen con `allow_pickle=False`. El auditor obtiene los contadores literales iniciales de checkpoints Lightning inspeccionando opcodes, sin ejecutar pickle ni cargar Torch.

Todos los indicadores de exactitud se refieren a las referencias EVA candidatas. Regiones compartidas no significan tinta ajena certificada; palabras exactas no significan traducciones. Revisión experta nueva e identificación de lengua: **NOT_RUN**.
