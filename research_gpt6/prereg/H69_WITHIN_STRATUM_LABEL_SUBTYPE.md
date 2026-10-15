# H69 — within-documentary-stratum label-subtype discrimination

Status at preregistration: NOT_RUN.

## Motivation
H68 established that a nontrivial exchangeable subset exists after conditioning on documentary metadata: O|A|1 and S|A|1 contain Lc/Lf; M|B|2 contains Ln/Lt. Ls/Lz have no within-stratum comparator and are excluded. This experiment asks only whether surface lexical/form features distinguish visual label subtypes *within* those fixed strata. It is not a translation or semantic identification.

## Frozen source
Use the same frozen IT_ivtff_1a.txt source and SHA-256 gate as H67/H68: db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee.

## Frozen strata/classes
- O|A|1: Lc vs Lf
- S|A|1: Lc vs Lf
- M|B|2: Ln vs Lt
All other units/strata excluded.

## Unit of split
Folio is the grouping unit. No folio may occur in both train and test. Evaluate each of the three strata independently by leave-one-folio-out (LOFO), then pool predictions only for a predeclared overall balanced-accuracy summary.

## Features
Use only the five symbol-renaming-invariant token features frozen by H66: token length, number of distinct symbols, adjacent-repeat count, maximum symbol multiplicity, and normalized equality-pattern complexity. No literal EVA character identity, no folio/quire/Currier/hand metadata, no unit code as a predictor.

## Model
Deterministic logistic regression with standardized features fitted on training folds only. If a fold's training set lacks either class, that fold is NOT_RUN and excluded from neither numerator nor denominator; if fewer than 3 valid test folios remain in a stratum, that stratum is BLOCKED.

## Null / inference
Within each stratum, perform 999 group-preserving permutations (seed 690069): permute subtype labels at the folio level while preserving each folio's token rows, refit the full LOFO procedure, and compare observed balanced accuracy to the null. This tests beyond folio identity while retaining documentary stratum.

## Decision
Familywise alpha = 0.05/3 = 0.0166667 per stratum (Bonferroni).
A stratum is PASS iff BA >= 0.60 and permutation p <= 0.0166667. Otherwise FAIL, unless preregistered execution is impossible, then BLOCKED. Overall H69 PASS requires >=2 of 3 strata PASS. H69 FAIL if executable and <2 strata PASS. No semantic claim follows from PASS.

## Controls/reporting
Report class counts, folios, valid folds, observed BA, majority baseline BA, permutation p, and SHA-256. Report PASS/FAIL/BLOCKED/NOT_RUN exactly.