# 31. Q20 — localización del bifolio perdido `109|110` como gap latente

Fecha: 2026-10-07

## Regla

No se inventa ningún texto para `109|110`. El bifolio perdido se modela como un
nodo sin observaciones. La pregunta es únicamente: **¿qué interfaz de la cadena
Q20 actual parece menos defendible como adyacencia directa y, por tanto, es la
mejor candidata para ser interrumpida por un nodo perdido?**

Orden de trabajo condicionado por el análisis Pareto previo:

`105|114 → 107|112 → 106|113 → 104|115 → 108|111 → 103|116`

## Interfaces observadas

| interfaz | bootstrap residual | score residual | dirección de borde |
|---|---:|---:|---|
| `105|114 → 107|112` | 78,5% | -0,0673 | apoya la dirección |
| `107|112 → 106|113` | 72,7% | 1,0544 | flecha estable en sentido contrario (`106→107`) |
| `106|113 → 104|115` | 45,1% | 0,7585 | apoya la dirección |
| `104|115 → 108|111` | **34,8%** | 0,1153 | **sin flecha estable entre la pareja** |
| `108|111 → 103|116` | **90,6%** | 0,4981 | apoya la dirección |

## Frente de Pareto para debilidad del gap

Cuando se consideran por separado:

1. frecuencia bootstrap baja;
2. score residual bajo;
3. ausencia/conflicto de dirección estable;

quedan dos interfaces no dominadas:

### Candidato A — `105|114 — 107|112`

Es la interfaz con menor score residual (`-0,0673`), pero esta debilidad queda
contradicha por dos evidencias:

- aparece en `78,5%` del bootstrap residual;
- `105|114 → 107|112` mantiene el mismo sentido en todas las ventanas de borde
  probadas.

Por ello no es un buen candidato físico para insertar `109|110` sólo por su
score residual puntual.

### Candidato B — `104|115 — 108|111`

Es la interfaz con:

- **menor frecuencia bootstrap de las cinco adyacencias del candidato: 34,8%**;
- score residual relativamente bajo: `0,1153`;
- **ninguna flecha direccional estable** entre `104|115` y `108|111`.

Si el gap se coloca aquí, la suma bootstrap de las cuatro adyacencias observadas
que permanecen es `2,869`, mayor que para cualquier otra posición posible.

## Hipótesis de trabajo

La colocación más informativa para intentar falsar es:

`105|114 → 107|112 → 106|113 → 104|115 → [109|110 ?] → 108|111 → 103|116`

El signo `?` es obligatorio: esto **no es una reconstrucción demostrada**.

## Qué significa y qué no significa

Sí significa:

- que `104|115—108|111` es el puente observado menos estable de la cadena;
- que no posee apoyo direccional de borde independiente;
- que la hipótesis del nodo perdido allí requiere menos ruptura de aristas
  robustas que las alternativas.

No significa:

- que sepamos qué decía `109|110`;
- que el bifolio perdido deba necesariamente conectar esos dos bloques;
- que la baja similitud sea causada por pérdida física en lugar de cambio de
  tema, mano, estilo o régimen lingüístico;
- que la posición central del bifolio en la encuadernación actual determine su
  posición en una hipotética pila original de singuliones.

## Resultado reproducible

- `results/order_q20_latent_gap.json`
- `code/order_q20_latent_gap.py`

## Próxima falsación

Buscar evidencia física independiente que discrimine específicamente entre:

1. `104|115 ↔ 109|110 ↔ 108|111`;
2. continuidad directa `104|115 ↔ 108|111`.

Los candidatos de evidencia son manchas de agua, transferencias de pigmento o
tinta, defectos de pergamino, agujeros, patrones de suciedad, secuencia de manos
y marcas de pliegue. Ninguno debe convertirse en score hasta verificar primero
que no refleja una reencuadernación posterior.