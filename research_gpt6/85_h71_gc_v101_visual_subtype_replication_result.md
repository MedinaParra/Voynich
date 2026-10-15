# H71 — GC/v101 single-source visual-subtype morphology replication result

Status: **BLOCKED**.

This records execution of the preregistered protocol in `84_h71_gc_v101_visual_subtype_replication_preregistration.md`. The workflow executed successfully, but one frozen contrast failed the preregistered sample-validity gate. No classifier score or permutation p-value was computed.

## Execution evidence

- Workflow: `H71 GC v101 visual-subtype replication`.
- Run: `37615429911` (run number 1), conclusion `success`.
- Job: `112772498715` (`h71-gc-v101-visual-subtype-replication`), conclusion `success`.
- Experimental branch head executed: `80f3606264fe7ecd9f1ce96d2e91e3b2e398e4d7` (PR merge checkout `8ac12e9c56bd9cbf338c9e7c3fce25f04667d48a`).
- IT SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`.
- GC/v101 SHA-256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`.
- Artifact: `h71-gc-v101-visual-subtype-replication-results`, ID `11478949631`.
- Artifact SHA256: `1899acf23f149815ce40c84cac99c7681f8c550301f389b026eb3d30f6c34343`.

## Exact-locus aligned GC inventory

Single-token IT↔GC exact-locus rows under the frozen strata: **274**.

- `Lc`: **30**;
- `Lf`: **158**;
- `Ln`: **53**;
- `Lt`: **33**.

## Lc vs Lf

After exact `(Q,L,H,folio,GC_token_length)` matching:

- matched pairs: **20**;
- represented folios: **8**;
- unmatched exclusions: `Lc` **10**, `Lf` **138**;
- sample-validity status: **PASS**.

No BA or p-value was computed because the family-level preregistration required both frozen contrasts to satisfy their validity gates before statistical execution.

## Ln vs Lt

After exact `(Q,L,H,folio,GC_token_length)` matching:

- matched pairs: **16**;
- represented folios: **7**;
- unmatched exclusions: `Ln` **37**, `Lt` **17**;
- preregistered minimum: **20 matched pairs** and >=5 folios;
- sample-validity status: **BLOCKED** due to insufficient matched-pair count.

## Decision

Because one frozen contrast failed a mandatory sample-validity gate, the protocol stopped with:

- permutations requested: 9,999;
- permutations completed: **0**;
- scientific status: **BLOCKED**.

H71: **BLOCKED**.

The threshold is not lowered post hoc and the valid `Lc` vs `Lf` subset is not silently promoted to a family PASS.

## Conservative interpretation

The GC/v101 source has enough raw exact-locus coverage to align all four classes, but exact within-folio/documentary/GC-length pairing leaves only 16 `Ln` vs `Lt` pairs. Under the preregistered design, this is insufficient to execute the two-contrast replication family.

H70 remains **FAIL** and H69 remains **FAIL**. H71 provides no positive or negative morphology evidence because the scientific test did not run.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
