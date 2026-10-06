# 24. Ausencias del comparador y distancia al descifrado

Fecha: 2026-10-06. Continuación del informe 23.

## Avance ejecutado

Se buscaron referencias de imagen y encabezamientos de entrada para los 27 folios sin bloque candidato. El resultado está en `results/ljs419_missing_folios.json` y se reproduce con `code/audit_missing_ljs419.py`.

| Grupo localizado | Folios | Resultado y limitación |
|---|---:|---|
| Referencia de imagen presente, sin bloque extraído | 2 | 5r y 5v. 5r tiene una entrada sin el marcador esperado; en 5v hay una nota medicinal candidata sin marcador inicial |
| Encabezamiento de entrada, sin referencia TIFF ni bloque extraído | 1 | 64r contiene una nota candidata en varias partes; se localizó su texto en la edición, no se validó contra la imagen |
| Sin referencia individual ni encabezamiento de entrada reconocido | 24 | La edición los agrupa en una lista de páginas que considera vacías o inacabadas; afirmación secundaria pendiente de contrastar con el facsímil |

La inspección del OCR comprobó que 5v y 64r contienen notas propuestas. No se han eliminado automáticamente sus intervenciones, traducido de nuevo ni certificado sus lecturas. No se cuenta su localización como aumento del número de transcripciones validadas.

Para los 24 folios restantes, la edición afirma ausencia de texto y dibujos. El OCR de esa lista presenta errores, por ejemplo letras confundidas con dígitos. No se transcribe esa lista como si fuera inventario primario ni se da por comprobada la ausencia de escritura. La coincidencia de cantidad y folios plausibles orienta la revisión; no la reemplaza.

El primer criterio de encabezamiento reconoció por error el comienzo de una lista agrupada como entrada de 41v. Se restringió a encabezamientos con guion de título y se repitió la ejecución. Resultado final: 2 referencias sin bloque, 1 encabezamiento sin referencia y 24 sin referencia individual. El JSON publicado corresponde al criterio corregido.

## Ejecución

```bash
python research_gpt6/code/audit_missing_ljs419.py \
  ljs419_folio_links.json LJS419_Erbario_ILLUMINATED_djvu.txt \
  --out ljs419_missing_folios.json
```

Python/Linux, salida 0. La fuente OCR debe coincidir con el hash registrado en el resultado de reconciliación. Las observaciones sobre 5r, 5v y 64r son inspecciones de esta versión concreta de la edición y se señalan como tales dentro del JSON.

## ¿Cuánto falta?

No existe un porcentaje defendible ni un plazo calculable para el descifrado. La localización de fuentes y la limpieza de un comparador son tareas delimitadas; recuperar el significado de una escritura desconocida depende de encontrar una hipótesis que sobreviva a pruebas nuevas. Resolver la cobertura de LJS 419 no garantiza resolver el Voynich.

| Hito | Estado actual |
|---|---|
| Corpus EVA y controles estadísticos reproducibles | Ejecutados en informes anteriores; detectan estructura, no significado |
| Comparadores históricos con procedencia | Localizados; imágenes y metadatos adquiridos |
| Texto histórico comparable depurado y validado | Pendiente; hay lecturas candidatas, notas omitidas y comentario moderno |
| Regla estable que convierta signos en palabras | No obtenida |
| Traducción de páginas reservadas con esa misma regla | No obtenida |
| Validación independiente y comparación con alternativas | Pendiente de una regla candidata comprobable |

Seguimos en una fase temprana respecto de la traducción. Los tres últimos hitos son el núcleo del problema y no se pueden estimar como una cantidad fija de horas o folios.

El siguiente objetivo medible es depurar un conjunto de notas del comparador, verificarlo contra imágenes y reservar páginas para evaluación. Solo entonces se podrán comparar registros médicos históricos sin que el comentario inglés contamine el resultado. Una preferencia estadística por latín o italiano, si apareciera, tampoco sería una traducción.

Fuentes: [edición candidata independiente](https://archive.org/details/ljs-419-erbario-illuminated), OCR y hashes registrados en informes 21–23; [OPenn LJS 419](https://openn.library.upenn.edu/Data/0001/html/ljs419.html) para el facsímil primario. Ninguna equivalencia semántica nueva del Voynich se afirma en este informe.
