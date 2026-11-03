# 86 — Primero recuperar una clave conocida

3 de noviembre de 2026. Base `37159556eb92c380a8a8a14c5a05855a1144ef7b`. [Plan fijado](data/known_cipher_recovery_plan.json).

Se entrenará un modelo de caracteres latino sólo con Apicio y se intentarán recuperar tres textos de César cifrados con claves aleatorias ocultas al algoritmo. Son autores separados. El preparador guardará claves, pasajes y semilla fuera de la entrada pública; publicará su compromiso SHA256 antes de resolver. La separación es procedimental: los agentes comparten archivos y las fuentes públicas ya existen en el repositorio.

Habrá tres pares con/sin espacios de los mismos textos y claves, tres negativos de letras barajadas con frecuencias conservadas y un homofónico de 26 símbolos. Los pares no son seis mensajes independientes. El homofónico conserva el tamaño del alfabeto pero rompe la hipótesis de permutación; su techo de exactitud bajo un decoder biyectivo se medirá por separado.

El solver usará un modelo condicional de cuatro caracteres y búsqueda por intercambios con presupuesto fijo. La tabla logarítmica se cuantiza a enteros y la aceptación pseudoaleatoria se fija en una tabla para reproducir las decisiones de búsqueda. No usa diccionario, segmentación de palabras, OCR ni etiquetas Voynich. Todos los casos recibirán el mismo procedimiento. Se congelarán código, tablas y predicciones antes de evaluar con las respuestas ocultas.

El éxito estricto exige texto completo y clave sobre todos los símbolos observados exactos en los tres positivos independientes. Los símbolos ausentes no permiten recuperar su asignación. Se publicarán errores parciales si falla, sin convertir porcentaje alto o apariencia latina en éxito exacto. No habrá nuevos ajustes a los controles tras revelar su respuesta.

Esta tarea prueba una familia conocida con una lengua conocida y textos limpios. Incluso si pasa no demuestra que Voynich use ese idioma, esos caracteres o ese cifrado. Una reconstrucción que vuelve a cifrar correctamente sólo prueba coherencia con la clave candidata; no prueba que sea la clave histórica.
