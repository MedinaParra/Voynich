# Resultado 30 — Reconstrucción ciega de bifolios y controles adversariales

Fecha: 2026-10-07

## Pregunta

¿La señal textual observada en los bifolios físicos sirve para **predecir** qué folios pertenecen a la misma hoja física cuando se oculta `$B`, y sobrevive a controles por distancia, mano de Davis, Currier y transcripción?

Esto no prueba significado, traducción ni orden de lectura. La variable objetivo es exclusivamente **pertenencia al mismo bifolio físico**.

## Conjunto predictivo hold-out

Se excluyen Q13 (`Q=M`) y Q20 (`Q=T`) porque motivaron la regla. Para la prueba predictiva también se excluye `Q=B` por contener un grupo físico incompleto que haría depender la selección del conjunto de `$B`.

Hold-out completo: **A, C, D, E, F, G** = 6 quires × 4 bifolios = **24 bifolios físicos**.

Regla predictiva congelada inicial:

1. agregar texto del recto y verso de cada folio;
2. TF–IDF;
3. similitud coseno entre todos los pares candidatos;
4. centrar por distancia absoluta entre números de folio;
5. elegir el *maximum-weight perfect matching*;
6. revelar `$B` sólo al final para puntuar.

## Reconstrucción ciega

### ZL3b

- Recuperados: **14/24 = 58,3%**.
- Esperado bajo emparejamiento aleatorio: **3,43/24**.
- Null conjunto exacto: `1,340,095,640,625` combinaciones.
- `p = 2.68949e-5`.

### Takahashi IT2a — transcripción independiente

Misma regla, sin retuning.

- Recuperados: **16/24 = 66,7%**.
- Esperado aleatorio: **3,43/24**.
- `p = 1.52275e-6`.

La capacidad reconstructiva no es un artefacto exclusivo de la transcripción ZL3b.

## Control exacto condicionado por mano y Currier

Se mantiene fija la predicción textual y se randomiza la arquitectura física **sólo** entre perfect matchings que preservan exactamente el mismo patrón observado de pares `misma/diferente mano de Davis × mismo/diferente Currier`.

### ZL3b

- Observado: **14/24**.
- Esperado bajo null condicionado: **8,343/24**.
- `p exacto = 0.0182106`.

### Takahashi IT2a

- Observado: **16/24**.
- Mismo esperado condicionado: **8,343/24**.
- `p exacto = 0.00246979`.

Conclusión: mano/Currier explica una fracción grande del éxito bruto, pero no toda la capacidad reconstructiva.

## Control doble: residualizar distancia + metadatos antes de predecir

Control más agresivo. Sobre cada arista candidata se elimina aditivamente:

1. efecto de distancia absoluta entre folios;
2. efecto de la categoría exacta del par de firmas de mano de Davis + Currier.

El maximum-weight perfect matching se obtiene **sólo con los residuos**. `$B` continúa oculto hasta evaluar.

### ZL3b

- Recuperados: **10/24 = 41,7%**.
- Null ordinario: `p = 0.0035942`.
- Null condicionado por mano/Currier: esperado **3,276**, `p = 0.00132193`.

### Takahashi IT2a

- Recuperados: **8/24 = 33,3%**.
- Null ordinario: `p = 0.0262982`.
- Null condicionado: esperado **2,943**, `p = 0.00673419`.

La señal residual sobrevive en ambas transcripciones, aunque con menor exactitud, como cabe esperar tras retirar información predictiva real.

## Leave-one-quire-out — prueba de influencia

Se repite la inferencia exacta omitiendo un quire completo cada vez, sin cambiar la regla.

### Predictor inicial, null condicionado por mano/Currier

| Omitido | ZL3b p | IT2a p |
|---|---:|---:|
| ninguno | 0.01821 | 0.00247 |
| A | 0.05050 | 0.00768 |
| **C** | **0.20466** | **0.05050** |
| D | 0.00657 | 0.000557 |
| E | 0.01551 | 0.01551 |
| F | 0.04219 | 0.00622 |
| G | 0.00657 | 0.000557 |

### Predictor doble-residual, null condicionado

| Omitido | ZL3b p | IT2a p |
|---|---:|---:|
| ninguno | 0.001322 | 0.006734 |
| A | 0.00407 | 0.02198 |
| **C** | **0.05283** | **0.20182** |
| D | 0.00197 | 0.01013 |
| E | 0.00135 | 0.00717 |
| F | 0.00360 | 0.00360 |
| G | 0.000456 | 0.00266 |

### Lectura crítica

El **quire C es un punto influyente**. Bajo el control más agresivo, eliminar C lleva el resultado fuera de `p < 0.05` en ambas transcripciones. Por tanto, no es defendible afirmar que la reconstrucción residual fuerte sea homogénea en todos los quires.

Esto no elimina el hallazgo más general:

- el análisis inferencial previo mostró efecto ajustado positivo en **7/7** quires elegibles A–G (`p_signo = 0.0078125`);
- Q13 y Q20 replicaron independientemente el pairing físico;
- la reconstrucción ciega supera ampliamente el azar en ambas transcripciones;
- la señal predictiva residual existe globalmente, pero **su magnitud está concentrada y C contribuye de manera desproporcionada**.

## Conclusión defendible

### Fuerte

> Las estadísticas textuales del Voynich contienen información reproducible sobre la pertenencia de folios al mismo bifolio físico. Esa información permite reconstrucción por encima del azar en datos no usados para seleccionar la regla y replica en dos transcripciones.

### Moderada

> Parte de la capacidad reconstructiva permanece después de controlar distancia, mano de Davis y Currier.

### Todavía no demostrada

> Que esa información residual sea uniforme en todo el manuscrito o independiente de cualquier covariable de producción no observada.

### Refutada por nuestro propio experimento

> Que estas métricas recuperen un orden inter-bifolios único: el test Q13 de orden exacto falló.

## Siguiente falsación

El siguiente objetivo no debe ser optimizar más el predictor sobre A–G. Eso produciría *researcher degrees of freedom*. Hay que tratar el quire C como un caso influyente y buscar una explicación externa o una réplica verdaderamente independiente:

1. descomponer qué rasgos concretos hacen C perfectamente reconstruible;
2. probar controles visuales/temáticos y de distribución de ilustraciones sin ajustar el predictor al resultado;
3. buscar quires completos adicionales o reconstrucciones físicas publicadas que no estén codificadas en el conjunto usado;
4. si no hay otra muestra independiente, formular el resultado como **evidencia de acoplamiento textual con la arquitectura física**, no como método universal de reconstrucción.

## Posicionamiento científico

La similitud dentro de bifolios tiene precedentes en Torsten Timm / BAAFU y es compatible con la discusión de singuliones de Layfield–Davis. La novedad potencial de esta rama no es “descubrir que los bifolios se parecen”, sino el paquete metodológico:

- null exacto de perfect matchings;
- control de distancia;
- Q13 → Q20;
- hold-out automático;
- reconstrucción ciega;
- réplica en transcripción independiente;
- randomización exacta condicionada por mano/Currier;
- residualización adversarial;
- auditoría leave-one-quire-out que identifica explícitamente la dependencia del quire C.

Ese conjunto ya es suficiente para plantear un paper metodológico serio, siempre que el manuscrito se redacte con la limitación de influencia de C en primer plano y sin reclamar desciframiento.
