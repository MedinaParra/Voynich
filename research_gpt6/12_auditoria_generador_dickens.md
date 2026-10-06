# Auditoría de un generador público «Voynich-like»: claim de vocabulario 99,6%

**Estado: FAIL para la interpretación literal de cobertura exacta de formas; BLOCKED para reproducir el pipeline/resultado completo del autor.** No es prueba de que el manuscrito tenga o no significado.

## Afirmación evaluada
Adam Dickens, “The Voynich Manuscript Is Not a Language: A Falsifiable Proof” (sitio independiente, publicado en 2026, no peer-reviewed) dice que un generador con prefijo opcional, base y sufijo opcional reproduce ≈99,6% de las formas de palabra Voynich. El sitio publica listas literales: 12 prefijos (qo, o, y, sh, ch, s, k, p, f, t, c, d), 33 bases y 9 sufijos (y, dy, ey, aiy, eey, am, an, chy, shy). Fuente: https://solvedvoynich.com/

## Reproducción de la gramática literal
Corpus fuente fijado: `cesarjz/Voynich`, commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, `corpus/voynich_eva.txt` (Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`). Se conservan las líneas de texto IVTFF con etiquetas que contienen `P`; se eliminan anotaciones y alternativas entre corchetes; los tokens se convierten a minúscula y se dividen por puntuación no alfabética. La lista del generador se copia del sitio y se enumeran todas las concatenaciones con prefijo/sufijo opcionales.

| Métrica | Resultado |
|---|---:|
| Líneas procesadas | 4.130 |
| Tokens después de normalización | 35.376 |
| Formas únicas observadas por este parser | 6.797 |
| Combinaciones brutas | 4.290 |
| Salidas distintas tras colisiones | 4.107 |
| Formas únicas con coincidencia literal exacta | 643 (9,46%) |
| Ocurrencias con forma generable | 13.139 (37,13%) |

La limitación combinatoria ya contradice el 99,6% si “forma de palabra” significa tipo ortográfico exacto: el generador solo puede emitir 4.107 cadenas distintas; el artículo de Matlach et al. describe 8.114 tipos EVA en su corpus de referencia. Aun en el supuesto imposible de que cada cadena generada aparezca, el máximo es 50,6% de esos tipos. En la reproducción directa con el parser indicado, la coincidencia exacta es 9,46% de tipos y 37,13% de ocurrencias.

## Interpretación y límites
- **FAIL:** la afirmación literal de 99,6% de formas exactas no se reproduce con las listas/cadena de concatenación publicadas y el corpus fijado.
- **BLOCKED:** no se pudo reproducir el valor total del sitio porque no se encontró allí código/dataset de evaluación que defina “matches”, la transcripción EVA-Takahashi exacta ni una regla de normalización alternativa. Si el 99,6% significa similitud no literal, la métrica no está especificada en la afirmación consultada.
- Este cálculo **no** refuta que una gramática con prefijos/raíces/sufijos pueda generar palabras de aspecto parecido. Refuta únicamente la cobertura literal exacta del generador tal como está publicado.
- El test de independencia entre líneas de esa página sigue **NOT_RUN**. Un MI redondeado a cero debe contrastarse con valor no redondeado, número efectivo de pares, incertidumbre/permutaciones que mantengan secciones y manuscritos de control, y con más de una transcripción. Aislamiento de líneas no implica por sí solo que el texto no codifique significado.

Código: `code/audit_dickens_generator.py`. Salida: `results/dickens_generator_audit.json`.
