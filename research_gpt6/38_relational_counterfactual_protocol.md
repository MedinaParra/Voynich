# 38. Hipótesis de notación relacional y prueba por intercambio de rótulos

Fecha: 2026-10-06. Estado: hipótesis exploratoria; originalidad no establecida.

## Pregunta concreta

¿Parte de la escritura codifica relaciones entre componentes dibujados, en vez de limitarse a nombres de objetos? Una familia de formas podría estar asociada a conexiones, pertenencia o secuencia. Estas son posibilidades funcionales, no glosas propuestas para palabras EVA.

La diferencia respecto de clasificar una página como botánica o zodiacal es intentar recuperar una relación local entre dos objetos en diagramas no usados para ajustar el modelo. El intercambio computacional de rótulos es un control de correspondencia, NO una intervención causal sobre un escriba medieval.

## Antecedentes y alcance de la novedad

La vía multimodal ya está descrita en nuestros protocolos 30 y 31. La notación técnica y el anclaje entre modalidades están tratados en https://github.com/tedficient-source/VoynichNotation/blob/main/PAPER_DRAFT_v5.md . Existe una transcripción espacial abierta: https://github.com/alessandroplaca-uro/voynich-spatial-data . Las relaciones texto-layout y los mapas de rótulos también tienen antecedentes en https://voynich.nu/writing.html y https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/97-10-23-label-maps/source.html . Son propuestas y recursos de autores, no demostraciones aceptadas de desciframiento.

Nuestra propuesta específica es evaluar mejora predictiva de la topología visual al añadir formas textuales, usando cuadernos retenidos y permutaciones completas de rótulos. La búsqueda acotada no permite afirmar «jamás explorado». Antes de reclamar novedad se requiere revisar implementaciones y pruebas equivalentes, incluyendo las fuentes anteriores.

## Integración holística

1. Materialidad/codicología: la unidad independiente es el folio o desplegable físico, agrupado por cuaderno; considerar reordenamientos sin duplicar muestras.
2. Imagen: anotar conexiones observables sin ver transcripciones ni identificaciones de plantas; registrar conectores explícitos, incertidumbre y acuerdo entre anotadores. No inferir flujo dirigido cuando no haya dirección visible.
3. Texto: conservar transcripción y ambigüedades; comenzar con rasgos de caracteres, sin diccionario inventado. Comprobar sensibilidad a otra transcripción.
4. Historia: comparar el mismo protocolo en diagramas medievales de relaciones conocidas; no escoger comparadores según el resultado Voynich.
5. Modelo: contrastar geometría, geometría + texto, escritura imitativa de proximidad, y etiquetas meramente nominales. Una asociación entre nombres similares y conexiones NO identifica operadores.

## Piloto ejecutable y límites

`code/relational_graph_probe.py` acepta JSON con folios, cuadernos, nodos (id, text, x, y normalizados) y lista completa de aristas visuales no dirigidas. Exige al menos tres cuadernos y anotación ciega declarada. Estas declaraciones deben auditarse; el código no puede certificar cómo se anotó.

Compara regresión logística fija de geometría/longitudes contra geometría/longitudes + diferencias y productos de n-gramas de caracteres. Evalúa Brier medio por cuaderno retenido. Con 199 permutaciones, mueve rótulos completos dentro del folio, vuelve a ajustar ambos modelos y estima p Monte Carlo. Los pares de un mismo dibujo NO son réplicas independientes.

Este primer piloto no controla por sí solo mano, Currier, sección ni longitud exacta en la permutación. La base geométrica es sencilla y puede infraajustar. Cualquier señal exige luego: controles más ricos, intercambio por longitud/rol, controles de autocopia, bootstrap por cuaderno, holdout por mano, otro corpus de transcripción y replicación en otra clase de diagrama. No declarar significación confirmatoria con el piloto.

Hipótesis de continuidad: ganancia positiva en todos los cuadernos y p <= .01 serían motivos para una replicación, NO criterio de traducción. Si falla, se rechaza este modelo concreto, no toda notación relacional posible.

## Ejecución real de esta sesión

- Recuperación: 539 tokens posicionados, 44 grupos de párrafos, un desplegable f85v–f86r del recurso Placa. Registrar SHA de archivo normalizado en `results/relational_source_audit.json`; posiciones no equivalen a conexiones semánticas. Archivo externo no redistribuido en este commit.
- Código: control sintético positivo y control aleatorio ejecutados; resultados en `results/relational_harness_checks.json`. Son controles del programa, no evidencia del manuscrito.
- Prueba científica sobre Voynich: BLOCKED por ausencia en el conjunto recuperado de aristas visuales independientes y de muestra de múltiples cuadernos. No simularlas a partir de distancia y llamarlas significado.
- Traducción: NOT_RUN.

## Siguiente experimento concreto

Construir anotación visual ciega de diagramas con conexiones explícitas en al menos tres cuadernos, con todas las parejas elegibles y negativos completos. Mantener por separado aristas inciertas. Congelar muestra, reglas y parámetros antes de descubrir formas textuales. Si no hay suficientes diagramas comparables entre cuadernos, registrar falta de identificabilidad y reformular, sin rebautizar párrafos como muestras.

La primera salida útil sería «estas formas ayudan a predecir una conexión visual». Para una glosa relacional se necesita distinguir conexión de similitud de entidades y anticipar relaciones nuevas, con apoyo histórico y estructura textual independiente. Para traducción se necesita además lectura composicional de pasajes retenidos.
