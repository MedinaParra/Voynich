# 43. Enlace de bordes y copia local: predicción frente a generación

7 de octubre de 2026. Exploratorio; traducción NOT_RUN; originalidad NOT_ESTABLISHED.

## Resultado que cambia nuestra lectura

Añadir un canal de copia/modificación al modelo de enlace mejora ligeramente la predicción de la siguiente cadena en las cinco particiones y con ambos tratamientos de comas. La reducción media es 0,00335/0,00419 bits por token, alrededor del 0,03% de la pérdida del modelo de enlace. El criterio numérico local fijado se cumple, pero la generación libre sigue fallando en repeticiones, variantes y riqueza de formas. Hay una mejora predictiva pequeña; no se ha encontrado un mecanismo que explique el manuscrito ni una traducción.

Este experimento sigue la carencia del informe 19: allí un enlace sin significado imitaba los bordes y fallaba otras firmas. Aquí se añade copia con una edición, vocabulario abierto y separación por mano/Currier. Es un paso nuevo en nuestro repositorio; la autocita y los análisis de estructura textual ya tienen antecedentes. No se presenta como un método jamás explorado.

## Protocolo fijado y fuente

El [commit de protocolo 25db5028e465d2d5e9f7755b671a03527ed20230](https://github.com/MedinaParra/Voynich/commit/25db5028e465d2d5e9f7755b671a03527ed20230) precede al primer ajuste y puntuación del nuevo modelo. Se habían inspeccionado metadatos y los resultados anteriores. Es una fijación trazable dentro del mismo proyecto, no prerregistro externo ni reserva semántica nueva. No se cambiaron parámetros después de ver estas cifras.

Fuente EVA: commit externo 47e6a77dc9d5cd570c375f4aff710fa4a0567278, blob 2a4533ab9bdfa85db9bad602d590978953055df1, SHA-256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc. Solo párrafos; se excluyen rótulos. Las incertidumbres y huecos de dibujo rompen la adyacencia; nunca se cruzan líneas. Comas separadas y unidas. fRos queda excluido porque no se inventa su asignación a una hoja física.

Tres estratos grandes con metadatos conocidos: A/mano 1, B/mano 2 y B/mano 3. Se agrupan recto, verso y todos los paneles por f+numero: 89 grupos de hoja. Se ordenan lexicográficamente y se retiene índice módulo cinco, una partición cada vez. Mano y Currier están condicionados; sección temática y geometría fina siguen siendo posibles factores de confusión. No se retiene un cuaderno completo y la dependencia entre hojas puede continuar.

## Tres generadores probabilísticos

1. **Independiente:** distribución de palabras de entrenamiento por cuatro bandas dentro de cada tramo limpio, mezclada al 95% con un 5% de Markov de caracteres que admite cadenas nuevas. La banda no representa siempre una línea física completa.
2. **Enlace:** repondera el primer carácter según el último del token anterior y banda, con suavizado de 20 hacia la base. Después conserva la distribución interna de la base.
3. **Enlace + copia:** mezcla el enlace con identidad, inserción, eliminación o sustitución de un carácter del token inmediatamente anterior. Se estiman operaciones, zonas de edición y caracteres en entrenamiento. Se agregan las diferentes rutas que producen la misma cadena. La mezcla se ajusta con 30 iteraciones EM, inicial 0,1, sin consultar la reserva.

El alfabeto es ASCII EVA literal, no glifos ni fonemas establecidos. Las cadenas tienen entre 1 y 64 caracteres; la generación no consulta vocabularios ni longitudes de palabras del test. Las tres distribuciones están normalizadas y tienen soporte abierto por el canal Markov. No hay mensaje, diccionario traducido ni significado en estos modelos.

La primera perspectiva puntúa la siguiente palabra real condicionada al pasado real (teacher forcing). La segunda genera secuencias completas usando sus propias salidas anteriores. Para generar se condiciona solo el número de tokens por tramo y el estrato de la geometría retenida; no se imponen sus iniciales/finales, palabras ni longitudes. Predicción condicionada y generación libre son pruebas diferentes.

## Predicción en hojas retenidas

| Comas | Tokens | Pares | Enlace: bits/token | Enlace+copia: bits/token | Reducción bits/token | Reducción relativa |
|---|---:|---:|---:|---:|---:|---:|
| split | 31368 | 26294 | 11.524502 | 11.521154 | 0.003348 | 0.029% |
| join | 29083 | 24042 | 12.552285 | 12.548091 | 0.004194 | 0.033% |

Las ganancias equilibradas por hoja son 0,003089 y 0,003883 bits/token, también positivas. El signo es positivo en las cinco particiones de ambos modos; se cumplen las condiciones locales fijadas. Esto no es un p-valor ni diez réplicas independientes: entrenamiento se solapa entre particiones y ambos parsers provienen de los mismos trazos.

B/mano 2 concentra la mayor ganancia: 0,00759/0,01010 bits/token. A/mano 1 da 0,00139/0,00177; B/mano 3, 0,00093/0,00054. Los pesos de copia ajustados son muy pequeños: desde aproximadamente 10^-9 hasta 0,000652 (0,0652%). No describen una tasa histórica de copia. La base empírica y el peso se ajustan sobre los mismos tokens de entrenamiento, lo que puede favorecer a la base; calibrar ese peso con validación interna sería otro experimento, no una corrección oculta de este resultado.

También se sustituye el contexto anterior por otra palabra de entrenamiento de igual longitud y mismo final, en el mismo estrato, sin consultar el objetivo. El enlace conserva exactamente su probabilidad; el modelo con copia favorece en promedio el contexto real en unos 0,00037–0,00793 bits/token según grupo/modo. Esto es un sondeo descriptivo con cinco sustitutos por par, no una intervención causal ni un test formal de permutación. Las ubicaciones sin alternativa quedan registradas, no se rellenan con falsos controles.

## Generación libre: la deuda del mecanismo

Sobre la partición 0 se hicieron 30 simulaciones por modelo y modo, con 19 barajados por muestra para exceso MI. Rangos: segundo y penúltimo valor de 30, descriptivos; no intervalos de confianza ni rechazo estadístico de una familia histórica.

| Firma | Manuscrito, split | Enlace+copia, mediana split | Manuscrito, join | Enlace+copia, mediana join |
|---|---:|---:|---:|---:|
| MI de bordes, bits | 0,21571 | 0,19826 | 0,18495 | 0,17089 |
| Exceso MI sobre barajado, bits | 0,18023 | 0,16628 | 0,15045 | 0,13949 |
| H1 interno de caracteres, bits | 1,97407 | 2,00938 | 1,99574 | 2,03314 |
| Repetición exacta adyacente | 1,146% | 0,509% | 1,190% | 0,456% |
| Distancia de edición ≤1, incluida identidad | 4,931% | 2,738% | 4,482% | 2,281% |
| Longitud media ASCII | 5,044 | 4,998 | 5,413 | 5,384 |
| Fracción de tipos que aparecen una sola vez | 69,115% | 62,108% | 72,760% | 64,342% |

El modelo enlace+copia contiene el observado dentro de su rango en 0/7 firmas split y 3/7 join. El enlace solo lo hace en 2/7 y 3/7. Son diagnósticos correlacionados y no una puntuación universal; los distintos rangos Monte Carlo permiten, por ejemplo, que enlace+copia quede fuera en split aunque su mediana esté más cerca en MI. Ninguno cubre simultáneamente las siete firmas. La pequeña ganancia de probabilidad no implica adecuación generativa.

Las formas que aparecen una sola vez y las repeticiones son dos aspectos diferentes: se exige ambas, no se aumenta mecánicamente la copia para aproximar una mientras se rompe la otra. Se conservan todos los valores de cada simulación. El archivo de ejemplos muestra las primeras cinco líneas por estrato de la primera muestra; no son páginas traducidas ni todas las muestras.

## Alcance frente a investigaciones existentes

- Timm, *How the Voynich Manuscript was created* (2014, revisión 2015), https://arxiv.org/abs/1407.6639 : antecedente de análisis de formas parecidas. Nuestro canal de vecino inmediato y una edición no es una réplica del procedimiento completo ni permite refutar la autocita en general.
- Montemurro y Zanette (2013), https://doi.org/10.1371/journal.pone.0066344 : organización de palabras a larga distancia y coocurrencias. Aquí no se prueba su afirmación semántica ni se reproduce su análisis.
- Rozanova y Temerev (preprint 2026), https://arxiv.org/abs/2608.17096 : diferencias entre unidades, bordes, orden de tokens y controles. Este piloto comparte preguntas sobre firmas conjuntas, pero no reproduce sus unidades ni sus controles publicados.

Una dependencia local puede deberse a gramática, abreviaciones, tema, notación o procedimiento de escritura. Que un modelo sin significado mejore una predicción no significa que el texto carezca de contenido. Renombrar el alfabeto preserva nuestras probabilidades y métricas: estas no seleccionan una glosa.

## Controles y reproducción

Catorce controles pasan: normalización de los tres canales y del canal de edición en los límites de longitud, múltiples rutas de una misma edición, límites/no cruces del parser, comas, agrupación por hoja, señal sintética de copia, vecinos sintéticos ajenos, contexto sustituto emparejado, invariancia a renombramiento, soporte para palabra nueva, ausencia de actualización al puntuar reserva y validación de la configuración fijada. El positivo sintético demuestra sensibilidad del software a una señal construida, no verdad del mecanismo en Voynich.

Python local 3.12.14, biblioteca estándar. Comandos reales y hashes en `results/local_copy_checks.json`; datos completos en `results/local_copy_result.json`.

La [ejecución de GitHub Actions 37596432044](https://github.com/MedinaParra/Voynich/actions/runs/37596432044), commit `66d2c4f73270ba28ef1c0dbf9a4191212e0d17b0`, y su job `112710109467` terminaron con éxito. Pasaron los catorce controles. Los logs coinciden exactamente con el resumen compacto local, las diez ganancias redondeadas por partición y los seis recuentos de firmas cubiertas. Coincide el SHA-256 de los ejemplos representativos generados (`592e2118b237a9b4d31ebec84f60057dd429c5d4e6409318496e7fd315b97e0f`). Auditoría: `results/local_copy_ci_audit.json`. No se descargó el artefacto ni se verificó por hash todo el JSON de resultados o cada valor individual de simulación; no se afirma ese alcance.

```sh
curl -L --fail -o voynich_eva.txt 'https://raw.githubusercontent.com/cesarjz/Voynich/47e6a77dc9d5cd570c375f4aff710fa4a0567278/corpus/voynich_eva.txt'
python -m unittest discover -s research_gpt6/code -p test_local_copy_probe.py -v
python research_gpt6/code/local_copy_probe.py --corpus voynich_eva.txt --plan research_gpt6/data/local_copy_plan.json --out research_gpt6/results/local_copy_result.json --samples research_gpt6/results/local_copy_generated_examples.json
```

## Decisión

Conservar el hallazgo limitado: la forma del contexto anterior añade una señal predictiva muy pequeña a este modelo, más fuerte en B/mano 2. Descartar su uso como explicación suficiente del manuscrito o como traductor. Mantener las siete firmas como obligación conjunta para cualquier sucesor.

La calibración interna del peso y una memoria de varias palabras/filas son hipótesis futuras que deben tener un protocolo propio. No se aumenta el peso retrospectivamente para arreglar los gráficos. Para asignar significados sigue haciendo falta evidencia externa y composición verificable.

Ejecución PASS_EXECUTED. Criterio predictivo local: CUMPLIDO, con efecto pequeño. Adecuación conjunta de estos generadores: NO_ENCONTRADA. Significado: BLOCKED. Traducción: NOT_RUN. Originalidad: NOT_ESTABLISHED.
