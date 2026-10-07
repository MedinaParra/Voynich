# 41. Reutilización visual interna: auditoría y recuperación textual

Fecha: 2026-10-07 (UTC). Exploratorio. Sin glosas ni traducción.

## Resultado principal

Se fijaron siete correspondencias visuales **propuestas** entre dibujos herbales y fragmentos farmacéuticos con rótulos Lf inequívocos. Ninguno de los siete rótulos aparece como token exacto inequívoco en el texto herbal correspondiente. La recuperación por semejanza textual no coloca el par correcto primero en ninguna dirección. No se trata como refutación universal de nombres: puede haber flexión, segmentación distinta, palabras ambiguas, función diferente o correspondencias visuales incorrectas.

## Qué se corrigió en el planteamiento

La tabla 9 de IVTFF 2.0 distingue Lc (rótulo de recipiente) de Lf (rótulo de fragmento vegetal). Su clasificación indica proximidad a un elemento dibujado, no una palabra traducida. El rótulo de una jarra no debe convertirse en el nombre de una planta vecina.

Fuente de tipos: https://voynich.nu/software/ivtt/IVTFF_format.pdf , página impresa 21.

Las correspondencias se tomaron de la descripción de René Zandbergen: https://voynich.nu/q19/index.html . Allí se distinguen equivalencias aparentes de semejanzas parciales. Se conservaron esas categorías sin convertirlas en identificaciones taxonómicas. El manifiesto mantiene `visual_verified_here=false`: una inspección dirigida por un par ya propuesto no equivale a verificar su identidad a ciegas. Dos pares tienen ahora `visual_inspected_here=true` y observaciones del original, detalladas más abajo.

Hay discrepancias con notas antiguas del corpus. En particular, la nota de f23r cita f102r2[3,1], igual que f18v, mientras la descripción consultada relaciona f18v con 212 y f23r con 213. La nota antigua de f90v2 cita f100r[1,3], mientras la descripción consultada propone semejanza con 136 en f100v. No se modificó ni «corrigió» silenciosamente el corpus: el manifiesto declara la fuente utilizada para este piloto. Estas diferencias refuerzan la necesidad de cotejar imágenes originales.

## Recuperación ejecutada

Corpus EVA congelado: blob `2a4533ab9bdfa85db9bad602d590978953055df1`.

Extracción de párrafos P y rótulos Lf, excluyendo formas ambiguas. Comentarios IVTFF y marcas de párrafo se eliminan; interrupción por dibujo se trata como separador; no se rescatan partes alfabéticas de palabras ambiguas. El identificador numérico de fragmento se conserva y no se confunde con los sufijos de recipientes.

TF-IDF de n-gramas de caracteres (2–4, `char_wb`) con coseno, fijado antes de ver puntuaciones. En la dirección rótulo → página, el vectorizador se ajusta al conjunto de 95 folios H de Currier A/mano 1 con al menos 20 tokens, y compara cada rótulo con sus párrafos. En la dirección página → rótulo, se ajusta al conjunto de 164 rótulos Lf literales A/mano 1. Los conjuntos tienen objetivos y cardinalidades distintos: no comparar sus exactitudes como prueba de cifra frente a notación.

Es recuperación transductiva sobre corpus conocido, **no** validación predictiva en corpus nuevo. Se conserva el rango mínimo, máximo y medio para empates; las formas repetidas no se presentan como identificación única.

| Herbal | Fragmento/rótulo farmacéutico | Apariciones exactas en herbal | Rango página / 95 | Rango rótulo / 164 |
|---|---|---:|---:|---:|
| f96v | 116: sochorcfhy | 0 | 94 | 89 |
| f13v | 133: opchor | 0 | 69 | 24 |
| f90v2 | 136: ykchochdy | 0 | 86 | 53 |
| f18v | 212: koldarod | 0 | 13 | 92 |
| f23r | 213: odalydary | 0 | 9 | 50 |
| f36r | 225: sarol | 0 | 12 | 74 |
| f19r | 240: loralody | 0 | 14 | 81 |

Los siete rótulos proceden de solo **dos hojas físicas**, f100 y f102. No son siete réplicas independientes. No se calculó un p agregado: no se ha calibrado la dependencia entre consultas ni la selección visual. Cuatro rangos de página relativamente altos tampoco justifican escoger solo esos cuatro casos ni ajustar ahora los n-gramas para mejorar el resultado.

## Comparaciones visuales sin rótulo individual utilizable

f1v ↔ fragmento 204; f37v ↔ 203; f47v ↔ 205; f32v ↔ 206. No hay un Lf literal individual con esos identificadores en el corpus. La descripción de f102r1 sitúa su único rótulo vegetal en el fragmento superior, no en los dos inferiores que se comparan con páginas herbales. El corpus contiene rótulos de recipientes cercanos: eso no rellena el dato faltante.

No trasladar `otodeeodor` o `ddardsh` a f1v como nombre de planta mediante cercanía: el primero corresponde a otro fragmento en el esquema y el segundo a un recipiente. Una glosa exigiría otra evidencia.

## Verificación

`code/internal_reuse_retrieval.py` y `data/internal_reuse_anchors.json` producen `results/internal_reuse_result.json`. Cuatro controles científicos pasan: empates no crean ganador único, recipientes no pasan a rótulos de planta, formas ambiguas no generan recurrencia exacta y continuaciones de párrafo no se pierden.

```sh
python -m pip install 'numpy==2.3.5' 'scikit-learn==1.8.0'
curl -L --fail -o voynich_eva.txt 'https://raw.githubusercontent.com/cesarjz/Voynich/47e6a77dc9d5cd570c375f4aff710fa4a0567278/corpus/voynich_eva.txt'
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s research_gpt6/code -p test_internal_reuse_retrieval.py -v
OPENBLAS_NUM_THREADS=1 python research_gpt6/code/internal_reuse_retrieval.py --corpus voynich_eva.txt --anchors research_gpt6/data/internal_reuse_anchors.json --out research_gpt6/results/internal_reuse_result.json
```

Python 3.12.14, NumPy 2.3.5, scikit-learn 1.8.0. Ejecución local real, códigos de salida 0, huellas en `results/internal_reuse_checks.json`.

El workflow `.github/workflows/dual-perspective-voynich.yml` incorpora estos cuatro controles y la recuperación, con las dos dependencias fijadas. La repetición nueva se verificará mediante sus logs; su configuración no cuenta por sí sola como ejecución remota.

## Cotejo de originales Yale: alcance y resultado

El catálogo devolvió 403, pero el servicio público IIIF sí permitió descargar las imágenes. Se inspeccionaron la apertura farmacéutica con f102r1 y f102r2 (`child_oid=1006251`), un detalle de f102r2 y los originales de f18v (`1006109`) y f23r (`1006118`). URLs, dimensiones y SHA-256 figuran en `data/internal_reuse_visual_audit.json`. No se presentan las miniaturas de otro sitio como sustituto de esos originales.

| Par previamente propuesto | Observación dirigida sobre imágenes originales | Límite |
|---|---|---|
| f18v ↔ 212, parte inferior izquierda de f102r2 | Raíz horizontal anaranjada con lóbulos, zona bulbosa vertical y prolongación que vuelve en curva por debajo; composición distintiva compatible en ambas figuras | Semejanza visual, sin especie ni nombre establecidos |
| f23r ↔ 213, parte inferior derecha de f102r2 | Rizoma horizontal segmentado con extremos circulares, inserciones superiores y raicillas inferiores; la disposición farmacéutica es más reducida | Semejanza visual, sin demostrar identidad botánica |

En f102r2 se observan dos cadenas cortas aisladas sobre las dos figuras inferiores, coherentes con los Lf 212 y 213 del corpus. La imagen no aporta por sí sola su función lingüística: no llamar «nombre» a una cadena solo por su posición. En f102r1 los dibujos inferiores no muestran sendos rótulos aislados comparables; esto es compatible con la ausencia de Lf 203/204 en el corpus.

La asociación de f23r con 213, frente a la nota antigua que repetía la posición de 212, resulta visualmente plausible: f23r tiene un rizoma segmentado, f18v la raíz lobulada. La observación no modifica la transcripción congelada. Los otros cinco pares puntuados no se cotejaron aquí. No hubo emparejamiento ciego entre candidatos, segundo anotador, medición automática ni prueba de rareza de estos motivos; todos los pares siguen siendo tentativos. La inspección se hizo después de calcular la recuperación y no se usó para escoger ni optimizar parámetros o retirar pares.

## Repetición remota del harness anterior

Actions run 37553560808, job 112574448642, commit e65cf8dd27fc050541d7f0aebc7344e77320528d: completado con éxito. Reproduce n=201, p conjunto=0,529 y ganancias negativas en ambas direcciones. Diferencia local/remoto de ganancia forward del orden de 10^-16, tolerancia 10^-12; no cambia ningún juicio. La repetición verifica reproducibilidad computacional; no añade una muestra semántica.

## Decisión

La vía «misma figura → mismo nombre literal presente en ambos textos» no encuentra apoyo en esta muestra y este filtro. El cotejo de dos pares hace menos probable que esos dos resultados negativos se expliquen únicamente por una comparación de formas claramente equivocada; no mide esa probabilidad ni valida los otros cinco pares. La conclusión es condicional a que el mismo nombre debía estar escrito explícitamente en ambos lugares: no descarta una lengua, una cifra de sustitución o un nombre que simplemente no aparezca en un párrafo.

No proponer nombres de especies. El siguiente experimento debe distinguir funciones locales (objeto, parte, preparación), con roles fijados por posición e imagen antes de leer las palabras, y reservar pares nuevos para evaluación. Una transformación aprendida para acomodar estos siete pares requiere después pares nuevos; estos ya no cuentan como holdout.

Ejecución: PASS_EXECUTED. Ancla semántica: NOT_VALIDATED. Traducción: NOT_RUN. No hay un desciframiento ni un método declarado inédito.
