# H107 — Rosettes joint-geometry incremental-value test

Status at preregistration: NOT_RUN.

## Motivation
H105 found a preregistered association between combined spatial geometry (position + orientation) and token length. H106 reproduced H105 exactly but neither POSITION nor ORIENTATION alone passed the multiplicity-adjusted alpha=0.005 threshold. H106 does not establish that combining feature families adds predictive information beyond the stronger single family. H107 tests that narrower claim prospectively.

## Frozen cohort and source
Use exactly the H105/H106 frozen CSV and cohort: source commit `7580dafa624cf23a63665f4819022003f8d128ef`, CSV SHA-256 `ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d`, exactly 482 retained tokens in exactly 23 paragraphs. Any mismatch => BLOCKED.

## Frozen predictor and preprocessing
Reuse H106 without alteration: paragraph-wise normalization, 5-nearest-neighbor leave-one-out regression, absolute-error loss. Feature sets are POSITION=(x,y), ORIENTATION=(sin(theta),cos(theta)), COMBINED=(x,y,sin(theta),cos(theta)). H105 exact numerical replay is an infrastructure/reproduction gate; mismatch => BLOCKED.

## Primary statistic
For every retained token compute absolute prediction errors e_COMBINED, e_POSITION and e_ORIENTATION. Define the paired incremental improvements:

- D_position = mean(e_POSITION - e_COMBINED)
- D_orientation = mean(e_ORIENTATION - e_COMBINED)

Positive D means COMBINED predicts token length better than that reduced feature family.

## Null and inference
Within each paragraph independently, keep token lengths and POSITION fixed and circularly rotate the ORIENTATION rows by a uniformly sampled non-zero offset. This preserves paragraph membership, the marginal position geometry, orientation distribution, and token-length distribution while breaking the observed position↔orientation coupling. For each of 9,999 preregistered permutations, refit COMBINED and compute both D statistics; POSITION and ORIENTATION reduced-model errors remain the observed frozen reduced-model errors. Seeds: 20261015 for D_position and 20261016 for D_orientation. One-sided p=(1 + count(D_null >= D_observed))/(10000).

Because two incremental claims are tested, Bonferroni alpha=0.005 for each.

## Decision rule
PASS only if BOTH D_position > 0 with p<=0.005 AND D_orientation > 0 with p<=0.005. Otherwise FAIL. Infrastructure/cohort/replay mismatch is BLOCKED. A PASS supports only incremental predictive value of the joint spatial representation in this frozen Rosettes dataset; it is not evidence of semantics, language identity, plaintext, translation, or decipherment.

Semantics: NOT_RUN. Language: NOT_RUN. Translation: NOT_RUN. Decipherment: NOT_RUN.
