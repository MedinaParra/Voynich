# H109 — Rosettes paragraph-identity confound test

Status: PREREGISTERED / NOT_RUN

## Motivation
H105 produced a reproducible association between Rosettes spatial geometry and token length, while H106, H107, and H108 did not isolate a robust position/orientation interaction or incremental value over local order. A remaining simple confound is paragraph identity: paragraph-specific lexical-length baselines may covary with paragraph-specific spatial regions.

## Frozen cohort and gate
Use exactly the H105 Rosettes cohort and preprocessing: 482 eligible tokens in 23 paragraphs, same token normalization, coordinates, orientation representation, 5-NN LOOCV machinery, and source-integrity checks. Before H109 inference, reproduce H105 COMBINED MAE = 1.5950207469 (within floating-point tolerance used by H106–H108). If the cohort or gate cannot be reproduced, H109 = BLOCKED and no inferential result is reported.

## Models
Outcome: normalized token length exactly as H105.

COMBINED: frozen H105 geometry features (x, y, sin(theta), cos(theta)).

PARAGRAPH: paragraph identity only. Prediction for each held-out token is the mean outcome of the remaining tokens in the same paragraph. If a paragraph has fewer than 2 eligible tokens, the run is BLOCKED.

COMBINED+PARAGRAPH: residualize the outcome by the training-only paragraph mean, predict the residual using the frozen H105 5-NN geometry within the same evaluation protocol, then add the training paragraph mean back. The held-out token never contributes to its paragraph mean.

## Primary falsifiable contrast
D = MAE(PARAGRAPH) - MAE(COMBINED+PARAGRAPH).

Positive D means geometry improves prediction after paragraph identity is controlled.

## Null and permutation
Within each paragraph independently, circularly rotate the complete geometry tuple (x, y, sin(theta), cos(theta)) relative to outcomes. Preserve paragraph membership, paragraph sizes, token lengths, geometry marginals, and within-paragraph geometry configuration; break only token-level geometry↔length alignment. Exclude the identity rotation for paragraphs with more than one eligible token. Use 9,999 Monte Carlo permutations with seed 20261019.

One-sided p = (1 + count(D_perm >= D_obs)) / 10000.

## Decision rule
Familywise alpha is frozen at 0.005 for this prospective continuation.

PASS iff: H105 gate PASS, D_obs > 0, and p < 0.005.

FAIL iff the gate passes but any PASS condition fails.

BLOCKED iff cohort/source integrity/gate/model computation cannot be completed exactly as preregistered.

NOT_RUN until a GitHub Actions execution actually evaluates this preregistration.

## Interpretation limits
PASS would support token-level geometric information beyond paragraph-specific length baselines; it would not establish semantics, language, translation, object identity, or decipherment. FAIL would make paragraph-level heterogeneity a viable explanation for the H105 association and would argue against escalating H105 as a lexical-object anchor without stronger independent evidence.
