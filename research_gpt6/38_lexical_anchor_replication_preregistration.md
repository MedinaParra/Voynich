# Lexical-anchor replication / robustness preregistration

Status: **NOT_RUN**.

This document is frozen before the replication result is generated. It follows the completed Lc-vs-Lf pilot (BA 0.6499178945; 999 permutations; Monte Carlo p=0.001) and does not alter its interpretation.

## Question

Does the Lc-vs-Lf signal survive removal of the most obvious token-length information, while preserving the original out-of-quire design?

## Frozen population

Use exactly the same frozen corpus blob (`2a4533ab9bdfa85db9bad602d590978953055df1`), parser, inclusion criteria, classes (`Lc`,`Lf`), Currier/hand stratum (`A|1`), and eligible quires (`O`,`S`) as `label_pair_holdout.py`. No rows/classes/quires may be added or removed after inspecting the replication result.

## Frozen replication model

Use the same nearest-class-centroid classifier and leave-one-quire-out folds as the pilot, but REMOVE absolute token length from the feature vector. The only permitted features are the five already-defined non-length pilot features: fraction `o`, fraction `a`, fraction `y`, starts-with-`q`, ends-with-`y`.

No feature selection, hyperparameter tuning, alternative classifier, token inspection, or semantic glossing is permitted after execution.

## Null/control

Run exactly 999 label permutations within quire with deterministic seed `20261006`, identical to the pilot. This preserves quire membership and class counts within each quire.

## Primary statistic and decision

Primary statistic: mean leave-one-quire-out balanced accuracy over eligible folds.

Replication **PASS** iff BOTH:

1. aggregate balanced accuracy > 0.5; and
2. Monte Carlo permutation p <= 0.05.

Otherwise replication **FAIL**, provided execution and both folds are valid. Infrastructure/data inability to execute as frozen is **BLOCKED**. Before execution it is **NOT_RUN**.

## Interpretation boundary

PASS would show that the pilot association is not explained solely by absolute token length and survives a preregistered robustness control. It would still NOT establish translation, lexical meaning, object identity, language identity, or decipherment. FAIL would materially weaken the pilot by showing that its signal does not survive this basic control.

Translation claim: **NOT_RUN**.