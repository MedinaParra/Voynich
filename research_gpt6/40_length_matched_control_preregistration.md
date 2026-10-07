# Lc vs Lf length-matched negative control — preregistration

Status: **NOT_RUN**.

Frozen before execution. This control follows the valid length-ablation replication FAIL and must not be modified after its result is observed.

## Hypothesis

If the original Lc-vs-Lf pilot reflects lexical/morphological structure beyond the class-associated token-length distribution, discrimination should remain above chance when the held-out evaluation is exactly balanced by token length within each quire.

## Frozen data and model

Use corpus blob `2a4533ab9bdfa85db9bad602d590978953055df1` and exactly the parser/inclusion criteria of `label_pair_holdout.py`: Lc vs Lf, Currier/hand A|1, quires O and S, unique certain single-token labels only.

Use the ORIGINAL six pilot features, including token length, and the same nearest-class-centroid classifier. No tuning or feature selection.

## Length matching

Within each held-out quire independently, form exact token-length strata. For every length containing both classes, retain all observations of the minority class and a deterministic random sample without replacement of the same number from the majority class, seed `20261006`. Length strata lacking either class are excluded. The held-out test set is therefore class-balanced within every retained exact-length stratum. Training remains the full opposite quire, unchanged, so the intervention targets evaluation confounding rather than silently redefining the learned model.

The script must report retained counts by quire and length. If either held-out quire has fewer than 10 observations per class after matching, the experiment is **BLOCKED** rather than interpreted.

## Null

Exactly 999 permutations. Permute class labels ONLY within exact `(quire, token_length)` strata before rebuilding the matched held-out evaluation. This preserves the observed quire and token-length structure. Deterministic seed `20261006`.

## Statistic and decision

Primary statistic: mean balanced accuracy across the two length-matched held-out quire folds.

**PASS** iff both folds satisfy the minimum matched sample rule, aggregate balanced accuracy > 0.5, and Monte Carlo p <= 0.05. **FAIL** if execution is valid but either inferential threshold is not met. **BLOCKED** if the minimum matched sample rule or frozen execution cannot be satisfied. Before execution: **NOT_RUN**.

## Interpretation boundary

PASS would support residual Lc-vs-Lf structure not reducible to the marginal token-length distribution under this exact matching control. FAIL would further weaken the lexical-anchor interpretation. Neither outcome is a translation or decipherment.