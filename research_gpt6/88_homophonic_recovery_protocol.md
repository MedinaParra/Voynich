# 88 — Protocolo de recuperación homofónica con respuestas ocultas

**4 de noviembre de 2026. Rama `experiment/kraken-voynich`.**

La etapa 86 recuperó tres controles monoalfabéticos, pero obtuvo 62,95% en un control homofónico cuya familia biyectiva impedía superar 77,55%. El siguiente experimento amplía la función inversa: varios símbolos pueden descifrarse como la misma letra.

Esto es una prueba de capacidad con latín conocido. No supone que el Voynich sea latín o un cifrado homofónico y no autoriza presentar una salida como traducción.

## Diseño fijado antes de generar casos

Se conservan sin reentrenar las tablas enteras de cuatro letras de Apicio de la etapa 86, ancladas en `960254605ab910ed90af8d3a8cc7278bbb202185`. Un preparador separado elegirá tres ventanas nuevas de 2.000 letras de César 1–3, excluyendo todos los intervalos usados en la etapa anterior, incluido su control homofónico. Cada contenido tendrá una versión monoalfabética y otra homofónica de 26 símbolos. Otros tres casos serán permutaciones del ciphertext homofónico y conservarán sus frecuencias. No se suministrarán espacios, roles o pares al algoritmo.

Son nueve casos pero tres unidades de contenido; los pares no constituyen replicaciones independientes. El generador y el evaluador se publicarán, manteniendo las respuestas ocultas hasta congelar las predicciones. La separación será procedimental; los agentes y repositorio no ofrecen aislamiento de seguridad.

## Comparación

Ambos métodos usarán ocho reinicios de 50.000 propuestas por caso, las mismas tablas lingüísticas y un máximo de 100 pasos de pulido. El método anterior conserva una permutación. El nuevo permite 26 asignaciones independientes a letras a–z mediante reasignaciones de un símbolo y swaps.

Cada caso se resuelve por separado. No se transfiere texto entre versiones del mismo contenido, no se añade el candidato del otro solver como fallback y no se usa verdad para seleccionar salidas. El criterio es mayor score entero, con desempate lexicográfico de clave. El presupuesto y las semillas quedan en el [plan](data/homophonic_recovery_plan.json).

Igual número de propuestas no significa igual cómputo: cambian los vecinos y el coste del pulido. Se publicarán contadores y tiempos sin reclamar equivalencia computacional. No se cambiarán datos, parámetros o criterios al conocer las respuestas.

## Criterios y límites

El éxito estricto primario requiere recuperar las 2.000 letras completas y todas las asignaciones observadas en **los tres controles homofónicos**. Las correspondencias ausentes se excluyen. La regresión en los tres monoalfabéticos se informa por separado.

Se medirán también exactitud de letras y claves, techo biyectivo, número de letras claras utilizadas y scores de candidato/verdad. La verdad homofónica está fuera de la familia anterior: su score no diagnostica por sí solo un fallo del optimizador biyectivo. Para el método nuevo, una verdad representable con mayor score indica búsqueda insuficiente; un candidato incorrecto con mayor score identifica preferencia equivocada del modelo.

Los controles aleatorios son descriptivos: no se ha calibrado rechazo automático. Una familia más flexible puede subir el score sin mejorar el texto. El análisis conservará los fallos y distinguirá estos casos.

## Ejecución verificable

No hay ejecutor local disponible en esta sesión; las compilaciones y búsquedas se realizarán mediante GitHub Actions. Se publicarán fuentes y entradas antes de buscar, las predicciones completas antes de revelar y la evaluación/auditoría después. Un replay tras la revelación será reproducción informática, no otro ensayo ciego.

No se reentrenará Kraken ni se traducirá el Voynich en este ensayo.
