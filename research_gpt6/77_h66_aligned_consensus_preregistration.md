# H66 — Aligned cross-transcription consensus-label test

Status: **NOT_RUN**

## Question
Does the H65 three-feature retention failure in Source B persist when both transcriptions are restricted to the **same physical label loci with identical token readings**?

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, `corpus/voynich_eva.txt`, Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, `IT2a-n.txt`, Git blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

## Frozen alignment
Parse certain single-token `L*` loci in each source and retain an event only if:
1. the full IVTFF locus identifier matches exactly between sources;
2. the cleaned EVA token matches exactly;
3. Currier and hand metadata match exactly;
4. both sources have at least one eligible strict `P*` control on the same folio, same Currier, same hand, and exact token length.

Controls are selected independently within each source using seed `20261007`. The common retained event list is fixed before classification.

Minimum valid aligned sample: **100 events across at least 8 folios**. Otherwise H66 is **BLOCKED**; the threshold must not be lowered.

## Models
Same leave-one-folio-out nearest-class-mean classifier with train-fold standardization as H60/H63/H65.

Full model:
`frac_o, frac_a, frac_y, starts_q, ends_y`

Reduced model:
`frac_o, frac_a, starts_q`

## Nulls
For each source and each model, run exactly **999** within-pair class-identity permutations with seed `20261007`.
Monte Carlo p-value is `(1 + count(null_BA >= observed_BA)) / 1000`.

## Retention
For each source:
`retention = (BA_reduced - 0.5) / (BA_full - 0.5)`.
If full-model BA <= 0.5 the experiment is **BLOCKED** for that source.

## PASS criterion
H66 is **PASS** iff:
- aligned sample >=100 events and >=8 folios;
- all four permutation sets complete 999/999;
- full and reduced models have BA>0.5 and p<=0.05 in both sources;
- reduced-model retention is >=0.80 in both sources.

A valid execution missing any PASS condition is **FAIL**.

## Interpretation
PASS would support the hypothesis that H65's source-B loss was largely caused by differences in effective label sample and/or transcription disagreement. FAIL with strong full-model replication would instead support the need for additional multivariate information beyond the three H64 components, even on identical physical label loci with agreed readings.

No semantic, language, plaintext, cipher, translation or decipherment claim is tested.
