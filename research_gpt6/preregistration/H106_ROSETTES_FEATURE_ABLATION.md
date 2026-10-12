# H106 — Nine Rosettes spatial lexical-anchor feature ablation

Status before execution: NOT_RUN.

## Motivation
H105 returned PASS for the preregistered combined geometry feature set (x, y, sin(theta), cos(theta)). H106 is a prospective decomposition test: determine whether that signal is reproducibly attributable to position, orientation, or requires their combination. This does not test semantics, language, translation, or decipherment.

## Frozen source
Use exactly `rosettes/tokens_f85v_86r.csv` from `alessandroplaca-uro/voynich-spatial-data` commit `7580dafa624cf23a63665f4819022003f8d128ef`, requiring SHA-256 `ff7b779e9ff2468ca04c0e07d0bd9999110d554a962faad1d78fc99c5e7e712d`.

## Cohort and outcome
Reproduce the H105 filtering exactly: only paragraphs with >=5 admissible tokens, same token-length outcome, same within-paragraph 5-NN leave-one-out predictor and normalization rules. Expected frozen analysis cohort is 482 rows in 23 paragraphs; mismatch => BLOCKED.

## Tests fixed before execution
Run three models independently:
1. POSITION: features (x,y).
2. ORIENTATION: features (sin(theta),cos(theta)).
3. COMBINED: features (x,y,sin(theta),cos(theta)); this is an exact H105 replay control.

For each model use 9,999 within-paragraph label permutations. Seeds: POSITION=20261013, ORIENTATION=20261014, COMBINED=20261012. One-sided statistic: observed MAE lower than permutation MAE. Alpha=0.01 for the exact H105 replay only. For the two new ablations use Bonferroni alpha=0.005 (0.01/2).

## Gates
Infrastructure/source/cohort/deterministic-replay gates must PASS. The COMBINED replay must reproduce H105 exactly to numerical precision: observed MAE 1.5950207468879667, null median MAE 1.675933609958506, p=0.0049. Otherwise H106 = BLOCKED.

## Decision rule
PASS iff the combined H105 replay gate passes and at least one of POSITION or ORIENTATION has observed MAE < null median and p <= 0.005. FAIL iff replay passes but neither ablation passes. BLOCKED iff any frozen-source/cohort/replay gate fails. Report both ablations regardless of outcome. No feature tuning, alternate k, alternate normalization, token filtering, paragraph filtering, or post-hoc threshold changes are permitted.

Semantics = NOT_RUN. Language = NOT_RUN. Translation = NOT_RUN. Decipherment = NOT_RUN.