# 30. Protocolo multimodal: imagen + texto + iconografía histórica

Fecha: 2026-10-06

## Objetivo

Probar si las ilustraciones de MS 408 permiten inferir contenido probable y, de manera independiente, anclar familias textuales EVA a clases visuales o históricas. No asumir traducciones.

## Corrección terminológica

No usar OCR convencional para interpretar dibujos. El OCR se reserva para glifos, rótulos, notas marginales y texto. Para ilustraciones usar visión computacional/iconografía: segmentación, detección de objetos, embeddings visuales, geometría y comparación con manuscritos históricos.

## Fuentes primarias

1. Imágenes de alta resolución de Yale/Beinecke MS 408, preferentemente IIIF.
2. Transcripción IVTFF/EVA congelada ya usada por el proyecto.
3. Cuando estén disponibles, imágenes multiespectrales para comprobar trazos, correcciones y capas.

## Taxonomía visual ciega

Etiquetar sin mirar el texto EVA:

- botánica: raíz, rizoma/bulbo, tallo, hoja, flor, fruto/semilla, hábito de crecimiento, simetría, número de lóbulos, color;
- recipientes/farmacéutica: forma, cuello, pie, tapa, asas, repetición de módulos;
- balneología/anatomía: figura humana, sexo aparente si es iconográficamente codificable, piscina, tubo/conducto, recipiente, flujo/conexión, posición corporal;
- astronomía/astrología: signo zodiacal, estrella, número de figuras, anillos, orientación, cardinalidad;
- cosmología: rosetas, conexiones, murallas/torres, cauces/caminos, cardinalidades y simetrías;
- layout: ubicación de texto, labels, párrafos, relación espacial label-objeto.

Toda etiqueta debe incluir confianza y evidencia visual. No convertir una semejanza en identificación botánica.

## Comparadores históricos prioritarios

- herbarios Pseudo-Apuleius y tradiciones herbales medievales mediterráneas/centroeuropeas;
- Tacuinum Sanitatis y manuscritos médicos/fitoterapéuticos;
- De Balneis Puteolanis y tradición de baños medicinales;
- ciclos zodiacales tardomedievales y paranatellonta;
- manuscritos farmacéuticos/apotecarios con raíces y recipientes;
- diagramas cosmológicos y meteorológicos del siglo XIV-XV.

Comparar composición y motivos, no solo parecido global de imagen.

## Experimentos

### E1 — clasificación visual ciega

Entrenar/evaluar representaciones visuales para recuperar sección mediante holdout por quire. Controlar fondo de pergamino, densidad de tinta y layout para impedir atajos.

### E2 — correspondencia imagen-texto

Para cada rasgo visual binario/multiclase calcular asociación con tokens, prefijos, sufijos y n-gramas EVA. Validación leave-one-quire-out y dentro de Currier/mano cuando haya tamaño suficiente.

### E3 — labels cercanos a objetos

Detectar texto corto espacialmente asociado a una planta, estrella, figura, recipiente o componente. Comparar recurrencia del mismo label/familia cuando reaparece el mismo motivo visual. Este es el brazo con mayor potencial para anclaje léxico.

### E4 — recuperación histórica

Construir embeddings/rasgos iconográficos de cada objeto Voynich y recuperar candidatos en comparadores históricos. Exigir coincidencia en varios atributos (morfología, composición, cardinalidad, relación espacial), no similitud CLIP aislada.

### E5 — prueba semántica conjunta

Un candidato `morfema -> concepto` solo asciende si cumple simultáneamente:
1. asociación imagen-texto significativa fuera de muestra;
2. estabilidad entre folios independientes;
3. no explicable por Currier/mano/quire;
4. coherencia posicional/morfológica del morfema;
5. apoyo iconográfico histórico independiente.

## Controles adversariales

- permutar imágenes entre páginas dentro de sección;
- permutar labels dentro de página;
- igualar densidad/layout;
- comparar contra rasgos visuales irrelevantes;
- separar train/test por quire y, cuando sea posible, por mano;
- corregir comparaciones múltiples;
- probar varias transcripciones si una asociación depende de glifos ambiguos.

## Criterio de resultado

`PASS_SEMANTIC_ANCHOR` únicamente si un concepto o clase funcional sobrevive E2/E3, holdout y controles, y tiene soporte histórico independiente. Una planta visualmente parecida o una correlación en el mismo folio no constituye traducción.

## Estado inicial

- Digitalización completa de alta resolución disponible: PASS.
- Existencia de secciones visuales botánica, astronómica/astrológica, balneológica, cosmológica, farmacéutica y recetas: PASS.
- Estudios previos de visión computacional/iconografía: PASS; por tanto la vía visual no es inédita en sí misma.
- Análisis multimodal reproducible del proyecto con los controles anteriores: NOT_RUN.
- Traducción derivada de imágenes: NOT_RUN.

## Prioridad inmediata

Comenzar por E3: labels cortos ligados espacialmente a objetos en páginas zodiacales, farmacéuticas y herbales. Los labels ofrecen una relación texto-objeto mucho menos ambigua que los párrafos largos. Después cruzar esos candidatos con E2 y comparadores históricos.