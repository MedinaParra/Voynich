# 39. Confound-matched label-pair lexical anchor protocol

Date: 2026-10-07
Status: PREREGISTERED / NOT_RUN
Branch: experiment/wild-decipherment

## Why this test now
The adversarial compositional null rejected the strong ch/sh claim at the frozen threshold. We therefore do not tune that result. The next independent evidence source is externally annotated IVTFF object-label subtype.

## Frozen source
- Corpus Git blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Only explicit IVTFF label subtypes are used; no object class is inferred from Voynichese.
- Only single-token, certain labels enter the primary test.

## Pre-model audit inherited from experiment/timesfm-voynich
Counts observed before any classifier:
- Lc=36, Lf=177, both Currier A / hand 1.
- Ln=59, Lt=39, both Currier B / hand 2.
- Ls=69, Lz=249, both Currier ? / hand 4.
- Lp=1 and La=3 are too sparse for standalone pair tests and are excluded before modeling.

The old all-class leave-one-quire-out design is not valid for these data because several classes occur in only one or two quires. This amendment is based only on the pre-model sample audit, never on classifier performance.

## Frozen primary comparisons
Three within-documentary-stratum binary comparisons:
1. `Lc vs Lf` — container vs pharmaceutical herb fragment; same Currier/hand stratum.
2. `Ln vs Lt` — nymph/human vs tube/tub/bath; same Currier/hand stratum.
3. `Ls vs Lz` — star vs zodiac; same hand stratum.

These names are IVTFF annotation classes, not translations.

## Features
Character n-grams learned on training data only. Primary representation: EVA character 1-3 grams with TF-IDF. Negative controls: token length and first/last glyph families. No historical-language lexicon is allowed.

## Grouped evaluation
Primary grouping is folio. A fold is evaluable only when its training and test partitions contain both classes. Use leave-one-folio-out predictions pooled across evaluable folios. Report balanced accuracy, macro-F1, class recall, confusion matrix, labels, unique folios and evaluable folds.

No random label-level CV can establish PASS.

## Adversarial null
For each pair, run 999 permutations in this exploratory-confirmatory bridge. Shuffle class labels only within folio when both classes coexist. Folios without exchangeability keep their labels fixed and contribute no permutation freedom. Report exchangeable-label coverage explicitly.

If local-folio exchangeability is too low to produce a meaningful null, classification is `BLOCKED_CONFOUND` rather than relaxing the null.

Seed: `20261007`.

## Gate
A pair is `PAIR_CANDIDATE` only if all are true:
- grouped balanced accuracy > 0.60;
- grouped balanced accuracy exceeds length and edge-glyph controls;
- Monte Carlo p <= 0.01 under the local-folio null;
- at least 25% of labels are in exchangeable folios;
- both class recalls exceed 0.50.

The overall experiment is `PASS_EXPLORATORY_LEXICAL_ANCHOR` only if at least two of the three frozen pairs independently satisfy the pair gate. Otherwise it is `FAIL_EXECUTED` or `BLOCKED_CONFOUND` as appropriate.

## Interpretation ceiling
PASS permits only: `visual-class lexical-anchor candidate`.
It does not permit a natural-language gloss, a plant name, a translation, or a decipherment claim.

## Next independent replication if PASS
Replicate on an alternate transcription and test whether the train-only discriminating component occurs in running text in contexts compatible with the same visual class. No gloss is assigned before that replication.