# Topology-conditioned lexical-anchor falsification preregistration

Status: **NOT_RUN**.

## Motivation
The original Lc/Lf lexical-anchor pilot passed, but exact token-length matching reduced it to chance (BA=0.5, p=0.993), so that lexical interpretation remains rejected as robust evidence. Separately, H1-H4 now support a reproducible text-internal latent topology. This experiment asks a new, falsifiable question without rescuing the failed pilot post hoc: does the already-frozen topology provide any *independent* information about the Lc/Lf label contrast after exact token-length control?

## Frozen inputs
- Same frozen EVA corpus/blob and parser used by the prior lexical-anchor controls and H1-H4.
- Label classes: exactly Lc vs Lf.
- Restriction: Currier/hand `A|1`, as in the original lexical pilot.
- Exact token-length strata remain mandatory.
- The topology representation is frozen from the already-defined A/B consensus machinery; no label class is used to build topology.

## Feature blocks
### Baseline
Use the length-ablated lexical feature set from the failed replication:
- fraction `o`
- fraction `a`
- fraction `y`
- starts `q`
- ends `y`

Absolute token length is not a predictor and is controlled by exact matching.

### Topology-conditioned model
Use the same baseline features plus topology-only context features computed without Lc/Lf labels:
- mean A-distance from the label's folio to its A/B-consensus neighbors;
- mean B-distance to those neighbors;
- consensus degree of the folio;
- Family C mean distance to consensus neighbors.

If a folio has no consensus neighbor, topology context is missing and the item is excluded before class balancing; report exclusions.

## Evaluation
Use leave-one-quire-out on the lexical labels where both classes are present in the held-out quire. Within every held-out fold, exact-match Lc and Lf by token length and balance classes. Training uses all other eligible quires.

Use the same nearest-class-mean classifier family as the original lexical pilot. Standardize predictor columns from training data only.

Primary statistic: difference in aggregate balanced accuracy:
`delta_BA = BA_topology - BA_baseline`.

Also report baseline and topology BA separately and per-fold values.

## Null
Exactly 999 deterministic permutations, seed `20261006`.

Permute Lc/Lf labels within exact `(quire, token_length)` strata, preserving all text and topology features. Refit/evaluate both models for each permutation and record null `delta_BA`.

Monte Carlo p = `(1 + count(null_delta_BA >= observed_delta_BA)) / 1000`.

## Decision
**PASS** only if:
1. at least 2 held-out quires are evaluable;
2. at least 10 matched examples per class are available in aggregate held-out evaluation;
3. 999/999 permutations complete;
4. `delta_BA > 0`;
5. p <= 0.05;
6. topology-conditioned aggregate BA > 0.5.

**FAIL** if execution is valid but any inferential criterion fails.

**BLOCKED** if sample/evaluable-fold requirements are not met or the frozen topology cannot be attached without violating leakage rules.

Before execution: **NOT_RUN**.

## Interpretation boundary
PASS would show that topology contains independent predictive information for this narrow label contrast after exact length control. It would not establish the semantic identity of Lc or Lf, a word meaning, language, plaintext, cipher, or translation. FAIL would leave the lexical-anchor route unsupported despite the topology results.

No thresholds, classes, feature blocks, matching rule, or classifier may be changed after observing this experiment.

Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
