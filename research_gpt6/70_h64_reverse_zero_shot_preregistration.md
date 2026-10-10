# H64 — Reverse zero-shot cross-transcription label-form transfer preregistration

Status: **NOT_RUN**.

## Motivation
H63 transferred a strict L* label-versus-P* paragraph classifier from frozen Zandbergen-Landini (ZL) to frozen Takahashi without fitting on Takahashi. H64 freezes the directional mirror before execution: train only on Takahashi and predict ZL zero-shot.

The purpose is falsification of asymmetric source-specific transfer. This is not a semantic or translation test.

## Frozen sources
Training source:
- Takahashi IT2a-n Git blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.
- `oklo/voynich_gpt@2d7c61c387ad6962de730caf73c48612bc8f6957`, path `IT2a-n.txt`.

Replication/test source:
- Zandbergen-Landini Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- `cesarjz/Voynich@47e6a77dc9d5cd570c375f4aff710fa4a0567278`, path `corpus/voynich_eva.txt`.

No other transcription or manual recoding may be introduced.

## Frozen extraction and matching
Independently in each transcription, apply the H60/H62 rules unchanged:
- positive: certain single-token generic `L` locus;
- control pool: generic `P` loci only;
- exclude C*, R*, and L* from controls;
- same cleaning policy;
- match same folio, exact token length, and Currier/hand metadata when available;
- deterministic control selection with seed `20261007`.

The ZL test set must contain >=60 matched pairs across >=8 folios, otherwise **BLOCKED**.

## Frozen predictors
Exactly the H60-H63 five predictors: fraction `o`, fraction `a`, fraction `y`, starts `q`, ends `y`.

No length, folio, hand, Currier state, section, locus subtype, token identity, illustration class, semantics, or test-source-derived parameter is allowed as predictor.

## Zero-shot evaluation
For every ZL test folio `f`:
1. build the frozen Takahashi matched-pair training set;
2. exclude every Takahashi training pair from folio `f`;
3. fit standardization parameters only on the remaining Takahashi training tokens;
4. fit the same nearest-class-mean classifier only on those standardized Takahashi tokens;
5. transform and classify all ZL matched pairs from folio `f` with those frozen training parameters.

No ZL test token may contribute to standardization, class means, model selection, or hyperparameter choice.

Primary statistic: aggregate balanced accuracy over all ZL test pairs.

## Null
Exactly 999 deterministic within-pair identity swaps on the ZL test pairs, seed `20261007`. Takahashi-trained predictions remain fixed; no refitting occurs under the null.

Monte Carlo p = `(1 + count(null_BA >= observed_BA))/1000`.

## Negative control
Descriptive only: matched ZL P-vs-P using a second P-only token where possible, evaluated with the same Takahashi-trained models. It is not part of PASS.

## Decision
H64 is **PASS** iff all hold:
1. ZL test set >=60 pairs;
2. >=8 represented ZL folios;
3. 999/999 permutations complete;
4. zero-shot BA > 0.5;
5. Monte Carlo p <= 0.05.

**FAIL** if valid execution misses either inferential threshold.

**BLOCKED** if source verification, frozen extraction, or sample requirements fail without protocol change.

Before execution: **NOT_RUN**.

## Interpretation boundary
PASS would demonstrate bidirectional zero-shot transfer of the strict label-versus-paragraph token-form distinction across the two frozen transcription traditions. FAIL would show that H63 transfer is directional and would narrow the claim accordingly; H63 would remain PASS but bidirectional robustness would be rejected.

Even PASS would not identify label semantics, a language, plaintext, cipher, or translation. Shared EVA-family conventions and shared manuscript/locus annotations remain possible explanations.

Historical Lc-vs-Lf and other subtype/semantic-anchor tests remain **FAIL**.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
