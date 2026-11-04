# 89 — El mapeo homofónico libre falla: el objetivo prefiere colapsos

**4 de noviembre de 2026. Rama `experiment/kraken-voynich`. Resultado experimental: FAIL.**

Se implementó y ejecutó la ampliación pendiente: permitir que varios símbolos se descifren como una misma letra. El resultado fue negativo. El método libre recuperó **12,30%** de las letras de los controles homofónicos y ninguno completo, frente a **70,62%** del método biyectivo anterior.

La auditoría encuentra algo más preciso que una baja exactitud: los candidatos libres, reducidos a dos o tres letras distintas, tienen mayor puntuación que sus textos verdaderos en todas las nueve presentaciones. Por tanto, la verdad conocida no maximiza este objetivo congelado en esos casos. No se modificó el objetivo o el solver después de ver las respuestas.

**Voynich permanece NOT_TRANSLATED. Kraken no se reentrenó.**

## Diseño y procedencia

El [protocolo 88](88_homophonic_recovery_protocol.md) y su [plan](data/homophonic_recovery_plan.json) se publicaron antes de generar casos. Se reutilizaron sin cambios las tablas de cuatro caracteres aprendidas con 40.013 letras de Apicio en la etapa 86, fijadas en `960254605ab910ed90af8d3a8cc7278bbb202185`.

Un preparador separado eligió una nueva ventana de 2.000 letras de cada libro César 1–3. Se excluyeron los cuatro intervalos únicos usados anteriormente, incluido el homofónico previo. Cada contenido recibió una sustitución biyectiva nueva y otra homofónica de 26 símbolos; se añadieron tres permutaciones de los ciphertexts homofónicos que conservan sus frecuencias. Los nueve casos carecen de espacios y sus roles/pares permanecieron ocultos al solver.

Son **tres pasajes distintos, seis presentaciones positivas emparejadas y tres nulos dependientes**. No son nueve textos independientes ni una muestra representativa de todo el latín. Los fragmentos pueden comenzar o terminar dentro de palabras.

La separación fue procedimental: agentes en un repositorio compartido, corpus público y respuestas guardadas como objetos Git sin referencias de rama hasta revelar. No hubo aislamiento de seguridad ni evaluación humana externa. La semilla de preparación no es un secreto criptográfico; su compromiso permitió comprobar que no se reemplazaron casos.

## Orden verificable

| Etapa | Commit o ejecución |
|---|---|
| Protocolo antes de generar | `4a08ab48386964dc0a031855952bcda0bd80dabf` |
| Código, tablas fijadas por hash y paquete público antes de buscar | `941d846e9da5dfe2ed6e8d33842c5c83da0cf2e2` |
| Predicciones completas publicadas antes de autorizar revelación | `bea2d33091d0711108c02a8a24790814d6458b4f` |
| Anclaje de predicciones y compromisos | `74974da26b504c90525a2067f82131057a3f403a` |
| Revelación de los objetos originales y evaluación | `c8e9246ec4cff2fa197a104c8c3889a572ffae83` |
| Búsqueda sin respuestas nuevas | [GitHub Actions 41887651597](https://github.com/MedinaParra/Voynich/actions/runs/41887651597) |
| Evaluación, auditoría y reproducción | [GitHub Actions 41888198170](https://github.com/MedinaParra/Voynich/actions/runs/41888198170) |

Las [predicciones](results/homophonic_recovery/predictions.json) conservan SHA256 `94911e8f3c41589d05fb77d0329ca6498b93a2acebe9382d38e23e03a05e8bc6`. El [freeze](results/homophonic_recovery/freeze.json) enlaza su publicación con los compromisos originales de verdad y semilla. No se reemplazó ningún caso fallido.

## Implementación y coste real

Ambos métodos puntúan exactamente el mismo modelo entero de cuatro letras. El anterior conserva una permutación; el nuevo permite asignaciones repetidas, mediante reasignaciones de un símbolo y swaps. Cada ciphertext se resuelve por separado, sin transferir una respuesta entre sus versiones mono/homofónica, sin fallback del otro método y sin consultar verdad.

Se fijaron ocho reinicios de 50.000 propuestas por caso y un máximo de 100 actualizaciones de pulido por reinicio. El método libre inicializa por frecuencia y perturba los reinicios no iniciales; no impone el número verdadero de letras de salida.

| Método | Propuestas de recocido | Evaluaciones de vecinos de pulido |
|---|---:|---:|
| Biyectivo | 3.600.000 | 24.050 |
| Muchos-a-uno | 3.600.000 | 79.950 |

Se ejecutaron 18 búsquedas y 7.200.000 propuestas; el pulido sumó 104.000 evaluaciones. Los vecinos no cuestan lo mismo: 325 swaps posibles frente a 650 reasignaciones y 325 swaps por pasada. Igual número de propuestas no acredita igual cómputo.

La búsqueda inicial en GitHub tardó aproximadamente 18,22 segundos en ese entorno. Es metadato de ejecución, no un benchmark controlado de velocidad.

## Resultados contra respuestas conocidas

| Condición | Biyectivo: exactos | Biyectivo: letras correctas | Libre: exactos | Libre: letras correctas |
|---|---:|---:|---:|---:|
| Monoalfabéticos nuevos | 2/3 | 5.999/6.000 = 99,9833% | 0/3 | 738/6.000 = 12,30% |
| Homofónicos nuevos | 0/3 | 4.237/6.000 = 70,6167% | 0/3 | 738/6.000 = 12,30% |
| Nulos de frecuencias conservadas | 0/3 | 375/6.000 = 6,25% | 0/3 | 603/6.000 = 10,05% |

El criterio primario de tres homofónicos completos **falla**. La regresión estricta monoalfabética también falla: el baseline recupera dos textos exactamente y comete una sola sustitución en el tercero; el libre no recupera ninguno. El éxito 3/3 de la etapa 86 no se convierte en garantía sobre pasajes nuevos.

Las correspondencias ausentes se excluyen de la exactitud de clave. Los controles mono usan 21, 22 y 22 símbolos observados. Los homofónicos usan los 26.

Los techos biyectivos exactos de los homofónicos son **76,15%, 80,45% y 80,85%**. Su verdad no pertenece a esa familia: el score de su texto verdadero no es una referencia alcanzable por el baseline para recuperar todas las letras.

## Diagnóstico: hay contraejemplos explícitos al objetivo

El método libre emite principalmente `i` y `v`, con `a` adicional en un par de presentaciones positivas. En los seis positivos sólo conserva dos o tres letras de salida. Todos los colapsos alcanzan un score mayor que el de la verdad, que sí pertenece al espacio muchos-a-uno.

En los tres controles homofónicos positivos la ventaja del colapso sobre la verdad es **1.380.358, 1.459.025 y 1.595.393 unidades enteras**, aproximadamente 1.380–1.595 nats con la escala usada. Esto no prueba que los candidatos sean óptimos globales. Sí prueba que la verdad no es un máximo: ya conocemos un candidato factible mejor puntuado.

Los [diez testigos](results/homophonic_recovery/objective_counterexamples.json) preservan claves factibles y ambos scores: nueve del método libre y uno monoalfabético del baseline. El auditor vuelve a calcular los scores desde las tablas. Una búsqueda más exhaustiva del mismo objetivo no elimina esos contraejemplos.

La cuantización aislada no explica la ventaja masiva: redondear cada log-probabilidad a 0,001 puede cambiar la comparación de dos secuencias de 1.997 términos como máximo en 1,997 nats. Esto acota el redondeo; no valida el suavizado, el corpus o la forma del objetivo.

### El caso mono con una letra incorrecta

En U04 el baseline sustituye `k` por `z` en la posición 187 contando desde cero, dentro del fragmento de control `...eratadvkalaprl...`. El candidato alcanza −6.223.943 y la verdad −6.226.632: una ventaja errónea de **2.689 unidades**, o 2,689 nats.

También es una preferencia incorrecta del modelo, no una diferencia que pueda atribuirse sólo a que faltaron reinicios. Como sólo cambian cuatro cuaternas interiores, el error máximo de redondeo de esa diferencia es 0,004 nats. Las tres primeras letras permanecen iguales; añadir únicamente una distribución inicial no resolvería este caso. La causa lingüística concreta sigue abierta.

El pasaje es latín de un control preparado, **no una lectura del Voynich**.

## Qué se verificó

La compilación y los controles previos pasaron: **2.079 comprobaciones de deltas frente a puntuación completa** en C++ y **15 controles matemáticos independientes**.

Tras revelar, el [evaluador](results/homophonic_recovery/evaluation.json) y el [auditor independiente](results/homophonic_recovery/audit.json) coincidieron en los 18 casos. El auditor terminó **PASS, 597 comprobaciones, cero discrepancias**, incluyendo fuentes, ventanas exactas, disjunción, presupuestos, claves, Hamming, scores y techos. PASS es integridad de métricas; el gate experimental permanece falso.

El generador Python reprodujo byte por byte los cuatro JSON preparados en JS: ciphertexts, manifiesto, verdad y semilla. Se recompilaron ambos ejecutables y se repitieron exactamente las predicciones congeladas. Esa ejecución posterior es reproducción informática, no otro ensayo ciego.

Se archivaron los logs y los JSON reconstruidos de sus fragmentos, verificando sus Git blobs contra los declarados por CI. Los recibos conservan metadatos de los ZIP de Actions; no se descargaron ni se verificaron los bytes de esos ZIP en este entorno. Véanse [recibo de búsqueda](results/homophonic_recovery/ci_search_receipt.json) y [recibo de evaluación](results/homophonic_recovery/ci_evaluation_receipt.json).

## Siguiente metodología propuesta, aún sin ejecutar

La omisión de un canal de emisión es una explicación metodológica plausible del colapso. El score actual premia el texto producido sin cobrar cómo sus pocas letras generarían tantos símbolos cifrados diferentes. Esto no demuestra que cualquier uso de un LM sobre mapas generales deba fallar; el fallo corresponde a la combinación congelada de corpus, suavizado, objetivo y capacidad.

Una alternativa a probar es añadir un canal de alias. Bajo emisión uniforme, si una letra clara tiene `m_p` alias y aparece `N_p` veces, el término de canal es:

\[
\log P_{\rm LM}(f(C)) - \sum_p N_p\log m_p.
\]

Es un diseño pendiente, no un resultado. Hace falta fijar alfabeto, soporte y normalización. Si una letra del LM carece de alias, se debe modelar explícitamente un fallo o la condición de codificabilidad; ignorarlo no produce sin más un modelo normalizado. Un alfabeto claro fijado externamente y más símbolos cifrados permite probar la formulación sin escoger la cardinalidad mirando estas respuestas. Un prior uniforme por clave, por sí solo, tampoco penaliza las fusiones.

Primero corresponde verificar normalización y comparar la recuperación con el óptimo obtenido mediante enumeración exhaustiva en un alfabeto pequeño; la verdad generada no tiene por qué ser siempre el máximo del modelo. Después, separar controles muestreados del propio modelo —capacidad del optimizador— de nuevos textos latinos auténticos —desajuste lingüístico—. Ambos necesitan criterios fijados antes de nuevos casos ocultos. El canal uniforme y las emisiones con prior Dirichlet son hipótesis distintas; no deben elegirse como un arreglo validado usando estos mismos nueve casos.

El canal uniforme aporta cero penalización en una biyección, por lo que no resolvería por sí solo el error U04. Ese fallo requiere comprobar también el modelo lingüístico y sus convenciones.

Este camino tiene antecedentes: [Ravi y Knight 2011](https://aclanthology.org/P11-1025/), [Berg-Kirkpatrick y Klein 2013](https://aclanthology.org/D13-1087/) y [Kambhatla y colaboradores 2018](https://aclanthology.org/D18-1102/). Se verificaron las fichas primarias; no se reivindica una técnica inédita ni una réplica de sus experimentos.

El resultado útil de esta etapa es un diagnóstico falsable de nuestro objetivo y la conservación pública de su fracaso. No identifica idioma, clave, homofonía o significado del manuscrito Voynich.
