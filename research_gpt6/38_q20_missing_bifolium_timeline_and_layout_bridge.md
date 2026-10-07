# 38. Q20 — cronología de `109|110` y puente de layout `108v → 111r`

Fecha: 2026-10-07
Estado: **corroboración codicológica/layout; no localiza por sí sola el bifolio perdido en el orden de producción**

## 1. Cronología material de `109|110`

Una declaración pública de Lisa Fagin Davis del 26-07-2026 resume la secuencia material relevante:

1. los números de cuaderno fueron añadidos y el manuscrito fue (mal) encuadernado en algún momento del siglo XV;
2. la foliación fue añadida en el siglo XVII;
3. seis bifolios y dos hojas individuales fueron retirados después de esa foliación y antes de que Voynich adquiriera el manuscrito en 1911/12.

Entre esas pérdidas se encuentra un bifolio retirado **del centro de Quire 20**, correspondiente a los folios `109–110`.

Consecuencia estricta:

> `109|110` fue el bifolio central de un **estado encuadernado tardío ya foliado** de Q20.

Esto NO implica que hubiese ocupado la misma posición en una secuencia anterior de singuliones o de producción.

## 2. Geometría de la foliación

Si los siete bifolios del estado encuadernado se anidan exterior→interior como:

`103|116 → 104|115 → 105|114 → 106|113 → 107|112 → 108|111 → 109|110`

la secuencia de hojas al leer el cuaderno encuadernado es exactamente:

`103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116`.

Por eso `109` y `110` son consecutivos y centrales en la foliación del estado anidado. Su numeración es totalmente coherente con que el bifolio todavía estuviera presente cuando se numeraron los folios.

Tras retirar `109|110`, el salto visible pasa a ser:

`108v → [109r,109v,110r,110v ausentes] → 111r`.

## 3. Una anomalía de layout que atraviesa ese salto

Existe una observación independiente especialmente informativa: hacia la mitad de `f108v` el escriba deja de separar cada estrella marginal en un párrafo corto y pasa a escribir grandes bloques continuos. Ese patrón reaparece al comienzo de `f111r`.

La transcripción ZL3b congelada permite cuantificarlo sin interpretar palabras:

### `f108v`, líneas 20–53

En ese tramo aparecen **11 anotaciones de estrella marginal**. Sin embargo, el texto está organizado en sólo **dos grandes párrafos**:

- líneas 20–29;
- líneas 30–53.

El segundo bloque contiene ocho estrellas marginales asociadas a líneas internas sin reiniciar el párrafo en cada una.

### `f111r`, líneas 6–35

Aparecen **11 estrellas marginales** dentro de **un único párrafo continuo de 30 líneas**. Las estrellas se distribuyen dentro del bloque en vez de marcar once párrafos separados.

## 4. Por qué esto importa

`f108` y `f111` son las dos hojas conjoint del mismo bifolio físico `108|111`.

Bajo lectura como singulión con orientación:

`108r → 108v → 111r → 111v`,

las dos páginas anómalas son **directamente consecutivas**:

**`108v → 111r`**.

Bajo el estado anidado y foliado, en cambio, el bifolio `109|110` queda insertado entre ellas:

`108v → 109r → 109v → 110r → 110v → 111r`.

Por tanto, la continuidad del mismo modo gráfico excepcional a ambos lados del hueco se entiende naturalmente si `108|111` funcionó como unidad antes del anidamiento.

Esta señal es especialmente útil porque no depende de:

- similitud léxica;
- EVA vs v101;
- TF-IDF;
- Currier A/B;
- optimización del orden global.

Es una propiedad de **layout y segmentación de párrafos**.

## 5. Lo que esta evidencia SÍ y NO demuestra

### Sí apoya

- que `108|111` constituye una unidad funcional fuerte, no sólo una pareja física accidental;
- que el anidamiento posterior interrumpe una continuidad gráfica interna del bifolio;
- que separar `orden de producción/singulión` de `orden encuadernado` es necesario.

### No demuestra

- que `109|110` siguiera originalmente a `105|114`;
- el contenido de las cuatro páginas perdidas;
- que todos los bifolios de Q20 debieran leerse necesariamente del mismo modo;
- desciframiento.

## 6. Relación con nuestro candidato

Nuestro orden aumentado de trabajo sigue siendo:

**`105|114 → [109|110] → 106|113 → 107|112 → 104|115 → 108|111 → 103|116`**

La nueva evidencia no puntúa la posición de `109|110` dentro de esa cadena. Lo que sí hace es fortalecer una premisa estructural de fondo: al menos el bifolio `108|111` conserva una continuidad de producción/layout que el estado anidado tardío separó artificialmente.

## Clasificación revisada de esta evidencia

**`INDEPENDENT_LAYOUT_SUPPORT_FOR_SINGULION_FUNCTION / LATE_CENTRAL_POSITION_OF_109|110_CONFIRMED / ORIGINAL_POSITION_OF_109|110_UNRESOLVED`**

## Guardrails

- Los conteos de estrellas/párrafos se hicieron sobre la transcripción ZL3b congelada y sus comentarios de layout; no sustituyen inspección directa del pergamino.
- La selección del caso `108v/111r` es exploratoria, motivada por una observación previa de Jorge Stolfi; no se presenta como test ciego.
- Que un bifolio sea una unidad funcional no fija automáticamente su posición relativa frente a otros singuliones.
