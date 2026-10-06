# Dependencia entre grupos y sus bordes: experimento ejecutado
Fecha: 6 de octubre de 2026. Estado: **EXPLORATORY_NEW_ANALYSIS_NOT_EXACT_PAPER_REPLICATION**. No es un desciframiento ni una réplica exacta del preprint sobre unidades.

## Fuente y reproducción
Corpus EVA de `cesarjz/Voynich`, commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, ruta `corpus/voynich_eva.txt`, blob Git `2a4533ab9bdfa85db9bad602d590978953055df1`. SHA-256: `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`; 411671 bytes. El código verifica el blob antes de calcular. Python 3.12.14, biblioteca estándar, ejecución terminada con código 0. Las comprobaciones de MI independiente=0, identidad binaria=1 y constante=0 pasaron durante la ejecución.

[Script](code/boundary_dependence.py) y [resultados completos](results/boundary_dependence.json). Descarga el corpus de la [revisión fijada](https://github.com/cesarjz/Voynich/blob/47e6a77dc9d5cd570c375f4aff710fa4a0567278/corpus/voynich_eva.txt) sin alterar sus bytes y ejecuta desde la raíz:

```bash
python research_gpt6/code/boundary_dependence.py --corpus corpus/voynich_eva.txt --out research_gpt6/results/boundary_dependence.json --permutations 199 --seed 20261006
```

## Método
Solo loci de párrafo P; se excluyen etiquetas. Se retienen tokens de letras minúsculas ASCII completos. Fragmentos inciertos o ilegibles rompen la adyacencia. Los huecos `<->` de ilustraciones también la rompen: no se unen palabras a través de ellos. Nunca se cruzan líneas. Se prueban comas como separador (`split`) y como unión (`join`).

MI entre tokens: vocabulario de los K=200,1000,2000 tipos más frecuentes y una clase OTHER para el resto. MI entre bordes: último carácter EVA del grupo anterior y primero del siguiente. Esos caracteres son unidades de transliteración, no letras o glifos establecidos. Se usan marginales izquierda/derecha de las transiciones para calcular MI. El exceso es MI observada menos media de 199 permutaciones Fisher–Yates independientes dentro de cada tramo limpio. El nulo conserva composición, frecuencia y longitud de los tramos; cambia orden. No es un estimador necesariamente no negativo ni una medida de significado. La normalización de borde usa entropía de extremos agrupados.

## Resultados
| Medida | Coma separadora | Coma unida |
|---|---:|---:|
| Tokens retenidos | 33935 | 31477 |
| Tipos | 6532 | 7462 |
| Pares adyacentes | 28432 | 26010 |
| Exceso MI tokens K=200, bits | 0,12233 | 0,08819 |
| Exceso MI tokens K=1000, bits | 0,11053 | 0,07592 |
| Exceso MI tokens K=2000, bits | 0,07106 | 0,04826 |
| Exceso MI bordes, bits | 0,19178 | 0,15722 |
| Exceso tokens K=2000 / entropía marginal | 0,843% | 0,584% |
| Exceso tokens K=200 / entropía marginal | 2,438% | 1,870% |
| Exceso bordes / entropía de extremos | 5,587% | 4,629% |

Ambos modos contienen 4130 loci de párrafo, 4127 líneas con tokens limpios y 207 identificadores de página. El campo JSON `folios` cuenta identificadores de transcripción, no 207 hojas codicológicas independientes. Con K=2000 la masa cubierta es 86,15%/82,01%; OTHER no representa un vocabulario completo.

En los ocho contrastes ninguna permutación alcanzó la MI observada: p Monte Carlo unilateral `(1+0)/(199+1)=0,005`; Holm para la familia de ocho: 0,04. Resolución limitada por 199 permutaciones. No justifica significación de hipótesis adicionales seleccionadas tras mirar resultados.

## Interpretación y límites
La asociación entre caracteres de borde persiste con ambas segmentaciones. El orden de tokens añade una señal pequeña frente al nulo en K=2000; decir «menos de 1%» sin indicar K sería engañoso porque K=200 supera 1%. Las métricas de borde y token usan alfabetos y entropías diferentes: no deben compararse como si midieran el mismo porcentaje de significado.

Esto orienta el trabajo hacia unidades, reglas de enlace y modelos de generación o cifrado capaces de explicar bordes. No demuestra idioma, sintaxis, ausencia de semántica ni el generador histórico. Faltan controles de lenguas y cifrados con tamaño/frecuencias emparejados, segunda transcripción, estratificación por mano/Currier/quire, incertidumbre por bloques y predicción fuera de muestra de un mecanismo fijado. Esas pruebas quedan **NOT_RUN**.

Advertencia para la auditoría previa de Dickens: cifras de cobertura calculadas con un parser que elimina `<->` sin insertar límite pueden fusionar tokens. Deben tratarse como dependientes del parser hasta repetirlas con límites conservadores; el techo combinatorio de 4107 cadenas del inventario literal no depende de ese problema. No se ha ejecutado aquí esa reevaluación de cobertura.

No se obtuvo traducción. El avance verificable es un contraste reproducible que restringe modelos aceptables y evita confundir una regularidad con una clave.
