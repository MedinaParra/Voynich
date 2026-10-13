# H65 — Minimal replicated three-feature L-vs-P model

Status: **NOT_RUN**

## Question
Can the independently replicated L-vs-P separation be reduced to the three H64 components that survived familywise correction in both transcriptions: `frac_o`, `frac_a`, and `starts_q`?

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, `corpus/voynich_eva.txt`, Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, `IT2a-n.txt`, Git blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

## Frozen sample reconstruction
For each source, reconstruct the strict H60/H63 sample independently:
- positives: certain single-token `L*` loci;
- controls: only generic `P*` loci;
- exact matching on folio, Currier, hand, and token length;
- deterministic control selection with seed `20261007`.

Expected reconstruction:
- Source A: 780 positive tokens, 495 matched pairs, 34 represented folios, 285 unmatched positives.
- Source B: 669 positive tokens, 388 matched pairs, 32 represented folios, 281 unmatched positives.
Any mismatch => **BLOCKED**.

## Models
Use the same leave-one-folio-out nearest-class-mean classifier and train-fold standardization used in H60/H63.

Full model predictors, descriptive comparator only:
1. `frac_o`
2. `frac_a`
3. `frac_y`
4. `starts_q`
5. `ends_y`

Reduced confirmatory model predictors:
1. `frac_o`
2. `frac_a`
3. `starts_q`

No absolute token length or metadata predictor is allowed.

## Null
For the reduced model only, run exactly **999** within-pair class-identity permutations independently in each source, seed `20261007`.
Monte Carlo p-value: `(1 + count(null_BA >= observed_BA)) / 1000`.

## Signal-retention metric
For each source:
`retention = (BA_reduced - 0.5) / (BA_full - 0.5)`.
If `BA_full <= 0.5`, the experiment is **BLOCKED** for that source.

## PASS criterion
H65 is **PASS** iff, in **both** sources:
1. exact frozen reconstruction succeeds;
2. 999/999 reduced-model permutations complete;
3. `BA_reduced > 0.5`;
4. reduced-model Monte Carlo `p <= 0.05`;
5. `retention >= 0.80`.

Otherwise a valid execution is **FAIL**. Infrastructure/data mismatch is **BLOCKED**.

## Interpretation boundary
PASS would support that the replicated L-vs-P token-form distinction is largely captured by the compact three-component signature `{more o, more a, less q-initial}`. It would not establish semantics, label identity, language, plaintext, cipher mechanism, translation, or decipherment.
