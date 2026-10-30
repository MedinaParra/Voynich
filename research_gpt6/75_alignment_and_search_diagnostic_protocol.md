# 75 — Diagnóstico de asociaciones, recortes y búsqueda CTC

30 de octubre de 2026. Rama `experiment/kraken-voynich`. Base `aa132207ccb9128bf88e4b5e31e9138a5c0dd9f7`.

Los dos reentrenamientos del ensayo 72 no mejoraron las formas no vistas. El haz del ensayo 74 redujo ocho errores EVA en la hoja 7, pero mantuvo 0/76 formas no vistas exactas. Antes de seguir aumentando épocas o ancho del haz, se examinan dos posibles obstáculos con entradas ya preservadas. Este es un diagnóstico exploratorio sobre datos conocidos, sin nueva reserva ciega.

## Perspectiva de probabilidades

Se usa únicamente la primera pasada congelada del ensayo 73: 282 matrices tiempo×clase, su codec y las predicciones ya publicadas. No se vuelve a inferir, entrenar o seleccionar una pasada.

Para cada referencia y salida del haz se calcula por programación dinámica la probabilidad CTC de la cadena completa, sumando **todas** sus alineaciones, en logaritmos de doble precisión. Se compara la masa exacta de ambas cadenas. Si otra cadena tiene más masa que la referencia, esa referencia no puede ser el máximo global de ese modelo, aunque se ampliara indefinidamente la búsqueda. Esto distingue un fallo que puede atribuirse a búsqueda de una incompatibilidad entre señal del modelo y etiqueta candidata; no demuestra cuál de las dos es paleográficamente correcta.

También se puntúa cada texto único de la misma página y longitud EVA. La referencia forma parte explícita de ese catálogo: son rangos diagnósticos con conocimiento de etiquetas, **no** predicciones de reconocimiento ni un diccionario que se adopte para mejorar artificialmente el CER. Se preservan todos los candidatos y empates; los catálogos de un único texto se excluyen del resumen de rangos. No se calculan p-valores a partir de palabras como si fueran hojas independientes.

Se cuenta el mínimo temporal necesario, incluyendo blancos entre caracteres repetidos. Ya se inspeccionó este punto antes de fijar el plan: ninguna de las 282 referencias supera la capacidad temporal de su matriz. Se declara esa inspección previa; no se presenta como resultado confirmatorio nuevo.

## Perspectiva de geometría y píxeles

Se verifican las 724 parejas y máscaras del dataset fijo. En cada recorte se calcula la unión de intersecciones con las máscaras de otras palabras del mismo folio, usando las mismas coordenadas Yale y la dilatación de cuatro píxeles existente. Se conservan todos los vecinos e intersecciones. Un píxel compartido indica solapamiento de anotaciones, no propiedad real de un trazo.

Se informa la fracción de máscara compartida y, como aproximación descriptiva, la fracción de píxeles oscuros compartidos. El umbral oscuro es la mediana de gris dentro de la máscara menos 40 unidades; se repite con 20 y 60 sin escoger después la cifra favorable. Estos umbrales no son una segmentación validada de tinta. Se fijan los grupos de solapamiento ≤1 %, entre 1 y 25 %, y ≥25 %. Se informa CER por hoja, vocabulario y longitud, preservando denominadores y grupos vacíos.

No se quitan píxeles ni se corrigen etiquetas automáticamente. No se identifica el renglón propietario de un trazo, ni se identifica una lengua. La correlación entre solapamiento y error no demuestra causalidad y puede estar confundida por longitud, formas, posición y calidad de las cajas.

## Controles y conservación

El plan fija hashes de datos, modelo, codec, posteriors y resultados previos. Se verificará el cálculo CTC con enumeración exhaustiva de caminos diminutos, caracteres repetidos, ceros, secuencia vacía y probabilidades muy pequeñas. Las intersecciones se controlarán con máscaras conocidas en encuadres desplazados. Una segunda implementación en probabilidades reescaladas verificará las masas calculadas en logaritmos; otra representación de las máscaras verificará los solapamientos.

Se publican este protocolo y el plan antes del diagnóstico completo. Se guardan código, controles, resultados completos por muestra, rangos, auditoría y procedencia. Las vistas inspeccionadas previamente son las del ensayo 66 y la hoja de recortes de f4r; esa inspección tampoco es revisión experta independiente. Las referencias siguen siendo candidatas de la misma tradición de transcripción, no una segunda lectura independiente.

La documentación primaria de [Voynichese](https://github.com/voynichese/voynichese/blob/wiki/DataSets.md) describe asociaciones espaciales semiautomáticas y reconoce incertidumbre de límites de palabra. Su propia estimación histórica de errores no se usa como una tasa validada para nuestro dataset. Los documentos y la probabilidad CTC no resuelven esa incertidumbre.

Entrenamiento, inferencia nueva, revisión paleográfica independiente y traducción: **NOT_RUN**.
