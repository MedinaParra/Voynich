# H71 — Exact-prefix paragraph-baseline residual result

Status: **PASS**

## Frozen execution
- Run: `37645162166`
- Job: `112873911655`
- Head commit: `3354ee79689f12a26902ae25e9caa2cee46538ce`
- Artifact: `11493049456` (`h71-prefix-baseline-residual-results`)
- Artifact SHA-256: `86f0e163c93cd2f609a85eb302ce0375e63db97c6b2b0abbb15cd29c5385de2f`
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Sample
- Aligned exact-prefix events: **122**
- Represented folios: **27**
- Preregistered minimum: >=100 events and >=15 folios — met.

## Source A
- Compatible strict-P occurrences contributing to baselines: **493**
- Equal-folio-weighted mean residual internal EVA `a`: **0.06236996482422819**
- Event-weighted mean residual: **0.071905921699259**
- Null mean: **-0.0008823060100438064**
- One-sided Monte Carlo p: **0.015**
- Permutations: **999/999**

Prefix descriptives with >=5 events:
- `ch`: n=17, mean residual +0.0616608366
- `da`: n=7, +0.1000000000
- `ok`: n=24, +0.0325178872
- `ol`: n=10, +0.0650231481
- `ot`: n=37, +0.0851351351
- `qo`: n=6, -0.0788398693

## Source B
- Compatible strict-P occurrences contributing to baselines: **502**
- Equal-folio-weighted mean residual internal EVA `a`: **0.06208074275975512**
- Event-weighted mean residual: **0.07250493321190042**
- Null mean: **-0.000879467166618516**
- One-sided Monte Carlo p: **0.020**
- Permutations: **999/999**

Prefix descriptives with >=5 events:
- `ch`: n=17, mean residual +0.0659239453
- `da`: n=7, +0.1000000000
- `ok`: n=24, +0.0327020202
- `ol`: n=10, +0.0755787037
- `ot`: n=37, +0.0819819820
- `qo`: n=6, -0.0776234568

## Interpretation
H71 supports a replicated excess of internal EVA `a` in `L*` labels relative to strict paragraph-text (`P*`) baselines after conditioning on folio, Currier/hand, exact token length and exact first two EVA characters. The effect is evaluated at the folio level to reduce within-page pseudoreplication.

The prefix descriptives suggest heterogeneity (`qo` is negative while several other families are positive), but these family-level values were descriptive and are not independent confirmatory discoveries.

This result does **not** identify a morpheme, phonetic value, semantics, language, plaintext, cipher mechanism, translation or decipherment. Those remain **NOT_RUN**.
