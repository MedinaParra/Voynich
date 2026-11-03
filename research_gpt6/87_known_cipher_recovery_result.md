# 87 — Tres controles latinos descifrados exactamente; Voynich sigue sin traducción

**3 de noviembre de 2026. Rama `experiment/kraken-voynich`.**

Se completó el paso que faltaba: **recuperar claves y textos conocidos antes de intentar interpretar una salida como lectura del Voynich**. El solver recuperó los tres fragmentos positivos de César, de 2.000 letras cada uno, y todas las asignaciones de sus símbolos observados. El modelo había aprendido únicamente de Apicio.

El resultado es un éxito de descifrado de controles monoalfabéticos con lengua conocida. No identifica lengua o cifrado del manuscrito. No se ejecutó el solver sobre Voynich ni se convirtió ningún candidato suyo en latín.

## Protocolo, respuestas ocultas y congelación

El [protocolo 86](86_known_cipher_recovery_protocol.md) y el [plan](data/known_cipher_recovery_plan.json) se publicaron antes de generar los controles en `674c993525c6e09a88ca4ae34d42d9683da394f1`. Un preparador separado eligió los pasajes y claves y publicó un compromiso de verdad, sin entregarlos al solver.

El paquete de cifrados, corpus permitido, fuentes del solver y manifest de hashes del modelo quedaron publicados **antes de buscar** en `7d976cedcc49b093676704d4d23ec1600f1d8dc7`. Las predicciones completas y su [recibo de congelación](results/known_cipher_recovery/freeze.json) se publicaron **antes de autorizar la evaluación** en `1b17500d4670410de0e9d2fba456839373145460`.

| Compromiso SHA256 | Valor |
|---|---|
| Verdad fijada por el preparador | `6edd45616bed607b6dad38c1fcfda3b1928cd3e46a649c1eaf08d0475c4e6a0e` |
| Manifest del solver/modelo/entradas | `2fdebe6140d25246826bda73da0d764f56a2a4252f76c2502a3daa348d6fef85` |
| Predicciones antes de revelar verdad | `3342583e05ac60b9b2091df42f2505c5b278886733dd5651c76a9f5fecf85929` |

La separación fue algorítmica y procedimental: el ejecutable sólo recibió ciphertext y tablas permitidas, pero los agentes compartían archivos y las fuentes clásicas estaban disponibles previamente en el repositorio. No se afirma un ensayo humano con aislamiento de seguridad. Tras congelar, el evaluador verificó compromisos y comparó con las respuestas; éstas se publican ahora en [reveal](results/known_cipher_recovery/reveal) para reproducir el experimento.

No se ajustaron corpus, claves, pasajes, presupuesto o modelo después de abrir las respuestas. No hubo búsqueda de otro caso favorable para reemplazar uno fallido.

## Familia y datos

El modelo de cuatro caracteres se entrenó con **40.013 letras normalizadas de Apicio 1–5**. Los pasajes de **César 1–3** quedaron íntegramente fuera de sus entradas de entrenamiento. Es separación por autor, aunque las fuentes no representan toda la diversidad del latín histórico.

Se conservaron los filtros de las fuentes previas: primera línea y líneas en mayúsculas excluidas, minúsculas y tokens ASCII a–z, sin unificar u/v o i/j. Los 2.000 caracteres se fijan en el flujo normalizado; una ventana puede empezar o terminar dentro de una palabra. No son capítulos completos ni transcripciones diplomáticas de manuscritos latinos.

El paquete contiene:

- Tres mensajes positivos distintos, uno por libro de César, con tres claves aleatorias de sustitución biyectiva.
- Un par con/sin espacios de cada mensaje y clave: seis presentaciones, **no seis mensajes independientes**. Ambas conservan las mismas letras.
- Tres controles con letras barajadas, frecuencias y posiciones de espacio conservadas.
- Un cuarto pasaje disjunto cifrado homofónicamente con 26 símbolos: algunas letras tienen varios símbolos. Mantiene el tamaño del alfabeto, pero no se representa mediante una permutación.

Los originales latinos, commit, hashes y licencia Public Domain Mark 1.0 ya están en `data/latin_sources.json` y [LATIN_LICENSE](data/LATIN_LICENSE.md). En el paquete público se puede inspeccionar exactamente qué recibió el algoritmo.

## Procedimiento realmente ejecutado

La puntuación es un modelo condicional de cuatro letras con suavizado hacia órdenes menores. No usa diccionario ni espacios. Las log-probabilidades se congelaron como enteros y la aceptación de movimientos usa tablas y un generador pseudoaleatorio determinista. Es una implementación de métodos clásicos con antecedentes publicados; no una técnica de descifrado inventada aquí ni una réplica exacta de los artículos citados.

Para cada flujo distinto se hicieron ocho reinicios de 50.000 intercambios, con selección por el mayor score del modelo, sin consultar respuestas. Se añadió el pulido fijado. Se cargaron diez presentaciones, pero sólo hubo **siete búsquedas distintas**, porque los tres pares de espacio comparten su flujo. Se registraron **2.800.000 propuestas de recocido** y 19.175 evaluaciones de pares en el pulido. Los reinicios y movimientos no son nuevos textos o experimentos independientes.

La ejecución local de búsqueda tardó 5,88 segundos en ese entorno; no es una comparación controlada de rendimiento. Los tiempos y el hash del binario se guardan aparte; las predicciones deterministas no incluyen reloj. El fuente C++, las tablas y el comando de compilación se conservan para la reproducción.

## Resultado contra respuestas conocidas

| Condición | Casos exactos | Exactitud de letras | Clave sobre símbolos observados |
|---|---:|---:|---:|
| Sustitución monoalfabética, con espacios |3/3|100%|100%|
| Mismos mensajes, sin espacios |3/3|100%|100%|
| Letras barajadas, frecuencias conservadas |0/3|8,52% media|11,11% media|
| Homofónico, familia incorrecta para el solver |0/1|62,95%|50%|

El criterio estricto fijado pasa en los **tres contenidos positivos**: todo el plaintext normalizado y las 21 asignaciones observadas por caso son exactos. Las cinco asignaciones ausentes de cada caso positivo no son identificables y no se cuentan como clave recuperada.

Las presentaciones con y sin espacios producen la misma clave candidata por diseño y caché. Eso demuestra invariancia de presentación del mismo procedimiento, no aprendizaje de límites de palabra ni replicación independiente. En los casos sin espacios se recuperó el flujo de letras; no se reconstruyeron palabras o puntuación.

### Ejemplo de descifrado, exclusivamente de un control César

```text
Cifrado:
nygzgsgnw znmun znwunqwy uwzmsg btb ynjbmy gb qw yghgsnqg mumy fndwdnbs

Recuperado:
amicitiae causa caesarem secuti non magnum in re militari usum habebant
```

Este [fragmento verificado](results/known_cipher_recovery/decoded_control_example.json) procede del control C03 y sus espacios estaban en la entrada de esa presentación. **No es texto del Voynich**. Su versión sin espacios recuperó las mismas letras.

## Límite demostrado por homofonía

En el homofónico, el mejor descifrado biyectivo posible, medido contra la verdad por grupos disjuntos de alias, tiene techo **1.551/2.000 = 77,55%**. Cualquier clave de la familia utilizada debe fallar al menos 449 letras. La búsqueda obtuvo 1.259/2.000 = 62,95%, 292 letras por debajo de ese techo.

Esto separa dos problemas: la restricción de familia hace imposible el 100%, y la diferencia restante no se identifica aquí enteramente como búsqueda o como preferencia del modelo lingüístico. El score del plaintext verdadero se calcula después de revelar la verdad, pero esa decodificación muchos-a-uno está fuera del espacio biyectivo: su score no es una cota alcanzable que permita culpar sólo al optimizador.

Este fallo de control no demuestra homofonía en Voynich. Indica una capacidad que el solver actual no tiene.

## Un score alto no equivale a recuperar la verdad

El algoritmo siempre devuelve un candidato, incluso en los nulos. No se calibró un umbral para abstenerse: **no se ha demostrado que detecte automáticamente pseudotexto**.

En los tres nulos, la clave candidata obtiene mayor score lingüístico que la clave generadora verdadera, aunque apenas coincide con sus letras. No es sólo que la búsqueda se quedara lejos de un máximo: el objetivo lingüístico favorece una respuesta distinta para un texto barajado. Por tanto, maximizar apariencia latina no basta para declarar una lectura histórica.

En los positivos, candidato y verdad tienen el mismo score y el texto coincide exactamente. Eso verifica recuperación en esos casos; no prueba que se alcanzara un óptimo global único de la función objetivo para todos los textos posibles. Volver a cifrar una salida con su clave candidata sólo verifica coherencia y no se contó como evidencia de descifrado verdadero.

## Auditoría y reproducción

Un [auditor separado](code/audit_known_cipher_recovery.py), sin importar el solver ni el evaluador, recalculó aplicación de claves, Hamming, asignaciones observadas, techo homofónico y scores de candidato/verdad: **PASS, 302 comprobaciones**, incluidos sus controles matemáticos. No vuelve a ejecutar la búsqueda, no prueba optimalidad global ni certifica aislamiento del proceso.

Las [predicciones congeladas](results/known_cipher_recovery/predictions.json), [evaluación](results/known_cipher_recovery/evaluation.json), [auditoría](results/known_cipher_recovery/audit.json), [manifest del solver](results/known_cipher_recovery/solver_manifest.json) y tablas completas quedan preservados. La [reproducción desde un checkout limpio en GitHub Actions](https://github.com/MedinaParra/Voynich/actions/runs/41676142145) pasó sobre el commit `ed054cf860597b1e4b682e622a927155522693c3`: controles públicos y revelados idénticos, tablas reconstruidas idénticas, nueva compilación C++ con predicciones byte por byte idénticas a las congeladas y métricas/auditoría iguales. El [recibo](results/known_cipher_recovery/ci_receipt.json), log y copia del artefacto se conservan; se verificó el SHA256 del ZIP descargado y la igualdad de sus dos registros con los originales.

```bash
python -m pip install numpy==2.3.5
g++ -O3 -std=c++17 research_gpt6/code/known_substitution_solver.cpp -o /tmp/known_cipher_solver
python research_gpt6/code/recover_known_ciphers.py --repo research_gpt6 \
  --bundle research_gpt6/results/known_cipher_recovery --binary /tmp/known_cipher_solver \
  --out work/predictions.json
python research_gpt6/code/audit_known_cipher_recovery.py --repo research_gpt6 \
  --bundle research_gpt6/results/known_cipher_recovery --out work/audit.json
```

El replay posterior a revelar respuestas no es otro ensayo ciego. Se conservan código/entradas/predicciones de antes y después para comprobar que no se retocaron al conocer la solución.

## Qué aporta y qué queda pendiente

Ahora existe un **descifrador verificado en estos controles de latín conocido y sustitución simple**, con recuperación exacta medida. Es una capacidad inversa que las estadísticas anteriores, invariantes a cambiar nombres de letras, no ofrecían.

No permite escoger latín para Voynich, convertir códigos EVA en letras originales, resolver signos compuestos, recuperar abreviaturas o superar homofonía. La siguiente ampliación útil deberá demostrar recuperación de una familia más flexible en controles antes de presentar una salida del manuscrito como traducción. En este paso, Voynich permanece **NOT_TRANSLATED** y Kraken no se reentrenó.

Antecedentes primarios consultados: [Megyesi y colaboradores, HistoCrypt 2023](https://ecp.ep.liu.se/index.php/histocrypt/article/view/701), sobre modelos históricos y homofonía; [Hauer, Hayward y Kondrak 2014](https://aclanthology.org/C14-1218/), modelos combinados; [Aldarrab y May 2021](https://aclanthology.org/2021.acl-long.561/), una tarea más amplia de sustitución con lengua desconocida y ruido. No se afirma reproducir sus resultados ni haber leído sus artículos completos en esta continuación: se verificaron fichas y resúmenes de las fuentes primarias. Véase [NOTICE](results/known_cipher_recovery/NOTICE.md).
