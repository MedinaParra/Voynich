# Voynich: revisión crítica y metodología para la siguiente etapa

**Corte: 3 de noviembre de 2026.** Continuación de la revisión [46, con corte al 14 de octubre](46_estado_del_arte_2026_10_14.md), y del diagnóstico [76](76_alignment_and_search_diagnostic_result.md). Investigación para Exequiel Medina Parra. Traducción validada en este proyecto: **ninguna**.

## 1. Alcance y criterio de lectura

Se actualizaron fuentes institucionales, artículos, preprints, datos de autores y documentación de software. El [registro de quince fuentes](data/estado_arte_2026_11_03_sources.json) distingue fecha de publicación, versión, acceso y límite de interpretación. Es una revisión dirigida a decisiones experimentales, no una afirmación de haber localizado todos los trabajos existentes ni una revisión sistemática con cobertura exhaustiva.

Se contrastaron texto primario, métodos cuando estuvieron disponibles, repositorios y metadatos. Para CVPR/HTR y el estudio de unidades se leyeron secciones metodológicas, controles y limitaciones; para algunos registros sólo fue accesible su resumen. Se conserva esa diferencia. OpenEdition presentó una protección Anubis; ciertos PDF de Zenodo fallaron al extraerse; otros editores devolvieron 403 o timeout. Un acceso bloqueado no se transforma en una lectura completa. Noticias y agregadores sirvieron para localizar documentos, no para acreditar resultados técnicos.

La fecha de consulta tampoco convierte un recurso viejo en una novedad reciente: el snapshot espacial de Placa verificado es del 18 de julio de 2026, aunque se haya encontrado ahora. Se separan asimismo publicación online de Greshko en 2025 y su presencia posterior en un volumen de revista. Un DOI, un depósito o un repositorio no certifican por sí solos una interpretación.

## 2. Qué avances cambian las preguntas

### Estado institucional y material

Yale sigue describiendo el manuscrito como una escritura no identificada, sin lectura establecida, y ofrece fotografías y documentación material. Eso acredita custodia y acceso; no avala una clave particular. La fecha del pergamino, la fecha de escritura y la atribución de catálogo son preguntas distintas. No se elige una lengua o un supuesto alfabeto sólo por una fecha de catálogo. [S01]

### Cifrados que imitan el manuscrito

El Naibbe de Greshko constituye una construcción criptográfica explícita, históricamente plausible y acompañada de código: puede cifrar texto conocido conservando varias propiedades parecidas a las del Voynich. Su autor distingue esa demostración de una solución del manuscrito. Nuestra consecuencia es exigir controles de cifrados recuperables, además de controles de texto sin sentido; parecerse a Voynich no identifica el mecanismo histórico ni su clave. [S02]

Parisel analiza firmas de posición y dirección y contrasta clases concretas de generadores. Es un preprint con restricciones útiles para comparar explicaciones. El rechazo de los generadores ensayados no rechaza todos los generadores; una firma direccional tampoco determina automáticamente cómo leer la página o qué lengua contiene. No se trasladan esas conclusiones a una clave fonética. [S03]

### Las unidades y los límites de palabra

Rozanova y Temerev cuestionan que glifo, cadena entre blancos y espacio transcrito equivalgan, respectivamente, a letra, palabra lingüística y separación léxica. Su comparación incorpora controles y remuestreo por cuaderno. La parte espacial usa coordenadas de Voynichese: son independientes de ciertas etiquetas de separador de ZL, pero no independientes de la segmentación de otro transcriptor. Esa distinción es importante para nuestro problema de recortes. Sus restricciones a sustitución simple se limitan a fuentes y representaciones ensayadas; no excluyen todo sistema con significado. [S04]

Layfield y Davis plantean reconsiderar la estructura física y secuencia de los bifolios. En esta actualización no fue posible recuperar directamente todo el artículo, de modo que no se presenta una nueva réplica de sus tablas. Su pertinencia para nuestro diseño es separar unidades físicas de producción y evaluación. No se presupone que reordenar páginas vaya a producir una traducción. [S05]

### Paleografía como dato y como hipótesis

El depósito Archetype de Timm ofrece 1.684 grafos anotados en 203 imágenes, concentrados en cinco categorías de formas. El README contiene ocho etiquetas de sección/mano que se corresponden con cinco escribas propuestos: **no son ocho autores históricos demostrados**. Es un recurso para contrastar variación de formas; no un corpus completo de palabras certificadas. Su papel en una crítica a la hipótesis de cinco escribas exige conservar también incertidumbre de las etiquetas. No se importó al entrenamiento de esta continuación. [S06]

### Estructura recuperada frente a significado recuperado

El preprint de Dominik, registro de versión 2 fechado el 18 de octubre de 2026, declara estructuras morfológicas y pruebas protegidas. Su propio resumen diferencia el 98,4314 % de un benchmark condicional de roles de una recuperación literal de texto. La descripción también informa fallos al promover estructura a significado. Aquí sólo se accedió al registro y resumen: no se auditó su código ni se reprodujeron sus resultados. No se adopta ese porcentaje como traducción o como consenso. [S07]

La diferencia afecta a la metodología: clasificar posiciones o familias de cadenas puede ser una regularidad útil y, aun así, dejar el contenido léxico sin identificar. Las hipótesis semánticas necesitan predicciones que una estructura alternativa no pueda obtener con igual libertad de ajuste.

## 3. Recursos que pueden mejorar el canal visual

| Recurso | Qué se verificó | Uso razonable y límite |
|---|---|---|
| Placa, Voynich Spatial Data | Snapshot `2026-07-18b`, commit `7580dafa624cf23a63665f4819022003f8d128ef`; 539 tokens de Rosettes posicionados y orientados | Fuente candidata para estudiar coordenadas y variantes. La transliteración deriva de la comunidad; se excluye la capa interpretativa latina. Datos espaciales CC BY 4.0 y fuente tipográfica con condiciones diferentes. No se incorporó aquí. [S08] |
| Archetype | Registro y README, categorías y relación entre etiquetas | Comparar formas aisladas y revisar hipótesis de mano; la cobertura parcial no permite convertirlo directamente en verdad de palabras. [S06] |
| Voynichese | Documentación de asociaciones espaciales semiautomáticas y de límites de palabra interpretables | Sus cajas son candidatas. La coincidencia XML/JSON verifica serialización, no dos lecturas independientes. Su estimación histórica de errores no mide nuestro dataset. [S14] |
| FINO | Preprint y disponibilidad de implementación | Adaptación visual guiada por metadatos; no fue evaluada en Voynich aquí. Metadatos de sección o mano pueden introducir confusores. [S10] |
| SSL por contexto espacial | Resumen primario de editor; texto completo bloqueado | Línea de preentrenamiento visual pertinente, pendiente de reproducir y de evaluar fuera del dominio original. [S11] |

Los nuevos recursos no se mezclaron apresuradamente con las etiquetas de entrenamiento. Integrar coordenadas exige comprobar encuadres, orientación, escala, atribución y licencia. Una capa de interpretación latina no puede usarse a la vez como hipótesis y como etiqueta que luego la confirme. La inspección de recursos es trabajo de investigación; **su incorporación al modelo está NOT_RUN**.

## 4. Qué dice HTR sobre nuestro fracaso de generalización

El estudio de Garrido-Munoz y Calvo-Zaragoza, CVPR 2025, compara ocho modelos en 336 escenarios fuera de dominio, con siete datasets y cinco idiomas. Distingue divergencia textual y visual, y sitúa la primera como un factor fuerte. Incluye aumentos convencionales y experimentos sintéticos; no demuestra que aumentar tamaño o capacidad resuelva el dominio desconocido. Sus idiomas conocidos no validan el Voynich. [S09]

La consecuencia para nosotros es acotada: una intervención visual puede fallar aunque esté bien ejecutada, porque no aporta formas o secuencias suficientes. Nuestros ajustes anteriores casi memorizaban entrenamiento y fallaban en cadenas no vistas. El ensayo 76 demostró además un desacuerdo entre probabilidades del modelo y referencias candidatas. Esas observaciones no permiten atribuir toda la diferencia a vocabulario, imagen o etiqueta.

El procesamiento por incertidumbre y diccionario de Kim y colaboradores ofrece otra dirección de OCR, pero aquí sólo se verificó su resumen primario. No se adoptó el diccionario: devolver cadenas conocidas puede ocultar precisamente el fallo en cadenas nuevas. La incertidumbre útil debe conservar alternativas y señalar errores; no basta con elevar la confianza de una palabra frecuente. [S12]

Kraken 7.1 ya contiene una receta de aumento para manuscritos históricos, con variaciones de geometría, apariencia y artefactos. Se inspeccionó su implementación y se registra el código instalado en cada ajuste. Es una base técnica existente, no nuestra invención. La función objetivo CTC también es estándar desde Graves y colaboradores: suma alineaciones para reconocer secuencias, sin establecer significado. [S13, S15]

## 5. Nueva metodología propuesta: incertidumbre física antes de interpretación

La propuesta completa tiene tres etapas, con estados separados. Sólo la primera se implementa y se ejecuta en esta continuación. No se afirma que las otras estén implementadas o probadas.

### Etapa A: contrastar el canal de imagen — IMPLEMENTED, ejecución en el protocolo 78

Se conserva una vista intacta de cada recorte. Una segunda vista atenúa suavemente píxeles oscuros de zonas compartidas entre anotaciones. Se enfrenta a un control con igual cantidad de píxeles oscuros elegidos al azar y a otro de originales repetidos. Todas las condiciones reciben la misma augmentación estándar, semilla, pesos, codec, número de vistas y pasos. Las etiquetas no se cambian y no se certifica propiedad de tinta.

Esto permite distinguir tres resultados posibles: ventaja del tratamiento espacial frente a ambos controles; ventaja de perturbación genérica sin un beneficio espacial; o ausencia de mejora y posible daño a trazos legítimos. Una mejora frente al modelo antiguo pero no frente al control repetido no sería evidencia de nuestra hipótesis espacial.

La reserva f8r/f8v se fijó antes de consultar su OCR. Las hojas 4 y 7 ya exploradas se conservan como medidas secundarias. Se evalúa siempre la imagen original, de modo que el ensayo mide cambios del aprendizaje y no un cambio oportunista de preprocesamiento de evaluación. Épocas, checkpoint final y reglas no se eligen con el resultado nuevo. El [protocolo 78](78_shared_region_retraining_protocol.md) y sus hashes fijan los detalles; los resultados se publican por separado en el informe 79.

### Etapa B: representar discrepancias entre lecturas — DESIGN ONLY / NOT_RUN

El objetivo sería alinear por posición imágenes y al menos dos transcripciones realmente diferenciadas, manteniendo desacuerdos de glifos, unión/separación y límites. No basta con dos exportaciones de una misma fuente. La unidad operativa tendría que poder ser un grupo de trazos o un segmento, sin forzar desde el inicio una letra o una palabra lingüística.

No conviene reducir esa incertidumbre al mejor texto de nuestro OCR: el modelo actual asigna masa baja a muchas referencias y un haz truncado puede excluir alternativas correctas. Una red calibrada y una revisión independiente deberían justificar qué alternativas entran en una representación de lecturas. Hasta entonces sus probabilidades son observaciones del modelo, no una autoridad paleográfica.

Se necesitaría una muestra de revisión con trazabilidad y acuerdos/desacuerdos conservados. El recurso Archetype y los trazados espaciales podrían aportar material de contraste, sujeto a cobertura y derechos. No se atribuye a la inspección de un asistente el carácter de esa revisión independiente.

### Etapa C: falsar mecanismos y evaluar identificabilidad — DESIGN ONLY / NOT_RUN

Sobre lecturas suficientemente controladas se compararían modelos acotados de producción: copia/modificación, plantillas o morfología de superficie, y cifrados recuperables. Cada familia tendría presupuesto de parámetros, fuentes y reglas fijados antes de la prueba. Se entrenaría por unidades físicas, conservando dependencia de cuaderno y mano como alternativas, no como explicaciones ciertas.

Los controles incluirían texto histórico conocido cifrado con mecanismos explícitos y pseudotexto de estructura semejante. Primero el procedimiento tendría que recuperar el texto conocido y rechazar asociaciones espurias. Después se exigirían predicciones de observaciones reservadas: dependencia de bordes, cambios entre posiciones, formas no vistas y, sólo cuando esté justificado, pasajes continuos bajo una clave fija.

Se conservaría la posibilidad de no identificar el significado: si dos interpretaciones incompatibles explican los mismos signos con la misma libertad, el dato no las distingue. Elegir la que suena más convincente no lo resuelve. Una interpretación sólo se promovería cuando haga predicciones externas que fallen en alternativas comparables y sobreviva a una lectura independiente.

Esta arquitectura de trabajo combina ideas conocidas y un contraste visual nuevo para este repositorio. No se presenta como un enfoque que nadie haya probado en el mundo ni como una demostración de que haya texto lingüístico recuperable.

## 6. Qué se ejecuta y qué no se debe concluir

| Trabajo | Estado de esta continuación | Evidencia que corresponde |
|---|---|---|
| Actualización bibliográfica | Realizada, con niveles de acceso explícitos | Registro S01–S15, enlaces y notas críticas |
| Metodología completa | Diseñada; etapas B/C sin ejecutar | Este documento, sin cifras de traducción |
| Intervención de imagen y controles | Implementada y publicada antes del ajuste | Código, plan y protocolo 78 |
| Tres reentrenamientos | Ejecutados: 100 épocas y 5.600 pasos por condición; auditados | [Informe 79](79_shared_region_retraining_result.md), checkpoints y procedencia de Actions |
| Reserva nueva OCR | Evaluación de candidatos, sin revisión paleográfica nueva | Geometría, fuentes y hashes de f8r/f8v |
| Desciframiento | No obtenido | No se infiere de un CER, de una entropía o de una estructura |

Una semilla y una hoja física nueva permiten un piloto controlado, no una declaración general de superioridad. Las palabras de una misma hoja no se convierten en manuscritos independientes por contarlas por separado. Si la hipótesis espacial falla, su resultado negativo se conserva y la siguiente decisión debe cambiar con la evidencia.

## Referencias verificadas

S01. [Yale Library, The Beinecke Cipher (Voynich) Manuscript](https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript).

S02. [Greshko, The Naibbe cipher, Cryptologia, online 2025](https://doi.org/10.1080/01611194.2025.2566408), con [explicación del autor](https://www.michaelgreshko.com/naibbe-cipher) y [código](https://github.com/greshko/naibbe-cipher).

S03. [Parisel, Evidence of Layered Positional and Directional Constraints, v2, 2026](https://arxiv.org/abs/2604.19762).

S04. [Rozanova y Temerev, What the Units of Voynichese Are Not, 2026](https://arxiv.org/html/2608.17096v1), con [archivo de análisis citado por el artículo](https://github.com/lrozanova/voynich-units).

S05. [Layfield y Davis, Singulion Structure and the Voynich Manuscript, 2026](https://doi.org/10.4000/16k0a). Acceso directo completo bloqueado en esta actualización.

S06. [Timm, Archetype: Voynich Palaeography, 2026](https://zenodo.org/records/18827108), [README](https://zenodo.org/records/18827108/files/README.md?download=1).

S07. [Dominik, Structural Decipherment Without Lexical Recovery, registro v2, 2026](https://zenodo.org/records/23444474). Evaluación de alcance basada en registro y resumen, no réplica.

S08. [Placa, Voynich Spatial Data, snapshot verificado](https://github.com/alessandroplaca-uro/voynich-spatial-data/tree/7580dafa624cf23a63665f4819022003f8d128ef).

S09. [Garrido-Munoz y Calvo-Zaragoza, On the Generalization of Handwritten Text Recognition Models, CVPR 2025](https://arxiv.org/html/2411.17332v2).

S10. [Gardès y colaboradores, Who Needs Labels?, FINO, 2026](https://arxiv.org/abs/2606.05107), [implementación oficial](https://github.com/facebookresearch/dinov3/tree/FINO).

S11. [Spatial context-based Self-Supervised Learning for HTR, registro de editor](https://www.sciencedirect.com/science/article/pii/S0167865525002120). Resumen consultado; texto directo bloqueado.

S12. [Kim y colaboradores, Uncertainty-Aware Processing for OCR, Electronics Letters, 2026](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/ell2.70630). Resumen consultado; página directa con timeout.

S13. [Kraken 7.1, código oficial de augmentación](https://github.com/mittagessen/kraken/blob/7.1/kraken/lib/dataset/augment.py), [dataset de reconocimiento](https://github.com/mittagessen/kraken/blob/7.1/kraken/lib/dataset/recognition.py).

S14. [Voynichese Project, Data Sets](https://github.com/voynichese/voynichese/blob/wiki/DataSets.md).

S15. [Graves y colaboradores, Connectionist Temporal Classification, ICML 2006](https://www.cs.toronto.edu/~graves/icml_2006.pdf).
