# H98 — cross-transcription label-object lexical-anchor closure

Status: **PASS (preregistration only)**

## Purpose
Close the H91–H95 label-object/lexical-anchor family with one genuinely independent transcription-level robustness test rather than inventing another lexical endpoint on the same transcription. H98 asks whether the already frozen H92 primary endpoint (label token length predicted by frozen H91 geometry) changes conclusion under an independent transcription representation.

## Firewall and frozen hypothesis
No new visual feature, lexical feature, model family, folio selection, pair selection, alpha, or rescue endpoint may be introduced. Geometry and eligible object↔label ordinal pairs are exactly the H91 Stage-B frozen family (expected 9 folios / 153 stable pairs). The sole primary endpoint is exactly H92 label length with the H92 five geometry predictors and LOOCV MAE.

The independent lexical source MUST be the repository's frozen GC v101 transcription already used by prior cross-transcription experiments. If that exact frozen source/provenance cannot resolve the H91 label ordinals without changing ordinal rules, H98 = **BLOCKED**. Do not substitute another transcription after execution begins.

## Normalization and ordinal mapping
Reuse the existing frozen GC-v101 normalization and label-ordinal resolution code from prior repository experiments. Do not create a new normalization after inspecting H98 tokens. For every H91 eligible pair, resolve the same folio and frozen label ordinal in GC v101. Empty/unresolved tokens are not dropped: any unresolved eligible pair makes H98 = **BLOCKED**.

Raw token strings MUST NOT be emitted to the result artifact. Only numeric lengths, pair IDs, folio IDs, ordinals and hashes may be recorded.

## Primary model
Exactly H92:
- predictors `[x_norm, y_norm, radius_norm, sin(theta), cos(theta)]` from frozen H91 geometry;
- linear least squares with intercept;
- leave-one-out cross-validation over all 153 eligible pairs;
- primary statistic = MAE.

## Null and criterion
Exactly 9,999 permutations, stratified within folio, preserving folio composition and pair counts. RNG `numpy.default_rng(20261011)`.

Finite-sample one-sided p-value: `(1 + count(null_MAE <= observed_MAE))/10000`.

H98 primary = **PASS** iff BOTH:
1. observed MAE < median null MAE; and
2. p <= 0.01.
Otherwise H98 = **FAIL**.

## Mandatory controls
1. **Pair-scramble:** independently derange GC label lengths within each folio, no fixed points where n>=2; seed `98090`; evaluate with the same stratified test using seed `98091`. Significant predictive-direction scramble at p<=0.01 forces H98 = **FAIL**.
2. **Ordinal coverage:** exactly 153/153 frozen H91 pairs must resolve in GC v101; otherwise **BLOCKED**.
3. **Geometry identity:** hash the H91 pair IDs + geometry and require identity with the frozen H92 input provenance; mismatch = **BLOCKED**.
4. **Cross-transcription disagreement report:** report numerically how many resolved GC token lengths differ from the corresponding Takahashi H92 lengths, but this is descriptive only and cannot rescue/change the primary result.
5. **Determinism:** rerun with identical inputs/seeds must reproduce the exact statistics JSON hash.

## Family-level interpretation
H98 does not reopen H92–H95. If H98 = FAIL, the preregistered simple label-object lexical-anchor family is considered **CLOSED/FAIL** for the tested endpoints and no further endpoint may be added to these same 153 pairs without a new independent dataset and a separately motivated protocol.

If H98 = PASS, it supports only a cross-transcription geometry→label-length association and requires a new independent visual/folio holdout before any stronger interpretation. It does not rescue H93–H95 and does not identify meaning.

## Required provenance/output
Record executing commit SHA, H91 Stage-B provenance, H92 provenance, exact GC v101 source path/hash, runner hash, 153 pair IDs/ordinals, geometry hash, numeric token lengths, disagreement count, seeds, observed/null MAE, p-value, scramble statistics, controls and PASS/FAIL/BLOCKED.

Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.
