# 91 — Canal normalizado e inferencia exacta: calibración completa en un modelo pequeño

**4 de noviembre de 2026. Rama `experiment/kraken-voynich`.**

Se implementó el siguiente paso propuesto en la etapa 89: puntuar conjuntamente lenguaje y emisión del cifrado. En un modelo pequeño fijado antes de calcular resultados, las probabilidades suman exactamente uno y dos programas independientes coinciden en **147.456 likelihoods y 4.096 filas de decisión**.

El auditor terminó **PASS, 352.323 comprobaciones, cero discrepancias**. Esto verifica matemáticamente el modelo finito y su implementación. **No es una recuperación latina, ni una traducción del Voynich, ni una solución demostrada al colapso de la etapa 88.**

## Qué se fijó antes de ejecutar

El [protocolo 90](90_exact_channel_protocol.md) y el [plan](data/tiny_channel_plan.json) quedaron publicados en `7e3592b8b4420061ae7eef914f61712a0dcaad75`. Las [fuentes congeladas](data/exact_channel_source_freeze.json) se publicaron en `6e9fe69fa62d10c9466981a82db1407d843dd116`, antes de la primera enumeración completa local y en GitHub.

El alfabeto claro es `abc`, el cifrado `wxyz`, la longitud seis y el prior uniforme sobre las **36 claves suryectivas**. Estos alfabetos se fijaron externamente; no se dedujeron de Voynich ni de los textos revelados en la etapa 88.

La distribución inicial de la cadena de Markov es `[3,2,1]/6` y su matriz de transición:

```text
[3,2,1] / 6
[1,4,1] / 6
[2,1,3] / 6
```

Cada letra clara tiene uno o dos alias cifrados y emite uniformemente uno de ellos. Todas las letras tienen al menos un alias. Por ello cada fila de emisión está normalizada sin condicionar a una selección posterior de letras observadas.

No hubo semilla, muestra aleatoria, verdad elegida como objetivo o filtrado de casos. Se enumeró toda la distribución especificada.

## Modelo y aritmética exacta

Para una clave `f`, el texto compatible con el ciphertext `C` es único. Su likelihood combina la probabilidad Markov del texto con las emisiones uniformes. Cada uso de una letra con dos alias aporta un factor adicional `1/2`.

Si `L` es el numerador entero del LM y `k` cuenta esas posiciones, el likelihood es:

```text
P(C | f) = L × 2^(6-k) / 12^6
12^6 = 2.985.984
P(f,C) = P(C | f) / 36
```

Se usan enteros y fracciones exactas. No hay scores redondeados, tolerancia numérica o Monte Carlo en los resultados principales.

Los 4.096 ciphertexts se comparan con las 36 claves: **147.456 pares**. Para cada clave, la suma de sus numeradores es exactamente 2.985.984; al sumar la distribución conjunta, numerador y denominador son ambos **107.495.424**. Los 4.096 posteriores, incluidos sus marginales por posición, también están normalizados.

El comparador sin canal usa **las mismas 36 claves** y maximiza sólo la probabilidad lingüística del texto obtenido. Así se aísla la contribución del canal dentro de esta familia. En el control de LM uniforme, sumar ese score sobre ciphertexts da `(4/3)^6 = 4096/729`, no uno; al incluir emisiones, la masa es exactamente uno.

## Distintas pérdidas requieren distintas decisiones

Se implementaron cinco reglas, con desempates fijados antes de calcular resultados:

1. Clave que maximiza el LM sin canal.
2. Clave MAP que maximiza el posterior con canal.
3. Texto MAP, sumando antes las probabilidades de las claves que producen el mismo texto.
4. Decisión Hamming por posición, para maximizar el número esperado de letras correctas.
5. Decisión Hamming restringida a salidas de claves admisibles.

La tercera regla no equivale siempre a descifrar con la clave MAP. Cuando faltan símbolos cifrados, distintas claves pueden producir el mismo texto y su masa debe agruparse.

## Resultados integrados sobre el modelo completo

Las cifras siguientes son **probabilidades esperadas bajo este modelo inventado**, no porcentajes de traducción de un corpus real. Se calculan sumando toda la distribución conjunta, con sus pesos; no se cuentan todos los ciphertexts como equiprobables.

| Decisión | Clave exacta esperada | Texto completo exacto esperado | Letras correctas esperadas |
|---|---:|---:|---:|
| Clave por LM sin canal | 6,9524% | 10,1455% | 44,1846% |
| Clave MAP con canal | 15,7216% | 25,7948% | 48,4211% |
| Texto MAP agrupado | No selecciona clave | 27,0176% | 48,2264% |
| Hamming restringido a clave | 8,6303% | 24,8092% | 49,0893% |
| Hamming libre por posición | No selecciona clave | 24,6785% | 49,1025% |

Los valores exactos se conservan como cocientes enteros en [result.json](results/exact_tiny_channel/result.json). Cada regla optimiza su pérdida correspondiente: la clave MAP no tiene por qué maximizar las letras acertadas, y maximizar letras no tiene por qué maximizar textos completos.

La mejora del canal frente al comparador LM es una propiedad de esta distribución explícita. No demuestra una tasa de descifrado para textos históricos. Tampoco exige que una verdad generada cualquiera sea siempre MAP: todas las claves conservan probabilidad posterior positiva.

## Ambigüedad y decisiones que no corresponden a una clave

En **584** ciphertexts, el texto obtenido de la clave MAP no pertenece al conjunto de textos MAP; la diferencia excede un simple desempate. En **688**, la salida elegida difiere del texto MAP lexicográfico, incluyendo diferencias debidas a empates.

Hay **856** ciphertexts con empate entre claves MAP y **204** con empate entre textos MAP. Los conjuntos MAP se conservan conceptualmente separados de una salida elegida por orden lexicográfico.

En **168** ciphertexts, la decisión Hamming libre no puede producirse con ninguna clave admisible. Su probabilidad total bajo el modelo es `28703/1119744`, aproximadamente 2,56%; 168/4096 es un conteo distinto que no usa pesos del modelo. Por eso una respuesta que acierta más letras en esperanza no debe presentarse automáticamente como una clave histórica coherente.

Los [testigos](results/exact_tiny_channel/witnesses.json) muestran el primer caso lexicográfico de cada fenómeno y sus pesos, como ilustraciones posteriores a la enumeración. No son ensayos adicionales.

Los **1.560** ciphertexts que contienen los cuatro símbolos tienen una correspondencia inyectiva entre clave y texto. Sus conjuntos MAP coinciden al descifrar las claves; los desempates lexicográficos de claves y textos aún pueden elegir representantes diferentes. No se confundió esa diferencia con un error probabilístico.

## Auditoría por una construcción diferente

El [programa principal](code/exact_tiny_channel.py) calcula likelihoods en dirección inversa: descifra cada ciphertext bajo cada clave y aplica los factores de emisión.

El [auditor](code/audit_exact_tiny_channel.py) no lo importa. Genera primero los **729 plaintexts** y, para cada clave, expande todas sus emisiones posibles. Reconstruye las 147.456 contribuciones a la tabla conjunta y después recalcula decisiones y riesgos. Se compararon todas las entradas y filas, no sólo promedios.

Los controles incluyen referencias cerradas de longitud uno: marginal cifrada `1/4`, posterior claro igual a la distribución inicial, éxito MAP de texto `1/2` y de clave `1/18`. También se comprueban cinco pesos calculables a mano, la equivarianza al intercambiar dos nombres cifrados y los recuentos por inclusión-exclusión.

El [auditor completo](results/exact_tiny_channel/audit.json) registra **352.323 comprobaciones sin discrepancias**. Sus 18 controles propios también pasaron antes de leer las tablas principales. Son comprobaciones matemáticas, no 352.323 experimentos de descifrado histórico.

## Ejecución y reproducción

La primera [ejecución en GitHub Actions](https://github.com/MedinaParra/Voynich/actions/runs/41891614314) pasó desde las fuentes publicadas, antes de existir los resultados preservados. El entorno local también completó la enumeración y auditoría.

Se preservan las tablas completas comprimidas, decisiones, controles, fracciones, testigos y fuentes. Para repetir:

```bash
python research_gpt6/code/exact_tiny_channel.py \
  --plan research_gpt6/data/tiny_channel_plan.json --out work/tiny_channel
python research_gpt6/code/audit_exact_tiny_channel.py \
  --repo research_gpt6 --bundle work/tiny_channel --out work/tiny_channel/audit.json
```

La [reproducción desde un checkout limpio](https://github.com/MedinaParra/Voynich/actions/runs/41892387013) pasó sobre el commit `cee5290511f19fdd70e21dbd49856e3c179428f5`: se recalcularon todas las tablas, decisiones y controles y se repitió la auditoría, coincidiendo con los cinco registros preservados. La condición prevista compara JSON descomprimido para las tablas gzip y bytes para los demás JSON; en esta ejecución coincidieron también los contenedores comprimidos completos. Se descargó el ZIP de Actions, se verificó su SHA256 `c1cd891b807e80641456c12978b35f2bceaef7532d2a55fc5b7816a61cf35651` y se contrastaron sus cinco miembros. Se conservan el [recibo](results/exact_tiny_channel/ci_replay_receipt.json), ZIP y log. Esta reproducción informática no es otro experimento independiente.

## Qué habilita y qué sigue pendiente

Ahora existe un prototipo generativo normalizado con inferencia exacta y auditoría independiente. Permite distinguir fallos del optimizador, errores del objetivo y ambigüedad inherente, antes de confiar en resultados de un buscador grande.

El régimen cambia respecto a la etapa 88: el alfabeto claro es conocido y la suryectividad ya excluye claves que usen sólo una o dos letras. Esta prueba **no demuestra haber corregido el colapso 26→26 sin restricciones**. No se volvió a entrenar ni ajustar aquel experimento.

El siguiente paso deberá ampliar alfabetos y canal bajo una especificación explícita y separar dos bancos: datos generados por ese modelo, para comprobar inferencia, y textos auténticos reservados, para medir desajuste lingüístico. La corrección del canal no elimina por sí sola errores del LM como el `k→z` de la etapa 88.

Se trata de una implementación y verificación de conceptos probabilísticos conocidos, no de una técnica de descifrado inédita. El manuscrito Voynich sigue sin una lectura verificable en este proyecto.
