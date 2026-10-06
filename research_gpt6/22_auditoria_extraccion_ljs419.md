# 22. Auditoría de extracción de la edición candidata de LJS 419

Fecha: 2026-10-06. Continúa el informe 21. Resultado: extracción automática de candidatos ejecutada; corpus histórico validado todavía no disponible.

## Lo que se ejecutó

Se implementó y ejecutó `code/audit_ljs419_extraction.py` sobre el OCR descargado de la [edición independiente de LJS 419](https://archive.org/details/ljs-419-erbario-illuminated), atribuida por su portada a Mamontov con Claude, 2026. La procedencia y hash del OCR se registraron en el informe 21. El nuevo resultado conserva hash de fuente, intervalos de caracteres, números de línea, hashes de bloques y alertas. No reproduce el texto moderno completo ni autoriza sus lecturas para entrenamiento.

El programa busca el marcador `TRANSCRIPTION (AS WRITTEN)` después del comienzo del recorrido principal por f. 1r y corta ante traducción, descripción, identificación, notas o siguiente encabezamiento reconocido. Comprueba también el número del archivo de imagen `0265_NNNN.tif` frente al encabezamiento de folio. Este número es una referencia dentro de la edición candidata, no prueba de haber inspeccionado esa imagen.

## Resultado real

| Comprobación | Resultado |
|---|---:|
| Bloques candidatos encontrados | 171 |
| Etiquetas distintas de folio según encabezamientos OCR | 169 |
| Tokens definidos por `\b\w+\b` dentro de candidatos | 6.472 |
| Bloques con texto de calificación editorial | 36 |
| Bloques con indicios de comentario inglés | 42 |
| Bloques con signos de incertidumbre | 80 |
| Bloques con corchetes de intervención | 82 |
| Discrepancias entre encabezamiento y referencia de imagen | 7 |
| Números de folio fuera del intervalo 1–99 | 3 |
| Bloques con pie editorial | 1 |
| Bloques sin marcador final reconocido | 1 |
| Bloques validados para entrenamiento | **0** |

Las alertas se solapan. Los 6.472 tokens incluyen contaminación y números: **no son el tamaño de un corpus medieval limpio**. Las 169 etiquetas tampoco acreditan 169 folios correctamente transcritos. Ausencia de alerta no significa lectura correcta.

## Problemas comprobados

- f. 1r: entre los marcadores de transcripción y traducción hay explicaciones inglesas de legibilidad y una calificación editorial. No basta extraer todo ese intervalo para obtener texto histórico.
- f. 5v: la nota se presenta sin el marcador inicial esperado. Más adelante el OCR pierde el encabezamiento del folio siguiente. Una asignación al último encabezamiento visible vincularía erróneamente ese bloque a 5v; la referencia de imagen indica 6r y activa una alerta.
- Los encabezamientos OCR `933v`, `988r` y `988v` están fuera del rango del manuscrito. No se corrigen silenciosamente a valores plausibles.
- Hay dos bloques asociados por el OCR a `35v` y dos a `60r`. La discrepancia con imagen permite señalar posibles encabezamientos perdidos; no se convierten automáticamente en duplicados textuales del manuscrito.
- Los encabezamientos válidos `41v` y `79r` no tienen bloque detectado por este criterio. Eso no demuestra que sus páginas carezcan de escritura. Hay otras omisiones posibles porque el propio reconocimiento de encabezamientos es incompleto.

Estos fallos pertenecen al OCR y al formato de extracción. No prueban que todas las lecturas propuestas por la edición sean incorrectas, ni permiten aprobarlas.

## Reproducción y verificación

Descargar el OCR candidato desde el enlace de procedencia y ejecutar desde la raíz del repositorio:

```bash
python research_gpt6/code/audit_ljs419_extraction.py LJS419_Erbario_ILLUMINATED_djvu.txt --out ljs419_extraction_audit.json
```

Ejecución real en Python, Linux, código de salida 0. Resultado guardado en `results/ljs419_extraction_audit.json`. Los offsets son caracteres de texto UTF-8 decodificado, desde cero, con extremo final excluido; no son offsets de bytes. El hash de cada bloque permite comprobar la extracción sin republicar el contenido.

Tres comprobaciones sintéticas adicionales pasaron: exclusión de la traducción posterior; detección de discrepancia folio/imagen; detección de intervención editorial. Comprueban comportamiento del extractor, no fidelidad paleográfica. No se ha ejecutado un modelo de identificación lingüística sobre estos bloques.

## Consecuencia para el descifrado

El progreso es una auditoría reproducible que impide confundir comentario moderno con texto medieval. La hipótesis de comparación latín médico / italiano septentrional / mezcla continúa sin una puntuación lingüística nueva.

La siguiente etapa debe reconstruir la asociación folio-imagen, recuperar las notas sin marcador y validar lecturas contra los facsímiles. Se necesita separar encabezamientos, notas, expansiones y conjeturas, con dos representaciones: diplomática y normalizada. Solo después tendría sentido repetir los controles estadísticos del informe 19. Entrenar ahora con estos bloques podría producir una preferencia lingüística artificial.

No se ha recuperado ninguna equivalencia semántica del Voynich ni una clave que traduzca páginas reservadas.
