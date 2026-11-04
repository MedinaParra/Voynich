# 90 — Canal de cifrado normalizado: prueba exhaustiva antes de volver al latín

**4 de noviembre de 2026. Protocolo fijado antes de ejecutar.**

La etapa 88 falló porque el objetivo congelado prefería candidatos incorrectos a la verdad. Esta etapa implementará un modelo generativo diminuto que se pueda comprobar por completo, separando normalización, inferencia y exactitud. No pretende traducir el Voynich ni demostrar recuperación latina.

Se fijan externamente tres letras claras `abc`, cuatro símbolos cifrados `wxyz`, longitud seis, las 36 claves suryectivas y un prior uniforme sobre ellas. La cadena de Markov usa probabilidades racionales: inicial `[3,2,1]/6` y transiciones `[[3,2,1],[1,4,1],[2,1,3]]/6`. Cada letra emite uniformemente uno de sus alias. Todas las letras tienen al menos un alias y las filas de emisión suman uno.

Se enumerarán **4.096 ciphertexts × 36 claves = 147.456 pares**. El likelihood puede representarse exactamente con denominador común `12^6 = 2.985.984`. Un auditor separado construirá la misma tabla en la dirección generativa: primero los 729 textos claros y luego sus emisiones, sin importar el programa principal.

Se compararán cinco decisiones: clave de mayor score LM sin canal, clave MAP con canal, texto MAP sumando las claves equivalentes, Hamming óptimo por posición y Hamming óptimo restringido a claves admisibles. La comparación sin canal conserva las mismas 36 claves; no se confundirá el efecto del canal con cambiar la familia. Los desempates son lexicográficos y se conservan los tamaños de los conjuntos MAP.

Las verificaciones principales exigen masa condicional y conjunta exactamente uno, coincidencia independiente de todas las probabilidades y decisiones, y referencias cerradas de longitud uno y LM uniforme. Los riesgos se integran sobre toda la distribución conjunta: no se exige que una verdad muestreada sea siempre el máximo del posterior. La decisión Hamming libre puede no corresponder a una clave admisible; se informará.

**Límite importante:** la suryectividad sobre un alfabeto fijado ya prohíbe claves que usen sólo una o dos letras. Por ello esta prueba no demuestra haber resuelto el colapso sin restricciones de la etapa 88. Verifica el modelo pequeño y el código que después podría ampliarse.

El [plan exacto](data/tiny_channel_plan.json) fija constantes, referencias, criterios y límites. Se publicarán fuentes antes de resultados y todos los casos enumerados. No habrá ajuste de la matriz o de la familia buscando un resultado favorable. No se modificará el experimento 88. No se reentrenará Kraken.
