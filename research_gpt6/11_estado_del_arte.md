# Estado del arte del manuscrito Voynich y evaluación de propuestas
**Corte: 6 de octubre de 2026.** Objeto: Beinecke MS 408. Esta revisión cubre la bibliografía primaria influyente y las propuestas públicas recientes localizadas en Yale, ACL, Crossref/editoriales, arXiv, CEUR, Zenodo y sitios de autores. No existe catálogo exhaustivo de cada libro, foro o afirmación informal; «todos» significa cobertura amplia y rastreable de líneas importantes, no una lista matemáticamente completa.

## Síntesis
No existe una lectura integral del manuscrito que haya sido reproducida de forma independiente y que prediga texto no utilizado para construir la clave. Yale lo cataloga como escritura no identificada y texto no descifrado, si es que está codificado. La fecha del pergamino es compatible con 1404–1438; no establece el idioma ni la fecha exacta de escritura del texto. citeturn19search6

Está bien establecido que las secuencias de glifos no son aleatorias simples y que hay restricciones internas, variación de sección/mano y comportamiento posicional inusual. Esos rasgos permiten tanto modelos lingüísticos transformados como modelos de generación; por sí solos no deciden si el manuscrito codifica significado. La revisión de Bowern y Lindemann hace explícita esta brecha entre estructura lingüística plausible y contenido aún indescifrable. citeturn23search5

En la rama de trabajo `research/gpt6-audit`, una n-grama de orden 2 predice mejor que unigramas folios y quires reservados (3,005 bits/glifo frente a 4,149–4,161). Esto demuestra regularidad predictiva local que generaliza, no lectura. El crib literal de nombres zodiacales hebreo/arameos retuvo un signo por pliegue y obtuvo 0/10 aciertos exactos, cobertura de 29,3% y p=1,0. Debilita esa versión literal concreta; no descarta otras codificaciones.

## Criterio de desciframiento
Una propuesta solo pasa a **CANDIDATE_DECIPHERMENT** cuando fija antes del test la transcripción, el mecanismo, idioma/ortografía y segmentación; produce lectura coherente en secciones distintas; predice pasajes reservados; supera controles y corrección por búsqueda múltiple; y otro equipo puede repetirla sin conocer las respuestas. Coincidencias de etiquetas elegidas tras mirar dibujos generan hipótesis, no las validan.

## Trabajos académicos y de investigación formal
«Revisado» describe el canal editorial, no garantiza que la interpretación sea correcta ni aceptada por consenso.

| Fecha | Trabajo / estado editorial | Aporte y límite |
|---|---|---|
| 1976–78 | Prescott Currier, hallazgos A/B; Mary D’Imperio, informe técnico NSA *An Elegant Enigma* | Diferencias estadísticas entre grupos de páginas y observaciones de transcripción/manos. A y B son etiquetas descriptivas; no prueban dos idiomas. |
| 2001 | Gabriel Landini, [“Evidence of linguistic structure… using spectral analysis”](https://doi.org/10.1080/01611190108984235), *Cryptologia* | Analiza estructura espectral y secuencial compatible con texto organizado; no recupera semántica. |
| 2004 | Gordon Rugg, [“An elegant hoax? A possible solution…”](https://doi.org/10.1080/0161-110491892755), *Cryptologia* | Una técnica de tabla/rejilla puede producir texto con rasgos parecidos. Demuestra posibilidad generativa, no que MS 408 se hiciera así. |
| 2007 | Andreas Schinner, [“Evidence of the Hoax Hypothesis”](https://doi.org/10.1080/01611190601133539), *Cryptologia* | Usa caminata aleatoria y repeticiones para defender generación. Depende de métrica y nulo; no prueba fraude. |
| 2011 | Reddy y Knight, [“What We Know About The Voynich Manuscript”](https://aclanthology.org/W11-1511/), ACL LaTeCH | Sintetiza evidencia computacional y límites de inferencia; no asigna idioma ni clave. |
| 2013 | Montemurro y Zanette, [“Keywords and Co-Occurrence Patterns…”](https://doi.org/10.1371/journal.pone.0066344), *PLOS ONE* | Observa patrones de distribución/coocurrencia en escalas mayores; inferir estructura temática no equivale a traducir. |
| 2013 | Amancio et al., [“Probing the Statistical Properties of Unknown Texts…”](https://doi.org/10.1371/journal.pone.0067310), *PLOS ONE* | Compara redes y estadísticas con lenguas y texto barajado. Voynich no parece aleatorio simple; el marco no fue diseñado para descifrar. |
| 2014 | Stephen Bax, [“A Proposed Partial Decoding…”](https://stephenbax.net/wp-content/uploads/2014/01/Voynich-a-provisional-partial-decoding-BAX.pdf), borrador/autopublicación | Propone nombres de plantas y Taurus desde ilustraciones. Las anclas y valores se eligen de manera relacionada, con riesgo de circularidad; no ofrece validación ciega global. |
| 2016 | Hauer y Kondrak, [“Decoding Anagrammed Texts Written in Unknown Languages”](https://doi.org/10.1162/tacl_a_00084), *TACL* | Método probado con textos sintéticos anagramados; para Voynich señala hebreo como candidato. No valida ese candidato ni produce traducción coherente del manuscrito. |
| 2017 | Rugg y Taylor, [“Hoaxing Statistical Features…”](https://doi.org/10.1080/01611194.2016.1206753), *Cryptologia* | Reproduce varios rasgos con una rejilla; demuestra que algunas métricas no diagnostican significado por sí solas. |
| 2018 | Janick y Tucker, [*Unraveling the Voynich Codex*](https://doi.org/10.1007/978-3-319-77294-3), libro académico | Hipótesis mesoamericana/Náhuatl y asociaciones botánicas; no ha producido lectura ciega integral aceptada. |
| 2019 | Gerard Cheshire, [“The Language and Writing System of MS408 Explained”](https://doi.org/10.1080/02639904.2019.1599566), *Romance Studies* | Publicó afirmación proto-romance en revista revisada; recibió fuertes críticas de método/lingüística y no hay reproducción de corpus traducido que prediga texto reservado. El peer review no equivale a validación de la solución. |
| 2019 | Luis Acedo, [HMM para análisis lingüístico](https://doi.org/10.3390/mca24010014), *Mathematical and Computational Applications* | Explora estados latentes y similitud de transiciones; estados calculados no son automáticamente fonemas o morfemas. |
| 2019 | Smith y Ponzi, [dependencias entre palabras adyacentes](https://doi.org/10.1080/01611194.2019.1596998), *Cryptologia* | Describe combinaciones de glifos a través de límites de palabra; importante para modelos de tokens independientes, no una clave. |
| 2020 | Davis, “How Many Glyphs and How Many Scribes?”, *Manuscript Studies* 5:164–180 | Paleografía digital apoya cinco manos como hipótesis de trabajo; no determina idioma ni semántica. |
| 2020 | Timm y Schinner, [“A possible generating algorithm…”](https://doi.org/10.1080/01611194.2019.1596999), *Cryptologia* | Algoritmo de autocita reproduce algunas estadísticas; no demuestra que el contenido carezca de significado ni cubre por sí solo todas las señales. |
| 2020 | Layfield et al., [“Word Probability Findings…”](https://aclanthology.org/2020.lt4hala-1.11/), ACL LT4HALA | Analiza probabilidad de palabras/subsegmentos y defiende compatibilidad con rasgos de lengua; no identifica la lengua. |
| 2020–21 | Lindemann y Bowern, [corpus y entropía de caracteres](https://arxiv.org/abs/2010.14697), preprint | Compara cientos de lenguas y textos históricos; encuentra restricciones posicionales inusuales, no resueltas por las sustituciones simples estudiadas. |
| 2021 | Sterneck, Polish y Bowern, [topic modeling](https://arxiv.org/abs/2107.02858), preprint con [datos en Yale Dataverse](https://doi.org/10.60600/YU/PXULND) | Estudia agrupación por tópicos/ilustraciones; cambios Currier A/B dificultan vocabulario estable. No produce traducción. |
| 2021 | Bowern y Lindemann, [revisión lingüística](https://doi.org/10.1146/annurev-linguistics-011619-030613), *Annual Review of Linguistics* | Revisión central de enfoques lingüísticos; separa evidencia de estructura de una lectura aún ausente. |
| 2021 | Parmentier, [“Deciphering… propositions to unlock research”](https://doi.org/10.1080/01611194.2021.1919944), *Cryptologia* | Recomendaciones metodológicas y examen de supuestos de etiquetas/alfabeto; no ofrece desciframiento. |
| 2022 | Farrugia, Layfield y van der Plas, [atribución computacional de escribas](https://ceur-ws.org/Vol-3313/paper5.pdf), VOY 2022 | Compara perfiles de manos; estudia organización, no significado. |
| 2022 | Gaskell y Bowern, [“Gibberish after all?”](https://ceur-ws.org/Vol-3313/paper4.pdf), VOY 2022 | 42 personas escribieron muestras intencionalmente sin sentido; algunas replican métricas Voynich. Esto reduce la fuerza de métricas aisladas; no prueba que el manuscrito sea gibberish. citeturn23search36 |
| 2022 | Bowern y Gaskell, [“Enciphered after all?”](https://ceur-ws.org/Vol-3313/paper6.pdf), VOY 2022 | Compara 22 manipulaciones; algunas bajan entropía condicional. Exploratorio, no prueba de un cifrado histórico concreto. |
| 2022 | Matlach et al., [“Symbol roles revisited”](https://doi.org/10.1371/journal.pone.0260948), *PLOS ONE* | Reporta autocorrelación excepcional por símbolo y cercanía a texto generado por autocita. Es una señal estadística específica; interpretación como mecanismo debe compararse con más generadores. |
| 2022 | Zattera, análisis computacional, conferencia Malta | Formaliza restricciones de posición/“slots”; describe regularidad, no establece significado de cada casillero. |
| 2023 | Daruka, “On the Voynich manuscript”, *Cryptologia* | Debate de estructura e hipótesis; sin lectura aceptada. |
| 2023 | Zelinka et al., [comparación con dialectos antiguos](https://doi.org/10.1016/j.asoc.2023.110217), *Applied Soft Computing* | Clasificación basada en características/corpus. Clasificar similitud no equivale a identificar la lengua ni a descifrar. |
| 2025 | Greshko, [“The Naibbe cipher”](https://doi.org/10.1080/01611194.2025.2566408), *Cryptologia* | Construye cifrado homofónico verbose históricamente plausible que codifica latín/italiano y reproduce varios rasgos Voynich. Es un generador de referencia, no la clave demostrada de MS 408. citeturn25search4 |
| 2025 | Ponnaluri, [“The Voynich Manuscript was written in a single, natural language”](https://doi.org/10.1080/01611194.2024.2414128), *Cryptologia* 49(6) | Argumenta por texto de lengua natural con leyes de frecuencia; eso no aporta clave o lectura continua. |
| 2025 | Parísel, [“Directionality of the Voynich Script”](https://arxiv.org/abs/2509.10573), preprint | Hipótesis direccional, pendiente de contrastes independientes. |
| 2026 | Parísel, [restricciones posicionales/direccionales](https://arxiv.org/abs/2604.19762), arXiv | Contrasta lenguas, generador de slots y rejilla Cardano contra cuatro señales conjuntas. Reporta que configuraciones probadas no reproducen todas; no excluye mecanismos distintos ni descifra. citeturn22academia38 |
| 2026 | Kinnison, [“Positional entropy collapse…”](https://doi.org/10.1080/01611194.2026.2697318), *Cryptologia* | Artículo revisado publicado en septiembre; comparación de lenguas/cifrados. El texto y datos completos no estaban localizables en acceso abierto para esta revisión; reproducibilidad pendiente. citeturn25search6 |
| 2026 | Timm, [“The Challenge of Analyzing a Dynamic Text”](https://doi.org/10.1080/01611194.2026.2693462), *Cryptologia* | Defiende vocabulario en evolución/autocita como explicación de una red de palabras; es una explicación generativa, no traducción. Debe competir con modelos de sección/mano y controles fuera de muestra. citeturn25search2 |

## Propuestas independientes, preprints y lecturas públicas recientes
Estas fuentes pueden producir hipótesis evaluables, pero no se deben etiquetar automáticamente como artículos revisados ni como desciframientos.

| Propuesta y fuente | Estado y evaluación |
|---|---|
| Newbold, Strong, Feely y otras lecturas históricas | Intentos de las décadas de 1920–40; dependen de segmentación/clave ad hoc y no sobrevivieron reproducción. |
| Herrmann, [hipótesis Pahlavi](https://arxiv.org/abs/1709.01634), 2017 | Preprint propone correspondencias de caracteres y algunas palabras; no presenta traducción integral verificable. |
| Burgos, [EVA–Romance Lexicon v3](https://zenodo.org/records/17070155), 2025 | Preprint/dataset grande con lecturas poéticas. Riesgo alto de grados de libertad por lexicón, asociaciones post hoc y cobertura; exigir mapping fijo y evaluación ciega. |
| Quereshi (checo/compresión), Basque, “Triple Cipher” y otros depósitos 2025 | SSRN/Zenodo/autopublicación; sin lectura repetida independiente al corte. Solicitar método ejecutable y test predefinido. |
| Jama, [números/Fibonacci/proporción áurea](https://arxiv.org/abs/2505.02261), 2025 | Preprint especulativo. Relaciones numéricas escogidas tras observar datos no identifican plaintext. |
| Turenne, [“Pastiche hypothesis”](https://arxiv.org/abs/2609.20835), 2026 | Preprint propone imitación estructurada/LLM y patrones de manuales herbarios; necesita benchmark común con Naibbe, generadores humanos y texto reservado. |
| Honeycutt, [“An Operator Grammar…”](https://zenodo.org/records/20368211), 2026 | Depósito Zenodo independiente, no se encontró revista asociada. Reporta 31 clases, 77 transiciones prohibidas y clasificación Currier; interesante como gramática estructural, pero reglas/clases deben fijarse y validarse en particiones independientes. El propio resumen retira interpretación léxica y no afirma lectura. citeturn18view1 |
| Averyanov, [*A Workshop Cipher* y *Thirty Names per Sign*](https://voynich.site/publications), Zenodo 2026 | Publica código/dataset y propone mecanismo de taller sin afirmar plaintext. Paper II informa shift 23 y p=0,0088 en ronda ciega 2, con alineación luego fija; requiere reproducción de pipeline, corrección por alineación/candidatos y control de selección. Nuestra prueba de nombres hebreo/arameos no es réplica de su codificación. citeturn29search1turn29search2 |
| Dickens, [*The Voynich Manuscript Is Not a Language*](https://solvedvoynich.com/), 2026 | Sitio independiente, no peer-reviewed. Alega MI trans-línea igual a cero y que un generador prefix+base+suffix reproduce ≈99,6% de formas. Auditoría concreta del generador, abajo. También falta replicar MI con idéntica transcripción/segmentación/nulo. citeturn29search0 |
| CLAVIS CODICIS / SilPart en [cesarjz/Voynich](https://github.com/cesarjz/Voynich) | Experimentos del proyecto, no consenso editorial. Etiquetas interpretativas son hipótesis del proyecto, no observaciones directas. La auditoría de la rama registra errores, límites y pruebas pendientes. |
| Blogs, foros, videos y traducciones completas | Fuente de hipótesis si publican regla/datos; frases seleccionadas a mano no son evidencia de desciframiento. |

## Hallazgos de la rama `research/gpt6-audit`
- PASS descriptivo: parseo STA1 reproduce 157.254 glifos, 37.087 tokens y 166 clases de glifo según el parser del proyecto.
- PASS predictivo: orden 2 generaliza entre folios y quires; es regularidad, no contenido.
- FAIL metodológico: un estimador de entropía de la notebook pierde masa condicional y no sostiene la interpretación anunciada de normalización/monotonicidad.
- FAIL aritmético: la celda de percentil de bigramas fuerza 0,1% por construcción; ese valor no sirve de evidencia.
- No apoyado: crib literal de nombres zodiacales, 0/10 etiquetas exactas bajo la clave congelada.
- NOT_RUN: familias completas de cifrado, otra transcripción, imagen-texto, Elu-Sinhala, slots con predicción ciega y generadores actualizados.
Detalles, comandos y JSON existentes: `research_gpt6/10_results.md`, `EVIDENCE.md`, `code/`, `results/`.

## Prioridad de reproducción
1. Ejecutar el script de auditoría del generador Dickens en una copia fijada de `corpus/voynich_eva.txt`; el informe adjunto registra su resultado y limitaciones.
2. Replicar independientemente la señal de etiquetas de Averyanov, usando sus 270 datos, sus alineaciones candidatas completas y permutación que repita todo el proceso de selección.
3. Calcular MI entre líneas a partir de registro físico de líneas, comparar línea ordenada vs. barajada y controles por sección/mano/dialecto/transcripción.
4. Comparar slot grammars, Naibbe, autocita y escritura sin sentido humano en un único benchmark por folio/quire retenido, con presupuesto de ajuste comparable.

Sin predicción correcta del texto reservado, la conclusión vigente es **no descifrado**.
