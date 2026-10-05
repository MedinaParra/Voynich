# 10 — Resultados actuales

## Resumen

La auditoría está fijada al commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278` de GitHub y al SHA-256 de STA1 `81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17`. Se añadieron tres scripts autocontenidos y JSON con sus salidas. Las reproducciones de conteos, H0–H4, MI posicional y conteos f57v terminaron con exit code 0. Los notebooks completos no pudieron correrse: el entorno no tiene torch, networkx, requests ni Jupyter/nbconvert y otros módulos.

### PASS

- El parser STA1 reproduce 157,254 glifos, 37,087 palabras y vocabulario de 166.
- H0–H4 publicados se reproducen desde los conteos con el parser señalado.
- MI glifo–posición = 0.657811 bits y es grande frente al nulo de 999 permutaciones intra-palabra (p empírico = 0.001).
- Predicción fuera de muestra por pliegues de folios: unigramas 4.1488, clase posicional 3.4981 y mejor n-grama (orden 2) 3.0051 bits/glifo; ganancia de orden 2 frente a unigramas 1.1437 bits/glifo (IC bootstrap por folio 95%: 1.1030–1.1826). Reproducible con `code/heldout_prediction.py`.
- Control más estricto, dejando fuera un quire completo cada vez (18 grupos `$Q`): unigramas 4.1607 vs. orden 2 en 3.0374 bits/glifo; ganancia 1.1233 (IC bootstrap por quire 95%: 0.9351–1.2147). Tasa de glifos no vistos en el entrenamiento: 0.062%. Reproducible con `code/leave_one_quire_out.py`.
- Auditoría de la búsqueda zodiacal de anclas: los tres p guardados son 0.6103, 0.8066 y 0.7713 (ninguno significativo); la celda posterior que imprime «percentile=0.1%» tiene un error aritmético que fuerza ese valor siempre que alguna permutación quede bajo el resultado observado. Ver `results/zodiac_crib_audit.json`; se auditaron outputs guardados, no se reejecutó la descarga del corpus hebreo.
- Los cinco símbolos candidatos se mantienen exclusivos de f57v en STA1 bajo parser general que incluye `fRos`.

### FAIL metodológico

La hipótesis de que la implementación de suavizado de notebook 03 proporciona una distribución condicional normalizada y garantiza H_N ≤ H_(N−1) **falla**: la masa por contexto es menor que uno, y la propia notebook informa violaciones para N=2,3,4. La curva numérica se reproduce, pero su interpretación debe reevaluarse. Dos alternativas normalizadas conservan la forma de rebote en este conjunto; eso no acredita su explicación teórica.

El percentil de bigramas de notebook 28 también **falla** por el denominador aplicado después de `mean()` sobre una lista de unos. El valor impreso de 0.1% no es interpretable como percentil.

### BLOCKED / NOT_RUN

- **BLOCKED:** ejecución íntegra de notebooks por dependencias no instaladas; no se intentó modificar o instalar dependencias en el entorno.
- **NOT_RUN:** otras transcripciones, glifos dudosos e imágenes; métricas espectrales/cluster/idioma/cifrado; SilPart; la gramática de cinco slots; semántica y validación ciega; hipótesis Elu-Sinhala; asociación de glifos f57v con diagramas/Picatrix.
- **NOT_RUN:** rerun independiente de la comparación con Torá y prueba de anclas zodiacales en glifos reservados; la auditoría actual inspecciona solo código y outputs guardados.

## Lectura provisional

**Sobrevive:** regularidad posicional y predictibilidad de secuencia que generalizan a folios y quires reservados en STA1, junto con concentración muy fuerte de cinco glifos en f57v, como descripciones del dataset.
**Refutado en su forma implementada:** normalización y garantía de monotonicidad del estimador H condicional de notebook 03.
**No resuelto:** origen lingüístico/codificado, significado, cinco categorías semánticas, cifrado, generador SilPart y desciframientos competidores. La capacidad predictiva de glifos no equivale a recuperar el texto; los datos aquí no autorizan una traducción.

## Reproducción

Desde la raíz del checkout, con Python 3.12.14 y NumPy instalado:

```bash
python research_gpt6/code/reproduce_core.py
python research_gpt6/code/reproduce_position.py
python research_gpt6/code/reproduce_f57v.py
python research_gpt6/code/heldout_prediction.py --corpus /ruta/a/Voynich/corpus/voynich_sta.txt
```

Los resultados completos están en `results/`; el resumen de código y dependencias está en `code/README.md`.
