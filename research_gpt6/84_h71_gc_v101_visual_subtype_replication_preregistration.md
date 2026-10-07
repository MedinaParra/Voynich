# H71 — GC/v101 single-source visual-subtype morphology replication

Status before execution: **NOT_RUN**.

## Rationale

H70 failed its preregistered requirement for two non-EVA replication-eligible sources. Only the frozen Glen Claston (`GC`) v101 transcription had sufficient exact-locus coverage for all four H68-admitted classes.

H71 does **not** rescue or redefine H70. It opens a new, explicitly single-source, cross-alphabet falsification test.

## Question

Using IT only to supply the frozen visual subtype annotation at an exact manuscript locus, can token morphology measured exclusively in the aligned GC/v101 transcription discriminate either of the H68-admitted visual subtype contrasts out of folio under exact documentary and GC-token-length matching?

## Frozen sources

Repository: `noah-chelednik/voynich-data`, commit `472ef7366606a799fc8f1044c037e06b413f6ddd`.

- IT annotation source: `IT_ivtff_1a.txt`, SHA-256 `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`.
- GC predictor source: `GC2a-n.txt`, SHA-256 `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`.

Any hash mismatch is **BLOCKED**.

## Frozen alignment

- Align IT and GC exclusively by exact `(page_id, locus_number)`.
- The IT locus supplies only the visual subtype annotation and documentary metadata.
- GC supplies the **only transcription token used as predictor data**.
- A locus is admitted only if IT and GC each contain exactly one known token at that exact locus after frozen markup/uncertainty cleaning.
- No fuzzy alignment, transliteration mapping, edit-distance matching, or manual correction is allowed.

## Frozen contrast family

Exactly two contrasts are tested:

A. `Lc` vs `Lf`, IT documentary strata `O|A|1` and `S|A|1`.

B. `Ln` vs `Lt`, IT documentary stratum `M|B|2`.

No other subtype may be added after execution. H68-excluded `Ls` and `Lz` remain excluded.

## Frozen pair construction

For each contrast independently:

1. use exact-locus-aligned single-token GC records only;
2. group records by exact `(Q,L,H,folio,GC_token_length)`;
3. within each cell, sort GC tokens lexicographically within class;
4. create `min(n_class0,n_class1)` one-to-one pairs;
5. discard unmatched class excess;
6. no pair may cross quire, Currier class, hand, folio, or **GC/v101 token length**.

IT token length is never used as a matching variable or predictor.

## Frozen validity gates

Each contrast must independently yield:

- >=20 matched GC pairs;
- >=5 represented folios;
- at least one training folio remaining for every held-out folio.

If either frozen contrast fails a validity gate, H71 = **BLOCKED**. We do not drop the weaker contrast after seeing counts.

## Frozen GC/v101 representation

Use exactly five token-shape features computed from the GC token only:

1. `unique_fraction`;
2. `singleton_type_fraction`;
3. `max_frequency_fraction`;
4. `adjacent_equal_fraction`;
5. `first_last_equal`.

These features are invariant to arbitrary bijective renaming of v101 symbols. Token length is exactly matched and is not a predictor.

No EVA token, GC character identity, full-token identity, n-gram, prefix/suffix identity, or transliteration correspondence is admitted.

## Frozen classifier

For each contrast:

- leave one **folio** out;
- z-standardize GC features on training folios only;
- fit nearest class centroid on training folios only;
- classify held-out GC tokens;
- aggregate predictions across all held-out folios;
- primary score = balanced accuracy.

No parameter may be fitted on a held-out folio.

## Frozen permutation null

Use exactly **9,999** paired permutations, seed `20261007`.

For every permutation and every contrast:

1. independently swap class labels inside each frozen matched pair with probability 0.5;
2. rerun the complete leave-one-folio-out fit/predict procedure under permuted labels;
3. compute permuted balanced accuracy.

Predictions are not frozen from the observed model; the classifier is refit under every null permutation.

## Familywise correction

The two frozen contrasts form one family. For each permutation calculate:

`max(BA_A - 0.5, BA_B - 0.5)`.

For each observed contrast:

`p_FWER = (1 + count(null_max >= observed_BA - 0.5)) / 10000`.

Retain the stringent candidate threshold: familywise `p <= 0.001`.

## Decision

H71 = **PASS** only if:

- both contrasts satisfy all validity gates;
- all 9,999/9,999 permutations complete; and
- at least one frozen contrast has observed BA > 0.5 and familywise `p <= 0.001`.

H71 = **FAIL** if both contrasts are valid but neither meets the scientific criterion.

H71 = **BLOCKED** if either frozen contrast lacks sufficient exact GC-matched pairs/folios or execution cannot satisfy the frozen protocol.

Before execution H71 is **NOT_RUN**.

## Interpretation boundary

A PASS permits only: **`single-source v101 visual-subtype morphology candidate`** for the passing contrast(s).

Because H70 failed the two-source coverage requirement, even a H71 PASS is not an independent multi-source confirmation. H69 remains FAIL and must be reported alongside any discordant H71 result.

A PASS does not establish lexical meaning, object names, language, plaintext, translation, or decipherment. Full lexical-anchor promotion would still require a separately preregistered running-text recurrence link and independent replication.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
