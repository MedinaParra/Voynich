# 31. Programa holístico de desciframiento multimodal

Fecha: 2026-10-06

## Objetivo

Intentar recuperar contenido del Voynich combinando evidencia física, codicológica, visual, textual e histórica sin convertir semejanzas subjetivas en traducciones.

## Evidencia que se integrará

1. Orden físico: bifolios, quires, singuliones y folios faltantes.
2. Texto: EVA/ZL congelado, morfología latente, dependencia direccional, Currier, mano y posición.
3. Imagen: plantas y partes, estrellas/zodiaco, figuras humanas, baños/conductos, recipientes, raíces y diagramas.
4. Microtexto: labels próximos a objetos, escritura no-Voynich, letras bajo pintura y anotaciones marginales.
5. Historia visual: Pseudo-Apuleius, Tractatus de Herbis, herbarios alquímicos, balneología medieval, diagramas astronómicos/astrológicos y farmacopeas.
6. Materialidad: pigmentos/tintas y estratigrafía cuando los datos publicados lo permitan.

## Hallazgos guía ya documentados externamente

- Las ilustraciones dividen el códice en dominios herbal, astronómico/astrológico, balneológico, cosmológico, farmacéutico y texto posiblemente de recetas.
- En f1v se ha observado una letra latina `g` bajo pintura.
- En f4r se han descrito caracteres latinos verticales interpretables como `rot`, alemán para rojo; esto es una hipótesis paleográfica a verificar sobre imagen de alta resolución.
- En f32r se describen dos caracteres dentro de una flor.
- Algunas ilustraciones farmacéuticas parecen reutilizar plantas del propio herbal.
- Se han propuesto paralelos iconográficos con Pseudo-Apuleius, Tractatus de Herbis y herbarios alquímicos.

Estos puntos son pistas, no traducciones.

## Experimentos prioritarios

### E1 — Microtexto y capas gráficas

Revisar sistemáticamente imágenes de alta resolución para localizar escritura latina/no-Voynich, glifos bajo pintura, correcciones, rótulos, marcas de color y diferencias de tinta. Separar mano original de anotaciones posteriores cuando sea posible.

### E2 — Label ↔ objeto

Extraer rótulos cercanos a estrellas, raíces, hojas, flores, figuras humanas, recipientes y elementos de diagramas. Medir si familias EVA predicen clases de objetos en holdout por folio/quire.

### E3 — Plantas por partes, no por parecido global

Codificar raíz, tallo, ramificación, hoja, nervadura, flor, fruto y hábito. Comparar esas partes contra herbarios históricos; evitar identificación por una sola semejanza.

### E4 — Reutilización interna

Buscar partes de plantas repetidas entre sección herbal y farmacéutica. Si una figura reutilizada conserva una familia textual/label, tratarla como candidato de anclaje semántico interno.

### E5 — Iconografía histórica ciega

Para cada folio, recuperar candidatos de manuscritos medievales sin usar primero las identificaciones Voynich publicadas. Sólo después comparar con literatura previa. Registrar top-k, rasgos compartidos y falsificadores.

### E6 — Texto condicionado por imagen

Dentro de Currier + mano + sección, modelar P(rasgo_visual | morfema/token). Exigir generalización a folios no vistos y controles de permutación.

### E7 — Hipótesis semánticas

Sólo elevar un token/morfema a candidato semántico si converge evidencia de al menos tres fuentes independientes: distribución textual, objeto/imagen y paralelo histórico; preferentemente también posición sintáctica o reutilización interna.

## Escala de afirmaciones

A0: asociación visual.
A1: asociación funcional (p.ej. término relacionado con raíz).
A2: campo semántico probable (p.ej. parte vegetal / preparación / cantidad).
A3: glosa candidata concreta.
A4: traducción local que predice texto no usado en su construcción.
A5: desciframiento reproducible de pasajes nuevos.

No se llamará traducción a niveles A0–A3.

## Controles adversariales

- permutar labels entre objetos de la misma sección;
- controlar Currier, mano, quire y longitud;
- comparar similitud de imágenes contra herbarios no relacionados;
- usar múltiples transcripciones;
- holdout por folio y por quire;
- penalizar hipótesis que requieren muchas excepciones;
- probar lectura inversa y segmentaciones alternativas;
- registrar hipótesis antes de consultar identificaciones históricas cuando sea viable.

## Criterio de avance hacia `qué dice`

El primer avance semántico serio será una familia EVA que alcance A2 o superior y prediga correctamente objetos/contextos en folios no usados para descubrirla. El primer avance de traducción será A4: una glosa/composición que permita anticipar contenido de un pasaje retenido.

## Estado al congelar

- Programa holístico: PASS (diseñado y congelado).
- Corpus textual fijado: PASS.
- Fuentes de imágenes de alta resolución identificadas: PASS.
- Revisión histórica inicial de iconografía: PASS.
- OCR/visión sistemática de todos los folios: NOT_RUN.
- Benchmark histórico automatizado: NOT_RUN.
- Anclaje semántico A2+: NOT_RUN.
- Traducción A4+: NOT_RUN.
