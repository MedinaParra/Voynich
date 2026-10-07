# H61 — Independent functional-role replication result

Status: **PASS_INDEPENDENT_FUNCTIONAL_REPLICATION**.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Workflow: `h61-independent-functional.yml`
- GitHub Actions run: `37610516299`
- Job: `112756374019` (`independent-functional-transfer-h61`), conclusion `success`
- Independent source: Takahashi `IT2a-n`
- Frozen independent Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Seed: `20261007`
- Permutations: `999/999`

## Eligibility
- Positive label/object tokens: `669`
- Exact-length/local matched pairs: `652`
- Excluded without match: `17`
- Evaluable quires: `H, I, J, K, L, M, O, S`
- Evaluable pairs: `652`

## Result
- Observed leave-one-quire-out balanced accuracy: **0.683282208588957**
- Null mean balanced accuracy: **0.5006686133986754**
- Null maximum balanced accuracy: **0.5460122699386503**
- Monte Carlo p: **0.001**
- Quires above chance: **7/8**; quire H = `0.5` exactly.

Per-quire BA:
- H: `0.500000`
- I: `0.639785`
- J: `0.632353`
- K: `0.653333`
- L: `0.576271`
- M: `0.786458`
- O: `0.802817`
- S: `0.700787`

## Frozen decision
All preregistered gates pass: sample/quire requirements, 999/999 permutations, aggregate BA > 0.60, p <= 0.01, and >=3 held-out quires above chance. Therefore H61 is **PASS_INDEPENDENT_FUNCTIONAL_REPLICATION**.

## Conservative interpretation
The label/object-locus versus locally matched running-text distinction generalizes across quires and replicates on an independently sourced Takahashi transcription. This materially reduces the probability that H60 was an idiosyncrasy of the primary transcription file.

This remains a **functional-locus** result. It does not establish that a label names its depicted referent, distinguish a specific semantic class, identify a language or cipher, recover plaintext, or translate any token. Existing Lc/Lf and other specific lexical-semantic failures remain failures.

Semantic identity: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
