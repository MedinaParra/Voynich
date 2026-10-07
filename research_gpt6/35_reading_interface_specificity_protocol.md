# 35. Protocolo congelado — especificidad de interfaz de lectura

Fecha: 2026-10-07

## Pregunta adversarial

El programa de ordenamiento ha usado como interfaz físicamente correcta entre hojas consecutivas:

`cola(verso de hoja origen) → cabeza(recto de hoja destino)`.

Después del PASS exploratorio de Quire B, se congela un control adversarial para preguntar si esa interfaz es realmente especial o si el mismo ranking aparece usando bordes que **no** corresponden a una transición normal de lectura.

Este protocolo se escribe después de observar los resultados del modelo correcto, por lo que es un **control adversarial post-resultado**. Sus reglas y modos se congelan antes de ejecutar los controles incorrectos.

## Unidades

Se usan siete quires con verdad física ya fijada:

- completos: A (`1–8`), C (`17–24`), D (`25–32`), E (`33–40`), F (`41–48`), G (`49–56`);
- parcial: B, con `9|16`, `10|15`, `11|14` y gap central `12|13`.

Q13 y Q20 se excluyen porque originaron hipótesis de orden no estándar.

## Datos y parámetros congelados

- ZL3b y Takahashi IT2a, exactamente las mismas fuentes/hashes del programa previo.
- ventanas 25, 50, 100, 200 tokens y página completa;
- mismas tres componentes: TF-IDF de tokens, TF-IDF de caracteres 3–5 y Jaccard de tokens;
- z-normalización por componente y promedio simple;
- orientación interna de cada bifolio fija;
- para A/C/D/E/F/G se enumeran `4! = 24` anidamientos;
- para B se enumeran `3! = 6` órdenes y sólo las cuatro transiciones que no cruzan el gap central.

No se retunea ningún peso, ventana ni orden a partir de este control.

## Modos de interfaz

Para cada transición hoja-origen → hoja-destino se construye una matriz con uno de cuatro modos, manteniendo todo lo demás igual:

1. **TH (correcto)**: `tail(verso origen) → head(recto destino)`.
2. **HH (control)**: `head(verso origen) → head(recto destino)`.
3. **TT (control)**: `tail(verso origen) → tail(recto destino)`.
4. **HT (control)**: `head(verso origen) → tail(recto destino)`.

Sólo TH corresponde a la interfaz de lectura que motivó el modelo.

## Endpoint por quire

Para cada modo y quire se calcula el rango del orden físico actual en cada una de las 10 combinaciones transcripción×ventana.

Como A/C/D/E/F/G tienen 24 candidatos y B tiene 6, se normaliza cada rango como:

`rango_normalizado = (rango - 1) / (N_candidatos - 1)`

De modo que 0 es mejor y 1 peor.

El resumen por quire/modo es la **mediana de los 10 rangos normalizados**. Las 10 observaciones son correlacionadas y no se tratan como réplicas independientes.

## Comparación primaria

Para cada quire se define:

`best_wrong = min(mediana_HH, mediana_TT, mediana_HT)`

TH “gana” sólo si:

`mediana_TH < best_wrong`.

Empates no cuentan como victoria.

## Regla congelada

- **PASS_EDGE_SPECIFIC_EXPLORATORY**: TH vence al mejor control incorrecto en al menos `6/7` quires, y además su mediana global entre los siete quires es menor que la de cada modo incorrecto por separado.
- **FAIL_EDGE_SPECIFIC**: TH vence al mejor control incorrecto en `3/7` quires o menos.
- **INCONCLUSIVE**: cualquier resultado intermedio.

Se reportará además el test exacto de signos unilateral para TH contra cada modo incorrecto y contra `best_wrong`, pero esos p-valores son secundarios y no modifican la regla anterior.

## Control de metadata

El endpoint primario usa matrices **raw**, porque la pregunta es si el borde geométrico correcto es específico antes de introducir residualizaciones de metadata. Como análisis secundario se repetirá la comparación con residualización exacta Davis-H + Currier-L, usando la misma función congelada del experimento anterior.

## Falsabilidad

Si TH no supera consistentemente a bordes incorrectos, la interpretación de que el score captura continuidad de lectura verso→recto queda debilitada, aunque algunos quires individuales hayan rankeado bien.

Si TH supera los controles, sólo aumenta la especificidad estructural del mecanismo de borde. No implica semántica, idioma, traducción ni descifrado.