# 64 - Corrección local de residuos geométricos, con validación espacial

Fecha: 27 de octubre de 2026. Base: `a6782f473df5e423c27d780ca830686e84b19e61`, rama `experiment/kraken-voynich`.

El ensayo 63 aceptó tres páginas y rechazó f4r: en sus puntos reservados, el percentil 90 era 9,72 píxeles Yale frente al máximo fijado de 5. La calibración de coordenadas XML→vista previa pasó en las cuatro páginas. Se conserva ese resultado sin modificar sus umbrales ni adjudicar retrospectivamente el éxito a f4r.

## Diagnóstico exploratorio previo

Se examinó únicamente la partición de ajuste ya exportada. Entre las correspondencias con residuo global ≤20 píxeles, predecir el residuo de un punto por la mediana de vecinos de ajuste redujo el percentil 90 de error residual de f4r de 5,43 a 1,97 píxeles. Se excluyeron vecinos a ≤0,5 píxeles fuente para evitar duplicados directos. Es un diagnóstico exploratorio sobre el ajuste anterior; no es puntuación reservada ni prueba de deformación física. Se conserva el cálculo y no se presenta como otra mejora de OCR.

Esto motiva un método fijado antes de ejecutar la nueva comparación: una homografía global más una corrección local robusta. La estructura espacial también podría reflejar sesgos del detector o del procesado de imágenes; este ensayo no identificará por sí solo su causa física.

## Entradas, particiones y métodos fijos

- Se usan las correspondencias SIFT preservadas del ensayo 63, con hashes fijados. No se vuelven a detectar rasgos ni se seleccionan nuevas coincidencias según la mejora de esta prueba. Los puntos siguen siendo propuestas del detector, no correspondencias expertas.
- Se ejecutan las cuatro páginas como desarrollo, con cinco particiones de bloques de la cuadrícula fuente 8×8: se reserva sucesivamente cada valor de `(columna + 2*fila) % 5`. Se conservan todos los puntos reservados, incluidos los atípicos. Los puntos de ajuste a ≤3 píxeles fuente de cualquier reservado se excluyen del ajuste para evitar casi duplicados a través de la frontera.
- La homografía se ajusta de nuevo únicamente con la partición de ajuste: RANSAC a 3 píxeles Yale, máximo 10.000 iteraciones, confianza 0,999 y semilla 20261027 más número de partición. Se registra la exclusión por banda de guarda. Es una comparación nueva, no una afirmación de reproducción exacta de las matrices anteriores.
- Tres condiciones emparejadas por página/partición: homografía global; homografía más mediana espacial de residuos; y la misma corrección después de permutar los residuos de ajuste entre posiciones.
- Corrección espacial: conservar residuos de ajuste de norma ≤20 píxeles Yale; agrupar posiciones fuente en celdas de 0,1 píxeles y tomar sus medianas; usar como máximo 20 vecinos dentro de 80 píxeles fuente, con al menos tres grupos. La corrección es la mediana por componente, limitada a norma 20; sin soporte suficiente se usa corrección cero. No se buscan otros radios o cantidades de vecinos después de observar la comparación.
- El control permutado usa las mismas posiciones y vectores, con una permutación fija por caso; destruye la asociación espacial sin cambiar su distribución. No es otra muestra independiente ni se utilizará para exportar palabras.

## Criterios y uso de los resultados

Cada caso conserva los límites anteriores: al menos 50 inliers globales de ajuste, cobertura de al menos la mitad de ancho y alto fuente, al menos 10 puntos reservados, mediana ≤2 píxeles Yale, percentil 90 ≤5 y fracción dentro de 5 ≥0,80. Se puntúan los mismos puntos reservados en las tres condiciones; ningún resultado difícil se elimina de la puntuación.

Sólo se habilitarán candidatos de f4r si la corrección espacial pasa esos criterios en **las cinco particiones**, y su percentil 90 agrupado es menor que el global y que el control permutado. Si eso ocurre, se ajustará el mapa final con todas las correspondencias de f4r; no se confundirá ese ajuste final con otra evaluación. Se comprobará la orientación de una cuadrícula de 17×25 puntos y la geometría de los polígonos de palabra antes de exportarlos. Esta comprobación de cuadrícula no demuestra ausencia de pliegues a todas las escalas.

Si no pasa, se conservará el rechazo y no se agregarán sus 64 palabras como aceptadas. Las otras tres páginas se ejecutan como controles de desarrollo; este ensayo no sustituye silenciosamente sus referencias anteriores.

## Límites y trazabilidad

Son datos y páginas ya explorados, con hipótesis motivada por resultados anteriores. Las cinco particiones están relacionadas y no representan cinco hojas nuevas ni cinco réplicas independientes. La mejora geométrica no se interpretará como exactitud de glifos, lectura correcta, identificación de lengua o traducción. La validación de correspondencias sigue condicionada al detector.

Se ejecutará en GitHub Actions con el entorno geométrico fijado del ensayo 62. Los controles numéricos del método local no necesitan importar OpenCV y se pueden ejecutar localmente. Se preservarán todos los casos, puntos, predicciones geométricas, controles permutados y fallos. Código propio; fuentes y atribución permanecen las del ensayo 63. OCR y traducción nuevos: **NOT_RUN**.
