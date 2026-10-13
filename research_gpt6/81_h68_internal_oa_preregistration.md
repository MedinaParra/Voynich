# H68 — Internal o/a enrichment after boundary ablation

Status: **NOT_RUN**

## Question
After removing the first two and final EVA characters of each token, do labels still show replicated enrichment of `o` and/or `a` relative to exact-matched strict paragraph controls?

This directly tests whether the H64/H66 `o/a` signal is merely a boundary phenomenon (`ok`, `ot`, etc.) or persists inside the residual token body.

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

## Sample
Recreate the H66 exact-agreement label-locus set and independently selected strict-P controls in each source:
- identical full IVTFF label locus and label token between sources;
- identical Currier/hand metadata;
- control from same folio, Currier, hand and exact original token length;
- deterministic control selection with seed `20261007`.

Retain only pairs where both label and control original token lengths are >=5. Residual body is exactly `token[2:-1]`.

Minimum valid sample: **100 pairs across >=8 folios** in the common aligned event list. Otherwise H68 is **BLOCKED**.

## Frozen confirmatory features
For each residual body:
1. `residual_frac_o`
2. `residual_frac_a`

Pair effect = label fraction minus matched-P fraction.

## Null and multiplicity
For each source independently, run exactly **999** within-pair label/control identity swaps, seed `20261007`.
For each permutation compute the absolute studentized effect for both features; use the permutation maximum across the two features to obtain max-stat familywise p-values.

## Replicated component criterion
A feature is replicated iff:
- its observed mean difference has the same positive direction (`L>P`) in both sources;
- `p_FWER <= 0.05` in Source A;
- `p_FWER <= 0.05` in Source B.

## PASS criterion
H68 is **PASS** iff at least one of the two preregistered residual features replicates. If neither replicates in a valid execution, H68 is **FAIL**.

## Interpretation boundary
PASS would show that at least part of the label-vs-paragraph compositional signature persists away from token boundaries and therefore cannot be reduced solely to initial/final glyph conventions. It would not establish semantics, language, plaintext, cipher mechanism, translation or decipherment.
