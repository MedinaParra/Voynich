# H68 — Dual-transcription q-initial paired-prevalence replication preregistration

Status: **NOT_RUN**.

## Motivation
H67 adaptively localized the strict exact-consensus H66 edge signal to `starts_q`, while `ends_y` was negative. H68 is a simpler confirmatory measurement-replication test. It removes the nearest-class-mean classifier and asks whether the q-initial label-vs-running-text contrast is directly observable when the two frozen transcriptions are constructed and tested separately.

H68 is adaptive to H67 and therefore does not constitute an independent manuscript sample. Its purpose is measurement replication across two frozen transcriptions, not semantic inference.

## Frozen sources
- primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`;
- independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

The two corpora are parsed **separately**. No exact-consensus filtering is used in H68.

## Frozen pair construction per transcription
For each transcription independently:
1. a positive is a locus marked as label (`L...`) containing exactly one certain alphabetic token of length >=2;
2. candidate controls are running-text tokens from the same folio, same Currier assignment, same hand assignment, and exact token length;
3. a positive with no candidate control is excluded;
4. candidates are sorted and one control is selected deterministically using `random.Random(20261007)` for the primary transcription and `random.Random(20261008)` for the independent transcription, iterating positives in sorted `(locus, token)` order;
5. no token identity, prefix, suffix, interior glyph, illustration, section meaning, semantic proposal, or translation is used in matching.

## Frozen feature
The sole feature is:
- `starts_q(token)` = 1 if the token begins with EVA `q`, else 0.

No `ends_y` feature and no classifier are permitted.

## Primary statistic per transcription
For every matched pair i:

`d_i = starts_q(label_i) - starts_q(control_i)`.

Primary effect:

`delta_q = mean(d_i)`.

Report label q prevalence, control q prevalence, `delta_q`, pair count, per-quire `delta_q`, and the number of evaluable quires whose delta has the same sign as the corpus-wide effect.

## Null and inference
For each transcription independently, run exactly **999** deterministic within-pair swap permutations. On each permutation, swap label/control status with probability 0.5 inside every matched pair and recompute `delta_q`.

Use the two-sided Monte Carlo p-value:

`p = (1 + count(abs(null_delta) >= abs(observed_delta_q))) / 1000`.

No threshold, matching rule, feature, or direction may be changed after results are observed.

## Support gate
A transcription is evaluable only if:
- >=80 matched pairs;
- >=4 quires with >=10 matched pairs each;
- 999/999 permutations complete.

Pairs outside qualifying quires are excluded from the inferential statistic.

## Frozen replication gate
A transcription is **POSITIVE** iff:
1. support gate passes;
2. `abs(delta_q) >= 0.05`;
3. two-sided Monte Carlo `p <= 0.01`;
4. >=3 evaluable quires have per-quire delta with the same sign as the corpus-wide delta.

Experiment-level status:
- **PASS_REPLICATED_Q_REGISTER** iff both transcriptions are POSITIVE **and their `delta_q` signs agree**;
- **FAIL** if both are validly executed but the replication gate is not met;
- **BLOCKED** if either transcription fails the frozen support/infrastructure requirements.

Because the experiment-level claim requires both transcription-specific tests to pass, the joint replication claim is an intersection requirement; no post-hoc selection of the better transcription is permitted.

## Interpretation ceiling
PASS would confirm that the H67 q-initial localization is visible as a direct orthographic-register prevalence difference in each frozen transcription separately, without classifier machinery or exact-consensus selection.

PASS would **not** establish what `q` means, whether labels name depicted objects, a language, cipher, plaintext, semantic gloss, translation, or decipherment.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
