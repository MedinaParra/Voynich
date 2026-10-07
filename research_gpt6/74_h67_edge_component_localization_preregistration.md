# H67 — Exact-consensus edge-component localization preregistration

Status: **NOT_RUN**.

## Motivation
H66 passed on the strict exact-consensus subset using only two previously frozen edge indicators: `starts_q` and `ends_y`. H67 is an explicitly adaptive mechanism-localization test. It asks whether the H66 signal is attributable to either frozen edge indicator individually, or whether the two-feature combination is required.

This is not a new semantic hypothesis and cannot rescue or overturn H65.

## Frozen data construction
Use exactly the H66 sources and exact-consensus construction:
- IVTFF blob `2a4533ab9bdfa85db9bad602d590978953055df1`;
- Takahashi blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`;
- exact locus agreement and metadata agreement;
- same-folio, same Currier, same hand, exact-token-length running-text matching;
- deterministic control sampling seed `20261007`;
- same quire eligibility rule: >=10 pairs per held-out quire;
- require >=4 evaluable quires and >=80 evaluable pairs.

No new glyph feature, feature search, fuzzy matching, threshold tuning, or manual relabeling is permitted.

## Frozen component tests
Run two independent one-feature leave-one-quire-out classifiers using the same nearest-class-mean pipeline as H66:

- **H67-Q:** predictor = `starts_q` only.
- **H67-Y:** predictor = `ends_y` only.

Training standardization is fit on training quires only. Primary statistic for each component is aggregate balanced accuracy over all held-out predictions. Report per-quire BA and count of quires above 0.5.

## Multiple-testing control
Each component receives exactly 999 within-pair label-swap permutations, refitting the full leave-one-quire-out pipeline.

To control the two-test family, a component is called positive only if:
1. BA > 0.55;
2. Monte Carlo p <= **0.005**;
3. >=3 evaluable quires individually have BA > 0.5;
4. 999/999 permutations complete.

The p<=0.005 threshold is frozen before H67 results and is the Bonferroni allocation of familywise alpha 0.01 across the two component tests.

## Frozen experiment-level classification
- **PASS_Q_LOCALIZED** if H67-Q is positive and H67-Y is not.
- **PASS_Y_LOCALIZED** if H67-Y is positive and H67-Q is not.
- **PASS_BOTH_EDGES** if both components are positive.
- **PASS_COMBINATION_REQUIRED** if neither component is positive while H66 remains PASS; this means the pre-existing two-feature combination carries evidence that neither single component meets the confirmatory component gate.
- **BLOCKED** if support requirements fail.

No post-hoc alternative edge glyphs will be tested under H67.

## Interpretation ceiling
H67 can localize the H66 functional-register effect to `q`-initial behavior, `y`-final behavior, both, or their combination under the strict exact-consensus subset. It cannot establish lexical semantics, depicted-object identity, language, cipher, plaintext, glosses, translation, or decipherment.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
