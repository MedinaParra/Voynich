# 56 - Contrastar las hipótesis numéricas simples

Fecha: 26 octubre 2026. Base: `2433fdc127f70500b0633c2413d3c4c4dac7e513`.

**Exploratorio, no ciego.** Se fijan las reglas antes de ejecutar los nuevos conteos. La muestra, el corpus y algunos ejemplos ya se examinaron; no se presenta una reserva independiente ni una hipótesis inédita. El plan ejecutable es [numeral_probe_plan.json](data/numeral_probe_plan.json).

## Pregunta 1: ¿las cinco cifras de f49v ofrecen una clave numérica directa?

Se conserva la asociación espacial observada: `o→1`, `r→2`, `y→3`, `e→4`, `@140;→5`, como **hipótesis condicional**, sin afirmar que esa sea su lectura. Se evalúa si los valores predicen el número de palabras transcritas de los renglones acompañados por esos signos.

Los renglones 2-6 de f49v proporcionaron las asociaciones y quedan fuera de la nueva evaluación. Se usarán todos los demás renglones de esa hoja con signos incluidos en el mapa. Como transferencia externa se usarán los signos de f76r que preceden directamente a un renglón de texto en el archivo IVTFF. No se completan valores para otros signos. La prueba externa puede resultar muy pequeña; se informará su denominador.

Se informan cuatro políticas fijas: separar solo puntos o puntos y comas, contando toda la línea o solo el fragmento anterior a la primera interrupción por el dibujo. Las alternativas de lectura se mantienen dentro de un token. Los números resultantes son conteos editoriales, no traducciones.

Como sensibilidad exclusivamente paleográfica se permite `@192;→r`, fijada por la semejanza y el antecedente de Stolfi. No se añaden otras equivalencias tras ver los resultados. También se calcula el máximo ajuste posible de una función signo→cantidad en f49v: para cada signo, su cantidad más frecuente. Es un límite de ajuste en los mismos datos, no una predicción ni una validación.

**Se excluye el emparejamiento por índice en f66r:** hay 34 signos y 32 renglones, y el antecedente bibliográfico indica cambios de alineación. No se fuerza una equivalencia entre listas desiguales.

Un resultado negativo solo limita la interpretación concreta de cantidades de palabras. No demuestra que los signos carezcan de otros usos numéricos.

## Pregunta 2: ¿son las etiquetas zodiacales una lista fija del 1 al 30?

Modelo contrastado: cada posición distinta dentro de un signo recibe un numeral diferente; ese numeral tiene una representación completa, canónica y constante entre signos. Se reúnen las dos mitades de Aries y las dos de Tauro, manteniendo las excepciones del inventario anterior.

Este modelo tiene dos consecuencias que no dependen del orden de lectura:

1. No debería repetir una misma etiqueta completa en dos posiciones distintas del mismo signo.
2. Dos signos completos deberían compartir sus etiquetas, aunque las dibujen en órdenes diferentes.

La normalización primaria elimina comentarios editoriales, admite solo etiquetas inequívocas de letras minúsculas y palabras separadas por puntos, y conserva las separaciones. Se excluyen alternativas, interrogantes, ligaduras anotadas, códigos raros y comas. Una sensibilidad elimina espacios entre las mismas palabras, sin cambiar los casos elegibles.

Se registran todas las etiquetas omitidas. Para dos signos se calcula la intersección multiconjunto: el máximo de coincidencias exactas posible incluso permitiendo **cualquier reordenación**. Se añade un límite generoso que permite que cada etiqueta excluida aporte una coincidencia adicional. Las coincidencias o discrepancias no se convierten en p-valores.

La repetición conocida de `otaly` en f73r ya se había observado en el inventario; el interés es auditar los doce diagramas bajo una misma regla. Los ejemplos pertinentes se comprobarán en imágenes si la resolución permite reconocerlos, sin presentarlo como una lectura experta independiente.

Esta prueba no evalúa etiquetas con un número incrustado en una descripción, prefijos específicos de cada signo, variantes contextuales ni cifras homofónicas. Tampoco invalida una organización en 30 grados o un calendario esquemático: distingue la estructura del diagrama de la función de sus etiquetas.

## Criterio de avance

Conservar todos los resultados y sus denominadores. Una contradicción elimina únicamente el modelo explícito que la predice. Si falla una clave simple, no se buscará otra entre numerosas variantes para anunciar un éxito. El siguiente paso deberá plantear una predicción nueva y verificable.
