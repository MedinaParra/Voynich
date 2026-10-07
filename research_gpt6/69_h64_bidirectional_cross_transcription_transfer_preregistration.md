# H64 — Bidirectional cross-transcription functional-transfer preregistration

Status: **NOT_RUN**.

## Motivation
H60-H62 establish a robust FUNCTIONAL distinction between label/object-locus tokens and matched running text, including replication in an independent Takahashi transcription and survival after first/last-glyph ablation. H63 does not support escalation to local lexical coupling.

H64 therefore does **not** pursue semantics. It asks a stricter functional question: can a classifier learned in one transcription predict the label-vs-running-text distinction in the other transcription **without refitting on the target transcription**, while holding out the target quire?

This tests whether the functional signature itself transfers across transcription traditions rather than merely being rediscovered separately in each file.

## Frozen sources
1. Primary IVTFF blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
2. Independent Takahashi blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

No manual harmonization, relabeling, glyph repair, or threshold tuning is permitted.

## Frozen extraction and matching
In each corpus independently, reuse exactly H60-H62:
- positive = existing single-certain-token `L*` label/object locus;
- control = running-text token from same folio;
- exact original token length matched;
- Currier/hand matched when metadata exist;
- deterministic control selection with seed `20261007`;
- running text excludes every annotated `L*` locus.

## Primary representation
Use only the already-frozen H62 edge-ablated interior representation:
- remove the original first and final glyph;
- interior fraction `o`;
- interior fraction `a`;
- interior fraction `y`.

For length-2 tokens the interior vector is `[0,0,0]` as frozen in H62.

No edge feature, token length, folio, quire, section, hand, Currier, annotation subtype, topology, or semantic proposal may enter the model.

## Bidirectional transfer
Run two frozen directions:
- **P→T**: train only on primary IVTFF; test only on Takahashi.
- **T→P**: train only on Takahashi; test only on primary IVTFF.

For each target quire `q`:
1. target test set = all target-corpus matched pairs in `q`;
2. source training set = all source-corpus matched pairs from quires other than `q`;
3. fit standardization **only on source training examples**;
4. fit the same nearest-class-mean classifier used in H60-H62 on source training examples;
5. transform target examples using source training means/SDs only;
6. predict the frozen target labels.

There is no target-corpus model fitting and no target-corpus standardization fitting.

A target quire is evaluable if it has >=10 matched target pairs and the source training set spans >=4 other quires with >=80 source training pairs.

Require >=4 evaluable target quires and >=80 aggregate target pairs per direction; otherwise that direction is **BLOCKED**.

## Primary statistics
For each direction report:
- aggregate balanced accuracy over all held-out target predictions;
- per-target-quire balanced accuracy;
- number of target quires with BA > 0.5.

## Matched source-label null
Exactly 999 randomizations per direction, seed `20261007`.

For each randomization independently swap class identities within every **source training pair** with probability 0.5, refit the source-only class centroids for every held-out-target-quire fold, and evaluate against the unchanged frozen target labels.

Target features, target labels, pair structure, quire membership, source/target corpora and source-only standardization remain fixed.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

This null asks whether the observed cross-transcription class mapping is stronger than arbitrary source-pair class assignment.

## Frozen decision
A direction receives **PASS_CROSS_TRANSCRIPTION_TRANSFER** iff all hold:
1. >=4 evaluable target quires;
2. >=80 aggregate target pairs;
3. 999/999 null randomizations complete;
4. aggregate BA > 0.55;
5. Monte Carlo p <= 0.01;
6. >=3 held-out target quires individually have BA > 0.5.

Experiment-level **PASS_BIDIRECTIONAL_CROSS_TRANSCRIPTION_TRANSFER** requires PASS in **both** P→T and T→P.

**FAIL** if executions are valid but the bidirectional gate is not met.

**BLOCKED** if either direction cannot meet frozen support requirements without altering the protocol.

## Interpretation ceiling
PASS would show that an edge-ablated functional token-form signature learned in one transcription transfers directly to an independently sourced transcription in both directions and across held-out quires. This would strongly support a stable manuscript-level production/register distinction rather than a file-specific classifier artifact.

It would still be FUNCTIONAL evidence only. It would not establish lexical identity, semantic class, gloss, language, cipher, plaintext, author or translation.

H63 remains FAIL regardless of H64.

Semantic identity: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
