# 21. De los catálogos a una muestra paleográfica

Fecha: 2026-10-06. Continuación del informe 20. Rama: `research/gpt6-audit`.

## Resultado concreto

Se recuperaron los metadatos primarios y los inventarios de imágenes de los dos herbarios seleccionados. Además se localizó y descargó para inspección una edición independiente de LJS 419 de 2026 con transcripciones propuestas. Esto abre una vía de extracción textual, pero todavía no proporciona un corpus validado ni una traducción del Voynich.

| Fuente recuperada | Resultado ejecutado | Qué permite |
|---|---|---|
| Penn LJS 419, catálogo OPenn y TEI | Catálogo: 205 imágenes web. XML: 615 elementos `graphic`, correspondientes a diferentes derivados; cero elementos TEI `text` | Localizar folios e imágenes; el TEI no es una transcripción |
| BL Add MS 41623, Codex Bellunensis, manifiesto IIIF v3 | 331 lienzos; se inspeccionó visualmente f. 35v | Acceso organizado a imágenes; no se confunde el número de lienzos con el de plantas o folios |
| Mamontov con Claude, edición independiente de LJS 419, 2026 | Metadatos de Archive.org y OCR de la edición descargados; portada y entradas seleccionadas inspeccionadas | Pistas para la lectura y navegación; no texto de referencia aprobado |

Los hashes SHA-256 de los metadatos primarios y sus inventarios se conservan en `data/historical_sources_manifest.json`. Las URL y hashes de las cuatro imágenes de Penn revisadas están en `data/ljs419_sample_transcription.json`. La procedencia del OCR independiente está en `data/independent_edition_provenance.json`. No se redistribuye el libro moderno completo.

## Lecturas realizadas antes de consultar la edición independiente

| LJS 419 | Lectura visual provisional | Estado |
|---|---|---|
| f. 1r | `Tormentilla` | Etiqueta provisional; nota inferior sin transcribir |
| f. 11r | Nombre incompleto e incierto | Excluido; no se rellena con una identificación botánica |
| f. 39v | `Herba mandragora maschio` | Lectura normalizada, con s larga convertida a s; sentido aproximado: mandrágora macho |
| f. 40r | Nombre incierto | Excluido |

La muestra fue elegida por conveniencia, no al azar. La revisión corresponde a una sola inspección visual por IA y no a una validación paleográfica independiente. Ninguna entrada está autorizada como texto de entrenamiento. En f. 39v se observa una raíz antropomorfa y un perro; esto describe la imagen y no demuestra una identificación botánica moderna ni un parentesco textual con el Voynich.

En Bellunensis f. 35v se ven dos plantas con etiquetas y una nota de varias líneas. No se incorporan lecturas inciertas de esa página. Dos solicitudes de imágenes BL con tamaño modificado devolvieron HTTP 403; se conserva la URL exacta anunciada en IIIF para futuras descargas. No se interpreta ese fallo como ausencia del manuscrito.

## Edición independiente: avance y límites

La portada atribuye la obra a P. Mamontov con Claude (Anthropic), 2026. Se presenta como edición de trabajo independiente y declara que no cuenta con aval institucional. Afirma ofrecer transcripción, traducción, identificaciones y grados de confianza por folio. Estas son declaraciones de la edición, no resultados confirmados por nuestra auditoría.

Las entradas consultadas coinciden con la etiqueta provisional de f. 1r y con la lectura normalizada de f. 39v. En f. 11r y f. 40r la propia edición mantiene dudas. El OCR introduce ruido, entremezcla texto histórico con traducción y comentario moderno y puede confundir la s larga con f. Coincidir en una etiqueta legible no valida todas las páginas. Consultar otra salida asistida por IA tampoco sustituye una segunda revisión paleográfica humana.

Por tanto, no se debe alimentar un clasificador con el OCR completo: aprendería inglés moderno, comentarios editoriales y ruido tipográfico además del texto manuscrito. Tampoco se deben convertir los nombres botánicos modernos propuestos por la edición en traducciones literales de etiquetas inciertas.

Para Bellunensis se localizó la referencia de la edición de Giordana Canova Mariani, *Codex Bellunensis: erbario bellunese del XV secolo*, facsímil y comentario, 2006. No se obtuvo ni examinó su texto completo; no se afirma que sea una transcripción digital utilizable.

## Hipótesis operativa y prueba siguiente

Se mantiene como prioridad un registro médico de latín medieval, italiano septentrional del XV o mezcla de ambos. Es una prioridad de comparación histórica, no una identificación del idioma del Voynich. La mezcla lingüística y los nombres de plantas difíciles justifican separar encabezamientos de notas de recetas al construir los controles.

Antes de ajustar una clave se necesita:

1. Extraer de la edición candidata solo las transcripciones, conservando folio, incertidumbre y la imagen que permite revisarlas; dejar fuera traducciones e identificaciones.
2. Contrastar cada lectura seleccionada con el facsímil. Conservar versiones diplomática y normalizada por separado; esta muestra aún no constituye una edición diplomática.
3. Reservar folios completos para evaluación y no usar sus ilustraciones para escoger equivalencias durante el ajuste.
4. Repetir las métricas del informe 19 con controles de género y época adecuados. Una coincidencia estadística no será evidencia suficiente de traducción.
5. Exigir una regla estable que produzca lecturas en páginas reservadas y supere controles negativos. Si no la hay, rechazar la clave propuesta.

No se ha ejecutado todavía esa comparación textual histórica. Este avance resuelve la localización y trazabilidad de fuentes; no resuelve el paso de signos EVA a palabras.

## Reproducción y derechos

Desde la raíz del repositorio:

```bash
python research_gpt6/code/acquire_historical_sources.py --out historical_sources
```

Se ejecutó el programa sobre los dos archivos ya descargados: confirmó 0 elementos TEI `text`, 615 `graphic` y 331 lienzos IIIF. El modo registrado fue `cache`; las adquisiciones originales se realizaron por HTTP y sus tamaños y hashes quedan en el inventario. No se afirma haber ejecutado esta rutina en un entorno sin caché. `--refresh` fuerza descarga; un archivo cambiado producirá un hash distinto.

Penn declara imágenes y contenido bajo Public Domain Mark y metadatos bajo CC BY 4.0. Atribución: Kislak Center for Special Collections, Rare Books and Manuscripts, University of Pennsylvania, Oversize LJS 419, OPenn. El manifiesto BL remite a su política de reutilización; no se presupone la misma licencia. No se incluyen binarios de imágenes en este commit.

## Fuentes consultadas

- [OPenn, LJS 419, catálogo](https://openn.library.upenn.edu/Data/0001/html/ljs419.html).
- [OPenn, TEI primario](https://openn.library.upenn.edu/Data/0001/ljs419/data/ljs419_TEI.xml).
- [BL, manifiesto IIIF del Bellunensis](https://bl.digirati.io/iiif/ark:/81055/vdc_100165149757.0x000001).
- [BL, catálogo Add MS 41623](https://searcharchives.bl.uk/catalog/032-002085314).
- [Edición independiente de LJS 419, Archive.org](https://archive.org/details/ljs-419-erbario-illuminated).
- [Editor del facsímil Bellunensis de 2006](https://www.parks.it/parco.nazionale.dol.bellunesi/gui_dettaglio.php?id_pubb=3234).
