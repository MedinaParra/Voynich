# Fuentes y significado del experimento

Textos latinos: fuente CLTK Latin Library, commit76229acaf02efd1964ac32009408a90b6f279758, ya preservada en `data/latin_sources.json`. Véase `data/LATIN_LICENSE.md`, Public Domain Mark1.0. Se conservaron los filtros anteriores: primera línea y líneas completamente en mayúsculas excluidas; minúsculas y tokens ASCII a-z; sin normalizar u/v ni i/j.

El modelo aprende sólo de Apicio1–5. Los pasajes de César1–3, las claves, la semilla y el control homofónico quedaron fuera de las entradas del solver durante la primera búsqueda. Un agente preparador fijó el compromiso de verdad; se publicaron código/entradas permitidas y luego las predicciones congeladas antes de autorizar la evaluación. La separación fue procedimental, no una protección de acceso: los agentes compartían archivos y el corpus fuente ya estaba disponible.

`reveal/` se publicó DESPUÉS de congelar y evaluar para permitir reproducción completa. Contiene respuestas de controles sintéticos, no una clave del Voynich ni secretos de terceros. El workflow posterior reproduce archivos, búsqueda y métricas: no es un segundo ensayo ciego.

La búsqueda asume latín y una sustitución monoalfabética. Los grupos con y sin espacios comparten exactamente el mismo flujo de letras y búsqueda; son pares de presentación, no pruebas independientes de segmentación. El score no usa espacios ni diccionario.

Todo candidato se devuelve, incluso para texto barajado o cifrado fuera de la familia. No existe un umbral de abstención validado. Una salida legible o un score alto no certifican significado. Las correspondencias de símbolos ausentes no son identificables; no se cuentan como clave recuperada.

El modelo incluye tablas binarias little-endian de puntuación int32, umbrales uint64 y temperaturas int32. El fuente C++ usa deltas enteros y un generador pseudoaleatorio determinista para repetir la búsqueda. Se suministran el fuente, comando de compilación, manifest de hashes y contadores reales. Las constantes se fijaron antes de abrir las respuestas.

Este ensayo no usa texto Voynich como latín ni produce una traducción del manuscrito. El marco SA/modelo de caracteres tiene antecedentes publicados; no se reivindica invención de la técnica ni réplica exacta de los artículos citados en el informe87.
