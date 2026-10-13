# H110 — Rosettes leave-one-paragraph-out geometry→length replication

Status at preregistration: **PASS** (preregistration only). Implementation: **NOT_RUN**. Result: **NOT_RUN**.

## Motivation
H105 reported a preregistered within-paragraph association between spatial geometry `(x,y,sin(theta),cos(theta))` and token length. H106–H109 failed to isolate a robust mechanism, and H109 showed that paragraph identity alone predicts token length better than the H105 geometry model. H110 therefore asks a stricter prospective question: **does the geometry→length relation generalize to an entirely held-out paragraph?** This is a generalization test, not a rescue or retuning of H105.

## Frozen source and cohort
- External source repository: `alessandroplaca-uro/voynich-spatial-data`.
- Frozen source commit: `7580dafa624cf23a63665f4819022003f8d128ef`.
- Frozen CSV: `rosettes/tokens_f85v_86r.csv`.
- Frozen CSV SHA-256: `ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d`.
- Eligibility rules must be byte-for-byte equivalent to H105, yielding exactly **482 tokens / 23 paragraphs**. Any mismatch => **BLOCKED**.
- H105 replay gate: reproduce COMBINED within-paragraph 5-NN LOOCV MAE `1.5950207468879667` (absolute tolerance `1e-12`). Failure => **BLOCKED**.

## Primary prospective test
Perform leave-one-paragraph-out (LOPO) prediction over all 23 eligible paragraphs.

For each held-out paragraph:
1. Training data are all eligible tokens from the other 22 paragraphs only.
2. Standardize each geometry feature using **training-set mean and population SD only**; apply those frozen training statistics to the held-out paragraph. Zero-SD features, if any, make the experiment **BLOCKED**.
3. Predict each held-out token length using Euclidean **5-nearest-neighbour regression** in the four standardized geometry features `(x,y,sin(theta),cos(theta))`; prediction is the unweighted mean length of the 5 training neighbours.
4. No token, length, paragraph statistic or lexical feature from the held-out paragraph may enter fitting or scaling.

Pool all 482 held-out predictions and compute `MAE_GEOMETRY_LOPO`.

Baseline: for each fold predict every held-out token by the **mean token length of the training 22 paragraphs only**. Pool all predictions and compute `MAE_GLOBAL_LOPO`.

Primary observed contrast:
`D = MAE_GLOBAL_LOPO - MAE_GEOMETRY_LOPO`.
Positive D means geometry generalizes better than the training-only global-mean baseline.

## Exact null construction
Use **9,999** Monte Carlo permutations plus the observed assignment. In every permutation independently shuffle token lengths **within each paragraph**, leaving geometry, paragraph membership and paragraph sizes fixed. Re-run the full LOPO pipeline, including training-only scaling and both predictors, and calculate `D_perm`.

Seed: **20261020** using NumPy `default_rng`.
One-sided Monte Carlo p-value: `(1 + count(D_perm >= D_obs)) / 10000`.

## Decision rule
Familywise alpha is frozen at **0.005**.

- **PASS** iff all gates pass, `D > 0`, and `p < 0.005`.
- **FAIL** iff all gates pass but the PASS criterion is not met.
- **BLOCKED** iff source identity, cohort identity, H105 replay, numerical validity, or the frozen algorithm cannot be satisfied.
- **NOT_RUN** until an actual execution exists.

No alternative k, metric, normalization, paragraph subset, token subset, seed, baseline, sidedness or threshold may replace this test after results are opened. Any such analysis must receive a new hypothesis number and preregistration.

## Interpretation ceiling
A PASS would show only that spatial geometry carries token-length predictive information that generalizes across paragraphs in this frozen Rosettes dataset. It would **not** identify semantics, language, plaintext, cipher family, label meaning or decipherment.

A FAIL would materially weaken H105 as a paragraph-independent spatial lexical anchor and, together with H106–H109, trigger the stopping rule for further post-hoc subdivision of the H105 effect. A future label-object test would then require an independently frozen visual→token bridge or genuinely held-out spatial dataset.

Semantics = **NOT_RUN**  
Language = **NOT_RUN**  
Translation = **NOT_RUN**  
Decipherment = **NOT_RUN**
