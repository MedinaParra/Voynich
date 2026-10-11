# H100 — global folio-transition generator result

Status: **FAIL**

## Execution evidence
- Workflow run: `38148689530`
- Job: `114497357782`
- Workflow infrastructure: **PASS**
- Head branch at trigger: `experiment/h58-strict-l-vs-p`
- Head SHA: `7931750bda196280e13f7aaf85d3188ac5201e14`
- GitHub PR merge commit executed by Actions: `7339d01c84984356b9ac47acd5c51ddc21433c9e`
- Artifact: `11706078909` (`h100-global-folio-transition`)
- Artifact ZIP SHA-256: `841846bb15bf6dc75cf5b41f0c958555dc637426bdaf77be2336018cfeb24314`

## Frozen identity and controls
All mandatory controls reported **PASS**:
- source SHA
- partition hash
- inherited order identity
- holdout-fit firewall
- cluster occupancy
- development-adjacency-only transition estimation
- transition matrix
- exact token-count preservation
- degeneracy
- determinism

Eligible folios: 200 (160 development / 40 holdout).
Development-only adjacent transitions: 125.
Cluster occupancies: `[24, 53, 32, 51]`.
Replicas: 999.
Empty-token fraction: 0.0.

## Primary result
H100 preregistered criterion: **PASS iff 8/8 endpoints pass**.
Observed: **5/8**.
Therefore H100 = **FAIL**.

Endpoint pass mask in frozen order:
`[PASS, PASS, FAIL, PASS, FAIL, PASS, PASS, FAIL]`

The three failures are the same endpoint classes that remained problematic in H97:

1. Token type/token ratio
   - real: `0.33091311838542947`
   - synthetic 99% interval: `[0.25227172040364265, 0.32131553039625893]`

2. Character bigram conditional entropy H(C_t|C_{t-1})
   - real: `2.1006612513623275`
   - synthetic 99% interval: `[2.1110221179234703, 2.2042523594055043]`

3. Median consecutive-folio character-unigram JSD
   - real: `0.04390201931367363`
   - synthetic 99% interval: `[0.011005151634345029, 0.020065102195779373]`
   - synthetic median: `0.014500158831180648`

For comparison, H97's consecutive-folio JSD 99% interval was approximately `[0.0118773, 0.0204252]`. H100 therefore did not materially close the dominant between-folio heterogeneity gap despite adding a development-only global latent-state transition matrix.

Transition counts:
`[[3,6,2,4],[8,21,5,7],[5,7,10,6],[2,12,8,19]]`

Synthetic state-switch-rate median: `0.5897435897435898`.

## Conservative interpretation
A single global first-order transition process over the four H97 latent folio states is insufficient to reproduce the frozen eight-dimensional holdout signature. In particular, it leaves the real consecutive-folio divergence more than twice the upper end of the synthetic 99% interval.

This rejects the exact H100 generator. It does **not** establish a language, cipher key, scribe model, semantic section model, physical folio order, translation, or decipherment.

H100 = **FAIL**.
Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.
