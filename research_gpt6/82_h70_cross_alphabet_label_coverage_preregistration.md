# H70 — Cross-alphabet visual-label locus coverage audit

Status before execution: **NOT_RUN**.

## Purpose

Before attempting any cross-transcription visual-subtype replication, audit whether the four H68-admitted visual classes can be mapped from the frozen Takahashi IVTFF label annotation layer onto publicly frozen non-EVA transcription sources by exact manuscript locus ID.

This is a coverage/provenance gate, not a morphology or semantic test.

## Frozen repository and sources

Repository: `noah-chelednik/voynich-data`, commit `472ef7366606a799fc8f1044c037e06b413f6ddd`.

Frozen files and SHA-256 values from that commit's `data_sources/checksums_all.txt`:

- annotation/reference source `IT_ivtff_1a.txt` (Takahashi EVA): `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`;
- `CD2a-n.txt` (Currier-D'Impero / Currier alphabet): `edc18e6de699c50d575925d4f469685ccbbe22c9755b9b8a3b002f83253cbde5`;
- `FG2a-n.txt` (Friedman Study Group / FSG alphabet): `a1460a05ff610a406e62b4095a8f8e88c04653c1ef4aa5ad6428ddb1ac01fe06`;
- `GC2a-n.txt` (Glen Claston / v101 alphabet): `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`.

Any source hash mismatch is **BLOCKED**.

## Frozen class/locus scope

Only the H68-admitted classes and exact strata are eligible:

- `Lc` and `Lf` in `O|A|1` or `S|A|1`;
- `Ln` and `Lt` in `M|B|2`.

`Ls` and `Lz` remain excluded because H68 found no documentary-exchangeable strata for them.

## Frozen alignment rule

1. Parse the IT file and identify every eligible `L*` record by exact manuscript locus `(page_id, locus_number)`.
2. The IT locus subtype is used **only** as the frozen visual annotation; alternative sources are not required to carry the same subtype code.
3. Align each alternative source to IT solely by exact `(page_id, locus_number)`, matching the public mismatch-index convention used by the source repository.
4. A locus is `single-token-mappable` for a source only if both IT and that source contain exactly one known transcription token at that exact locus after removing IVTFF markup and unresolved `?` material.
5. No fuzzy text matching, edit-distance alignment, folio-neighbor substitution, or manual remapping is permitted.

## Reported coverage

For each of `CD`, `FG`, and `GC`, report by class:

- IT eligible locus count;
- exact locus present in source;
- single-token-mappable locus count;
- distinct mapped folio count.

Also report pairwise source overlap and the number of IT loci mappable in all three non-EVA sources.

## Frozen source-eligibility gate

A non-EVA source is `replication-eligible` only if its single-token-mappable inventory contains:

- `Lc` >=20 tokens across >=5 folios;
- `Lf` >=20 tokens across >=5 folios;
- `Ln` >=20 tokens across >=5 folios;
- `Lt` >=20 tokens across >=5 folios.

H70 = **PASS** only if at least **two** of the three non-EVA sources are replication-eligible.

H70 = **FAIL** if all frozen sources/hash/parsing/alignment execute validly but fewer than two sources meet the replication-eligibility gate.

H70 = **BLOCKED** for source/hash/parsing failures that prevent the audit.

Before execution H70 is **NOT_RUN**.

## Interpretation boundary

A PASS would establish only that a separately preregistered cross-alphabet visual-subtype replication is technically feasible on at least two non-EVA transcription sources. It would not itself establish independence of scribal observation, semantics, language, translation, or decipherment.

A FAIL would mean these three frozen alternate sources do not provide sufficient exact-locus coverage under the stringent single-token mapping rule; it would not prove that no other transcription can do so.

H69 remains **FAIL** regardless of H70.
