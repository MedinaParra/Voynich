# H105 — Nine Rosettes spatial→lexical anchor preregistration

Status before execution: NOT_RUN

## Rationale
H98 is BLOCKED because the frozen H91 visual label ordinals cannot be transferred to GC v101, H103 showed no common single-token GC locator class across the nine H91 pages, and H104 found 0/9 H91 coverage in the independent positioned dataset. H105 therefore does **not** rescue or modify H98. It opens a new, independently sourced spatial lexical-anchor test on the Nine Rosettes foldout, where token coordinates are explicitly available.

## Frozen external source
Repository: `alessandroplaca-uro/voynich-spatial-data`.
Frozen source commit: `7580dafa624cf23a63665f4819022003f8d128ef`.
Input path: `rosettes/tokens_f85v_86r.csv`.
The source commit and path are frozen before H105 execution. No interpretive/gloss layer is admissible.

## Units and exclusions
Use rows with finite `x_px`, `y_px`, `angle_deg`, a non-empty token, and a valid integer `paragraph`. Tokens containing `?` are excluded prospectively. Token strings are used only to compute character length; raw token strings are not written to the result artifact.

## Primary hypothesis
Within a positioned manuscript region, token geometry contains reproducible information about token length beyond paragraph membership.

Predictors are fixed as normalized x, normalized y, sin(angle), cos(angle). Outcome is character count of the token. Coordinates are normalized globally to [0,1].

## Evaluation
Use leave-one-out 5-nearest-neighbor regression in the four fixed geometric features. For each held-out token, prediction is the mean length of its 5 nearest remaining tokens **from the same paragraph**. Paragraphs with fewer than 6 admissible tokens are excluded before evaluation.

Primary statistic: MAE over all evaluable held-out tokens.

Null: 9,999 within-paragraph permutations of token lengths, with geometry and paragraph membership fixed. Seed = 20261012. For each permutation recompute the same LOOCV 5-NN MAE.

Primary one-sided p = `(1 + number(null_MAE <= observed_MAE)) / 10000`.

## Negative control
Rotate the complete length vector by a fixed offset of 137 rows after sorting admissible rows by `(paragraph, token_index, id)`, then run the identical within-paragraph permutation test with seed 105137. This deliberately destroys local token↔geometry correspondence while preserving the marginal length vector. The negative control must not achieve p <= 0.01 in the improving direction.

## Decision rule
H105 = PASS only if all mandatory controls PASS, observed MAE < null median, primary p <= 0.01, and the negative control does not produce an improving p <= 0.01. Otherwise H105 = FAIL.

H105 = BLOCKED if source commit/path cannot be fetched, required columns are absent, fewer than 100 rows are evaluable, fewer than 5 paragraphs are evaluable, any required numeric value is non-finite, or deterministic replay differs.

## Mandatory controls
- frozen source commit/path identity
- required columns present
- >=100 evaluable rows
- >=5 evaluable paragraphs
- finite geometry/outcome
- exactly 9,999 primary permutations
- exactly 9,999 negative-control permutations
- deterministic replay of observed MAE

## Firewall
No semantic glosses, proposed plaintext, language identification, translation, dictionary, KACHOOM interpretation, or decipherment is loaded or evaluated. PASS would establish only a geometry↔token-length association in this positioned Rosettes dataset. It would not validate H98, identify a language, or decipher the manuscript.
