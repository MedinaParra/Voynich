# 62 - Registro geométrico Voynichese–Yale, desarrollo sobre cuatro páginas

Fecha: 27 de octubre de 2026. Base: `e6cbf2a0ca491ff5eec4f2bff73278a7008ead27`, rama `experiment/kraken-voynich`.

Los ensayos 59/61 dejaron el reconocimiento en 73,8 % de error convencional en desarrollo. Este ensayo comprueba otra pieza: transportar las coordenadas de palabras de una fuente EVA al escaneo Yale sin usar las predicciones de Kraken para ajustar la geometría. No entrena un modelo ni mide traducción.

## Fuentes y dos transformaciones

Se mantienen f3r, f3v, f4r y f4v, ya exploradas. El archivo XML de Voynichese sigue fijado por SHA-256 `402d99ca8191ae53a4f25912ee0af0a7e6b6d9a3714b2beaf86404a27d5b7ad5`. Las imágenes Yale son las congeladas en el ensayo 59. Se adquirieron las imágenes de vista previa y los datos de coordenadas que sirve actualmente Voynichese, preservando URLs, tamaños y hashes.

En la comprobación preliminar de esquema, antes de estimar transformaciones, se verificó que las 345 palabras de las cuatro páginas conservan exactamente su secuencia EVA entre el XML y los datos actuales. Sus coordenadas están en encuadres distintos. Se calibra XML→vista previa con centros correspondientes de palabras de área positiva y un modelo afín. La caja de ancho cero se conserva señalada; no se inventa un ancho. La igualdad de secuencia entre estas dos serializaciones no acredita equivalencia con Boxer ni una transcripción experta independiente.

Separadamente se registra la imagen de vista previa contra Yale mediante SIFT, coincidencias L2 recíprocas con prueba de razón 0,70 y homografía RANSAC. El código es propio y utiliza las API de OpenCV; no copia código de la aplicación Voynichese.

## Particiones y criterios fijados antes de estimar

- Calibración de palabras: reserva por hash de folio/índice, módulo 5 igual a cero. Ajuste sólo en los demás centros. RANSAC a 3 píxeles de vista previa; al menos 20 inliers de ajuste y 8 centros reservados. En reserva se exige mediana ≤3 píxeles, percentil 90 ≤6 y fracción dentro de 6 píxeles ≥0,80.
- Registro de imágenes: máximo 6.000 puntos SIFT por imagen; `contrastThreshold=0.02`. Reserva de coincidencias por bloques de una cuadrícula de 8×8 en la imagen fuente: `(columna + 2*fila) % 5 == 0`. No se usan para ajustar la homografía. RANSAC a 3 píxeles Yale, 10.000 iteraciones máximas, confianza 0,999; al menos 50 inliers de ajuste y 10 coincidencias reservadas. En reserva: mediana ≤2 píxeles, percentil 90 ≤5 y fracción dentro de 5 píxeles ≥0,80. Los inliers de ajuste deben abarcar al menos la mitad del ancho y alto de la fuente.
- Se ejecutan los 16 pares de las cuatro vistas previas y cuatro imágenes Yale: cuatro pares correctos y doce de folios distintos. Todos se conservan, incluidos fallos y transformaciones rechazadas. El objetivo de control es aceptar los cuatro correctos y rechazar los doce incorrectos; no se retocan criterios después de ver qué par pasa.
- Semilla 20261027, dos hilos de OpenCV, modelos geométricos fijos. No se escoge entre varias arquitecturas según resultados.

La composición sólo autoriza candidatos de polígonos EVA en Yale para una página que pase ambas etapas. Se conservan los cuatro vértices, las incidencias de geometría y las cajas originales. El error por simple escalado de encuadres se informa como comparador geométrico.

## Alcance de la comprobación

Las coincidencias reservadas de imagen son propuestas del mismo detector de rasgos. Son una comprobación geométrica sin ajuste de esos puntos, no correspondencias certificadas por un experto ni una nueva muestra estadística del manuscrito. Los centros de palabra de calibración derivan de la misma tradición de transcripción, no de una segunda lectura independiente.

Se revisarán visualmente las superposiciones y se conservarán sus incidencias. No se convertirá el error de registro en precisión de glifos o palabras; una caja bien transportada puede estar mal anotada desde el origen. No se alinearán automáticamente Boxer y EVA por índice: sus cantidades de palabras difieren.

La ejecución será en CPU de GitHub Actions con dependencias fijadas. El intento local de controles se detuvo al importar el módulo nativo de OpenCV, con `SIGBUS`, antes de ejecutar los tests o estimar transformaciones; se conserva el registro. Se traslada el mismo método a un runner Ubuntu, sin mediciones previas de registro. El plan y el código se publicarán antes de calcular las transformaciones. No se entrena Kraken. Licencias y atribución de datos: Voynichese Project, datos XML Apache 2.0; fotografías procedentes de Yale. Identificación de lengua y traducción: **NOT_RUN**.
