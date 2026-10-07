# H63 — Independent-transcription strict label-vs-paragraph replication — result

Status: **PASS** under the preregistered decision rule.

## Execution
- Branch: `experiment/h63-independent-label-replication`
- Preregistration commit: `a50da87b4175df94a6eb9b3bb7c92c0387b36dd0`
- Implementation commit: `9d70188e4766e41da7d632c06f7ca1e4c9f130d7`
- Workflow commit: `c14fbf78b24e7132c435df06a7061df534e724e0`
- GitHub Actions run: `37615864518`
- Job: `112773909053`
- Artifact: `h63-independent-label-replication-results`
- Artifact ID: `11480780023`
- Artifact ZIP SHA-256: `0bab7524bf82584cc72bcd04c45f96cd048669332c5fe7cdffaef8ce4be72b4a`

## Frozen independent source
- Repository: `oklo/voynich_gpt`
- Commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- Path: `IT2a-n.txt`
- Expected Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Observed Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Source integrity: verified.

## Independent sample
Applying the frozen H60 structural rules independently to IT2a-n produced:
- positive single-token L* loci: **669**
- strict P-matched pairs: **388**
- represented folios: **32**
- positives excluded for lack of exact same-folio/length/Currier/hand P match: **281**

The replication thresholds (>=60 pairs, >=8 folios) were met without adjustment.

## Frozen H60 classifier
Predictors were unchanged:
- fraction `o`
- fraction `a`
- fraction `y`
- starts `q`
- ends `y`

Evaluation was leave-one-folio-out with training-fold-only standardization and nearest-class-mean prediction.

## Results
- observed balanced accuracy: **0.6945876288659794**
- null mean balanced accuracy: **0.5008410472327995**
- permutations: **999/999**
- Monte Carlo p: **0.001**
- descriptive P-vs-P negative-control BA: **0.5347938144329897**
- negative-control pairs: **388**

## Decision
All preregistered PASS criteria were met:
- immutable source verified;
- sample thresholds satisfied;
- 999/999 permutations completed;
- BA > 0.5;
- p <= 0.05.

**H63 = PASS.**

## Relation to H60
H60 discovery/strict replication on the original frozen corpus gave BA `0.6585858586`, p=`0.001` on 495 pairs / 34 folios.

H63 independently yields BA `0.6945876289`, p=`0.001` on 388 pairs / 32 folios from IT2a-n.

The direction and effect are therefore reproduced across transcription sources despite materially different positive-token and matched-pair counts.

## Interpretation
H63 substantially reduces the hypothesis that the strict L-vs-P token-form distinction is a peculiarity of one transliteration file or one transcription tradition. The safest supported statement is that certain single-token L loci and matched paragraph-text P tokens exhibit a reproducible difference in token-form statistics under the five frozen H60 predictors.

This remains a functional/statistical distinction, not a semantic identification.

Language identification: **NOT_RUN**.
Semantic identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
