# 67 - Reentrenamiento real de Kraken con palabras EVA y un control emparejado

Fecha: 27 de octubre de 2026. Base: `8519b2e6d3e8d175201e05ed004b1b027f615bd5`, rama `experiment/kraken-voynich`.

Se reentrenará el modelo conservado `repaired_200` con la referencia candidata uniforme v2. El modelo anterior usa códigos PUA de Boxer; la referencia nueva usa caracteres EVA convencionales. Se adaptará la capa de salida con `ketos train --load ... --resize new`, conservando las otras capas cargadas y permitiendo su ajuste. No se reanudará el estado del optimizador ni se presentará una inicialización aleatoria completa como continuación del mismo modelo.

## Datos y preparación fijados

- 344 palabras candidatas de las mismas cuatro páginas, sin una nueva revisión experta. Se conserva la exclusión original de ancho cero; no se completan palabras ni caracteres.
- Entrenamiento: f3r/f3v, **197 palabras y 944 caracteres EVA**. Desarrollo: f4r/f4v, **147 palabras y 744 caracteres EVA**. Son hojas físicas distintas, ya exploradas en esta investigación. El alfabeto de desarrollo está contenido en el de entrenamiento.
- Recorte de los polígonos v2 con cuatro píxeles de margen. Se dilata la máscara cuatro píxeles, se conservan los píxeles RGB originales dentro de ella y se pone blanco fuera. No se reescala la imagen exportada; Kraken aplica después su transformación de entrada. Se preservan las máscaras, coordenadas, imágenes, hashes y textos.
- Los nombres de archivo no contienen puntos internos, conforme al comportamiento ya verificado del parser de parejas de Kraken 7.1. Se comprueba cada pareja real con ese parser antes del ajuste.
- Se convierte el modelo fuente fijado a safetensors y se comparan todos sus tensores y su codec contra el original antes de usarlo. Los hashes, configuraciones y comandos se conservan.

## Dos ajustes de 200 épocas

Ambos parten del mismo modelo anterior, SHA-256 `b5df9eef0a783bec696b33636fbfb8d4807bfaa256d74ad6b34df4c58db66acb`. Se mantienen arquitectura cargada, semilla 20261027, CPU, dos hilos, lote 16, tasa 0,001 constante y ausencia de aumento. Se actualiza también el backbone: no se deja congelado. La nueva salida se ajusta al alfabeto de las etiquetas de entrenamiento EVA; no se proporciona un codec procedente de desarrollo.

1. `aligned_200`: imágenes con sus textos originales.
2. `permuted_200`: textos de entrenamiento reasignados por ciclos deterministas dentro de cada folio y longitud exacta. No cambian el inventario, la distribución de longitudes o los datos de desarrollo. Palabras duplicadas y grupos de un solo registro pueden conservar el mismo texto; se cuenta cuánto cambia realmente.

El monitor recibe sólo las 197 parejas usadas para entrenar, con las etiquetas asignadas de su condición. Se usa el último checkpoint, época de índice 199, sin elegir el que mejor puntúe en desarrollo. Se conservan ambos ajustes y todos los fallos. El control conserva las mismas referencias verdaderas para puntuar y los mismos comparadores basados en las etiquetas originales de entrenamiento.

## Medidas y límites de interpretación

La medida principal es distancia de Levenshtein micro por carácter EVA convencional. La proporción de palabras idénticas es secundaria. Se exportan las 147 predicciones de desarrollo y las 197 de entrenamiento por condición, los errores, el ajuste contra las etiquetas asignadas y el ajuste contra las referencias originales. Se desglosa desarrollo por folio y por palabras vistas/no vistas en el vocabulario verdadero de entrenamiento.

Comparadores fijados: vecino por imagen con los mismos rasgos usados en los ensayos anteriores, palabra de entrenamiento más frecuente, carácter de entrenamiento más frecuente repetido hasta su longitud mediana y salida vacía. Se informa también si el codec final conserva indebidamente caracteres PUA y se aborta si no se adapta a EVA.

El error anterior de 73,8197 % tenía otro denominador y otra notación —Boxer, sobre filas completas e incluyendo espacios—. **No se restará de una nueva cifra EVA para declarar una mejora porcentual directa.** La comparación válida dentro de esta prueba es entre condiciones y comparadores que comparten las 147 palabras y los 744 caracteres de referencia.

El cambio combina nuevas asociaciones de imagen/texto, recortes de palabra, adaptación de alfabeto y continuación de pesos. No aísla por sí solo cuánto aporta cada componente geométrico. Son dos ajustes con una semilla, no una estimación de incertidumbre ni una validación en páginas nuevas. Caracteres EVA reconocidos no son fonemas, significados o traducciones.

## Ejecución y evidencia

Se ejecutará en GitHub Actions con versiones fijadas en `.github/workflows/kraken-eva-word-retraining.yml`. Antes se ejecutarán controles sintéticos de fidelidad de píxeles, límites, degeneración, permutación y nombres de parejas. El plan, código y workflow se publicarán antes de entrenar. La preparación local no se contará como entrenamiento.

Se preservarán modelos finales, checkpoints en artefactos, configuraciones, comandos, logs, codec, entradas y predicciones. No se enviarán mensajes a terceros. Fuentes y atribución de las imágenes y textos EVA: referencia v2 y ensayos 63–66. Código nuevo propio. Identificación de lengua, revisión experta nueva y traducción: **NOT_RUN**.

### Corrección técnica antes de entrenar

La ejecución `40540130799`, commit `c261f8685de5e1b30cf4a5d6fd3d5b322f7f1851`, pasó instalación, cinco controles y preparación en ambas condiciones, pero falló antes de entrenar. El verificador intentaba leer safetensors con el cargador heredado `kraken.lib.models.load_any`, que sólo acepta el modelo CoreML. Se corrige usando `kraken.models.load_models` para leer ambos formatos y se comparan los estados de `TorchVGSLModel.nn`. La inferencia del modelo CoreML final conserva su API ya utilizada. Se preservan fallos, logs y hashes del intento inicial. No cambian datos, plan, épocas, optimizador ni condiciones experimentales.
