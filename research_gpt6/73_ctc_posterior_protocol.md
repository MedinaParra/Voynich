# 73 — Suma de alineaciones CTC sin diccionario

27 de octubre de 2026. Seguimiento del ensayo 71, ejecutado en `40571882695`: la agrupación EVA no mejoró el criterio principal de formas no vistas. Se mantiene el modelo fuente `35092d9baf56083eb6c70a2e32c478d8910ef5e685d0cee33fc5a935ca1c71d8`.

Se probará una mejora del decodificador sin actualizar pesos ni etiquetas. El código de Kraken 7.1 usa decodificación por ruta más probable: selecciona el máximo por instante y colapsa repeticiones y blancos. La formulación CTC distingue esa ruta de la probabilidad de un texto, que suma alineaciones. Se implementa búsqueda aproximada por prefijos con haz **32**, en espacio logarítmico y sin poda de caracteres. No es una técnica nueva ni se garantiza la búsqueda global exacta con ese haz finito.

El decodificador recibe únicamente la matriz de probabilidades y el tamaño del haz. No incorpora diccionario de palabras, modelo de lenguaje, referencia de evaluación, identificación de idioma o reglas de traducción. La salida se elige por la probabilidad CTC acumulada de los prefijos retenidos. Las referencias sólo puntúan después de decodificar.

Se mantienen los mismos 282 recortes, pesos y separación del ensayo 70. La medida principal continúa siendo CER EVA en las 76 formas no vistas de la hoja 7, con 446 caracteres de referencia. Se informa también toda esa hoja, la hoja 4 y los grupos por longitud. Son páginas ya exploradas y referencias candidatas, no validación paleográfica nueva.

## Comprobaciones y condiciones fijadas

1. Capturar las matrices que recibe el decodificador original de Kraken, sin modificar su resultado, dos veces sobre las 282 muestras en un mismo proceso CPU/dos hilos. Conservar matrices completas, longitudes, codec, hashes y llamadas reales a la red.
2. Exigir que un máximo por instante independiente, convertido con el codec del modelo, reproduzca los 282 textos originales en ambas pasadas. Si no coincide, se detiene la comparación antes de puntuar el haz y se conserva el fallo de interfaz.
3. Probabilidades finitas y no negativas, con suma por instante dentro de 0,00001 de uno. No se escogen temperaturas, umbrales o anchuras según resultados.
4. Comparar `greedy` y `beam32` sobre esas mismas matrices. Control temporal: `shuffled_beam32`, permutando todos los instantes con semilla `20261027+índice_de_muestra`, igual en ambas pasadas. Conserva los vectores de probabilidad, pero altera el orden. Es un control del decodificador, sin nuevas imágenes ni llamadas adicionales a la red.
5. Primera pasada como comparación principal, segunda como repetición. Se guardan discrepancias de matrices y de textos, aunque existan. Sin escoger la mejor pasada.
6. Comparador por imagen reutilizado de las mismas 442 parejas e imágenes fijadas, con hash y atribución al cálculo anterior.

Controles matemáticos antes de ejecutar: enumeración exhaustiva de todos los caminos en matrices pequeñas, coincidencia de todas las masas de prefijos, caso donde el máximo por instante pierde frente a la suma CTC, repetición separada por blanco, rechazo de probabilidades inválidas y orden de desempate determinista. La auditoría posterior implementará otra recurrencia en espacio de probabilidades y reescalado, separada del código principal en logaritmos. No requiere nuevas inferencias.

El ensayo no reentrena una tercera red ni cambia los dos modelos del ensayo 71. Los resultados negativos permanecen disponibles. No prueba que la notación EVA sea el alfabeto histórico ni que las palabras candidatas tengan una interpretación semántica identificada.

## Fuentes primarias

- A. Graves, S. Fernández, F. Gomez y J. Schmidhuber, [Connectionist Temporal Classification, ICML 2006](https://www.cs.toronto.edu/~graves/icml_2006.pdf), distinción entre ruta y texto y búsqueda por prefijos.
- Kraken 7.1, [decodificador CTC](https://github.com/mittagessen/kraken/blob/7.1/kraken/lib/ctc_decoder.py) y [wrapper de reconocimiento](https://github.com/mittagessen/kraken/blob/7.1/kraken/lib/models.py). Se captura el mismo softmax que utiliza su API.

Código propio; algoritmo CTC conocido y citado. Nueva revisión experta, identificación de lengua y traducción: **NOT_RUN**.
