# 29. Resultados de orden Q13/Q20 — consenso, bootstrap y dirección

Fecha: 2026-10-07

## Resumen ejecutivo

La investigación ya permite separar tres problemas que antes estaban mezclados:

1. **adyacencia**: qué singuliones parecen vecinos;
2. **topología**: qué cadena o grafo explica mejor esas vecindades;
3. **dirección**: en qué sentido se leería una adyacencia.

Los resultados no justifican todavía un único “orden original” para todo el manuscrito. Sí justifican varias vecindades locales robustas y dos órdenes de trabajo para Q13/Q20.

---

## Q13

Unidades:

- `75|84`
- `76|83`
- `77|82`
- `78|81`
- `79|80`

### Ranking exhaustivo con texto completo

Se evaluaron las `5! = 120` secuencias y se colapsó cada cadena con su reversa (`60` topologías).

- encuadernado actual: rango `37/60` con métrica combinada;
- Layfield–Davis: rango `13/60`;
- Held–Karp independiente reportado: rango `2/60`.

Por tanto, la reconstrucción independiente es claramente competitiva, mientras el orden encuadernado actual no aparece favorecido.

### Bootstrap de 1.000 réplicas

Frecuencia con que cada arista aparece en el camino óptimo:

| arista Q13 | frecuencia |
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
| `77|82 — 78|81` | 1,7% |

La conclusión fuerte cambia respecto de la hipótesis previa: **el núcleo robusto no es una cadena de tres singuliones**. Son, por ahora, dos parejas muy estables:

```text
75|84 — 78|81       76|83 — 77|82
  91,8%                 87,2%
```

El puente entre ambas parejas es ambiguo.

### Caminos bootstrap más frecuentes

1. `77|82 — 76|83 — 78|81 — 75|84 — 79|80` → 32,2%
2. `77|82 — 76|83 — 75|84 — 78|81 — 79|80` → 20,9%
3. `78|81 — 75|84 — 76|83 — 77|82 — 79|80` → 19,6%

El segundo es la reversa topológica del Held–Karp independiente publicado:

`79|80 — 78|81 — 75|84 — 76|83 — 77|82`.

Por ello ese orden sigue siendo un **candidato serio**, pero no único.

### Dirección Q13

Se compararon bordes de 4, 8, 12, 16 y 24 líneas.

- `75|84 — 78|81`: dirección **no estable**; la ventana de 4 líneas se invierte respecto de las demás.
- `76|83 — 77|82`: dirección **no estable**; 4/8 líneas y 12/16/24 líneas prefieren sentidos opuestos.
- `75|84 → 76|83`: signo estable en 5/5 ventanas, pero la adyacencia sólo tiene 48,1% de bootstrap.
- `76|83 → 78|81`: signo estable en 5/5, pero la adyacencia sólo tiene 47,3%.
- `78|81 → 79|80`: signo estable en 5/5, pero la adyacencia sólo tiene 23,3%.

**Conclusión Q13:** podemos defender vecindades locales; todavía no podemos orientar de manera robusta la cadena completa.

---

## Q20

Singuliones supervivientes:

- `S1 = 103|116`
- `S2 = 104|115`
- `S3 = 105|114`
- `S4 = 106|113`
- `S5 = 107|112`
- `S6 = 108|111`
- `S7 = 109|110` — perdido

### Control del gran confusor S/T

El ranking bruto recupera fuertemente la división lingüística conocida de Q20, por lo que no debe interpretarse como orden histórico.

Después de sustraer el promedio de similitud esperado para aristas `S-S`, `T-T` y `S-T`, el orden encuadernado actual queda aproximadamente al azar (`173/360`). Esto elimina una explicación trivial importante.

### Bootstrap residual de 1.000 réplicas

| arista Q20 | frecuencia |
|---|---:|
| `103|116 — 108|111` | **90,6%** |
| `105|114 — 107|112` | **78,5%** |
| `106|113 — 107|112` | **72,7%** |
| `106|113 — 108|111` | 51,2% |
| `104|115 — 106|113` | 45,1% |
| `104|115 — 107|112` | 40,6% |
| `103|116 — 104|115` | 36,1% |
| `104|115 — 108|111` | 34,8% |
| `105|114 — 106|113` | 17,3% |
| `104|115 — 105|114` | 15,2% |
| `103|116 — 106|113` | 10,8% |
| `103|116 — 107|112` | 3,3% |
| `105|114 — 108|111` | 2,3% |
| `107|112 — 108|111` | 1,5% |

### Camino topológico de trabajo Q20

El camino residual bootstrap más frecuente (16,3%) es:

`103|116 — 108|111 — 104|115 — 106|113 — 107|112 — 105|114`

Su reversa es topológicamente equivalente porque esta fase usa similitud simétrica.

Este camino es interesante porque usa las tres aristas más robustas:

- `103|116 — 108|111` (90,6%);
- `106|113 — 107|112` (72,7%);
- `107|112 — 105|114` (78,5%).

El enlace más débil que une ambos lados es `108|111 — 104|115` (34,8%). Esto sugiere una hipótesis falsable: el bifolio perdido `109|110` podría ocupar una región de transición cercana a ese puente, aunque **no se inserta en el orden** porque no existe texto que permita probarlo.

### Dirección Q20

El barrido de ventanas encuentra signos estables para varias aristas:

- `108|111 → 103|116` — estable en 5/5 ventanas;
- `105|114 → 107|112` — estable en 5/5;
- `106|113 → 107|112` — estable en 5/5;
- `106|113 → 108|111` — estable en 5/5;
- `106|113 → 104|115` — estable en 5/5;
- `104|115 → 103|116` — estable en 5/5.

Pero estas flechas forman un **grafo**, no una única cadena. Por ejemplo, tanto `105|114` como `106|113` apuntan hacia `107|112`. Eso impide interpretar automáticamente todos los scores de borde como transiciones narrativas consecutivas.

El mapa conservador es:

```text
105|114 ───────▶ 107|112
                    ▲
                    │
106|113 ────────────┘
   │
   ├──────────────▶ 108|111 ───────▶ 103|116
   │                                  ▲
   └──────────────▶ 104|115 ──────────┘

109|110 = perdido / posición no resuelta
```

Las flechas representan preferencia textual de borde, mientras el grosor conceptual de una conexión debe juzgarse por su frecuencia bootstrap. No equivalen aún a una secuencia histórica demostrada.

---

## Estado actual del orden

### Q13 — candidato topológico de trabajo

No se fuerza una orientación. La familia de soluciones está dominada por:

`79|80 — 78|81 — 75|84 — 76|83 — 77|82`

más variantes que conservan especialmente `75|84—78|81` y `76|83—77|82`.

### Q20 — candidato topológico de trabajo

`103|116 — 108|111 — 104|115 — 106|113 — 107|112 — 105|114`

con `109|110` como variable latente aún no colocada.

### Lo que sí podemos afirmar

- El orden encuadernado actual no es el óptimo textual en Q13 ni Q20 bajo estas métricas.
- Hay adyacencias locales que sobreviven 1.000 perturbaciones del corpus.
- Q20 conserva señal adicional después de controlar la partición lingüística S/T.
- Algunas direcciones de borde en Q20 mantienen el signo en cinco escalas distintas.

### Lo que todavía no podemos afirmar

- que una cadena concreta sea el orden original histórico completo;
- que la similitud textual sea continuidad semántica;
- dónde iba exactamente `109|110`;
- la orientación definitiva de Q13;
- la secuencia Q20 exacta de Layfield–Davis mientras no se extraiga/verifique su tabla primaria.

## Próxima etapa

1. integrar evidencia visual/codicológica como canal independiente, sin reentrenar pesos con Q13/Q20;
2. modelar el bifolio perdido `109|110` como un nodo latente/gap, no como texto inventado;
3. probar los candidatos en holdout por páginas y por manos/escribas;
4. extender la metodología a otros quires **solo como diagnóstico**, sin asumir que todos fueron singuliones;
5. usar el orden reconstruido como entrada para los experimentos de descifrado únicamente después de superar esos controles.
