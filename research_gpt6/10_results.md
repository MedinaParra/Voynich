# 10 — Resultados actuales

## Resumen

La auditoría está fijada al commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278` de GitHub y al SHA-256 de STA1 `81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17`. Se añadieron tres scripts autocontenidos y JSON con sus salidas. Las reproducciones de conteos, H0–H4, MI posicional y conteos f57v terminaron con exit code 0. Los notebooks completos no pudieron correrse: el entorno no tiene torch, networkx, requests ni Jupyter/nbconvert y otros módulos.

### PASS

- El parser STA1 reproduce 157,254 glifos, 37,087 palabras y vocabulario de 166.
- H0–H4 publicados se reproducen desde los conteos con el parser señalado.
- MI glifo–posición = 0.657811 bits y es grande frente al nulo de 999 permutaciones intra-palabra (p empírico = 0.001).
- Los cinco símbolos candidatos se mantienen exclusivos de f57v en STA1 bajo parser general que incluye `fRos`.

### FAIL metodológico

La hipótesis de que la implementación de suavizado de notebook 03 proporciona una distribución condicional normalizada y garantiza H_N ≤ H_(N−1) **falla**: la masa por contexto es menor que uno, y la propia notebook informa violaciones para N=2,3,4. La curva numérica se reproduce, pero su interpretación debe reevaluarse. Dos alternativas normalizadas conservan la forma de rebote en este conjunto; eso no acredita su explicación teórica.

### BLOCKED / NOT_RUN

- **BLOCKED:** ejecución íntegra de notebooks por dependencias no instaladas; no se intentó modificar o instalar dependencias en el entorno.
- **NOT_RUN:** otras transcripciones, glifos dudosos e imágenes; métricas espectrales/cluster/idioma/cifrado; SilPart; la gramática de cinco slots; semántica y validación ciega; hipótesis Elu-Sinhala; asociación de glifos f57v con diagramas/Picatrix.

## Lectura provisional

**Sobrevive:** regularidad posicional en STA1 y concentración muy fuerte de cinco glifos en f57v, como descripciones del dataset.  
**Refutado en su forma implementada:** normalización y garantía de monotonicidad del estimador H condicional de notebook 03.  
**No resuelto:** origen lingüístico/codificado, significado, cinco categorías, cifrado, generador SilPart y desciframientos competidores. Los datos aquí no autorizan una traducción.

## Reproducción

Desde la raíz del checkout, con Python 3.12.14 y NumPy instalado:

```bash
python research_gpt6/code/reproduce_core.py
python research_gpt6/code/reproduce_position.py
python research_gpt6/code/reproduce_f57v.py
```

Los resultados completos están en `results/`; el resumen de código y dependencias está en `code/README.md`.
