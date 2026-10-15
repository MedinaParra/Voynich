# H68 — Visual-subtype documentary-confound identifiability audit

Status before execution: **NOT_RUN**.

## Purpose

H67 established that the frozen LSI-derived IT IVTFF source contains six object-related `L*` subtypes with >=20 known tokens. H68 asks a necessary prior question before any multiclass morphology/semantic score:

> Is there enough overlap among those visual subtypes within documentary strata to distinguish a subtype signal from trivial quire/Currier/hand segregation?

H68 is an identifiability/data-geometry audit, not a semantic test.

## Frozen source

Use exactly the H67 source:

- `noah-chelednik/voynich-data`
- commit `472ef7366606a799fc8f1044c037e06b413f6ddd`
- `data_sources/cache/IT_ivtff_1a.txt`
- expected Git blob SHA-1: `4201d762a4bd6e9014e0e796d72dd5c3efb597da`
- expected SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`

Any hash mismatch is **BLOCKED**.

## Frozen candidate classes

Only the six H67-eligible classes are admitted:

`Lc`, `Lf`, `Ln`, `Lt`, `Ls`, `Lz`.

No class may be added or removed after seeing H68 overlap counts.

## Frozen parsing and metadata

Reuse H67 known-token parsing. For each folio page header read exactly:

- `$Q` = quire/documentary grouping used here as the quire code;
- `$L` = Currier-language metadata code;
- `$H` = hand metadata code.

Each known token from an admitted `L*` subtype inherits the current folio header metadata.

Report counts by:

- class;
- folio;
- quire `$Q`;
- Currier `$L`;
- hand `$H`;
- exact documentary stratum `(Q,L,H)`.

## Frozen exchangeability definition

An exact `(Q,L,H)` stratum is `exchangeable` only if:

1. it contains known tokens from at least **two** of the six frozen classes; and
2. each participating class contributes at least **5** known tokens inside that stratum.

A class is `confound-eligible` only if:

1. it contributes at least **20** known tokens total (already required by H67);
2. it contributes at least **15** known tokens to exchangeable strata in total; and
3. those exchangeable tokens occur on at least **3 distinct folios**.

## Future-test feasibility gate

H68 = **PASS** only if all of the following hold:

- at least **3** frozen classes are confound-eligible;
- exchangeable strata collectively contain at least **60** known tokens;
- exchangeable tokens span at least **8 distinct folios**;
- at least **2** distinct exact `(Q,L,H)` exchangeable strata exist.

H68 = **FAIL** if source/hash/parsing are valid but these preregistered overlap conditions are not met. A FAIL means a morphology classifier on this source would be too entangled with documentary metadata for the planned semantic interpretation.

H68 = **BLOCKED** only for source/hash/parsing failure.

Before execution H68 is **NOT_RUN**.

## Interpretation boundary

A PASS only permits construction of a separately preregistered confound-controlled multiclass visual-subtype experiment. It does not itself support visual semantics or lexical anchors.

A FAIL would not show that the labels lack semantics. It would show that this particular annotated source cannot cleanly identify subtype morphology independently of frozen documentary groupings.

Historical `Lc`-vs-`Lf` and topology-conditioned lexical-anchor tests remain **FAIL** regardless of H68.
