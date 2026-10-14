# 46. Manuscrito Voynich: estado del arte y herramientas emergentes

**Corte: 14-10-2026.** Revisión crítica para Exequiel Medina Parra.

**Estado: traducción no validada. Aplicaciones nuevas de herramientas: NOT_RUN.**

## Resumen ejecutivo

Corte de la revisión: 14 de octubre de 2026. No se identificó en las fuentes verificadas una traducción integral del manuscrito Voynich que hubiera sido reproducida de forma independiente con una clave fija y evaluación de texto reservado. La evidencia disponible restringe su estructura, sus unidades y su contexto; todavía no conecta de forma comprobada esos signos con significado. La conclusión no demuestra que el manuscrito carezca de contenido.

La recomendación de este informe es una línea de doble perspectiva: primero medir el canal físico de escritura con imágenes y transcripciones independientes; después evaluar un canal lingüístico o criptográfico restringido que deba predecir observaciones reservadas. Las herramientas emergentes pueden acelerar la primera parte y la búsqueda de modelos. Ninguna de las herramientas examinadas viene acompañada de una demostración de desciframiento Voynich.

| Conclusión | Evidencia / implicación |
| --- | --- |
| Avance relevante de 2026 | Debate de unidades, plantillas Currier, estructura de bifolios y procesos de producción. Son restricciones, no una clave. [R14-R20] |
| Prioridad inmediata | Otra transcripción independiente y registro imagen-locus. Después, HTR específico y modelos con reglas limitadas. [V01, R32, R41-R45] |
| Novedad instrumental útil | DINOv3, FINO 2026, SAM 3 y PaddleOCR-VL-1.6 para el canal visual y documentos comparadores. Uso Voynich aún NOT_RUN. [R36-R40] |
| Prioridad baja | Cambiar TimesFM 2.5 por 3.0 o Chronos-2 sin una nueva pregunta y baselines fuertes. La mejora de forecasting no equivale a lectura. [R50-R51, R55] |
| Estado del proyecto | Experimentos auditados; sin idioma identificado ni traducción validada. El resultado estricto del panel Q1/Q3/Q20 es negativo. [R55] |

## 1. Alcance, método de revisión y criterios de evidencia

Se revisaron fuentes institucionales, actas, publicaciones editoriales, preprints, documentos de autores y documentación oficial de herramientas. Se emplearon búsquedas web en dos motores y recuperación directa de páginas, PDF y repositorios. Se contrastaron fechas de publicación, fechas de versión, anuncios y fecha de consulta. El corpus bibliográfico recoge los 16 trabajos de VOY2022 y una selección crítica de antecedentes, novedades y herramientas; no es una revisión sistemática exhaustiva de todas las publicaciones o discusiones de internet.

La jerarquía es explícita: una fuente institucional acredita custodia o un ensayo material; una revista acredita un proceso editorial, no la corrección de una traducción; un preprint o depósito puede ser valioso sin estar revisado por pares. Un registro Zenodo etiquetado por su autor como journal article tampoco demuestra que haya una revista asociada. Se distingue el acceso a texto/métodos, al resumen y al registro bibliográfico. No se atribuyen cifras metodológicas a artículos cuyo texto no pudo recuperarse.

La fecha de corte no transforma una página mutable en una versión histórica inmutable. Para software se documentan lanzamientos o anuncios verificables anteriores al corte; para ejecutar después habrá que fijar commit, paquete, checkpoint y hash de pesos. Esta revisión no instaló ni ejecutó los nuevos modelos. Todas las aplicaciones propuestas a Voynich tienen estado NOT_RUN; su prioridad es un juicio de diseño, no un ranking empírico de rendimiento.

| Nivel de resultado | Qué basta para ese nivel | Qué todavía falta |
| --- | --- | --- |
| Observación | Medida sobre imagen/corpus con reglas y fuente explícitas. | Comprobar incertidumbre de anotación y representación. |
| Regularidad predictiva | Ventaja sobre baselines y controles en unidades reservadas. | Determinar qué mecanismo o significado produce la regularidad. |
| Modelo de mecanismo | Reproduce conjuntamente firmas y predicciones, con complejidad acotada. | Mostrar que la explicación histórica es identificable entre alternativas. |
| Desciframiento | Regla fija, texto reservado, lectura coherente y comprobación externa independiente. | Extensión y réplica por otros equipos, sin cambiar reglas al ver el resultado. |

## 2. Punto de partida material y documental

Yale conserva Beinecke MS 408 y facilita imágenes de alta resolución. Su página describe una escritura no identificada y contenido aún sin descifrar; agrupa convencionalmente las ilustraciones en secciones de plantas, astronomía/astrología, baños, cosmología, farmacia y posibles recetas. Esas etiquetas ayudan a organizar observaciones, pero no son una traducción de las líneas adyacentes. [R01]

Hay que separar edad del soporte, atribución de catálogo y fecha de escritura. El intervalo de radiocarbono del pergamino citado en la literatura es 1404-1438; no fecha automáticamente la tinta ni cada fase de producción. La página de Yale conserva una atribución de finales del XV o del XVI junto a una descripción material compatible con el XV. No se resuelve esa diferencia copiando una fecha única ni eligiendo una lengua sólo porque se considere muerta. [R01, R09]

La procedencia, las manos y los paralelos iconográficos sirven como restricciones. Los trabajos paleográficos, históricos y sobre secretos médicos abren hipótesis de producción y contexto. No fijan por sí solos un idioma, un alfabeto fonético o el nombre de una planta. Debe preservarse la posibilidad de que distintas manos, cuadernos y géneros produzcan distribuciones distintas. [R10-R12, V03, V05, V14-V16]

## 3. Qué aporta la literatura consolidada

| Familia | Aporte verificable | Límite de interpretación |
| --- | --- | --- |
| Criptanálisis y revisiones | D’Imperio, Reddy/Knight y Bowern/Lindemann ordenan restricciones y posibilidades. [R02-R04] | Que una hipótesis sea plausible o estadísticamente compatible no identifica plaintext. |
| Entropía y composición | Lindemann/Bowern muestran la importancia de transcripción, tamaño del alfabeto, abreviación y posiciones. [R05] | No comparar bytes EVA con fonemas como si la equivalencia estuviera demostrada. |
| Coocurrencias y tópicos | Montemurro/Zanette, Amancio y estudios de relaciones encuentran organización a varias escalas. [R06, R59, V08] | Un tópico estadístico puede reflejar sección, escriba, plantilla o generación, además de tema. |
| Copia y pseudotexto | Rugg/Taylor, Timm y Timm/Schinner proponen mecanismos; los pseudotextos humanos son controles empíricos. [R07-R08, R57-R58, V04] | Reproducir algunas firmas no identifica el mecanismo histórico ni elimina todos los cifrados. |
| Cifrado compatible | Hauer/Kondrak, Bowern/Gaskell y Naibbe exploran restricciones o construcciones que preservan ciertas métricas. [R09, R21, V06] | Un cifrado capaz de imitar rasgos no demuestra que fuera el usado. |
| Producción y posición | Feaster, Stafford, Zattera y Steckley/Steckley examinan forma, representación y disposición. [R11, V10, V12-V13] | Geometría y convenciones pueden generar regularidad sin fijar contenido léxico. |

Una aportación importante de VOY2022 es que incluye resultados compatibles con mecanismos distintos. Gaskell/Bowern muestran que muestras humanas sin sentido pueden compartir muchas métricas de Voynich; sus muestras cortas no prueban qué sucede a escala de cuaderno. Bowern/Gaskell muestran que ciertos cifrados también son compatibles con métricas de grupos. No se deben convertir esos dos resultados en pruebas universales de ausencia o presencia de lenguaje. [V04, V06]

Rugg propuso construir cadenas mediante tablas y rejillas; Rugg/Taylor ampliaron la comparación a distribuciones de frecuencia, longitud y heterogeneidad. Son mecanismos que pueden fabricar firmas similares, no una demostración de fraude histórico. Amancio y colaboradores combinaron frecuencias, redes e intermitencia y encontraron compatibilidad con lenguaje en varios aspectos. Juntos muestran por qué una familia aislada de métricas es insuficiente: debe discriminar también mecanismos alternativos con igual presupuesto de ajuste. [R57-R59]

Boxer construyó una transcripción independiente y comparó Voynich con el texto enochiano de Sloane 3188. Sus diferencias de riqueza de formas advierten que no existe una única clase de pseudotexto. El repositorio de esa transcripción quedó identificado y fijado al commit 255bd632, del 10-09-2026. Su README declara transcripción directa desde imágenes, notación propia y licencia CC-BY 4.0. Antes de usarla deben comprobarse correspondencia de páginas y cobertura; identificar el recurso no es haber ejecutado su análisis. [V01, R60]

## 4. Novedades relevantes de 2025-2026

4.1. Bifolios, singuliones y orden. Layfield y Davis proponen reconsiderar la estructura original del manuscrito y analizan continuidad con LSA. El artículo de estructura está publicado en Digital Medievalist; el registro de DHQ describe el trabajo previo. La página de la revista de estructura devolvió un control de acceso y no se presenta aquí una nueva lectura íntegra de su tabla de órdenes. LSA es el nombre de una técnica: sus componentes no traen significado lingüístico demostrado. [R13-R14]

La revisión independiente de Timm, compilada el 10-10-2026, distingue la similitud de páginas conjuntas de la recuperación del orden de lectura. Señala como alternativas la producción por hoja y el contraste Currier, y reclama nulos por permutación y calibración sobre textos conocidos deliberadamente desordenados. Es una crítica con hipótesis comprobables; no una refutación causal ya probada. Nuestro análisis por pares y sus resultados negativos son pertinentes a esa separación, sin sustituir una réplica exacta de LSA. [R15, R55]

El artículo de Timm de septiembre de 2026 desarrolla una interpretación de texto dinámico y proceso de producción. Se distingue su versión publicada del manuscrito accesible del autor. La consecuencia operativa es evaluar evolución, sesiones y copia como variables competidoras, no declarar resuelto el origen del manuscrito. [R16]

4.2. Currier y firmas direccionales. Parisel propone una confirmación cuantitativa de A/B y un modelo de plantillas y conmutación; otra contribución informa restricciones de dirección y controles de generadores. Son preprints. Una clasificación de A/B, incluso con folios reservados, no prueba dos idiomas ni convierte un conmutador estadístico en una clave. Que fallen las clases de generadores ensayadas tampoco descarta todas las clases restantes. [R17-R18]

4.3. Las unidades no se deben asumir. Rozanova y Temerev prueban glifos, grupos delimitados y separadores con controles y remuestreo por cuaderno, y conectan ciertos separadores con medidas de imagen. Su aporte es exigir evidencia antes de llamar letra, palabra o espacio léxico a una unidad observada. El rechazo de sustitución uno-a-uno se limita a los textos y representaciones ensayados; su estudio no afirma ausencia de significado. La réplica debe conservar su limpieza y sus controles, y después extenderlos a otras transcripciones. [R19]

4.4. Pastiche y LLM. Turenne combina gramáticas probabilísticas, comparaciones fonéticas y análisis de imágenes asistido por modelos para proponer un pastiche. El PDF dice submitted to ACM: es un preprint, no una aceptación comprobada. Su interpretación de símbolos como letras no debe reconciliarse automáticamente con R19: corpus y unidades difieren. Las semejanzas de plantas sugeridas por modelos necesitan negativos, anotación independiente y prueba de predicción; una explicación plausible generada por un LLM no es dato semántico. [R20]

4.5. Naibbe. La publicación de Greshko importa como construcción que transforma latín e italiano en texto con rasgos parecidos a Voynich. Esto debilita inferencias que descartaban el cifrado sólo por algunos rasgos de superficie. No valida una clave aplicada al manuscrito ni prueba origen histórico; la comparación debe exigir todas las firmas y texto reservado. [R21]

## 5. Propuestas de lectura, correcciones y autores independientes

| Propuesta | Estado al corte | Prueba que todavía se necesita |
| --- | --- | --- |
| Pahlavi / Herrmann [R22] | Preprint de correspondencias; el resumen no intenta traducción integral. | Mapping fijo, ambigüedades acotadas y lectura de pasajes reservados. |
| Nombres en dibujos / Bax [R23] | Documento de trabajo con identificación parcial propuesta. | Identificaciones visuales independientes, alternativas de nombres y negativos emparejados. |
| Proto-Romance / Cheshire [R24] | Artículo publicado; no se trata aquí como solución reproducida. | Reglas constantes, corpus histórico y predicción que no dependa de paráfrasis ad hoc. |
| Lectura turca / ATA [R25] | Documentación del proyecto y alegaciones de validación. | Método ejecutable y evaluación ciega; apoyos personales o de modelos no bastan. |
| Proporciones y números / Jama [R26] | Preprint estructural. | Comparar contra búsquedas equivalentes en controles; recuperar contenido comprobable. |
| Lexicón EVA-Romance / Burgos [R27] | Depósito v3 de 2025. | Penalizar amplitud del lexicón, opciones y segmentación; reservar rótulos y texto. |
| Gramática de operadores / Honeycutt [R28] | Versión del 30-09-2026; preprint. | La propia versión aclara inducción/comprobación sobre el mismo corpus: holdout pendiente. |
| Lectura latina / Owens [R29] | La v2 retira la afirmación de desciframiento. | Preservar la corrección: el nulo uniforme no sustentaba la lectura latina. |
| Generador e independencia / solvedvoynich [R30] | Sitio independiente con estimador y generador visibles. | Replicar definición de MI, frecuencias, unidades, parser y cobertura real. |
| Etiquetas zodiacales / Averyanov [R31] | Propuesta independiente y sitio mutable; acceso parcial. | Fijar versión y datos, corregir todas las alineaciones y probar otra fuente externa. |

La corrección de Honeycutt cambia su lectura metodológica: los 77 pares pasan a describirse como no observados, no como prohibiciones universales; la validación fuera de los folios de inducción se reconoce como siguiente paso. La retirada de la lectura latina de Owens recuerda que un nulo demasiado simple puede fabricar una aparente confirmación. Estas aclaraciones deben acompañar la versión original cuando se cite el trabajo. [R28-R29]

Las afirmaciones del sitio solvedvoynich sobre independencia entre líneas y cobertura casi total son alegaciones del autor. La ausencia de información mutua estimada no prueba ausencia de significado, y la cobertura de un conjunto de cadenas no prueba adecuación generativa. Es necesario reconstruir exactamente el estimador y compararlo con controles de igual género y tamaño. Nuestro generador de copia no encontró adecuación conjunta, lo que tampoco refuta todos los generadores. [R30, R55]

## 6. Qué demostró nuestro repositorio y qué no

| Ensayo ejecutado | Resultado auditado | Conclusión autorizada |
| --- | --- | --- |
| Transformación de rótulos, informe 42 | Diez pares utilizables; 0/10 rótulos generados. Contraste raíz/hoja BLOCKED. | Ese canal no aprendió una regla útil; no hay validación semántica. |
| Copia local, informe 43 | 89 grupos de hoja, cinco particiones; mejora de 0,00335-0,00419 bits/token. | Ganancia pequeña; la generación falla repeticiones, variantes y riqueza. |
| Pares Q13, informe 44 | TF-IDF bruto: rango 3/945. Control residual falla. TimesFM supera en error a la media. | Asociación descriptiva con bifolio; no continuidad semántica ni orden único. |
| Réplica Q1/Q3/Q20, informe 45 | P bruto conjunto restringido 0,00311/0,00441; residual 0,24277/0,43309. | FAIL_REPLICATION_PANEL; la hipótesis estricta no pasa. |
| Forecast en Q20, informe 45 | TimesFM 2.5 tiene 9,88% más error que la media de la fuente. | Sin ventaja del modelo grande en ese test; no evaluación de TimesFM 3.0. |

Los 29 controles del run autoritativo 37667152334 pasaron y se auditó la salida completa. Eso significa que el programa y los controles se ejecutaron correctamente; el resultado científico negativo permanece. Q1 y Q3 quedaron bloqueados sólo para TimesFM por el horizonte de cuatro filas limpias. El análisis léxico de esos grupos se mantuvo. Q20 cubrió cuatro bifolios seleccionados, no todo el cuaderno. [R55]

En Q13 el exceso de error de TimesFM frente al promedio fue 26,58%; en el subconjunto de Q20 fue 9,88%. Son porcentajes relativos de error, no porcentajes descifrados ni diferencias en puntos porcentuales. Los ensayos usaron el checkpoint google/timesfm-2.5-200m-pytorch y el paquete timesfm[torch]==3.0.2; el número del paquete no convierte ese checkpoint en TimesFM 3.0. [R55]

Q13, Q1, Q3 y Q20 se tomaron de un corpus previamente explorado. La coincidencia bruta y sus fallos de control no demuestran la ausencia de lengua o contenido; el ajuste de trigramas también puede retirar señal léxica real. La originalidad de una aportación y una traducción siguen sin estar establecidas. [R55-R56]

## 7. Herramientas emergentes y recursos que vale la pena considerar

La tabla distingue novedades instrumentales de 2025-2026 de herramientas maduras que permiten aplicarlas de manera controlada. La prioridad considera relación con nuestro cuello de botella, datos necesarios y posibilidad de falsación. Todos los usos Voynich propuestos en este apartado están NOT_RUN; no se extrapolan porcentajes de benchmarks ajenos.

| Herramienta / versión | Aplicación concreta | Límite / prioridad |
| --- | --- | --- |
| Boxer + IVTFF/ZL [V01, R32, R60] | Alinear otra transcripción por folio/línea y repetir las firmas sin cambiar criterios. | Maduro, inmediato. Repositorio identificado; verificar cobertura y alineación antes de ejecutar. |
| Kraken + eScriptorium [R41-R42] | Regiones, líneas, máscaras y reconocimiento supervisado de una notación operativa propia. | Alta. Requiere anotación revisada y particiones por hoja/mano; no trae idioma Voynich. |
| DINOv3 + FINO [R36-R37] | Comparar recortes de signos y aprender representaciones visuales adaptadas por metadatos. | Alta para piloto visual. Probar que no agrupa sólo mano, tamaño, tinta o procedencia. |
| SAM 3 [R38] | Proponer máscaras desde ejemplares revisados de tinta, signos o elementos gráficos. | Media-alta. Objetos naturales no son glifos; no usar un nombre de planta como verdad. |
| PaddleOCR-VL-1.6 [R39-R40] | Convertir y estructurar fuentes comparadoras con escritura conocida; probar extracción de layout. | Media. Fecha oficial 28-05-2026; no precisión demostrada en Voynich. |
| NeuroDecipher / prior fonético [R43-R45] | Calibrar segmentación y correspondencias en cifrados/lenguas con solución conocida. | Alta como benchmark condicionado. Parentesco y valores fonéticos aún desconocidos. |
| Pynini + CP-SAT / Z3 [R46-R48] | Expresar reglas globales, abreviación, homofonía o transducción y localizar contradicciones. | Alta para modelos explícitos. La solución del solver no es prueba de significado. |
| Aeneas / Ithaca [R33-R35] | Buscar paralelos y restaurar texto de comparadores griegos/latinos; arquitectura multimodal como referencia. | Media para comparadores; baja para traducción directa de EVA. |
| AlphaEvolve o búsqueda evolutiva de código [R49] | Generar programas candidatos que superen un evaluador congelado con negativos. | Condicional. Acceso e integración no comprobados; riesgo alto de optimizar un test débil. |
| TimesFM 3.0 / Chronos-2 [R50-R51] | Forecast multivariante con mano, posición y layout como covariables permitidas. | Baja para descifrado. Deben superar media, persistencia y modelos pequeños en reserva. |
| Pipeline Vesuvius [R52] | Ideas de trazabilidad píxel-máscara y validación física de tinta. | Baja aplicación directa: Voynich ya tiene superficie visible; no es el mismo problema. |

7.1. Novedad visual. DINOv3 proporciona características densas; FINO, presentado en junio de 2026, adapta representaciones usando metadatos. Es una oportunidad para modelar variación por mano y soporte con pocos rótulos semánticos. Sus benchmarks no incluyen una validación Voynich que hayamos comprobado. Una agrupación visual debe verificarse por anotadores y mantenerse separada de cualquier supuesto de equivalencia fonética. [R36-R37]

SAM 3 admite ejemplares además de conceptos. Para este proyecto preferiría recortes de tinta revisados a prompts como salvia, letra a o raíz medicinal: esos nombres incorporan interpretación en la entrada. Su utilidad prevista es medir signos y espacios, con fallos e incertidumbre guardados. No autoriza reconstruir trazos que no estén en la imagen. [R38]

PaddleOCR-VL-1.6 fue anunciado el 28-05-2026; el antecedente 1.5 tiene paper y anuncio de enero. El soporte de documentos antiguos y caracteres raros sigue siendo una capacidad general, no evidencia sobre un alfabeto sin lectura. Es más inmediatamente útil para transcribir los textos conocidos con los que vamos a comparar que para asignar significado al manuscrito. [R39-R40]

7.2. Descifrado restringido. Los trabajos de Luo y colaboradores son los más cercanos al tipo de problema lingüístico planteado: combinan restricciones y alineación o segmentación con priors fonéticos. Sus éxitos publicados son benchmarks en sistemas ya descifrados y relaciones lingüísticas aprovechables. El modelo de 2021 también muestra que no tiene que confirmar un parentesco supuesto. En Voynich debemos probar primero qué unidad puede relacionarse con un sonido y qué corpus relacionado se justificaría; el algoritmo no resuelve esas premisas por su nombre. [R43-R45]

Pynini permite representar un canal de escritura con varias reglas y pesos; CP-SAT o Z3 pueden imponer una misma clave a todo el material y detectar contradicciones. Son herramientas maduras, no descubrimientos de 2026. Propongo usarlas como disciplina contra reglas cambiantes: número de equivalencias, excepciones, inversiones y abreviaciones limitado antes del test. Una contradicción sólo refuta esa clase y esos supuestos; una asignación satisfactoria puede ser una de muchas. [R46-R48]

7.3. Modelos de contexto. Aeneas fue anunciado en julio de 2025 con publicación en Nature y código/datos públicos para inscripciones latinas; Ithaca es su antecedente para griego. Buscan paralelos, restauración y atribución en lenguas conocidas. No se deben alimentar las cadenas EVA como si fueran latín y considerar la salida una traducción. La transferencia útil es de arquitectura y de búsqueda en comparadores, o de hipótesis de plaintext ya justificadas externamente. [R33-R35]

7.4. Agentes y evaluación. AlphaEvolve combina propuestas de código y evaluadores. La idea transferible es que el agente proponga mecanismos ejecutables y el harness los juzgue. Su aplicación Voynich depende por completo de qué mida ese harness: si premia sólo Zipf, entropía o frases bonitas, puede producir falsos descifrados mejores ajustados. No se ha comprobado aquí acceso operativo al servicio ni una aplicación a nuestro corpus. [R49]

7.5. Forecasting nuevo. El README de TimesFM anuncia 3.0 en agosto y rollout de Cloud en septiembre de 2026; introduce multivariante y covariables. Los pesos 3.0 tienen condiciones distintas de 2.5, y la documentación diferencia pesos locales de uso en Cloud. Chronos-2 fue anunciado el 20-10-2025 y también incorpora multivariante/covariables. Son novedades reales y ninguna se evaluó en nuestros ensayos. Cambiar de forecaster merece un piloto sólo con una pregunta estructural nueva y comparación completa; no es la prioridad para leer el contenido. [R50-R51]

Vesuvius demuestra una vía distinta de avance: recuperar tinta y geometría de soportes enrollados mediante imágenes y aprendizaje. La lectura de letras griegas físicamente ocultas no es prueba de que un sistema pueda descifrar signos visibles de valor desconocido. Tomaría su trazabilidad y evaluación visual, no trasladaría el objetivo de reconstrucción 3D a Voynich sin una necesidad material concreta. [R52]

## 8. Estrategia recomendada: dos canales y un test externo

Mi elección es un modelo explícito que separe el canal de producción gráfica del canal lingüístico/criptográfico. Es una síntesis de enfoques ya existentes y no se presenta como una idea jamás explorada. Su utilidad sería reducir ambigüedad y obligar a cada hipótesis a hacer predicciones distintas. Los objetivos siguientes son propuestas de protocolo, no resultados ejecutados.

| Paso | Datos y método | Condición para avanzar |
| --- | --- | --- |
| A. Reproducir unidades | ZL y transcripción independiente; alineación por locus; comas, compuestos y fragmentos inciertos preservados. | Efectos estables o incertidumbre explícita por discrepancia. Nada de elegir la versión que da más señal. |
| B. Canal físico | Imágenes Yale; anotadores; Kraken/eScriptorium; piloto DINOv3/SAM para signos, anchos y geometría. | Reconocimiento y medidas verificados en hojas no usadas para ajustar. Sin nombres de plantas o fonemas como etiquetas. |
| C. Controles de mecanismo | Pseudotexto humano, copia, Naibbe, plantillas y prosa/catálogos con género y longitud comparables. | El evaluador distingue controles conocidos y rechaza falsos positivos con búsqueda equivalente. |
| D. Canal de clave | Pynini y solver; familias limitadas; corpora históricos; probabilidades de segmentación y variantes. | Una regla global supera baselines y controles en material reservado sin ampliar excepciones. |
| E. Anclaje externo | Rótulos o patrones vinculados a objetos y textos conocidos por fuentes independientes. | Identificación fijada antes de revelar test, con candidatos alternativos y negativos. |
| F. Lectura y réplica | Aplicación de la regla congelada a un nuevo pasaje; análisis gramatical y contraste histórico. | Otros investigadores obtienen la misma lectura y predicciones sin reinterpretar los signos. |

El canal físico estima variantes de signo, separadores, compuestos y efectos de mano/posición. El canal de clave transforma unidades operativas en candidatos limitados. La evidencia externa permite romper la ambigüedad de una recodificación que sólo produce texto fluido. Deben guardarse las alternativas, no colapsar todo a una única transcripción o frase antes de evaluar.

Un anclaje basado en una imagen necesita selección y verificación independientes: una misma planta convencional puede tener muchos nombres; una figura zodiacal puede indicar signo, grado, persona u otra categoría. Los experimentos de raíz/hoja del repositorio muestran precisamente que hoy falta ese contraste verificado. Una geometría sugerente no suministra automáticamente el nombre. [R55]

Los corpus históricos deben separarse por época, género, convención y abreviaciones. TLIO/OVI y MHDBDB ofrecen comparadores documentados para italiano antiguo y alemán medio. Son ejemplos de recursos, no candidatos ganadores. También se requieren fuentes latinas y otros controles adecuados; no se selecciona un idioma por un puntaje agregado que cambia con el alfabeto. [R53-R54]

El benchmark previo a tocar Voynich debe incluir sistemas de solución conocida con segmentación borrada o escritura transformada, y negativos sin contenido. El mismo presupuesto de búsqueda y todas las variantes se aplican a ambos. El score de entrenamiento combina predicción, adecuación de firmas y penalización de complejidad; el test final se mantiene cerrado. Los priors fonéticos sólo se activan cuando exista soporte para la unidad y la relación lingüística supuestas.

## 9. Harness mínimo y decisiones de investigación

- Congelar fuentes y unidades: imágenes, versión de corpus, hashes, máscara de exclusión, locus, manos, sección y cuaderno. Separar datos de anotación, selección de hipótesis y evaluación final.

- Reservar unidades físicas completas. Las dos caras de una hoja y familias o figuras relacionadas no pueden separarse de forma que filtren información al test. El análisis por línea no valida el reordenamiento de páginas.

- Repetir con transcripción independiente. Una transliteración recodificada del mismo original no es otra anotación independiente. Evaluar qué discrepancias cambian el resultado.

- Mantener nulos con frecuencia, longitud, mano, sección y geometría cuando proceda. Si se busca entre claves, offsets o segmentaciones, la permutación debe repetir toda esa selección.

- Comparar contra media, persistencia, n-gramas, modelos pequeños y mecanismos históricos. La ventaja del modelo grande debe medirse en el mismo test y con presupuesto de ajuste comparable.

- Evaluar generación libre además de predicción con contexto real. La copia local del repositorio mejora ligeramente una pérdida, pero falla otras firmas; eso impide ascender a explicación completa.

- Registrar complejidad de clave y excepciones. Cambiar una equivalencia tras leer el pasaje se cuenta como ajuste. Dar miles de significados candidatos no constituye cobertura semántica validada.

- Exigir validación externa para afirmar significado. Coherencia narrativa, traducción de un LLM o acuerdo entre agentes no son gold standard. Preservar contraejemplos y lecturas alternativas.

- Usar PASS, FAIL, BLOCKED y NOT_RUN con alcance estrecho. El éxito de una ejecución CI no implica PASS científico; una falsación de una clase no es falsación universal.

Decisión de inversión: primero transcripción independiente y benchmark controlado; después piloto visual y clave restringida. Aeneas es referencia y apoyo en comparadores. Los agentes pueden ayudar con código y búsqueda bajo evaluación cerrada. Nuevos forecasters quedan en una rama auxiliar hasta que demuestren una ventaja estructural que los modelos simples no proporcionen.

## 10. Qué podría sostener un paper serio

Con el material actual no sería justificable un artículo que anuncie el desciframiento. Sí puede prepararse un estudio de reproducción y falsación de métodos, sujeto a comprobar originalidad frente a R03-R21 y las actas. La posible aportación es un benchmark trazable que separe unidad física, generación, segmentación y continuidad; los resultados negativos deben publicarse junto a los positivos y la incertidumbre.

Una contribución nueva requeriría al menos otra transcripción, controles de mecanismo comparables, ablation de variables de producción y un resultado reservado que distinga explicaciones. Si el objetivo es traducción, además se necesita un anclaje externo y una regla que acierte en material nuevo. El rechazo de un modelo grande frente a una media es informativo sobre ese uso del modelo, pero no demuestra por sí solo una teoría histórica.

Conclusión al 14-10-2026: el problema permanece abierto en las fuentes revisadas. Las herramientas nuevas hacen más viable medir la escritura y buscar modelos disciplinados; no proporcionan una Rosetta automática. La ruta más defendible para este proyecto es mejorar la evidencia de entrada y someter reglas globales a controles que puedan hacerlas fracasar. Ese cambio de criterio es más valioso que multiplicar órdenes óptimos o respuestas plausibles.

## 11. Cobertura de VOY2022: los 16 trabajos

El índice CEUR declara 32 envíos y 16 aceptados con revisión doble ciego en dos fases. Las conferencias magistrales son entradas separadas. Se verificó el índice completo y se recuperaron los PDF salvo paper2, que excedió el límite de tamaño. Consulta de PDF no equivale a reproducción de código ni auditoría completa del método. Los temas de la tabla están traducidos y abreviados. [V01-V16]

| ID / autores | Tema | Lectura crítica |
| --- | --- | --- |
| V01 · Alexander Boxer | Comparación con Sloane 3188 | Transcripción independiente y repeticiones; no inferir significado del parecido. |
| V02 · Koen Gheuens; Cary Rapaport | Toldos y tiendas | Atribución iconográfica; no correspondencia glifo-sonido. |
| V03 · Keagan Brewer | Secretos ginecológicos medievales | Contexto de ocultamiento; no lectura del texto. |
| V04 · Daniel Gaskell; Claire Bowern | Pseudotextos humanos | Controles empíricos; muestras cortas no deciden estructura de cuadernos. |
| V05 · Kevin Farrugia; Colin Layfield; Lonneke van der Plas | Atribución computacional de escribas | Control por producción y estilo. |
| V06 · Claire Bowern; Daniel Gaskell | Compatibilidad con cifrados | Algunas métricas son compatibles con cifrado; no prueba de clave. |
| V07 · Jürgen Hermes | Polygraphia III | Comparador histórico de cifrado con apariencia de lengua. |
| V08 · Andrew Caruana; Colin Layfield; John Abela | Relaciones entre grupos de texto | Dependencia local; distinguir predictor y semántica. |
| V09 · Luke Lindemann | MATTR y morfología | Control por diversidad y ventana; no inferir idioma directamente. |
| V10 · Massimiliano Zattera | Transliteración y estructura | La representación modifica resultados; unidad operativa explícita. |
| V11 · Katie Painter; Claire Bowern | Historia de glifos | Métodos filogenéticos como hipótesis sobre escritura. |
| V12 · Patrick Feaster | Distribuciones de posición | Geometría de línea/página como covariable necesaria. |
| V13 · Tavi Stafford | Regularidades de párrafos | Separar firmas de párrafo y secuencia. |
| V14 · Farley Katz | Historia de propiedad | Evidencia documental, sin clave lingüística. |
| V15 · Klaus Schmeh; Elonka Dunin | Otros libros cifrados | Comparadores históricos y límites de analogía. |
| V16 · Stefan Guzy | Transacciones de Rodolfo II | Procedencia documentada, distinta de interpretación del texto. |

## 12. Límites de acceso, fechas y afirmaciones

Limitaciones registradas: páginas de Taylor & Francis devolvieron 403; Digital Medievalist mostró Anubis; DHQ y el depósito Penn no se recuperaron íntegramente; Nature redirigió a autenticación. Se usaron registros editoriales y manuscritos/explicaciones de autores cuando estaban disponibles, manteniendo la distinción. No se eludieron barreras ni se inventaron resultados de textos no leídos.

Correcciones de identificación: arXiv:2010.14697 corresponde al trabajo de entropía de Lindemann/Bowern, no a la revisión The Linguistics; esta última tiene el DOI de Annual Reviews [R04-R05]. Se usó Honeycutt 23068600, no la etiqueta de la versión anterior 20368211. El PDF de Turenne tiene una discrepancia entre fecha de cabecera y mes del identificador; se consigna sólo el año/versión consultada, sin inventar día de publicación. Para Rugg y Rugg/Taylor se separa año de volumen de digitalización o publicación online [R57-R58].

No se ofrecen porcentajes de probabilidad de resolver Voynich, plazos garantizados, listas exhaustivas de todos los idiomas ni precisión de OCR sobre escritura no evaluada. Las fechas de anuncios de herramientas no son fechas de validación Voynich. Ninguna noticia de octubre reemplaza la fecha o el contenido del artículo que describe.

## Referencias y recursos consultados

Las referencias enlazan fuentes primarias, páginas de autores o registros editoriales. Las notas de acceso y de versión completas están en el registro JSON acompañante. Las entradas con año s.f. o documentación al corte describen páginas consultadas el 14-10-2026, no una fecha de lanzamiento inventada.

**[R01]** Yale Library (s.f.). The Beinecke Cipher (Voynich) Manuscript. Institucional. Acceso: Página institucional consultada. [Fuente](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript).

**[R02]** Mary E. D’Imperio / NSA (1978). The Voynich Manuscript: An Elegant Enigma. Monografía institucional. Acceso: Referencia histórica; acceso directo limitado en esta actualización. [Fuente](https://www.nsa.gov/portals/75/documents/about/cryptologic-heritage/historical-figures-publications/publications/misc/voynich_manuscript.pdf).

**[R03]** Sravana Reddy; Kevin Knight (2011). What We Know About The Voynich Manuscript. Artículo de congreso. Acceso: PDF y registro consultados. [Fuente](https://aclanthology.org/W11-1511/).

**[R04]** Claire L. Bowern; Luke Lindemann (2021). The Linguistics of the Voynich Manuscript. Revisión de revista. Acceso: Resumen editorial y bibliografía; no auditoría íntegra del texto. [Fuente](https://doi.org/10.1146/annurev-linguistics-011619-030613).

**[R05]** Luke Lindemann; Claire Bowern (2021). Character Entropy in Modern and Historical Texts: Comparison Metrics for an Undeciphered Manuscript. Preprint. Acceso: Resumen y versiones: v2, 18-05-2021. [Fuente](https://arxiv.org/abs/2010.14697v2).

**[R06]** Marcelo A. Montemurro; Damián H. Zanette (2013). Keywords and Co-Occurrence Patterns in the Voynich Manuscript: An Information-Theoretic Analysis. Artículo de revista. Acceso: Texto editorial accesible y consultado. [Fuente](https://doi.org/10.1371/journal.pone.0066344).

**[R07]** Torsten Timm (2014). How the Voynich Manuscript was created. Preprint. Acceso: Resumen primario consultado. [Fuente](https://arxiv.org/abs/1407.6639).

**[R08]** Torsten Timm; Andreas Schinner (2020). A possible generating algorithm of the Voynich manuscript. Artículo de revista. Acceso: Registro editorial; texto directo bloqueado. [Fuente](https://doi.org/10.1080/01611194.2019.1596999).

**[R09]** Bradley Hauer; Grzegorz Kondrak (2016). Decoding Anagrammed Texts Written in an Unknown Language and Script. Artículo de revista TACL. Acceso: Registro y resumen primarios consultados. [Fuente](https://aclanthology.org/Q16-1006/).

**[R10]** Lisa Fagin Davis (2020). How Many Glyphs and How Many Scribes? Digital Paleography and the Voynich Manuscript. Artículo de revista. Acceso: Registro bibliográfico; depósito 2021, acceso directo limitado. [Fuente](https://repository.upenn.edu/items/5db6a3b2-e18d-4cf7-bfd4-ba8c0c347597).

**[R11]** Andrew Steckley; Noah Steckley (2024). Subtle Signs of Scribal Intent in the Voynich Manuscript. Preprint. Acceso: Resumen primario consultado. [Fuente](https://arxiv.org/abs/2404.13069).

**[R12]** Keagan Brewer; Michelle L. Lewis (2024). The Voynich Manuscript, Dr Johannes Hartlieb and the Encipherment of Women’s Secrets. Artículo de revista. Acceso: Registro editorial; acceso íntegro limitado. [Fuente](https://doi.org/10.1093/shm/hkad099).

**[R13]** Colin Layfield; Lisa Fagin Davis (2026). The Application of Latent Semantic Analysis to the Voynich Manuscript. Artículo de revista DHQ. Acceso: Registro verificado; texto directo no recuperado. [Fuente](https://www.digitalhumanities.org/dhq/vol/20/1/000857/000857.html).

**[R14]** Colin Layfield; Lisa Fagin Davis (2026). Singulion Structure and the Voynich Manuscript. Artículo de revista Digital Medievalist. Acceso: Registro y explicación de autora; página con control Anubis. [Fuente](https://doi.org/10.4000/16k0a).

**[R15]** Torsten Timm (2026). The Singulion and the Sequence: A Methodological Review of Layfield and Davis on the Voynich Manuscript. Revisión independiente / preprint. Acceso: Texto de autor accesible; compilado 10-10-2026. [Fuente](https://www.academia.edu/170072857/The_Singulion_and_the_Sequence_A_Methodological_Review_of_Layfield_and_Davis_on_the_Voynich_Manuscript).

**[R16]** Torsten Timm (2026). The challenge of analyzing a dynamic text: why the Voynich manuscript resists conventional interpretation. Artículo de revista Cryptologia. Acceso: Registro editorial y manuscrito del autor; versión publicada 07-09-2026. [Fuente](https://doi.org/10.1080/01611194.2026.2693462).

**[R17]** Christophe Parisel (2026). A Quantitative Confirmation of the Currier Language Distinction. Preprint. Acceso: Resumen primario; v2 del 05-05-2026. [Fuente](https://arxiv.org/abs/2604.25979v2).

**[R18]** Christophe Parisel (2026). Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript: Implications for Cipher-Like Structure. Preprint. Acceso: Resumen primario y versión v2 consultados. [Fuente](https://arxiv.org/abs/2604.19762v2).

**[R19]** Liudmila Rozanova; Alexander Temerev (2026). A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space: What the Units of Voynichese Are Not. Preprint. Acceso: HTML y métodos consultados; versión del 17-08-2026. [Fuente](https://arxiv.org/html/2608.17096v1).

**[R20]** Nicolas Turenne (2026). A Generative Grammar Underlying the Voynich Manuscript, the Pastiche Hypothesis: Evidence from Large Language Models. Preprint. Acceso: PDF consultado; indica submitted to ACM. [Fuente](https://arxiv.org/pdf/2609.20835).

**[R21]** Michael A. Greshko (2025). The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext. Artículo de revista Cryptologia. Acceso: Registro editorial; texto directo bloqueado. [Fuente](https://doi.org/10.1080/01611194.2025.2566408).

**[R22]** J. Michael Herrmann (2017). The Voynich Manuscript is Written in Natural Language: The Pahlavi Hypothesis. Preprint. Acceso: Resumen primario; v2 del 06-10-2017. [Fuente](https://arxiv.org/abs/1709.01634v2).

**[R23]** Stephen Bax (2014). A proposed partial decoding of the Voynich script. Documento de trabajo. Acceso: Descripción del autor y registro consultados. [Fuente](https://www.academia.edu/5932444/A_proposed_partial_decoding_of_the_Voynich_script).

**[R24]** Gerard Cheshire (2019). The Language and Writing System of MS408 (Voynich) Explained. Artículo de revista Romance Studies. Acceso: Registro editorial consultado; no auditoría completa del texto. [Fuente](https://doi.org/10.1080/02639904.2019.1599566).

**[R25]** Proyecto ATA / familia Ardıç (2020-2025). Voynich Manuscript Revealed y documentación del proyecto turco. Propuesta de autores. Acceso: Página del proyecto y descripciones públicas consultadas. [Fuente](https://turkicresearch.com/aboutus).

**[R26]** S. A. Jama (2025). The Voynich Codex Decoded: Statistical Symbolism and Scroll-Wide Logic. Preprint. Acceso: Resumen primario consultado. [Fuente](https://arxiv.org/abs/2505.02261).

**[R27]** David Aarón Burgos Córdova (2025). An Integral Framework for Translating the Voynich Manuscript: The EVA–Romance Lexicon, the Arrhythmic Principle, and a Complete Token Corpus (v3.0). Preprint. Acceso: Registro y descripción; 08-09-2025, v3. [Fuente](https://zenodo.org/records/17070155).

**[R28]** Edwin Marshall Honeycutt III (2026). An Operator Grammar for Beinecke MS 408: Full-Manuscript Validation, Challenge Testing, and Contemporary Manuscript Comparison. Preprint. Acceso: Versión del 30-09-2026 consultada. [Fuente](https://zenodo.org/records/23068600).

**[R29]** Matthew Owens (2026). Voynichese Has Natural-Language-Range Character Entropy but Anomalous Order-Scaling: A Corrected Statistical Characterization. Preprint corregido. Acceso: Descripción primaria v2; corrección indicada julio de 2026. [Fuente](https://doi.org/10.17613/5nhb8-ra074).

**[R30]** Autor del sitio solvedvoynich.com (2026 / sitio dinámico). The Voynich Manuscript Is Not a Language. Propuesta independiente. Acceso: Texto y generador visibles consultados; sin versión inmutable identificada. [Fuente](https://solvedvoynich.com/).

**[R31]** Averyanov / voynich.site (2026 / sitio dinámico). A Workshop Cipher y trabajos sobre rótulos zodiacales. Propuesta independiente. Acceso: Referencia de revisión previa; acceso actual parcial. [Fuente](https://voynich.site/publications).

**[R32]** René Zandbergen; Gabriel Landini y otros transcriptores (Documentación vigente al corte). Transcriptions and transliterations of the Voynich MS. Recurso de investigación. Acceso: Documentación pública consultada. [Fuente](https://www.voynich.nu/transcr.html).

**[R33]** Equipo Aeneas / Google DeepMind (2025). Aeneas transforms how historians connect the past. Anuncio técnico de autores. Acceso: Artículo oficial del 23-07-2025; enlaza artículo Nature. [Fuente](https://deepmind.google/blog/aeneas-transforms-how-historians-connect-the-past/).

**[R34]** Yannis Assael y colaboradores (2025). Contextualizing ancient texts with generative neural networks. Artículo de revista Nature. Acceso: Registro y anuncio de autores; acceso directo bloqueado. [Fuente](https://doi.org/10.1038/s41586-025-09292-5).

**[R35]** Google DeepMind (Documentación al corte). predictingthepast: Aeneas e Ithaca. Código/documentación oficial. Acceso: README y rutas de inferencia consultados. [Fuente](https://github.com/google-deepmind/predictingthepast).

**[R36]** Oriane Siméoni y colaboradores (2025). DINOv3. Preprint y código de autores. Acceso: Registro primario; 13-08-2025; implementación disponible. [Fuente](https://arxiv.org/abs/2508.10104). [Recurso 1](https://github.com/facebookresearch/dinov3).

**[R37]** Elouan Gardès y colaboradores (2026). Who Needs Labels? Adapting Vision Foundation Models With the Metadata You Already Have. Preprint / código FINO. Acceso: Resumen primario; 03-06-2026; código anunciado 12-06-2026. [Fuente](https://arxiv.org/abs/2606.05107). [Recurso 1](https://github.com/facebookresearch/dinov3/tree/FINO).

**[R38]** Nicolas Carion y colaboradores (2025-2026). SAM 3: Segment Anything with Concepts. Preprint y código de autores. Acceso: Resumen primario; v1 20-11-2025, v2 28-03-2026. [Fuente](https://arxiv.org/abs/2511.16719v2). [Recurso 1](https://github.com/facebookresearch/sam3).

**[R39]** PaddlePaddle / equipo PaddleOCR (2026). PaddleOCR-VL-1.6 y changelog de PaddleOCR. Documentación y código oficial. Acceso: README consultado: anuncio 28-05-2026. [Fuente](https://github.com/PaddlePaddle/PaddleOCR).

**[R40]** Equipo PaddleOCR (2026). PaddleOCR-VL-1.5: Towards a Multi-Task 0.9B VLM for Robust In-the-Wild Document Parsing. Preprint de herramienta. Acceso: Registro primario; 29-01-2026. [Fuente](https://arxiv.org/abs/2601.21957).

**[R41]** Equipo Kraken (Documentación al corte). Kraken 6.0.0: Training Tutorial. Herramienta madura / documentación. Acceso: Tutorial oficial consultado. [Fuente](https://kraken.re/6.0.0/tutorials/training.html).

**[R42]** Equipo eScriptorium (Documentación al corte). Automatic prediction - eScriptorium Documentation. Herramienta madura / documentación. Acceso: Guía oficial consultada. [Fuente](https://escriptorium.readthedocs.io/en/latest/predict/).

**[R43]** Jiaming Luo; Yuan Cao; Regina Barzilay (2019). Neural Decipherment via Minimum-Cost Flow: From Ugaritic to Linear B. Artículo de congreso ACL. Acceso: Resumen y código de autores consultados. [Fuente](https://aclanthology.org/P19-1303/).

**[R44]** Jiaming Luo; Frederik Hartmann; Enrico Santus; Regina Barzilay; Yuan Cao (2021). Deciphering Undersegmented Ancient Scripts Using Phonetic Prior. Artículo de revista TACL. Acceso: Resumen y enlace de código primarios consultados. [Fuente](https://aclanthology.org/2021.tacl-1.5/).

**[R45]** Jiaming Luo y colaboradores (2019/2021). NeuroDecipher / DecipherUnsegmented: implementaciones. Código de autores. Acceso: Repositorio verificado; segundo código enlazado en bibliografía. [Fuente](https://github.com/j-luo93/NeuroDecipher). [Recurso 1](https://github.com/j-luo93/DecipherUnsegmented).

**[R46]** Kyle Gorman / OpenGrm (Herramienta madura). Pynini: weighted finite-state grammar compilation. Código/documentación de autor. Acceso: README consultado; espejo de sólo lectura. [Fuente](https://github.com/kylebgorman/pynini).

**[R47]** Google OR-Tools (Herramienta madura). CP-SAT solver. Documentación oficial. Acceso: Documentación consultada. [Fuente](https://developers.google.com/optimization/cp/cp_solver).

**[R48]** Microsoft Research / equipo Z3 (Herramienta madura). Z3 Guide. Documentación oficial. Acceso: Guía y parámetros consultados. [Fuente](https://microsoft.github.io/z3guide/).

**[R49]** Google DeepMind / AlphaEvolve team (2025). AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms. Anuncio técnico de autores. Acceso: Artículo oficial del 14-05-2025. [Fuente](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/).

**[R50]** Google Research (2026). TimesFM 3.0: updates August and September 2026. Código/documentación oficial. Acceso: README y aviso de licencia consultados. [Fuente](https://github.com/google-research/timesfm).

**[R51]** Amazon Science (2025). Chronos-2. Código/documentación oficial. Acceso: README: lanzamiento 20-10-2025. [Fuente](https://github.com/amazon-science/chronos-forecasting).

**[R52]** Vesuvius Challenge (2023-2026). Reading the Herculaneum Scrolls with AI. Proyecto y documentación primaria. Acceso: Portal y avances oficiales consultados. [Fuente](https://scrollprize.org/).

**[R53]** CNR / Opera del Vocabolario Italiano (Recurso vigente al corte). Tesoro della Lingua Italiana delle Origini / corpus OVI. Infraestructura lingüística institucional. Acceso: Descripción institucional consultada. [Fuente](https://tlio.ovi.cnr.it/).

**[R54]** Universidad de Salzburgo (Recurso vigente al corte). Mittelhochdeutsche Begriffsdatenbank. Infraestructura lingüística institucional. Acceso: Descripción institucional consultada. [Fuente](https://mhdbdb.sbg.ac.at/).

**[R55]** MedinaParra/Voynich (2026). Pruebas 42-45 y auditorías de ejecución. Investigación propia no revisada. Acceso: Código, informes y salidas auditadas; snapshot fijo. [Fuente](https://github.com/MedinaParra/Voynich/tree/3d0b3878590829d7ffdcc47fe19c65833d200ff9/research_gpt6).

**[R56]** cesarjz/Voynich (2025 / snapshot). Corpus ZL EVA fijado para nuestras pruebas. Datos transcritos. Acceso: Blob comprobado por ejecuciones anteriores y auditorías. [Fuente](https://github.com/cesarjz/Voynich/blob/47e6a77dc9d5cd570c375f4aff710fa4a0567278/corpus/voynich_eva.txt).

**[R57]** Gordon Rugg (2004). An Elegant Hoax? A Possible Solution to the Voynich Manuscript. Artículo de revista Cryptologia. Acceso: Registro editorial: volumen 28(1), 2004; digitalización online 2010. [Fuente](https://doi.org/10.1080/0161-110491892755).

**[R58]** Gordon Rugg; Gavin Taylor (2017 / online 2016). Hoaxing statistical features of the Voynich Manuscript. Artículo de revista Cryptologia. Acceso: Resumen y registro editorial; volumen 41(3), 2017. [Fuente](https://doi.org/10.1080/01611194.2016.1206753).

**[R59]** Diego R. Amancio; Eduardo G. Altmann; Diego Rybski; Osvaldo N. Oliveira Jr.; Luciano da Fontoura Costa (2013). Probing the Statistical Properties of Unknown Texts: Application to the Voynich Manuscript. Artículo de revista PLOS ONE. Acceso: Texto primario consultado; 02-07-2013. [Fuente](https://doi.org/10.1371/journal.pone.0067310).

**[R60]** Alexander Boxer (2022-2026 / snapshot). voynich-attack: transcripción independiente y corpus comparadores. Código y datos de autor. Acceso: README y rama verificados; commit 10-09-2026 anterior al corte. [Fuente](https://github.com/alexanderboxer/voynich-attack/tree/255bd632e45459230eaf2a994e0557ed6c682869). [Recurso 1](https://github.com/alexanderboxer/voynich-attack/blob/255bd632e45459230eaf2a994e0557ed6c682869/transcription/vms.csv).

**[V01]** Alexander Boxer (VOY2022 / actas 2023). Fingerprinting Gibberish: A Quantitative Comparison of the Voynich and Sloane MS 3188. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper1.pdf).

**[V02]** Koen Gheuens; Cary Rapaport (VOY2022 / actas 2023). Above and Beyond Voynich Canopies: Tents as a Recurring Motif in Beinecke MS 408. Actas con revisión según índice CEUR. Acceso: Registro de actas; PDF excede límite de recuperación. [Fuente](https://ceur-ws.org/Vol-3313/paper2.pdf).

**[V03]** Keagan Brewer (VOY2022 / actas 2023). 'I beg your grace to suppress this chapter or else to have it written in secret letters': The Emotions of Encipherment in Late-Medieval Gynaecology. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper3.pdf).

**[V04]** Daniel Gaskell; Claire Bowern (VOY2022 / actas 2023). Gibberish after all? Voynichese is Statistically Similar to Human-Produced Samples of Meaningless Text. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper4.pdf).

**[V05]** Kevin Farrugia; Colin Layfield; Lonneke van der Plas (VOY2022 / actas 2023). Demystifying the Scribes behind the Voynich Manuscript using Computational Linguistic Techniques. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper5.pdf).

**[V06]** Claire Bowern; Daniel Gaskell (VOY2022 / actas 2023). Enciphered after all? Word-level Text Metrics are Compatible with some Types of Encipherment. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper6.pdf).

**[V07]** Jürgen Hermes (VOY2022 / actas 2023). Polygraphia III: The Cipher that Pretends to be an Artificial Language. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper7.pdf).

**[V08]** Andrew Caruana; Colin Layfield; John Abela (VOY2022 / actas 2023). An Analysis of the Relationship between Words within the Voynich Manuscript. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper8.pdf).

**[V09]** Luke Lindemann (VOY2022 / actas 2023). Crux of the MATTR: Voynichese Morphological Complexity. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper9.pdf).

**[V10]** Massimiliano Zattera (VOY2022 / actas 2023). A new Transliteration Alphabet brings new Evidence of Word Structure and Multiple "languages" in the Voynich Manuscript. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper10.pdf).

**[V11]** Katie Painter; Claire Bowern (VOY2022 / actas 2023). Examining the history of Voynich Glyphs using Phylogenetic Methods. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper11.pdf).

**[V12]** Patrick Feaster (VOY2022 / actas 2023). Rightward and Downward Grapheme Distributions in the Voynich Manuscript. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper12.pdf).

**[V13]** Tavi Stafford (VOY2022 / actas 2023). Seven Habits of Highly Eccentric Paragraphs. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper13.pdf).

**[V14]** Farley Katz (VOY2022 / actas 2023). From Voynich to the Beinecke, the Trail of Ownership. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper14.pdf).

**[V15]** Klaus Schmeh; Elonka Dunin (VOY2022 / actas 2023). The Voynich Manuscript Compared with Other Encrypted Books. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper15.pdf).

**[V16]** Stefan Guzy (VOY2022 / actas 2023). Book Transactions of Emperor Rudolf II 1576-1612. New Findings on the Earliest Ownership of the Voynich Manuscript. Actas con revisión según índice CEUR. Acceso: PDF consultado. [Fuente](https://ceur-ws.org/Vol-3313/paper16.pdf).
