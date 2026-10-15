# H94 initial-glyph → visual-object anchor — preregistration

## Status

**PASS** (preregistration only). Execution: **NOT_RUN**.

## Rationale

H92 and H93 falsified two continuous lexical endpoints (label length and whole-string edit similarity) in the frozen H91 family. H94 is a distinct prospective test of a narrower structural possibility: if label morphology encodes object class or function, the initial transcription symbol may carry reproducible information about coarse object geometry even when whole-string distance does not. H94 is not a rescue of H92/H93 and cannot alter their FAIL status.

## Frozen population and provenance

Use exactly the 153 H91 Stage-B object-label pairs from the 9 independent folios. Reconstruct and verify the same pair membership before lexical opening. No object or folio may be removed after strings are exposed except a deterministic provenance failure, which makes the confirmatory run **BLOCKED** unless resolved without lexical-value selection.

## Frozen visual predictors

For each object use only the already frozen geometry variables:

`[log(area), log(width/height), x_norm, y_norm]`.

Each predictor is standardized from the training data only inside each held-out-folio fold. Any exactly zero-variance training predictor is deterministically mapped to 0.0 in both train and test using the H93a convention. No lexical information may tune or select visual predictors.

## Primary lexical target

After pair reconstruction and visual-feature hashing, expose each frozen token string and take its **first transcription character exactly as stored**. No glyph collapsing, EVA reinterpretation, manual correction, semantic mapping, or transliteration normalization is allowed.

To make the classification endpoint deterministic, define eligible initial-glyph classes as characters occurring in at least **10 of the 153 frozen labels globally**. Labels whose initial glyph is below this support threshold are assigned to one single `OTHER` class; `OTHER` is retained only if it contains at least 10 labels, otherwise those labels remain an `OTHER` class but the run is **BLOCKED** if any held-out fold contains a target class absent from its training folds. This rule is frozen before inspecting class identities or frequencies.

## Model and validation

Primary model: multinomial logistic regression with L2 penalty, `C=1.0`, intercept enabled, `max_iter=10000`, deterministic solver `lbfgs`, no class weights. Use leave-one-folio-out validation across the 9 frozen folios. Fit standardization and the classifier on the eight training folios and predict the held-out folio. Concatenate all held-out predictions.

Primary statistic: **macro balanced recall** over the globally frozen target classes, i.e. arithmetic mean of per-class recall across the concatenated out-of-fold predictions. No training accuracy is evidential.

## Null and significance

Use **19,999** permutations with NumPy `default_rng(20261010)`. For each permutation shuffle complete initial-glyph target identities **within folio only**, preserving each folio's target multiset and all geometry; rerun the full leave-one-folio-out pipeline, including training-fold standardization and fitting.

One-sided p-value:

`(1 + count(null_score >= observed_score)) / 20000`.

Freeze alpha = **0.001**.

## Decision rule

- **PASS** iff observed macro balanced recall is strictly above the permutation-null median AND `p <= 0.001`.
- **FAIL** iff the complete protocol-faithful execution finishes and PASS is not met.
- **BLOCKED** iff frozen-pair reconstruction, token resolution, class support across LOFO folds, numerical fitting, or infrastructure prevents complete execution.
- **NOT_RUN** until an actual execution exists.

No alternative classifier, C value, class weighting, support threshold, glyph normalization, subset, folio deletion, two-sided reinterpretation, or secondary endpoint may rescue a primary FAIL.

## Mandatory controls

1. **Pairing-scramble negative control:** deterministic within-folio target scramble with seed `94001`, followed by the identical LOFO pipeline. Descriptive only.
2. **Terminal-character sensitivity:** repeat the same frozen class-construction rule using the final transcription character. This is explicitly secondary/descriptive and cannot rescue the initial-character primary endpoint.
3. Report class identities and counts only after execution, plus per-folio counts, observed score, null median, p-value, control scores, pair hash, visual-feature hash, and target hash. Do not report semantic glosses.

## Interpretation ceiling

A PASS would establish only that the first transcription character contains out-of-folio predictive information about the frozen coarse geometry variables under this protocol. It would not identify meanings, language, plaintext, cipher mechanism, translation, or decipherment. A FAIL would falsify this specific initial-glyph visual-anchor hypothesis.

## Strict downstream state at preregistration

- H91: **PASS**
- H92: **FAIL**
- H93: **FAIL**
- H94 preregistration: **PASS**
- H94 execution: **NOT_RUN**
- Semantics: **NOT_RUN**
- Language: **NOT_RUN**
- Translation: **NOT_RUN**
- Decipherment: **NOT_RUN**
