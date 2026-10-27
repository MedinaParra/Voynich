# 63 - Registro parcial: tres páginas y 280 polígonos de palabra candidatos

Fecha: **27 de octubre de 2026**. Rama `experiment/kraken-voynich`. [Ejecución 40518080288](https://github.com/MedinaParra/Voynich/actions/runs/40518080288), commit `4841278496f2bb0be82b5293bfe7c0a66d11d8ac`.

**Avance de preparación de datos: se transportaron candidatos EVA a Yale en f3r, f3v y f4v. El objetivo completo de cuatro páginas no pasó.** f4r falló los criterios de registro y sus 64 palabras quedaron excluidas. Los doce pares de páginas incorrectas fueron rechazados. No se volvió a entrenar Kraken y su error anterior de desarrollo, 73,8197 %, permanece como último resultado de reconocimiento; esta prueba no lo mejora ni produce una traducción.

El [protocolo 62](62_voynichese_registration_protocol.md), [plan](data/voynichese_registration_plan.json), código y fuentes se publicaron en el commit de ejecución antes de calcular las transformaciones. Las páginas ya estaban exploradas; es desarrollo geométrico, no una evaluación confirmatoria en hojas nuevas ni un método nuevo de desciframiento.

## Dos encuadres distintos de la misma transcripción EVA

Se verificó igualdad de secuencia en las **345 palabras** de las cuatro páginas entre el XML original de Voynichese y sus respuestas JSON actuales. La igualdad se comprobó antes de ajustar: no se emparejó texto reconocido por Kraken. Esa coincidencia vincula dos serializaciones de la misma tradición de transcripción; no aporta una lectura experta independiente ni alinea Boxer con EVA.

Las coordenadas corresponden a encuadres distintos. Para llevar el XML a la vista previa de 636×900 se ajustó una transformación afín con centros de palabras, reservando por hash parte de los centros. La caja de ancho cero de f3r se conservó señalada y se excluyó del ajuste y de los polígonos utilizables.

| Página | Centros reservados | Mediana con escalado simple | Mediana tras calibración | Percentil 90 tras calibración | Calibración |
| --- | ---: | ---: | ---: | ---: | --- |
| f3r | 26 | 31,08 px | 0,82 px | 1,47 px | Aceptada |
| f3v | 19 | 74,07 px | 0,76 px | 1,26 px | Aceptada |
| f4r | 17 | 30,94 px | 0,54 px | 1,19 px | Aceptada |
| f4v | 19 | 71,65 px | 0,79 px | 1,14 px | Aceptada |

Estas distancias están en **píxeles de la vista previa**, no del escaneo Yale. La comparación demuestra que cambiar solo la escala de los encuadres sería incorrecto para estos datos. No mide exactitud de lectura ni certifica el borde de cada signo.

## Registro independiente de las imágenes contra Yale

Se detectaron rasgos visuales SIFT en las fotografías, se filtraron coincidencias recíprocas y se ajustó una homografía sin usar los bloques espaciales reservados. Esa transformación se estimó con la imagen, sin utilizar las palabras de Kraken. Se conservaron los 16 pares intentados: cuatro del mismo folio y doce de folios distintos.

| Par del mismo folio | Coincidencias reservadas | Mediana de error Yale | Percentil 90 | Dentro de 5 px | Decisión |
| --- | ---: | ---: | ---: | ---: | --- |
| f3r→f3r | 110 | 1,19 px | 4,11 px | 95,45 % | Aceptado |
| f3v→f3v | 127 | 0,98 px | 4,53 px | 92,13 % | Aceptado |
| f4r→f4r | 93 | 1,77 px | **9,72 px** | **69,89 %** | **Rechazado** |
| f4v→f4v | 109 | 1,52 px | 4,25 px | 97,25 % | Aceptado |

En f4r, el percentil 90 supera el máximo fijado de 5 px y la fracción dentro de 5 px queda por debajo del mínimo de 80 %. La mediana pequeña no basta. No se relajaron esos límites después de observar el resultado ni se publicaron sus polígonos como aceptados.

Las otras páginas también tienen correspondencias atípicas: los errores máximos de puntos reservados son aproximadamente 570, 408 y 472 píxeles en f3r, f3v y f4v. Las medianas próximas a un píxel no describen todos los puntos. Los puntos son propuestas del mismo detector de rasgos, no correspondencias certificadas de forma independiente. Su reserva evita usarlos para ajustar la homografía, pero no convierte esta comprobación en una validación paleográfica.

Los doce pares incorrectos produjeron entre una y diez coincidencias recíprocas y ninguno alcanzó el soporte exigido. Se rechazaron los doce. Son controles entre estas cuatro páginas; no estiman una tasa universal de falsos positivos frente a todos los folios.

## Polígonos transportados y revisión visual

Solo se compusieron XML→vista previa→Yale cuando ambas etapas pasaron sus controles.

| Página | Palabras de la fuente | Polígonos candidatos exportados | Incidencia |
| --- | ---: | ---: | --- |
| f3r | 115 | 114 | Una caja de ancho cero, conservada y excluida |
| f3v | 83 | 83 | Referencias de fuente todavía provisionales |
| f4r | 64 | 0 | Registro de imagen rechazado |
| f4v | 83 | 83 | Referencias de fuente todavía provisionales |
| **Total** | **345** | **280** | **Sin revisión experta independiente** |

Se revisaron tres vistas generales y tres detalles superiores de las páginas aceptadas. Las cajas siguen aproximadamente la escritura visible; también se observan solapes y límites próximos a trazos de filas vecinas. No se verificaron una a una las 280 palabras. Son rectángulos de una anotación fuente transportados geométricamente, no máscaras de propiedad de tinta ni etiquetas expertas nuevas. [Registro de revisión](results/voynichese_registration/visual_review.json).

Superposiciones: [f3r](results/voynichese_registration/overlays/f3r.jpg), [f3v](results/voynichese_registration/overlays/f3v.jpg), [f4v](results/voynichese_registration/overlays/f4v.jpg); detalles de [f3r](results/voynichese_registration/overlays/f3r_detail.jpg), [f3v](results/voynichese_registration/overlays/f3v_detail.jpg) y [f4v](results/voynichese_registration/overlays/f4v_detail.jpg). La exportación de f4r contiene la fotografía sin polígonos aceptados, no una alineación validada.

## Ejecución, fallo local y auditoría

El intento local se detuvo con `SIGBUS` al importar el módulo nativo de OpenCV. No ejecutó los controles ni ajustó transformaciones. Se conserva el [registro](results/voynichese_registration/attempts/local_native_import_failure.json). Se trasladó el mismo método, antes de medir el registro, a Ubuntu de GitHub Actions con OpenCV 4.12.0.88, NumPy 2.2.6 y Pillow 12.3.0.

En CI pasaron cuatro controles sintéticos: composición conocida, recuperación de una geometría con outliers, partición espacial que mantiene duplicados juntos y rechazo de una caja de ancho cero. Después se completaron los 16 pares y se preservaron todos sus resultados. El script terminó con código 2 porque no se alcanzó el objetivo fijado de cuatro registros correctos aceptados. **El estado `failure` del workflow corresponde a ese criterio incumplido; no se oculta ni se reetiqueta como éxito completo.**

La [auditoría separada](code/audit_voynichese_registration.py) leyó los archivos XML/JSON originales, comparó textos, cajas y hashes, verificó las particiones y recalculó proyecciones, residuos, criterios y polígonos exportados: **10.142 comprobaciones, cero discrepancias**. No volvió a ejecutar SIFT/RANSAC, no verificó de forma independiente la máscara de inliers del ajuste robusto y no validó las lecturas. [Resultado](results/voynichese_registration/audit.json). Su estado de consistencia `PASS` convive con el criterio experimental global `FAIL_SOME_REGISTRATION_CHECKS`.

Se verificó el ZIP de 4.391.673 bytes contra el digest SHA-256 de GitHub: `9af5775142c9b5914e937d5e736a00a666abf83a76690a179aba6f3662b51e9b`. Contiene 11 archivos; el manifiesto por archivo es un inventario calculado, no una referencia externa individual.

Se preservan [resultado completo](results/voynichese_registration/result.json), [correspondencias y residuos](results/voynichese_registration/correspondences.json), [los 345 registros de palabra, incluidos los excluidos](results/voynichese_registration/word_polygons.json), [fuentes congeladas](results/voynichese_registration/inputs) y [procedencia](results/voynichese_registration/provenance.json). El artefacto tiene retención hasta el **26 de noviembre de 2026**; sus once archivos también se conservan en el repositorio.

```bash
python -m pip install -r research_gpt6/data/voynichese_registration_requirements.txt
python research_gpt6/code/test_register_voynichese_yale.py
python research_gpt6/code/register_voynichese_yale.py \
  --plan research_gpt6/data/voynichese_registration_plan.json \
  --repo research_gpt6 --out work/voynichese_registration
# El resultado actual devuelve código 2 por el criterio global incumplido.
python research_gpt6/code/audit_voynichese_registration.py \
  --bundle work/voynichese_registration --repo research_gpt6 \
  --output work/voynichese_registration_audit.json
```

## Qué cambia para la investigación

Ya hay un registro geométrico reproducible en tres páginas que permite estudiar parejas de imagen y transcripción EVA sin usar el propio OCR para decidir su ubicación. Se comprobó y corrigió un cambio de encuadre que habría introducido desplazamientos grandes con un escalado directo. Quedan pendientes f4r y la revisión de bordes y lecturas de fuente antes de convertir estos candidatos en referencia de entrenamiento.

Esta prueba todavía no determina qué parte del error previo de Kraken proviene de asociación de filas, recortes, anotaciones o del modelo. Tampoco alinea automáticamente EVA con Boxer, cuyos conteos de palabras difieren. No se entrenó un reconocedor con los nuevos candidatos ni se midió una nueva tasa de error. No existe aquí una clave lingüística, una traducción o un porcentaje de cercanía al desciframiento.

Fuentes: Voynichese Project, [datos y encuadres](https://github.com/voynichese/voynichese/blob/wiki/DataSets.md), XML original fijado y acreditado bajo Apache 2.0; [créditos fotográficos](https://github.com/voynichese/voynichese/blob/wiki/CreditsAndCopyright.md) a Yale University Library, Beinecke MS 408. [Métodos de rasgos y homografías de OpenCV](https://docs.opencv.org/4.x/d1/de0/tutorial_py_feature_homography.html). [Licencia y atribución de entradas](results/voynichese_registration/inputs/NOTICE.md). Código nuevo propio; no se incorpora el código compilado de la aplicación Voynichese.
