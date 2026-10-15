# Lc vs Lf lexical-anchor pair — preregistered result

Status: **PASS** (execution completed and preregistered pilot criterion met).

Evidence source: GitHub Actions run `37525615142`, job `lexical-anchor-pair` (`112481738126`), artifact `lexical-anchor-pair-results` (`11442416315`), head `aaa31acc2c9c68c0d45dcebdb1d2678d9dde44a0`.

Frozen contrast: `Lc` vs `Lf`, restricted to Currier/hand `A|1`, with leave-one-quire-out evaluation over quires `O` and `S` and 999 within-quire permutations.

Observed data:

- Lc: 36
- Lf: 177
- total: 213
- quire O: n=75, balanced accuracy=0.5667293233
- quire S: n=138, balanced accuracy=0.7331064657
- aggregate balanced accuracy=0.6499178945
- permutations completed=999
- Monte Carlo p=0.001
- artifact classification: `LEXICAL_ANCHOR_PAIR_PILOT_NOT_TRANSLATION`
- artifact status: `PASS_EXECUTED`

## Conservative interpretation

The preregistered pilot detects an out-of-quire morphological signal distinguishing these two label classes under the frozen controls. This is evidence of class-associated lexical/morphological structure, not evidence that any Voynich token has been translated and not proof that the labels denote the modern object-class names used by the transcription metadata.

The fold asymmetry (0.567 vs 0.733) is material and argues against treating the aggregate score as a stable semantic decoder. A replication/generalization test must therefore be defined before inspecting any new target contrast.

## Status ledger

- Workflow execution: **PASS** — job completed successfully.
- Preregistered Lc-vs-Lf pilot: **PASS** — balanced accuracy 0.6499 and permutation p=0.001.
- Translation claim: **NOT_RUN** — this experiment is not a translation test.
- Semantic identity of Lc/Lf labels: **NOT_RUN** — class names are metadata, not decoded meanings.
- Independent replication: **NOT_RUN** — requires a separately frozen target/control.

No thresholds or classes were changed after observing the result.