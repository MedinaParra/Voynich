# 40. Doble perspectiva: explicación del contenido frente a explicación de la producción

Fecha local: 2026-10-06. Corte de revisión bibliográfica: 2026-10-07 UTC. Hipótesis exploratoria; originalidad no establecida. No es una prueba final universal ni una solución del Voynich.

## Propuesta científica

En cada candidato deben competir dos explicaciones: (1) las formas transportan contenido; (2) las formas siguen convenciones de producción: mano, Currier, cuaderno, posición, longitud y plantilla gráfica. La segunda es un modelo rival, no un residuo que se pueda ignorar. Preguntar qué predicciones adicionales aporta el contenido y cuáles se mantienen al quitar atajos.

El programa integra dos vistas observables —texto e información visual independiente— y un ancla externa necesaria para interpretar sus clases. El contenido es una variable latente compartida que NO tiene nombre conocido al empezar. No asumir que cada glifo sea una letra, cada separación una palabra, ni cada ilustración la descripción literal del texto.

Para una interpretación local, exigir en muestra nueva:

1. Texto → rasgo visual: mejorar una base de producción/layout, con separación por cuaderno y control de mano/Currier cuando exista solapamiento.
2. Rasgo visual → texto: predecir unidades o rasgos textuales adicionales a la misma base; no usar la traducción propuesta como verdad de referencia.
3. Identificabilidad: una regla anclada en evidencia independiente debe distinguir el significado propuesto de renombramientos y glosas rivales. Una vuelta perfecta texto → clase → texto puede ser un diccionario arbitrario.
4. Composición: una regla congelada debe anticipar combinaciones nuevas o pasajes retenidos. Predecir proporciones de caracteres no equivale a recuperar texto literal.
5. Robustez: conservar resultado ante incertidumbre de transcripción, orden físico plausible, escriba distinto y comparadores históricos negativos, sin reoptimizar sobre la prueba.

La intersección de estas restricciones pretende reducir explicaciones acomodadas a posteriori. No garantiza que el manuscrito sea identificable con los datos actuales.

## Qué aporta y qué ya existe

La bidireccionalidad texto/imagen tiene antecedentes explícitos: `tedficient-source/VoynichNotation/PAPER_DRAFT_v5.md`, sección 3.7. El mismo borrador reconoce que sus resultados son correlacionales, la puntuación visual se hizo con un modelo de visión, y el holdout herbal ya fue consumido. No se trata como desciframiento establecido.

Rozanova y Temerev, arXiv:2608.17096 (agosto 2026), ponen a prueba las equivalencias entre glifos/letras, tokens/palabras y separadores/espacios. Parisel, arXiv:2604.19762v2 (junio 2026), evalúa restricciones direccionales y generadores concretos; no excluye todos los generadores. Estas son propuestas y mediciones de sus autores, no axiomas sobre cualquier lengua/cifra posible.

URLs primarias consultadas:
- https://github.com/tedficient-source/VoynichNotation/blob/main/PAPER_DRAFT_v5.md
- https://arxiv.org/abs/2608.17096
- https://arxiv.org/abs/2604.19762

La revisión focalizada encontró antecedentes directos: no reclamar «nadie lo ha pensado». La aportación candidata del proyecto es exigir simultáneamente generalización condicionada, controles del propio harness y una barrera explícita de identificabilidad. Su originalidad académica todavía requiere revisión sistemática y comparación de implementaciones. No se ha leído exhaustivamente toda publicación oficial/no oficial al corte.

## Límite matemático de una doble perspectiva sin anclas

Sean E: texto → clases latentes y D: clases → texto. Para cualquier renombramiento biyectivo π, usar E'=π∘E y D'=D∘π⁻¹ deja D'∘E'=D∘E. Por tanto la reconstrucción no elige nombres semánticos. Si el renombramiento se aplica consistentemente, las métricas de clasificación tampoco distinguen glosas. Esto es una simetría del problema, no un hallazgo de un idioma concreto.

Una asociación con rasgos visuales **independientes y observables** sí puede romper parte de esa simetría; una taxonomía inferida del propio texto no. Incluso con anclas visuales, la imagen solo describe parte del posible contenido y no certifica toda una oración.

La asimetría de exactitudes tampoco prueba por sí sola notación frente a cifra: las dos tareas pueden tener entropías, ruidos, cobertura y objetivos diferentes. Una cifra biyectiva entre textos NO implica una biyección entre un texto y el subconjunto de detalles visibles de una ilustración.

## Implementación ejecutada y alcance

`code/dual_perspective_harness.py` ejecuta un **piloto de metadatos**, no el programa semántico completo. Fuente EVA fijada por blob `2a4533ab9bdfa85db9bad602d590978953055df1`. Solo loci Lc/Lf con un token literal inequívoco `[a-z]{2,}`. Hay 201 registros, 15 folios transcritos, dos cuadernos O/S, Currier A/mano 1. Los sufijos de paneles pueden compartir hoja física; el holdout por cuaderno evita repartirla entre entrenamiento y prueba, pero no crea más cuadernos.

Vista 1: composición textual → categoría Lc/Lf. Compara error Brier equilibrado de base de longitud con base + 21 proporciones de caracteres/secuencias fijadas. Vista 2: categoría → esas 21 proporciones, comparando MSE estandarizado con base de longitud. Ambas vistas comparten datos y rasgos: NO son evidencias independientes.

Ridge α=1 fijo; centrado/escalado solo del entrenamiento; clases ordenadas determinísticamente; sin selección de hiperparámetros. Base: longitud lineal/cuadrática e indicadores exactos 2..15, con 16+ agrupado. Este grupo largo y la familia polinómica son aproximaciones, no un control perfecto de toda la producción. No hay coordenadas ni layout de estos loci en el input.

Retener un cuaderno cada vez y purgar en entrenamiento todas las formas literales presentes en el cuaderno de prueba. Permutar etiquetas 999 veces dentro de folio × Currier × mano × longitud exacta, reentrenando ambos modelos. Registrar cantidad de datos realmente intercambiables; no confundir 999 permutaciones con 999 muestras independientes. La intercambiabilidad de loci dentro de estas celdas es una suposición: dependencia espacial/orden no controlados impiden inferencia confirmatoria.

Para dos direcciones necesarias se usa máximo de los dos p (intersección-unión), sin suponer independencia ni multiplicar sus evidencias. Criterio numérico exploratorio: ganancias positivas en todos los cuadernos y p conjunto ≤ .01, con datos intercambiables. Aunque se cumpla, no abre una traducción: falta ancla y prueba composicional independiente.

## Resultados

| Vista | Ganancia media sobre longitud | p de permutación |
|---|---:|---:|
| Texto → categoría, reducción Brier | -0,026705 | 0,485 |
| Categoría → forma textual, reducción MSE | -0,011517 | 0,529 |

Ganancias negativas: este modelo empeora las dos bases en ambos cuadernos. p conjunto = 0,529. 69/201 filas están en celdas con clases intercambiables; solo 14,02 % cambia de clase en promedio. Esto limita potencia y alcance del nulo.

Resultado numérico del piloto: NO SUPERA EL CRITERIO. Ejecución: PASS_EXECUTED. Prueba semántica: BLOCKED. Traducción: NOT_RUN. No significación no demuestra inexistencia de contenido.

El anterior piloto Lc/Lf ≈65 % no se invalida con esta prueba: cambian filtro, modelo, rasgos, pérdidas, purga y nulo. Por tanto no atribuir causalmente el cambio a la longitud ni llamar esto réplica exacta. La afirmación «ya tenemos un decodificador semántico robusto Lc/Lf» sigue sin respaldo.

Renombrar Lc/Lf por dos etiquetas arbitrarias mantiene exactamente las ganancias (diferencia 0). No es falta de potencia: demuestra que estas métricas no seleccionan significado.

## Verificación del harness

Seis controles ejecutados con éxito: señal sintética conocida de longitud constante, señal solo de longitud, etiquetas aleatorias, invariancia a renombramiento, purga de diccionario memorizado, y exclusión de tokens ambiguos/múltiples. Los controles positivos desactivan la purga explícitamente porque sus cadenas se repiten por construcción. No son pruebas de generalización del manuscrito. El harness conserva la barrera semántica incluso si una señal sintética supera el criterio numérico.

Reproducción:

```sh
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s research_gpt6/code -p test_dual_perspective_harness.py -v
OPENBLAS_NUM_THREADS=1 python research_gpt6/code/dual_perspective_harness.py --corpus voynich_eva.txt --out research_gpt6/results/dual_perspective_result.json --permutations 999
```

Python 3.12.14, NumPy 2.3.5. Resultados y huellas: `results/dual_perspective_result.json` y `results/dual_perspective_harness_checks.json`.

## Qué afirmaciones dejan de sostenerse con la evidencia disponible

| Afirmación | Evaluación y alcance |
|---|---|
| Bidireccionalidad demuestra significado | No: renombramiento deja intactas las métricas; hacen falta anclas |
| Desigual exactitud ida/vuelta demuestra que no es cifra | No: objetivos y ruido distintos permiten asimetrías |
| TimesFM predice, por lo tanto traduce | No: predicción de series de rasgos sin glosas ni composición |
| Lc/Lf ya proporciona traducción robusta | No respaldado: metadatos; este modelo controlado no mejora bases |
| Rosetas conectadas comparten necesariamente texto semejante | No respaldado por el piloto 39; no exclusión universal |
| Un generador que explica entropía explica todo el manuscrito | Insuficiente: exigir firmas conjuntas y datos nuevos |
| Resultado nulo prueba texto sin significado | No: modelos concretos y pruebas con potencia limitada |

## Próximo salto necesario

Conseguir anotaciones visuales ciegas verificables con coordenadas, rasgos no triviales y acuerdo entre anotadores; conservar espacios/ambigüedades del texto; medir solapamiento real entre mano, Currier y dominio antes de definir holdouts. Si dominio y escriba están perfectamente confundidos, registrarlo como problema no identificable.

Congelar luego un candidato capaz de anticipar una combinación o pasaje no usado, con anclas históricas independientes y un registro de alternativas que harían la misma predicción. Solo allí se evalúa una glosa composicional. El corpus ya examinado sigue siendo exploratorio: más permutaciones no producen un holdout nuevo.
