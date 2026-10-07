# 33. Estado global del orden — calibración, Quire G y límites de inferencia

Fecha: 2026-10-07
Estado: **consolidación posterior a controles adversariales**

## Resumen

La línea de investigación sobre orden de páginas ya no se interpreta como un único problema. Hay al menos cuatro niveles distintos:

1. **integridad física del bifolio** — qué folios son conjoint;
2. **anidamiento codicológico** — en qué orden físico se apilaron bifolios al encuadernar;
3. **proximidad de producción** — qué unidades textuales parecen haber sido producidas cerca unas de otras;
4. **orden de lectura/intención** — una afirmación mucho más fuerte que exige evidencia adicional.

Los experimentos muestran que el método puede recuperar el anidamiento actual de cuadernos regulares cuando este es compatible con la señal textual (calibración fuerte en Quire C), pero también puede detectar señales textuales que no reciben corroboración visual independiente (Quire G). Por ello no se equipara ya `máxima continuidad textual` con `orden físico original`.

---

## 1. Calibración externa a Q13/Q20

### Recuperación ciega de bifolios físicos

En quires regulares A–G, excluyendo Q13 y Q20, la señal de pertenencia al mismo bifolio sobrevive controles de distancia y metadatos. La prueba más limpia es Quire C (f17–f24), donde las cuatro parejas físicas son recuperadas en ZL3b e IT2a.

Esto valida una afirmación limitada pero importante: **la transcripción contiene señal de unidad física/de producción del bifolio**.

No demuestra que toda similitud entre bifolios determine el orden de lectura.

### Quire C como control positivo de anidamiento

Bifolios físicos:

- `17|24`
- `18|23`
- `19|22`
- `20|21`

Anidamiento actual, exterior → interior:

`17|24 → 18|23 → 19|22 → 20|21`

Al evaluar las 24 permutaciones con cinco escalas de borde y dos transcripciones:

- ZL3b: rangos del orden actual `2,2,1,1,1`;
- IT2a: `7,3,1,1,1`;
- mediana conjunta: **1/24**;
- top-1: **6/10** ventanas;
- top-3: **9/10**.

Conclusión: el algoritmo **no reordena inevitablemente** los cuadernos. Puede reconocer un quaternion regular cuya secuencia actual es coherente con la señal textual.

---

## 2. Barrido de quires regulares y control de confusores

El primer barrido bruto produjo sospechas en D, F y G. Al retirar la contribución media asociada a transiciones de mano Davis y Currier, el resultado cambió:

| Quire | folios | estado después del control de metadatos |
|---|---|---|
| A | 1–8 | compatible con orden actual |
| C | 17–24 | **compatible; control positivo fuerte** |
| D | 25–32 | compatible con orden actual |
| E | 33–40 | compatible con orden actual |
| F | 41–48 | inconcluso; gran parte de la anomalía era mano/Currier |
| G | 49–56 | inconcluso en barrido; promovido a prueba adversarial |

Esto es un resultado negativo importante: el sistema detectó un aparente desorden en D/F que en buena medida desapareció al introducir un control paleográfico/lingüístico. Por tanto los controles están eliminando falsos positivos en vez de confirmar sistemáticamente una narrativa de reordenamiento.

---

## 3. Quire G — prueba adversarial específica

### Estructura física aceptada

- `49|56`
- `50|55`
- `51|54`
- `52|53`

Anidamiento actual:

`49|56 → 50|55 → 51|54 → 52|53`

Secuencia de folios implicada:

`49,50,51,52,53,54,55,56`

### Diseño

Se congeló antes de ejecutar:

- 24 anidamientos posibles;
- orientación de cada bifolio fija;
- cinco ventanas: 25, 50, 100, 200 tokens y página completa;
- residualización por transición exacta `mano Davis + Currier` tomada de ZL3b y aplicada también a IT2a;
- tres familias de rasgos: TF-IDF de tokens, TF-IDF de n-gramas EVA 3–5 y Jaccard;
- cuatro configuraciones: todos los rasgos y tres leave-one-feature-out;
- ZL3b e IT2a seleccionan el candidato **independientemente**.

### Resultado textual

Ambas transcripciones seleccionan exactamente el mismo anidamiento:

**`52|53 → 50|55 → 51|54 → 49|56`**

Secuencia de folios correspondiente:

**`52 → 50 → 51 → 49 → 56 → 54 → 55 → 53`**

#### ZL3b

Con todos los rasgos, el candidato obtiene rangos:

`7,2,1,1,1` → mediana **1/24**.

El orden actual:

`14,9,12,12,12` → mediana **12/24**.

#### IT2a

Con todos los rasgos, el mismo candidato obtiene:

`8,3,1,1,1` → mediana **1/24**.

El orden actual permanece en la mitad inferior del ranking en las escalas largas.

### Ablaciones

El mismo candidato gana **4/4 configuraciones en ZL3b** y **4/4 en IT2a**:

- todos los rasgos;
- sin token-TFIDF;
- sin char-3/5-TFIDF;
- sin Jaccard.

En todas las configuraciones su mediana es `1/24` y en ambas transcripciones aparece top-1 en 3/5 escalas.

### Qué elimina este resultado

La explicación trivial `el algoritmo sólo agrupa Currier A con A y B con B` queda debilitada porque:

- la residualización mano+Currier se aplica antes del ranking;
- el candidato aún intercala el bifolio B `50|55` dentro de bifolios A;
- la solución reaparece en dos transcripciones y sobrevive al retiro individual de cada familia de rasgos.

---

## 4. Control visual independiente de Quire G

Después de congelar el candidato textual se ejecutó un test que **no lee la transcripción**. Usa los perfiles visual-semánticos públicos Xenoglyph derivados de imágenes Yale, tres lentes de 16 dimensiones y ningún peso ajustado en Quire G.

Se promedió `r/v` de cada folio y se puntuaron los 24 anidamientos mediante la continuidad visual de la secuencia de folios que cada anidamiento implica.

### Resultado

El canal visual **NO confirma** el candidato textual.

Consenso de las tres lentes:

- mejor visual: `49|56 → 51|54 → 52|53 → 50|55`;
- candidato textual congelado: **rango 17/24**;
- anidamiento actual: **rango 13/24**.

Por lente:

- Voynich lens: candidato textual `10/24`, actual `15/24`;
- archaeology lens: candidato `22/24`, actual `12/24`;
- cryptological lens: candidato `15/24`, actual `9/24`.

Conclusión: la robustez textual de G **no es una simple consecuencia de que las ilustraciones vecinas se parezcan**. Pero tampoco recibe una validación visual independiente.

El canal visual no es codicología física; su desacuerdo no refuta por sí solo una secuencia de producción. Sí impide elevar el candidato a `orden original demostrado`.

---

## 5. Evidencia codicológica pública relevante para G

Quire 7 es un quaternion estándar f49–f56 y la marca de cuaderno está en `f56v`.

Observaciones públicas relevantes:

- `f50` presenta un agujero de pergamino en el centro;
- `f55` presenta una cresta/pliegue horizontal visible;
- la marca de cuaderno está en `f56v`;
- no se ha localizado hasta ahora una transferencia de pintura, desgarro complementario o defecto de piel publicado que seleccione de forma inequívoca uno de los 24 anidamientos.

La marca de cuaderno **no prueba el orden de producción**. Lisa Fagin Davis ha explicado públicamente que las marcas de cuaderno se añadieron cuando se organizó/encuadernó el manuscrito, una fase posterior en su modelo de singuliones. Por tanto, un orden de producción diferente puede coexistir con `f56v` como cierre del cuaderno encuadernado.

---

## 6. Clasificación actual de Quire G

Estado recomendado:

**`ROBUST_TEXTUAL_PRODUCTION_ORDER_CANDIDATE / PHYSICAL_REBINDING_UNCONFIRMED`**

No usar:

- `orden original demostrado`;
- `reencuadernación probada`;
- `secuencia semántica recuperada`.

Sí podemos decir:

> Tras controlar mano y Currier, dos transcripciones y cuatro configuraciones de rasgos convergen en el mismo anidamiento textual candidato para Quire 7. Sin embargo, un canal visual externo no lo reproduce y no existe todavía una pieza codicológica física pública que lo decida.

---

## 7. Estado global de la hipótesis de orden

### Q13

Sigue siendo un caso especial compatible con la hipótesis singulion.

Vecindades más robustas:

- `75|84 — 78|81`: 91,8%;
- `76|83 — 77|82`: 87,2%.

El candidato Held–Karp independiente supera a Layfield–Davis en el duelo bootstrap, pero la dirección completa no está fijada.

### Q20

Sigue siendo el segundo caso especial fuerte. Después de controlar el bloque lingüístico S/T persisten varias aristas robustas y un conjunto de flechas de borde estables. El bifolio perdido `109|110` debe permanecer como gap latente.

### Quires regulares

- C demuestra que el método puede recuperar un anidamiento actual coherente;
- A, D, E son compatibles con el orden actual tras controles;
- F queda inconcluso y confunde fuertemente mano/Currier;
- G posee una señal textual alternativa robusta, pero por ahora sin confirmación material/visual.

---

## 8. Próximo experimento con mayor valor informativo

Para G no conviene seguir creando métricas textuales parecidas. El siguiente avance real requiere un canal físico independiente:

1. inspección a alta resolución de `f49–f56` en Yale;
2. clasificar hair-side/flesh-side cuando sea visible;
3. registrar agujeros, pliegues, bordes, defectos de piel y costuras;
4. medir si defectos/ondulaciones forman patrones compatibles con algún orden de apilado;
5. buscar transferencias de pigmento y offsets entre superficies que debieron enfrentarse;
6. mantener oculto al evaluador visual cuál de los 24 anidamientos ganó textualmente, si se hace anotación humana.

Hasta completar ese canal, G se conserva como una **predicción codicológica falsable**, no como una conclusión histórica.
