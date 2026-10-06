# 23. Reconstrucción de los enlaces a folios de LJS 419

Fecha: 2026-10-06. Continuación del informe 22.

## Resultado ejecutado

Se cruzaron los números de imagen que aparecen junto a las transcripciones candidatas con las etiquetas de superficie del TEI primario de Penn. Ya no se depende exclusivamente del último encabezamiento reconocido por el OCR ni de una fórmula numérica inferida de la edición. El texto candidato conserva sus offsets y hashes sin alteraciones.

Resultado: 171 bloques enlazados a 171 folios primarios distintos; siete cambios de asociación respecto al encabezamiento OCR; cero duplicados de folio tras el cruce. Son enlaces documentales candidatos, no lecturas paleográficas validadas.

| Encabezamiento que heredaba el extractor | Folio del TEI primario por referencia de imagen | Explicación observada en el OCR |
|---|---|---|
| 5v | 6r | Encabezamiento siguiente perdido |
| 35v | 36r | Encabezamiento siguiente reconocido como 36x |
| 60r | 60v | Encabezamiento siguiente reconocido como 60vV |
| 64r | 79r | Encabezamiento 79r con prefijo que impedía reconocerlo al inicio de línea |
| 933v | 93v | Dígito duplicado |
| 988r | 98r | Dígito duplicado |
| 988v | 98v | Dígito duplicado |

La asociación 64r→79r merece especial atención: demuestra que heredar un encabezamiento anterior puede desplazar muchos folios un bloque. La fuente primaria confirma qué folio corresponde al archivo mencionado por la edición. No demuestra que la edición haya transcrito correctamente esa imagen.

## Cobertura incompleta localizada

De los 198 folios numerados esperados entre 1r y 99v, 27 no tienen bloque candidato por el criterio actual:

`5r, 5v, 41v, 44v, 45v, 47v, 48v, 49v, 50v, 51v, 52v, 53v, 54v, 55v, 56v, 57v, 58v, 61v, 62v, 63v, 64r, 64v, 66v, 68v, 71v, 72v, 73v`.

Esta lista no equivale a folios sin escritura. En particular, la nota candidata de 5v aparece sin el marcador de transcripción habitual, como ya se comprobó en el informe 22. Hay que revisar cada ausencia: algunas podrían ser páginas sin nota; otras, variaciones de formato u omisiones de extracción. Los folios preliminares y las cubiertas quedan fuera de este recuento.

## Código, evidencia y límites

```bash
python research_gpt6/code/reconcile_ljs419_folios.py \
  ljs419_extraction_audit.json LJS419_Erbario_ILLUMINATED_djvu.txt \
  ljs419_TEI.xml --out ljs419_folio_links.json
```

Ejecución real: Python/Linux, salida 0. Resultado en `results/ljs419_folio_links.json`, con hash de OCR y TEI, enlace web de cada imagen y alertas previas. El programa rechaza OCR cuyo hash no coincide con el auditado y comprueba el hash de cada bloque. Se verificaron la cobertura, los siete cambios, la ausencia de duplicados, la asociación del bloque desplazado a 6r y el rechazo de una fuente modificada. Estas comprobaciones pasaron; no validan el contenido medieval.

El enlace usa la última referencia TIFF anterior al marcador. Una referencia perdida podría quedar heredada: distancias mayores de 1.000 caracteres se marcan para revisión. En esta ejecución los 171 enlaces cumplieron el criterio, pero ese umbral es una alerta heurística y no garantiza correspondencia. Se conserva `validated_for_training: false` en todas las entradas.

El primer intento del parser esperaba el prefijo `fol.` en las etiquetas TEI y no enlazó ningún folio; se corrigió al comprobar que Penn emplea etiquetas como `1r`. El resultado publicado corresponde a la ejecución corregida.

## Consecuencia para la investigación

La recuperación de notas sin marcador y la separación de comentario editorial quedan ahora asociadas a imágenes concretas. El siguiente paso útil es revisar las 27 ausencias y depurar las notas, manteniendo transcripciones e intervenciones separadas. Aún no se ha entrenado un modelo lingüístico con estos candidatos ni se ha obtenido una equivalencia entre signos del Voynich y palabras.

Fuente primaria: [TEI de OPenn, LJS 419](https://openn.library.upenn.edu/Data/0001/ljs419/data/ljs419_TEI.xml). Metadatos bajo CC BY 4.0: University of Pennsylvania, Kislak Center, Oversize LJS 419. La procedencia y las limitaciones de la edición independiente constan en los informes 21 y 22.
