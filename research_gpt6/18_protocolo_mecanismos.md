# Filtro de mecanismos: protocolo previo a ejecución
6 de octubre de 2026. Comparación exploratoria, no selección definitiva de idioma.

Reserva: primer pliegue de los cinco grupos de hoja fijados en la fase anterior (índice ordenado módulo 5=0). Entrenamiento: otros cuatro. Ambos tratamientos de comas. Se conservan longitudes de tramos del test como geometría condicionada; no es generación libre de páginas.

Modelos fijados: (1) muestreo independiente de palabras por cuatro bandas de posición; (2) muestreo de primer carácter condicionado al último anterior y banda, suavizado 20 hacia distribución base, seguido de palabra muestreada por frecuencia dentro de esa inicial; (3) copia literal del anterior con probabilidad fija 0,15, y modelo independiente en otro caso. Este último es un control ilustrativo, no el algoritmo publicado de Timm/Schinner. Ningún modelo usa significado. No se calibrará 0,15 al test.

50 muestras por mecanismo; semilla 20261006. Métricas conjuntas: MI de bordes, exceso contra 19 barajados intra-tramo, entropía condicional de caracteres dentro de palabras, repetición exacta adyacente, distancia de edición ≤1 adyacente y longitud media. Intervalos descriptivos de simulación, no p-valores de prueba histórica. Se informan por separado; no se elige un ganador con ponderaciones retrospectivas.

Controles de lengua: CLTK Latin Library, commit 76229acaf02efd1964ac32009408a90b6f279758, Apicio libros 1–5 y César Gallia 1–3. Se verifican blobs, extraen letras ASCII a minúsculas y eliminan líneas en mayúsculas/títulos iniciales para reducir encabezados. Ventanas contiguas de igual número de tokens que el test, cortadas según su geometría. No están emparejadas en frecuencia, época, manos o tema; son solo dos corpus latinos. Sustitución monoalfabética fija bijectiva (rotación 7) conserva exactamente estas métricas: comprobación ejecutable.

Qué podría descartarse: modelos concretos que reproducen un borde pero fallan otras métricas. Qué no: todo cifrado, todo generador, o todo el latín. Traducción exige posteriormente unidades y mecanismo inverso identificados.
