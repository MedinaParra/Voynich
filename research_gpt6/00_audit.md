# 00 — Auditoría independiente del repositorio Voynich

**Fecha:** 2026-10-05 (UTC)  
**Fuente fijada:** `cesarjz/Voynich`, commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`  
**Rama de auditoría:** `research/gpt6-audit`  
**Estado:** inspección del repo **PASS**; reproducciones puntuales **PASS**; reproducción integral de notebooks **BLOCKED** por dependencias ausentes; inferencias semánticas **NOT_RUN**.

## Procedencia y entorno

El repositorio fue clonado desde GitHub en la carpeta `Voynich/`. El único contenido nuevo en esta rama es `research_gpt6/`; la auditoría no modifica los notebooks, corpus ni resultados originales.

| Acción | Resultado | Estado |
|---|---|---|
| Checkout de GitHub | `git clone https://github.com/cesarjz/Voynich.git Voynich`; luego checkout de `research/gpt6-audit`; HEAD fuente `47e6a77dc9d5cd570c375f4aff710fa4a0567278` | PASS |
| Validar corpus y hashes | Scripts propios sobre `corpus/voynich_sta.txt`; SHA-256 `81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17` | PASS |
| Reproducir notebook 03 | Puerto autocontenido del parser y estimador publicado, más diagnósticos | PASS, no es ejecución integral de Jupyter |
| Reproducir notebook 74 | Puerto autocontenido de parser y conteos de f57v | PASS, no incluye cotejo paleográfico |
| Reproducir MI posicional | Puerto del cálculo y 999 permutaciones intra-palabra; semilla `20261005` | PASS |
| Ejecutar notebooks originales íntegros | No disponibles `torch`, `networkx`, `requests`, `jupyter`, `nbconvert`, `nbclient`, `nbformat`, `tqdm` | BLOCKED en este entorno |

Entorno disponible: Python 3.12.14, NumPy, pandas, SciPy, scikit-learn, matplotlib y seaborn. Los scripts y JSON de resultados están en `code/` y `results/`.

## Lo que afirma el repositorio

El README define CLAVIS CODICIS como una llave sintáctica y dice que no es un desciframiento. También propone un código categorial artificial, descarta lengua natural/cifrados clásicos y relaciona f57v con Picatrix. Esta auditoría comprueba algunas estadísticas descriptivas, pero no valida esas conclusiones. Las hipótesis semánticas y el desciframiento siguen abiertos.

## Hallazgos metodológicos reproducidos

1. La forma H0–H4 de la notebook 03 se reproduce con el código publicado. Sin embargo, su fórmula de suavizado produce masa de probabilidad menor que uno por contexto (mínimos de 0,965 a 0,974 en órdenes 1–4), por lo que no es una distribución condicional normalizada como está implementada. La notebook además imprime violaciones de monotonicidad en N=2,3,4 pese a describir una garantía. Una renormalización y una variante Witten–Bell con masa de escape distribuida cambian las cifras, pero ambas conservan un rebote en órdenes altos. La existencia de esa forma en estos diagnósticos no demuestra una gramática, idioma ni semántica.
2. La MI posición–glifo de 0,65781 bits se reproduce; permanece al excluir palabras de un glifo o darles una categoría propia. En 999 permutaciones que reordenan glifos dentro de cada palabra, ninguna alcanza la MI observada (p empírico unilateral mínimo 0,001). Esto confirma asociación con las posiciones definidas; no identifica función lingüística.
3. Los cinco símbolos candidatos X2, Xd, Xf, Pc y Ea son exclusivos de f57v en STA1 según los conteos reproducidos. El valor p publicado usa el mismo corpus para seleccionar símbolos y folio, y presupone asignaciones independientes e intercambiables; no es inferencia calibrada. No prueba la lectura de glifos en el facsímil ni la conexión con Picatrix.

## Límites

No se reprodujeron las pruebas de EVA, espectro, clustering, SilPart, comparación de idiomas/cifrados, ni validación semántica ciega. No hubo anotación independiente de facsímiles. La validez de la transcripción y la dependencia por línea, folio, sección y quire deben tratarse en pruebas futuras. Ver `10_results.md` y los informes numerados.
