# 30. Ledger de evidencia para el orden Q13/Q20

Fecha: 2026-10-07

## Propósito

Este documento congela el estado de la reconstrucción del orden y, sobre todo,
**separa canales de evidencia que no deben mezclarse como si fueran equivalentes**.

Las categorías usadas son:

1. texto/transcripción;
2. imagen semántica global;
3. codicología física e ilustrativa;
4. paleografía/rasgos de escritura;
5. hipótesis auxiliares.

Una coincidencia entre canales independientes es más valiosa que un score alto
dentro de un único canal. Una contradicción se conserva: no se corrige ajustando
pesos hasta que desaparezca.

---

## 1. Q13 — evidencia textual

### Vecindades bootstrap, 1.000 réplicas

| arista | frecuencia |
|---|---:|
| `75|84 — 78|81` | **91,8%** |
| `76|83 — 77|82` | **87,2%** |
| `75|84 — 76|83` | 48,1% |
| `76|83 — 78|81` | 47,3% |
| `75|84 — 79|80` | 41,7% |
| `77|82 — 79|80` | 27,0% |
| `78|81 — 79|80` | 23,3% |
| `76|83 — 79|80` | 16,0% |
| `75|84 — 77|82` | 15,9% |
| `77|82 — 78|81` | **1,7%** |

Conclusión: las dos parejas robustas son `75|84—78|81` y `76|83—77|82`.
El puente entre ellas no está resuelto.

### Duelo directo con Layfield–Davis

Secuencia Layfield–Davis reportada públicamente:

`77|82 — 78|81 — 75|84 — 76|83 — 79|80`

Secuencia independiente ZL3b:

`79|80 — 78|81 — 75|84 — 76|83 — 77|82`

Ambas comparten el núcleo:

`78|81 — 75|84 — 76|83`

La diferencia está únicamente en la asignación de `77|82` y `79|80` a los extremos.
En un duelo prespecificado de 2.000 remuestreos de líneas:

- independiente ZL3b gana `1858/2000 = 92,9%`;
- Layfield–Davis gana `142/2000 = 7,1%`;
- empates: `0`;
- score corpus completo: `1,7094` vs `0,7036`;
- delta medio bootstrap independiente − L-D: `+0,9403`;
- intervalo empírico 2,5–97,5% del delta: `[-0,3506, 2,3691]`.

Esto no prueba orden histórico. Sí demuestra que con la transcripción ZL3b y la
métrica congelada la diferencia entre ambas asignaciones de extremos es fuerte
y reproducible.

Resultado reproducible:

- `results/order_q13_sequence_duel.json`

Fuente secundaria que reproduce la secuencia publicada de Layfield–Davis:

- https://www.voynich.ninja/archive/index.php/thread-5940.html

Artículo primario:

- Colin Layfield & Lisa Fagin Davis, *Singulion Structure and the Voynich Manuscript*, Digital Medievalist 19 (2026), DOI `10.4000/16k0a`.

---

## 2. Q13 — codicología física e ilustrativa

### Evidencia fuerte: integridad de bifolios

Hay continuidades gráficas físicas que atraviesan el pliegue de los bifolios:

- `f76v ↔ f83r`: parte del líquido pulverizado cruza la unión;
- `f78v ↔ f81r`: tubos dibujados continúan de una hoja a la otra.

Fuente descriptiva independiente:

- https://www.voynich.nu/q13/index.html

**Interpretación correcta:** estas observaciones son evidencia fuerte de que cada
pareja pertenece al mismo bifolio/singulion. **No determinan el orden entre
singuliones** y por tanto no se cuentan como votos a favor de una cadena global.

### Evidencia blanda: `f76r` como posible inicio

La descripción de Q13 señala que la forma de `f76r`, en particular su inicial
ornamentada, podría indicar que fue la primera página de la sección.

Se probó explícitamente la hipótesis de trabajo `76|83 = primer singulion` entre
las `4! = 24` órdenes compatibles.

Resultado:

- puede conservar buenas aristas bootstrap;
- el mejor orden condicionado por bootstrap queda `9/120` globalmente por ese
  criterio, pero sólo `47/120` por score textual combinado;
- los mejores compromisos Pareto condicionados quedan aproximadamente entre
  `31/120` y `57/120` por score textual;
- la secuencia ZL3b no condicionada queda `4/120` por score textual y `8/120`
  por estabilidad bootstrap.

Además, una de las flechas direccionales textuales estables es `75|84 → 76|83`,
que entra directamente en tensión con imponer `76|83` como primer nodo.

**Decisión:** `f76r = inicio` queda como pista codicológica blanda; no se usa como
restricción dura.

Resultado reproducible:

- `results/order_q13_codicology_pareto.json`

---

## 3. Q13 — canal visual-semántico externo

Se usaron perfiles públicos por página derivados sólo de imagen, en tres lentes
independientes (`voynich`, `archaeology`, `cryptological`), sin consumir nuestra
transcripción y sin ajustar pesos a Q13/Q20.

En el consenso de tres lentes:

- `76|83—77|82` sí aparece como la arista visual más fuerte de Q13;
- `75|84—78|81` no aparece entre las aristas visuales superiores;
- la secuencia textual ZL3b queda `21/60`;
- la prueba exacta de alineación del conjunto de dos aristas objetivo da `p = 0,20`.

**Conclusión:** existe validación visual parcial para `76|83—77|82`, pero no para
la secuencia Q13 completa.

Fuente de perfiles externos, commit congelado:

- repo: `xenoglyph-ai/voynich-public`
- commit: `d4b31a245ba8133b727dc4255278b5e8349bbe39`

Resultado reproducible:

- `results/order_visual_semantic_validation.json`

---

## 4. Estado Q13

### Topología de trabajo

Sin imponer dirección histórica:

`79|80 — 78|81 — 75|84 — 76|83 — 77|82`

más su reversa topológicamente equivalente.

### Grado de confianza

- alto para `75|84—78|81` como vecindad textual;
- alto y además parcialmente externo para `76|83—77|82`;
- medio/bajo para el puente entre ambas parejas;
- insuficiente para afirmar dirección global;
- la pista `f76r = inicio` permanece abierta pero actualmente pierde contra la
  evidencia textual global.

---

## 5. Q20 — evidencia física y codicológica

Q20 probablemente contenía siete bifolios normales; falta el bifolio central
actual `109|110`. Permanecen:

`103|116, 104|115, 105|114, 106|113, 107|112, 108|111`.

Fuente descriptiva:

- https://www.voynich.nu/q20/index.html

### Posible inicio

`f105r` tiene rasgos anómalos de comienzo de sección. La descripción de Q20 y
observaciones independientes han señalado su estructura inicial como especial.
Se usa sólo como **hipótesis de endpoint**, no como hecho.

### Posible cierre

En `f116r` las estrellas sólo ocupan la mitad superior; los dos últimos
párrafos no tienen estrellas. La descripción independiente señala que esto
sugiere comentarios finales. `f116v`, además, es la última página física del
manuscrito actual y contiene marginalia posterior.

Esto hace razonable probar, sin imponer como verdad, la pareja de hipótesis:

- `105|114` primero;
- `103|116` último, de modo que la lectura interna termine en `f116v`.

---

## 6. Q20 — evidencia textual controlada

Después de retirar el gran confusor lingüístico S/T, las aristas bootstrap son:

| arista | frecuencia |
|---|---:|
| `103|116 — 108|111` | **90,6%** |
| `105|114 — 107|112` | **78,5%** |
| `106|113 — 107|112` | **72,7%** |
| `106|113 — 108|111` | 51,2% |
| `104|115 — 106|113` | 45,1% |
| `104|115 — 107|112` | 40,6% |
| `103|116 — 104|115` | 36,1% |
| `104|115 — 108|111` | 34,8% |

Las flechas de borde cuyo signo sobrevive las ventanas 4/8/12/16/24 líneas son:

- `108|111 → 103|116`;
- `105|114 → 107|112`;
- `106|113 → 107|112`;
- `106|113 → 108|111`;
- `106|113 → 104|115`;
- `104|115 → 103|116`.

---

## 7. Q20 — Pareto condicionado por endpoints codicológicos

Se enumeraron las `24` órdenes compatibles con:

- `105|114` primero;
- `103|116` último.

No se construyó un score compuesto. Se mantuvieron tres objetivos separados:

1. suma de frecuencias bootstrap de las aristas;
2. score textual residual completo;
3. número de precedencias direccionales satisfechas.

Sólo tres órdenes quedan en el frente de Pareto.

### A — máxima compatibilidad direccional

`105|114 → 106|113 → 107|112 → 104|115 → 108|111 → 103|116`

- bootstrap sum: `2,560`;
- residual: `1,9413`;
- flechas: `6/6`;
- rango global bootstrap: `64/720`;
- rango global residual: `20/720`.

### B — mejor equilibrio actual / candidato principal

`105|114 → 107|112 → 106|113 → 104|115 → 108|111 → 103|116`

- bootstrap sum: **`3,217`**;
- residual: **`2,3590`**;
- flechas: `5/6`;
- rango global bootstrap: **`6/720`**;
- rango global residual: **`6/720`**.

Ésta es exactamente la orientación inversa del candidato topológico previo:

`103|116 — 108|111 — 104|115 — 106|113 — 107|112 — 105|114`.

### C — mayor score residual

`105|114 → 107|112 → 104|115 → 106|113 → 108|111 → 103|116`

- bootstrap sum: `3,060`;
- residual: **`2,6225`**;
- flechas: `4/6`;
- rango global bootstrap: `10/720`;
- rango global residual: **`4/720`**.

**Decisión:** B se mantiene como candidato de trabajo porque es Pareto-óptimo,
está entre los seis mejores de 720 tanto en bootstrap como en residual, y conserva
cinco de seis restricciones direccionales. No se elige por una suma arbitraria
de pesos.

Resultado reproducible:

- `results/order_q20_pareto_codicology.json`

---

## 8. Q20 — validación visual externa: resultado negativo

El canal visual-semántico externo **no recupera** la topología textual Q20:

- el candidato textual queda `150/360` en el consenso visual;
- el orden actual queda `60/360`;
- las tres aristas textuales objetivo quedan sólo `11/15`, `10/15` y `8/15`;
- prueba exacta del conjunto de aristas objetivo: `p = 0,5722`.

Esto se conserva como resultado negativo importante.

**Interpretación:** la señal de orden textual Q20 no parece ser simplemente un
reflejo de semejanza temática o gráfica global de las páginas. Tampoco hay
validación visual externa de la secuencia completa.

---

## 9. Evidencia exploratoria que NO se usa para ajustar el orden

### Grosor de etiquetas en Q13

Una discusión paleográfica reciente en Voynich Ninja observa etiquetas gruesas
y finas distribuidas de manera desigual entre los bifolios Q13 y propone que
podrían reflejar distintas pasadas de escritura.

Fuente exploratoria:

- https://voynich.ninja/thread-5823.html

No existe todavía una demostración de que el grosor implique secuencia temporal
entre bifolios. Por tanto se registra, pero no entra al optimizador.

### Offsets, manchas y transferencias

La historia de reencuadernación hace que offsets/contact transfers puedan reflejar
una encuadernación posterior en vez del orden original. Hasta obtener una matriz
física sistemática e independiente, no se usan como verdad de terreno.

---

## 10. Estado actual de la reconstrucción

### Q13

**Topología textual de trabajo:**

`79|80 — 78|81 — 75|84 — 76|83 — 77|82`

Orientación: **no resuelta**.

Puntos firmes:

- `75|84—78|81`;
- `76|83—77|82`.

Punto débil:

- conexión entre ambos subbloques.

### Q20

**Orden orientado de trabajo:**

`105|114 → 107|112 → 106|113 → 104|115 → 108|111 → 103|116`

con `109|110` como nodo latente/perdido todavía **sin posición asignada**.

---

## 11. Qué falsaría o modificaría estas conclusiones

### Q13

- evidencia física inequívoca de una interfaz entre dos singuliones;
- matriz sistemática de manchas/transferencias que sobreviva la historia de
  reencuadernación;
- replicación con una transcripción independiente que revierta el duelo de
  extremos;
- evidencia material fuerte de que `f76r` fue realmente el inicio, no sólo una
  página formalmente marcada.

### Q20

- una posición material demostrable para `109|110`;
- evidencia física que contradiga `105|114` como posible inicio o `103|116` como
  posible cierre;
- pérdida de las aristas principales al cambiar de transcripción o representación;
- direcciones de borde que dejen de ser estables en validaciones independientes.

---

## 12. Próxima prueba

La siguiente prueba no debe inventar el contenido de `109|110`. Se tratará como
**gap latente** y se preguntará únicamente qué interfaz observada es la candidata
más razonable para ser interrumpida por un bifolio perdido.

Criterios separados:

- debilidad bootstrap de la interfaz;
- debilidad del score residual;
- ausencia/presencia de una flecha direccional estable;
- compatibilidad con la topología Pareto.

La posición del gap sólo será propuesta si varios criterios independientes
coinciden.