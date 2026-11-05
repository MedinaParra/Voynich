# Un lector alienígena: igualdades entre signos y significados rivales

5 de noviembre de 2026. «Alienígena» es una metáfora de un lector sin lengua o alfabeto conocidos, no una hipótesis de autoría extraterrestre.

La pregunta ejecutable es: ¿las palabras vecinas comparten signos de una forma que persiste fuera de las hojas usadas para ajustar el modelo, después de conservar posición, longitud y composición de cada página? Una segunda perspectiva pregunta si ese resultado puede elegir un significado. El [plan](data/alien_protocol_plan.json), código y semillas se publican antes de calcular las métricas. No se reajustarán después de verlas.

## Conservar evidencia antes de comprimirla

Se mantiene cada pareja original y su código conjunto de igualdad. Por ejemplo, `ab|ba` se convierte en `01|10`, mientras `ab|cd` produce `01|23`. Un diccionario inverso reconstruye ambos grupos; un renombrado global de las unidades ya fijadas no altera las igualdades. En la proyección agrupada esa invariancia se prueba después de aplicar las seis agrupaciones EVA; no equivale a descubrir unidades ni a renombrar caracteres antes de agruparlos. Codificar cada palabra por separado perdería precisamente la relación que buscamos. Este código conserva la geometría de igualdades del par, no sus significados ni sus sonidos.

Para puntuar se usa una medida deliberadamente pequeña: C es el número de signos distintos compartidos, limitado a tres. Los modelos normalizados predicen sus cuatro resultados condicionando en longitudes y repetición interna de ambas palabras. MF añade la posición del par en el renglón; M0 no. La medida es un diagnóstico insuficiente para traducir. Los originales y códigos completos se conservan para que esa compresión no sustituya la evidencia.

MF se ajusta sobre pares reales y sobre ocho permutaciones que intercambian palabras completas dentro de página × longitud exacta × posición inicial/intermedia/final. Los conteos nulos se promedian antes de aplicar el mismo prior Dirichlet. La ventaja real/nulo se mide en otras hojas físicas, fijadas por hash antes de medir. Otras199 permutaciones reservadas calibran la cola. La permutación conserva el vocabulario, las longitudes, la posición y la composición de página; no es una reproducción de un mecanismo histórico.

## Sensibilidades y controles

Se ejecutan ocho proyecciones fijadas: VT/ZL × comas separadas/unidas × caracteres EVA/seis agrupaciones operativas ya usadas en este proyecto. Estas proyecciones se solapan y no son ocho testimonios históricos independientes. Se exige que todas superen el criterio para hablar de una señal compartida; se muestran todas aunque fallen. Las hojas ya se han explorado antes en este proyecto: la separación es interna al ensayo, no una reserva global nueva.

El parser conserva únicamente renglones completos de texto de párrafo con palabras literales. Una duda, laguna de dibujo, separador vacío o carácter no admitido descarta el renglón entero y se registra. No se unen palabras a través de una laguna ni se recorta una duda y se renumera lo restante. Esta selección reduce cobertura y puede sesgar la muestra.

Los controles son: instrucciones sintéticas independientes; las mismas con marcadores posicionales; instrucciones con repetición Markov; y una concordancia morfológica de juguete. La primera pareja no debería producir señal residual; la repetición debería detectarse. La concordancia es una explicación rival y puede activar el mismo diagnóstico. Todos son generadores inventados y conocidos por quienes preparan el ensayo, no pruebas ciegas o referentes históricos.

## El adversario de los significados

Se construyen dos claves de significado incompatibles para exactamente el mismo mensaje sintético. Ambas vuelven a codificar sus instrucciones al mismo texto observado. Los códigos de igualdad, las predicciones y los scores reciben solamente el texto, por lo que no pueden distinguirlas. Es un certificado explícito de ambigüedad, no una traducción alternativa del Voynich. Hace falta un ancla externa para romper esa simetría.

## Antecedentes y alcance

Las variantes de posición tienen antecedentes claros en Bowern y Lindemann, [*The Linguistics of the Voynich Manuscript* (2021)](https://alumniacademy.yale.edu/sites/default/files/2021-07/The%20Linguistics%20of%20the%20Voynich%20Manuscript.pdf). La discusión de unidades y fronteras incluye Rozanova y Temerev, preprint [arXiv:2608.17096](https://arxiv.org/abs/2608.17096). No se afirma que estudiar formato, vecindad o codificación por igualdades sea nuevo. Este ensayo combina un diagnóstico reproducible y un adversario semántico para limitar lo que podría afirmarse.

Un resultado positivo indica acoplamiento de igualdades bajo el nulo elegido. También puede deberse a morfología, repetición o copia sin significado. C es simétrico entre las dos palabras: tampoco identifica una dirección de lectura. Un resultado negativo limita esta medida y selección, no demuestra que el libro carezca de lenguaje. Ninguno valida una traducción, identifica una lengua o reentrena Kraken.
