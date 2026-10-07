# 28. Q20 — topología provisional y restricciones de orden

Fecha: 2026-10-07
Estado: **avance codicológico + diseño computacional; no confundir con orden original demostrado**.

## Objetivo

Continuar la reconstrucción del orden del manuscrito sin forzar una cadena lineal cuando la evidencia solo permite vecindades. Q13 ya posee un núcleo candidato estable; este documento abre Q20 como grafo de restricciones.

## Unidades físicas de Q20

Q20 probablemente tuvo siete bifolios normales; el central `109|110` falta. Los seis supervivientes se representan como:

- `S1 = 103|116`
- `S2 = 104|115`
- `S3 = 105|114`
- `S4 = 106|113`
- `S5 = 107|112`
- `S6 = 108|111`
- `S7 = 109|110` — perdido

El orden encuadernado actual de los seis supervivientes, de exterior a interior, es `S1-S2-S3-S4-S5-S6`, pero esto **no se adopta como orden de producción/lectura**.

## Evidencia independiente que restringe la topología

### 1. Partición lingüística fuerte

La clasificación extendida de René Zandbergen separa Q20 en dos conjuntos de tres bifolios:

- bloque tipo `S`: `S1 (103|116)`, `S5 (107|112)`, `S6 (108|111)`;
- bloque tipo `T`: `S2 (104|115)`, `S3 (105|114)`, `S4 (106|113)`.

Esto es una señal real de estructura, pero puede ser dialecto/mano/proceso de copia en vez de continuidad semántica. Se usará como covariable y como ablación, **no** como regla dura de orden.

### 2. Transferencias de pintura / proximidad física

La recopilación codicológica de Nick Pelling registra:

- transferencia de pintura `116r -> 115v`, que vincula físicamente `S1` y `S2` en algún estado de encuadernación/pintado;
- mancha roja entre `104v` y `105r`, que vincula `S2` y `S3`;
- transferencia desde `113v` hacia `115r` atravesando el defecto/borde de `114`, que sugiere proximidad del motivo `S4 ~ S3 ~ S2`;
- otra transferencia tenue entre `114v` y `115r`.

Estas restricciones son importantes, pero pueden describir una **fase de encuadernación posterior**, no necesariamente el orden original de producción.

### 3. Pergamino / posible estructura material

Una hipótesis material previa agrupa `S2,S3,S5,S6` por aspecto del pergamino, mientras `S1,S4` (y quizá el bifolio perdido) formarían otro conjunto. Esta partición no coincide con la lingüística 3+3, lo cual es útil: evita que una única señal domine la reconstrucción.

### 4. Marcadores de inicio/final

- `f105r` contiene un gallows ornamental excepcional y títulos/anomalías que lo convierten en candidato estructural a inicio o reinicio.
- `f116r` presenta una ruptura estructural en su mitad inferior; observadores han propuesto que los últimos párrafos parecen material de cierre.
- `f103r` conserva la marca de cuaderno 20, pero una marca de cuaderno no demuestra por sí sola que ese folio fuese el primer elemento de la secuencia de producción.
- `f115r` cambia de escriba en sus primeras doce líneas, otro posible marcador de frontera.

Ninguno se fijará como extremo a priori; se evaluarán como hipótesis.

## Grafo provisional de evidencia

No imponemos todavía dirección:

```text
             S5 = 107|112
              \
               [bloque S]
              /
S6 = 108|111 ---- S1 = 103|116
                         |
                  transferencia fuerte
                         |
                    S2 = 104|115
                         |
                  transferencia fuerte
                         |
                    S3 = 105|114
                         ~
                    S4 = 106|113

S7 = 109|110  [faltante; posición desconocida]
```

Lectura correcta del gráfico: `S1-S2-S3` es una vecindad **codicológica de alta prioridad para prueba**, mientras `S1/S5/S6` y `S2/S3/S4` son bloques lingüísticos. No se afirma que una de esas estructuras sea el orden original.

## Consecuencia metodológica importante

La similitud léxica por sí sola no puede fijar la **dirección** de una secuencia. Si el score es simétrico, una cadena y su reverso son equivalentes. Por tanto, el próximo benchmark separará:

1. **topología/adyacencia** — recuperable con similitud simétrica;
2. **dirección** — solo aceptable con rasgos asimétricos de borde, marcadores de inicio/cierre o evidencia codicológica independiente.

## Candidatos que se deben enfrentar, no asumir

### H0 — encuadernado actual
`S1-S2-S3-S4-S5-S6`

### H1 — dos bloques lingüísticos contiguos
Cualquier cadena que mantenga juntos `{S1,S5,S6}` y `{S2,S3,S4}`. Hay que rankear todas sus orientaciones/permutaciones, no escoger una post hoc.

### H2 — vecindad codicológica
Debe favorecer el motivo `S1-S2-S3` y evaluar `S4` como vecino de `S3/S2`, sin obligar a que esa cadena represente la fase original.

### H3 — orden LSA Layfield–Davis
La literatura de 2026 afirma una secuencia hipotética para Q20 y una reproducción independiente declara coincidir con ella. **La secuencia explícita aún no ha sido extraída de una fuente primaria accesible en esta rama**, por lo que no se inventa. Estado: `VERIFICATION_PENDING`.

### H4 — óptimo libre
Todas las `6! = 720` permutaciones de los seis bifolios supervivientes, evaluadas con representación congelada. El bifolio faltante `S7` queda como variable latente y no se inserta artificialmente.

## Prueba siguiente congelada

Para los seis singuliones supervivientes:

1. extraer texto ZL3b por folio;
2. agregar cada bifolio sin usar el orden objetivo;
3. construir dos scores independientes: token TF-IDF y n-gramas EVA;
4. puntuar las 720 cadenas abiertas;
5. reportar el rango del orden actual, el mejor score y el conjunto de cadenas casi óptimas (por ejemplo, dentro del 1% del máximo);
6. construir consenso de aristas entre esas cadenas;
7. repetir por bootstrap de párrafos y leave-one-feature-out;
8. controlar explícitamente la partición `S/T` para comprobar si el óptimo solo redescubre dialecto;
9. recién después incorporar rasgos dirigidos para probar inicio/final.

## Estado tras este avance

- Mapeo físico Q20: `PASS`.
- Grafo de restricciones codicológicas: `PASS_PROVISIONAL`.
- Partición lingüística independiente: `PASS_AS_COVARIATE`.
- Secuencia exacta Layfield–Davis Q20: `VERIFICATION_PENDING`.
- Orden total Q20: `NOT_CLAIMED`.
- Hipótesis ahora más precisa: **Q20 puede contener dos bloques lingüísticos superpuestos a una historia material de reencuadernación; el problema correcto es recuperar primero aristas estables y después, solo si la evidencia lo permite, orientar la cadena.**
