# 42. Generación de rótulos mediante una regla compartida

Fecha: 2026-10-07 UTC / noche del 6 de octubre en Chile. Exploratorio; traducción NOT_RUN.

## Resultado

Se ejecutó un generador de cadenas con una sola regla pequeña de prefijos/sufijos. En tres evaluaciones por hoja farmacéutica retenida, no encontró ninguna regla elegible respaldada por dos familias herbales y dos hojas de entrenamiento. Usó por ello la identidad, tal como estaba fijado. Ninguno de los diez rótulos reales se generó, ni como primera opción ni entre todas las opciones. No se aprendió una transformación útil con este canal.

El experimento semántico más fuerte —misma planta, rótulos individuales de raíz y hoja, predicción en otra familia— sigue **BLOCKED**. El inventario y las imágenes no suministran esos contrastes verificados. El piloto numérico no se presenta como ejecución de esa prueba semántica completa.

## Selección antes de los resultados

`data/transformation_inventory.json` recoge 35 relaciones propuestas explícitamente en las descripciones de los cuadernos 15 y 19 de René Zandbergen, incluidas notas tentativas. Fuentes:

- https://voynich.nu/q15/index.html
- https://voynich.nu/q19/index.html

No se adivina qué rótulo corresponde a un número de fragmento a partir del orden de las líneas. Se exige un único Lf con identificador numérico explícito, un rótulo literal de una palabra y párrafos herbales sin rescatar letras de formas ambiguas. Se cuentan también los Lf ambiguos o de varias palabras al decidir unicidad: el fragmento 110 tiene dos Lf y no se reduce artificialmente a uno. Lc identifica un recipiente y no puede rellenar un Lf faltante. Los sufijos 80b, 94b y 95b se conservan en su locus y se vinculan al número de figura correspondiente sin confundirlos con los Lc 80a/94a/95a.

La extracción produjo 11 pares con texto utilizable. f48r → fragmento 61 quedó fuera del modelo compartido: en el corpus congelado su párrafo es Currier B/mano 5 y el rótulo farmacéutico A/mano 1. Quedan **10 pares, nueve familias herbales, tres hojas farmacéuticas físicas** (f99, f100, f102), todos con fuente y rótulo A/mano 1. Todos los rótulos utilizables proceden de **un solo cuaderno**, el 19 (S); las hojas retenidas no son nuevos cuadernos ni replicación por mano. Ninguno tiene un Lp individual que establezca cuál es el nombre de la planta completa en el párrafo.

Se conserva `data/transformation_plan_v1.json`. La versión 2 registra que el filtro de mano/Currier se añadió después de la extracción de metadatos y antes del primer ajuste/predicción sobre Voynich; los límites de las reglas y la puntuación no se cambiaron. No se amplió el modelo tras obtener cero aciertos.

## Cotejo que evitó un falso contraste

f96v se relaciona tentativamente con los fragmentos 94 en f99r y 116 en f100r; también lo describe https://voynich.nu/q17/index.html . Se descargó el manifiesto primario Yale https://collections.library.yale.edu/manifests/2002046 y se inspeccionaron las imágenes correspondientes a 1006245, 1006246 y 1006248.

El 94 no es una raíz aislada: conserva raíces, tallos, hojas y grupos de frutos. El 116 conserva raíces, tallos y hojas. Hay semejanzas con f96v, pero también varios cambios simultáneos. No es un par mínimo «raíz frente a hoja». Las URLs, dimensiones y SHA-256 de las imágenes figuran en `data/transformation_visual_audit.json`. La inspección fue dirigida por correspondencias conocidas, no ciega ni una identificación botánica independiente.

Dentro del inventario hay una sola familia herbal con dos fragmentos propuestos, f96v; no aporta el contraste necesario. No se inferirá «raíz» de la mera diferencia entre texto herbal y texto farmacéutico.

## Modelo fijado

La entrada es el conjunto de palabras inequívocas del párrafo herbal; no se presupone que una sea su nombre. La salida son cadenas realmente generadas, **sin usar un vocabulario de los rótulos retenidos**.

Se agrupan las convenciones EVA `ch`, `sh`, `ckh`, `cth`, `cph`, `cfh` como unidades para que una regla no corte por dentro de esas representaciones. Las demás letras literales se mantienen. Esto no demuestra que las unidades sean fonemas ni resuelve la segmentación paleográfica.

Una regla quita un prefijo y un sufijo fijos y añade otros, con hasta dos unidades en cada uno y al menos tres unidades centrales conservadas. Se aprende como máximo una regla no idéntica. Debe estar respaldada por dos familias herbales distintas y dos hojas farmacéuticas de entrenamiento. Se maximiza ese respaldo y después se minimizan costo de edición y longitud de descripción; los desempates son deterministas.

Para ordenar las salidas se usa un modelo de bigramas y longitudes ajustado exclusivamente a los rótulos de entrenamiento, con suavizados fijados. La identidad usa exactamente la misma puntuación. Top 1 exige ganador único; top 5 no admite un empate que atraviese la quinta posición.

Se retiene una hoja farmacéutica completa y se purgan también todos los pares de entrenamiento que comparten familia herbal con la prueba. Así f96v no puede reaparecer como entrenamiento al evaluar su otra copia farmacéutica. Se guardan las cadenas predichas antes de puntuarlas contra los rótulos retenidos.

## Resultados ejecutados

| Hoja retenida | Pares de prueba | Pares de entrenamiento | Pares purgados por familia compartida | Reglas elegibles |
|---|---:|---:|---:|---:|
| f100 | 3 | 6 | 1 | 0 |
| f102 | 4 | 6 | 0 | 0 |
| f99 | 3 | 6 | 1 | 0 |

| Resultado | Generador acotado | Identidad |
|---|---:|---:|
| Rótulo exacto en primera posición única | 0/10 | 0/10 |
| Rótulo exacto entre primeras cinco opciones | 0/10 | 0/10 |
| Rótulo exacto entre todas las opciones | 0/10 | 0/10 |

Las listas tienen entre 43 y 66 cadenas. Como no se aprendió ninguna regla, ambos generadores son idénticos aquí. No se presenta la capacidad de emitir muchas cadenas como una traducción.

También se completaron **199 comparaciones incorrectas controladas**: se reasignaron páginas herbales ajenas al inventario, con la misma mano/Currier/sección y cantidad de tokens dentro de ±20%. Se conservó la familia como unidad y se evitaron páginas repetidas entre familias. Se volvió a ajustar el modelo entero en cada ensayo. Ninguno dio un acierto top 1 o top 5; en todas las opciones la media fue 0,171 rótulos exactos por diez casos y el máximo dos. Son un benchmark exploratorio: no un p confirmatorio, no asignaciones uniformes sobre una población definida y no contraste raíz/hoja.

## Controles y reproducción

Diez controles pasan: transformación sintética conocida (6/6 frente a identidad 0/6), rótulos sintéticos ajenos (0/6), aislamiento del rótulo retenido, purga de familia entre hojas, separación Lc/Lf, bloqueo de múltiples Lf, empates, límites de unidades EVA, asignación de controles sin duplicar páginas y respaldo mínimo por hojas.

```sh
curl -L --fail -o voynich_eva.txt 'https://raw.githubusercontent.com/cesarjz/Voynich/47e6a77dc9d5cd570c375f4aff710fa4a0567278/corpus/voynich_eva.txt'
python -m unittest discover -s research_gpt6/code -p test_transformation_probe.py -v
python research_gpt6/code/transformation_probe.py --corpus voynich_eva.txt --inventory research_gpt6/data/transformation_inventory.json --plan research_gpt6/data/transformation_plan.json --predictions research_gpt6/results/transformation_predictions.json --out research_gpt6/results/transformation_result.json
```

Python local 3.12.14, solo biblioteca estándar. Comandos reales, códigos de salida cero y hashes en `results/transformation_checks.json`. El resultado incluye los 25 casos excluidos y sus motivos; las predicciones completas están conservadas.

La [ejecución de GitHub Actions 37565664707](https://github.com/MedinaParra/Voynich/actions/runs/37565664707), sobre el commit `8b7e1befee4d701ed0abf4b05671b44aff0b921d`, terminó con éxito. El job `112612670252` pasó los diez controles de transformación y ejecutó el generador en Python 3.12.15. Se cotejaron los logs reales: coinciden 19 campos del resultado, las diez filas de generación/rango y el SHA-256 de las predicciones completas (`ddc626608907bdfcbb6a43887e80c7e1bb67f22f82578f47b6b2a79e019ff1c8`). La auditoría está en `results/transformation_ci_audit.json`. Se comprobó el hash que el programa escribió en el log; no se descargó el artefacto ni se comparó todo el JSON de resultado. Esta reproducción valida la ejecución del piloto y sus ceros; no agrega evidencia semántica.

## Decisión y límite

Este canal particular no encuentra apoyo: una regla compartida de cambios pequeños en extremos de una palabra, con centro conservado, no se pudo aprender bajo los controles fijados. No refuta una lengua, una cifra, un canal con cambios internos ni una regla que parta de información ausente del párrafo.

Antes de proponer operadores con glosas, hacen falta varios contrastes de partes de una misma entidad, con rótulos individualizados y correspondencias verificadas sin seleccionar por sus palabras. Ampliar ahora los límites para acomodar estos diez rótulos sería exploración posterior, no validación de la apuesta original. El siguiente modelo deberá tener su propia muestra reservada.

Ejecución: PASS_EXECUTED. Apoyo a este canal: NO_ENCONTRADO. Contraste semántico raíz/hoja: BLOCKED. Traducción: NOT_RUN. Originalidad del método: NOT_ESTABLISHED.
