# EVIDENCE — registro de hipótesis y pruebas

Convención: PASS = resultado reproducido; FAIL = afirmación metodológica contradicha; BLOCKED = obstáculo a ejecución; NOT_RUN = sin prueba. Las reproducciones son scripts autocontenidos que portan lógica concreta de notebooks y no equivalen a ejecutar los notebooks completos.

| Hipótesis o afirmación | Prueba | Resultado | Estado | Evidencia | Interpretación |
|---|---|---|---|---|---|
| El checkout y corpus corresponden al repo fijado | Git commit + SHA-256 | `47e6a77dc9d5cd570c375f4aff710fa4a0567278`; corpus SHA `81c331…29259b17` | PASS | `00_audit.md`, `01_corpus_validation.md` | Identidad de fuente trazable |
| El parser STA1 reproduce conteos de notebook 03 | `reproduce_core.py` | 157254 glifos, 37087 palabras, vocabulario 166 | PASS | `results/core_reproduction.json` | Confirmación de conteos/parser |
| Notebook 03 implementa masa condicional normalizada | Suma de P(next|context) para cada contexto | Masa menor que 1, mínimos 0.9653–0.9740 en órdenes 1–4 | FAIL | `results/core_reproduction.json`; `02_statistics.md` | El estimador no es una distribución condicional normalizada como está escrito |
| Notebook 03 garantiza monotonicidad H_N≤H_(N−1) | Reproducción H0–H4 y salida notebook | Curva sube en órdenes 1→2→3→4; notebook imprime violaciones N=2,3,4 | FAIL | `02_statistics.md` | El resultado empírico puede calcularse, pero garantía/documentación no concuerda con implementación |
| MI glifo–posición coincide con cifra informada | Puerto de conteo; 999 permutaciones intra-palabra | 0.657811 bits; p empírico unilateral 0.001; seed 20261005 | PASS | `results/position_reproduction.json` | Asociación estadística; no atribuye significado |
| La estructura de glifos generaliza a folios completos no vistos | Validación cruzada 5-fold agrupada por folio; unigramas vs posición vs n-gramas; bootstrap por folio | Orden 2: 3.0051 vs 4.1488 bits/glifo (ganancia 1.1437; IC95% 1.1030–1.1826) | PASS predictivo | `results/heldout_prediction.json`; `03_positional_grammar.md` | Generaliza dependencia de secuencia/posición; no infiere semántica ni descifrado |
| La predictibilidad se mantiene sin folios del mismo quire en entrenamiento | Leave-one-quire-out (18 grupos `$Q`), unigramas vs posición vs n-gramas; bootstrap por quire | Orden 2: 3.0374 vs 4.1607 bits/glifo (ganancia 1.1233; IC95% 0.9351–1.2147); OOV 0.062% | PASS predictivo | `results/leave_one_quire_out.json`; `03_positional_grammar.md` | Dependencia local se generaliza entre grupos anotados; no demuestra semántica, idioma ni descifrado |
| Exclusividad STA1 de cinco glifos en f57v | Parser notebook 74 + contraste parser general | X2=10, Xd=5, Xf=4, Pc=5, Ea=1; conteos continúan solo en f57v con `fRos` incluido | PASS descriptivo | `results/f57v_reproduction.json`; `07_f57v.md` | No es test paleográfico; p publicados no están calibrados tras selección |
| El f57v p-value publicado es evidencia inferencial calibrada | Nulo iid uniforme aplicado post-selección | No contempla selección, multiplicidad, dependencias, quire/sección ni incertidumbre | FAIL metodológico | `results/f57v_reproduction.json` | Los valores se reportan solo como aritmética descriptiva |
| Los nombres zodiacales proporcionan un crib compatible con una clave hebrea/aramea | Búsqueda y nulos guardados en notebook 28 | p=0.6103, 0.8066 y 0.7713; ninguno significativo | No apoyado por resultados guardados | `results/zodiac_crib_audit.json`; fuente `28_zodiac_cribs.ipynb` | Cinco signos/17 glifos es el mejor ajuste seleccionado; no constituye lectura validada |
| El bigrama hebreo de la clave zodiacal queda en percentil 0.1% | Auditoría de expresión y salida de notebook 28 | Expresión informa 0.1% para cualquier k>0 de 1000 permutaciones bajo la observación; z guardado=1.54 | FAIL aritmético | `results/zodiac_crib_audit.json` | Percentil impreso inválido; no se rerunearon los datos hebreos |
| La clave de nombres zodiacales predice un signo reservado | Leave-one-sign-out: mapa entrenado en etiquetas de otros nueve signos; 1,000 permutaciones de páginas/nombres | 0 de 10 etiquetas de signo predichas exactamente; cobertura de etiqueta mapeable 29.3%; p=1.0 para 0 aciertos | FAIL para crib literal | `results/zodiac_crib_holdout.json`; `05_cipher_tests.md` | No respalda que etiquetas de ninfas deletreen directamente el nombre esperado con sustitución 1-glifo→1-letra |
| La MI posicional demuestra gramática de cinco categorías | Hipótesis de cinco slots | No se probó predicción de slots ni validación por folio retenido | NOT_RUN | `03_positional_grammar.md` | Asociación con posición no equivale a semántica |
| SilPart supera generadores fuera de muestra | Reproducción con controles y búsqueda emparejada | No ejecutada | NOT_RUN | `04_visual_semantics.md`, `10_results.md` | Sin adjudicación |
| El manuscrito queda descifrado / tiene significado recuperable | Prueba ciega preregistrada | No ejecutada | NOT_RUN | `08_semantic_anchors.md`, `09_blind_validation.md` | Pregunta abierta |

## Contraste nuevo: bordes (6 de octubre de 2026)

**PASS descriptivo exploratorio**: asociación final/inicio EVA frente a 199 permutaciones intra-tramo, bajo dos tratamientos de comas; exceso 0,19178/0,15722 bits; p=0,005, Holm familia 8=0,04. Fuente EVA exacta verificada por blob y SHA-256; Python 3.12.14, exit 0. Ver [método y límites](15_dependencias_de_borde.md), `code/boundary_dependence.py` y `results/boundary_dependence.json`. No es réplica exacta ni evidencia semántica. Controles de lenguas/cifrados, segunda transcripción y validación por bloques: **NOT_RUN**. La cobertura previa Dickens requiere sensibilidad de parser para huecos de dibujo; no se recalculó aquí.

## Plan contextual: validación reservada

**PASS predictivo**, no semántico: último carácter EVA mejora predicción del primer carácter siguiente frente a contexto de posición/cuaderno. Ganancia 0,106–0,172 bits/inicio, cuatro intervalos bootstrap con límite inferior positivo (dos separadores × dos reservas). 100 grupos de hoja/16 quires; Python 3.12.14, exit 0. Ver `16_plan_descifrado.md`, `17_resultado_plan_descifrado.md`, `code/contextual_link.py`, `results/contextual_link.json`. Identificación de idioma/mecanismo: **NOT_RUN**. Traducción defendible: **BLOCKED** por falta de correspondencia semántica validada.

## Filtro de mecanismos (6 de octubre de 2026)

**PASS ejecución**: 5 controles × 2 segmentaciones × 50 muestras, 20 grupos de hoja reservados; fuentes latinas (8 archivos) verificadas por blob/SHA-256. Python 3.12.14, exit 0. **PASS invariancia** de seis métricas bajo sustitución monoalfabética fija. Generador sin semántica con enlace reproduce magnitud de MI/exceso de bordes en ambas segmentaciones, pero **FAIL de adecuación descriptiva conjunta** de las seis métricas para todos los controles. No es rechazo estadístico de familias; controles no igualan todas las propiedades ni quires. Idioma/clave: **NOT_RUN**; traducción: **BLOCKED** sin correspondencias semánticas. Ver `18_protocolo_mecanismos.md`, `19_resultados_mecanismos.md`, `code/mechanism_controls.py`, `results/mechanism_controls.json` y fuentes durables `data/latin_sources.json`.


## 2026-10-06 — fuentes históricas y muestra paleográfica

- PASS (adquisición/inventario): LJS 419 OPenn TEI: 0 elementos text, 615 graphic; Bellunensis IIIF: 331 lienzos. Código e inventario con hashes incorporados.
- PROVISIONAL: dos etiquetas de LJS 419 leídas por una sola inspección visual por IA; dos nombres inciertos excluidos. Ninguna entrada validada para entrenamiento.
- CANDIDATE: edición independiente Mamontov con Claude (2026), localizada y descargada para inspección. OCR y comentario moderno no admitidos como corpus histórico.
- NOT RUN: comparación con transcripciones históricas depuradas; NOT SOLVED: equivalencias EVA→palabras. Véase informe 21.


## 2026-10-06 — auditoría de extracción LJS 419

- PASS (extractor): 171 bloques candidatos, 169 etiquetas OCR, 42 bloques con indicios de comentario inglés y 7 discrepancias de encabezamiento/imagen. Informe 22 y JSON con hashes/offsets.
- PASS (3 comprobaciones sintéticas): límite ante traducción, discrepancia con imagen y alerta editorial; no certifican paleografía.
- NOT VALIDATED: 0 bloques admitidos para entrenamiento; 6.472 tokens candidatos incluyen contaminación.
- NOT RUN: identificación lingüística sobre estos bloques. NOT SOLVED: traducción del Voynich.


## 2026-10-06 — reconciliación documental de folios

- PASS (cruce ejecutado): 171 bloques enlazados a 171 folios distintos del TEI primario; siete asociaciones de encabezamiento OCR corregidas explícitamente; cero duplicados; 27 folios numerados sin bloque candidato. Informe 23.
- PASS (comprobaciones): cobertura, siete cambios, no duplicados, asociación 6r y rechazo de hash de fuente modificado.
- NOT VALIDATED: contenido paleográfico, 0 transcripciones admitidas para entrenamiento. NOT SOLVED: traducción del Voynich.
