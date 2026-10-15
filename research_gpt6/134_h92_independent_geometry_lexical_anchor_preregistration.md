# H92 — independent geometry→label-length replication preregistration

Status: **PASS (preregistration only)**

## Purpose
Prospectively test whether the H90 geometry→label-length signal replicates on the independent H91 family that passed the blind Stage-B pairing gate. H92 is confirmatory. No H91 lexical strings or lengths were inspected to define this protocol.

## Frozen eligibility
- H91 Stage B must be PASS.
- Use exactly the admissible folios and stable object↔label-ordinal pairs emitted by the frozen H91 Stage-B procedure; no folio/pair dropping after lexical exposure.
- Expected gate evidence before lexical opening: 9 admissible folios, 153 stable pairs, ≥80% per-folio stability, family gate ≥2 folios and ≥40 stable pairs.
- Pairing, jitter, object extraction, and eligibility are frozen by H91/H91g and MUST NOT be changed in H92.

## Primary endpoint
The sole confirmatory lexical endpoint is **label token length**, reproducing H90. For each frozen label ordinal, resolve its token only after the frozen pairing family is loaded and verified. Normalize exactly as H90: Unicode NFC then `.strip()`, reject empty tokens. Length is Python `len()` of the normalized token.

## Frozen geometry predictors
For each admissible folio independently, use the H91 frozen object centroid `(x,y)`. Normalize x and y within that folio to [0,1] using min/max over the H92 eligible paired objects in that folio. Let c be the within-folio mean normalized centroid; compute radial distance from c, normalized by the within-folio maximum radius, and angle theta=`atan2(dy,dx)`. Primary predictor vector is exactly the H90 five-feature family: `[x_norm, y_norm, radius_norm, sin(theta), cos(theta)]`.

If any admissible folio has zero x/y span or zero maximum radius, H92 = **BLOCKED** rather than changing the predictor.

## Primary model and loss
Linear least squares with intercept, evaluated by **leave-one-out cross-validation (LOOCV)** over all eligible pairs. For each held-out pair, fit on all other pairs using the same five predictors and predict token length. Primary statistic is mean absolute error (MAE), exactly as H90.

## Null and multiplicity
Use 9,999 permutations plus the observed statistic and the finite-sample p-value `(1 + count(null_MAE <= observed_MAE))/10000`.

Because the independent family contains multiple folios, permutations MUST be **stratified within folio**: token lengths are permuted only among eligible pairs from the same folio, preserving folio composition and pair counts. RNG: NumPy `default_rng(20261010)`.

Primary H92 = **PASS** iff BOTH:
1. observed LOOCV MAE < median null MAE; and
2. one-sided permutation p <= 0.01.

Otherwise H92 = **FAIL**. Alpha 0.01 is frozen and cannot be relaxed. No secondary endpoint can rescue a FAIL.

## Mandatory negative control
Pair-scramble control: independently derange label lengths **within each folio** (no fixed points where a folio has ≥2 pairs), seed `92090`; evaluate with the same stratified permutation test using seed `92091`. A significant scramble at p<=0.01 in the predictive direction is a control failure and forces overall H92 = **FAIL** even if the primary passes. If a folio has only one eligible pair, that folio cannot be deranged and H92 = **BLOCKED** rather than silently changing the control.

## Descriptive ablation
As in H90, also report the x/y-only predictor `[x_norm,y_norm]` with the same LOOCV/permutation machinery. This is descriptive/secondary and cannot rescue the primary.

## Provenance/output requirements
The result artifact MUST record: executing commit SHA; H91 Stage-B source/result provenance; exact eligible folio IDs and pair IDs/label ordinals; pair count per folio; source hashes; runner SHA-256; seeds; observed/null MAE and p; control statistics; and PASS/FAIL/BLOCKED. Raw token strings MUST NOT be written to the result artifact. Token lengths may be recorded only as numeric values tied to frozen pair IDs for auditability.

## Interpretation ceiling
A PASS would support only an independent association between frozen visual geometry and label length under this protocol. It would **not** identify semantics, language, plaintext, translation, or decipherment. A FAIL means the H90 exploratory/suggestive geometry→length signal did not replicate under the preregistered independent test.

Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.
