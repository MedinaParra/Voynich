# H108 — Rosettes paragraph-order confound test

Status at preregistration: **NOT_RUN**.

## Motivation
H105 found a preregistered association between spatial geometry `(x,y,sin(theta),cos(theta))` and token length. H106 did not isolate that signal to POSITION or ORIENTATION at the corrected threshold, and H107 found no preregistered incremental advantage of COMBINED over either reduced geometry under its coupling null. Before any semantic interpretation, test the simpler explanation that H105 is induced by ordinary within-paragraph token order.

## Frozen cohort and upstream gate
Use exactly the H105 frozen Rosettes source, parsing, exclusions, normalization, 482-token / 23-paragraph cohort, token lengths, and 5-NN leave-one-out machinery. The implementation MUST first reproduce the H105 COMBINED observed MAE `1.5950207469` (absolute tolerance 1e-10) and cohort counts. Otherwise H108 = **BLOCKED**.

No tokens, paragraphs, coordinates, orientations, or lengths may be added, removed, relabelled, or manually corrected after this preregistration.

## Predictors
For each token, define normalized paragraph order

`ORDER = token_index / max_token_index_within_paragraph`

with the first token at the minimum observed index and denominator determined only from that paragraph. If a paragraph has zero range, set ORDER=0. This rule is frozen before execution.

Models:

1. `COMBINED = (z(x), z(y), sin(theta), cos(theta))`, exactly as H105.
2. `ORDER = (z(ORDER),)`.
3. `COMBINED_PLUS_ORDER = (z(x), z(y), sin(theta), cos(theta), z(ORDER))`.

All z-scoring and distance handling must reuse the H105 implementation conventions. Prediction target is token length. Evaluation is 5-NN leave-one-out within paragraph, identical to H105.

## Primary falsifiable contrasts
Define:

- `D_geom_over_order = MAE(ORDER) - MAE(COMBINED_PLUS_ORDER)`
- `D_order_over_geom = MAE(COMBINED) - MAE(COMBINED_PLUS_ORDER)`

The scientific question is whether geometry retains predictive information after explicit adjustment for local token order, and whether order itself adds information beyond geometry.

## Null and permutations
Use 9,999 permutations per contrast. Within each paragraph independently, circularly rotate the ORDER vector by a non-zero offset drawn from a seeded RNG while leaving geometry and token lengths fixed. This preserves paragraph membership, the marginal order sequence, geometry, orientation, and target lengths while breaking the observed order↔geometry alignment. Use seeds:

- `20261017` for `D_geom_over_order`
- `20261018` for `D_order_over_geom`

For each permutation refit/evaluate the relevant models with the same 5-NN LOOCV. One-sided p-value: `(1 + count(D_null >= D_observed)) / 10000`.

## Decision rule
Familywise alpha = 0.01; Bonferroni threshold = **0.005** for each of the two preregistered contrasts.

- Geometry survives order control only if `D_geom_over_order > 0` and `p_geom_over_order < 0.005`.
- Order adds beyond geometry only if `D_order_over_geom > 0` and `p_order_over_geom < 0.005`.

Overall H108:

- **PASS** only if geometry survives order control under the first criterion.
- **FAIL** if the upstream gate passes but geometry does not survive order control.
- **BLOCKED** if the frozen cohort/H105 reproduction gate fails or required source/infrastructure is unavailable.
- **NOT_RUN** until an actual execution exists.

The second contrast is diagnostic and must be reported regardless of outcome; it does not change the primary PASS/FAIL definition.

## Interpretation boundary
A PASS would show only that H105's geometry-length association is not reducible to this preregistered one-dimensional within-paragraph order covariate. A FAIL would support local order as a sufficient confound under this test. Neither outcome establishes semantics, language identity, translation, decipherment, object names, or lexical meaning.
