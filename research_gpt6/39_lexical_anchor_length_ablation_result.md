# Lc vs Lf lexical-anchor length-ablation replication — result

Status: **FAIL** (execution valid; preregistered criterion not met).

Evidence: GitHub Actions run `37533104531`, job `lexical-anchor-replication` (`112507162888`), artifact `lexical-anchor-replication-results` (`11445481410`), artifact SHA-256 `7732365d162a158c0499c7187b96317d6b0871544a8d0c22c802b269efd51f7e`, experimental head `2d86237b90487eb45308183dad9293729ccca998`.

Frozen corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.

Observed preregistered replication:

- contrast: Lc vs Lf
- Lc: 36
- Lf: 177
- total: 213
- Currier/hand: A|1 = 213
- held-out quire O: n=75, balanced accuracy=0.6113721805
- held-out quire S: n=138, balanced accuracy=0.5369470102
- aggregate balanced accuracy=0.5741595953
- permutations completed: 999/999
- Monte Carlo p=0.085
- replication_pass=false
- artifact status: FAIL

Preregistered decision rule was aggregate balanced accuracy > 0.5 AND Monte Carlo p <= 0.05. The first condition passed; the second failed. Therefore the replication is **FAIL**. Thresholds, population, folds and features are not changed post hoc.

## Conservative interpretation

The original Lc-vs-Lf pilot signal does not survive the preregistered removal of absolute token length at the required significance threshold. This materially weakens any interpretation of the pilot as a robust lexical/object-class association. It does not prove that length alone generated the original effect: the ablated model retains a modest above-chance aggregate balanced accuracy, but p=0.085 is insufficient under the frozen rule and fold performance is heterogeneous.

No semantic meaning, translation, object identity, language identity or decipherment follows from either the original pilot or this failed robustness replication.

## Status ledger

- Infrastructure/execution: **PASS**
- Original Lc-vs-Lf pilot: **PASS** (previous experiment)
- Length-ablation replication: **FAIL**
- Translation: **NOT_RUN**
- Decipherment: **NOT_RUN**

## Next falsifiable step

Before testing any additional semantic label pair, preregister a length-matched negative-control analysis for Lc vs Lf. The purpose is to distinguish a class-associated length distribution from residual character/morphological structure without selecting a favorable new pair after seeing these results.