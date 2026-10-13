# H61 — Residual transition grammar after boundary ablation — result

Status: **FAIL** under the preregistered decision rule.

## Execution
- Branch: `experiment/h61-residual-transition-grammar`
- Preregistration commit: `d81ed40d90fce7295f0aba13615c9c2897e35583`
- Implementation commit: `ae90e7a4344b4e89d9e5764483bdddf932f03916`
- Workflow commit: `b47ea7a982a4f341be7fcf54095e9dd117e09f68`
- GitHub Actions run: `37614950165`
- Job: `112770932984`
- Artifact: `h61-residual-transition-grammar-results`
- Artifact ID: `11478793518`
- Artifact ZIP SHA-256: `e3977e597e9046edcf1775d0872d0a870f6a20cd99efc13f7096229618c7b808`
- Corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`

## Frozen sample recreation
H60 was recreated exactly before filtering:
- positive tokens: 780
- matched pairs: 495
- represented folios: 34
- excluded with no strict P match: 285

H61 then applied the preregistered length >=5 filter without rematching:
- retained pairs: 382
- represented folios: 33
- excluded short pairs: 113

## Boundary ablation
Each token was transformed as `token[2:-1]`, removing the first two EVA characters and the final EVA character. The predictive model saw only adjacent character transitions inside this residual body.

## Results
Observed balanced accuracy: **0.6937172774869109**.

Class-identity null (999/999):
- mean BA: `0.5009420415179573`
- median BA: `0.5013089005235603`
- Monte Carlo `p_identity = 0.001`

Sequence-order null preserving each residual body's exact character multiset (999/999):
- mean BA: `0.683722990005712`
- median BA: `0.6832460732984293`
- Monte Carlo `p_order = 0.251`
- mean fraction of residual bodies whose literal order changed during shuffle: `0.7337324235229985`

## Decision
The preregistered PASS rule required both `p_identity <= 0.05` and `p_order <= 0.05`.

The class distinction is highly reproducible relative to identity randomization, but the observed transition ordering does **not** outperform the composition-preserving order-null at the preregistered level (`p_order = 0.251`). Therefore:

**H61 = FAIL.**

## Interpretation
After removing the first two and final characters, L and P tokens remain strongly distinguishable by the fitted residual-bigram classifier. However, nearly the same discrimination remains after independently scrambling character order inside each residual body while preserving its character multiset.

The parsimonious interpretation is that this residual L-vs-P signal is driven primarily by **which characters are present / their composition**, rather than by a special internal character-transition order captured by this model.

This narrows H60 rather than overturning it: the strict L-vs-P distinction remains real, but H61 does not support the stronger claim that a residual token-internal transition grammar is responsible once major boundary positions are removed.

Language identification: **NOT_RUN**.
Semantic identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
