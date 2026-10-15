# H67 — Richer IVTFF label-source admissibility audit result

Status: **PASS**.

This records execution of the preregistered data-admissibility protocol in `76_h67_richer_label_source_admissibility_preregistration.md`. It is not a semantic test.

## Execution evidence

- Workflow: `H67 richer label-source admissibility`.
- Run: `37613580641` (run number 1).
- Job: `112766461834` (`h67-richer-label-source-audit`).
- Experimental branch head executed: `cb341234eefbeecbabf65dc803e7778e02a38415` (PR merge checkout `d5ec94026d3adfc00fc22c1b9d5494f398bb0680`).
- Frozen external repository: `noah-chelednik/voynich-data`.
- Frozen external commit: `472ef7366606a799fc8f1044c037e06b413f6ddd`.
- Frozen path: `data_sources/cache/IT_ivtff_1a.txt`.
- Source byte count: **344691**.
- Source Git blob SHA-1: `4201d762a4bd6e9014e0e796d72dd5c3efb597da`.
- Source SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`.
- Required `#=IVTFF` header: present.
- Required provenance header `# Extracted from LSI_ivtff_0d.txt`: present.
- Artifact: `h67-richer-label-source-audit-results`, ID `11479201247`.
- Artifact SHA256: `96f12b4b2dd681860a45187ccf147ed8961478cfadc2fcfdc10b34bec4cb3021`.

## Audited inventory

Total `L*`:
- records: **548**;
- nonempty records: **472**;
- known tokens: **531**;
- known types: **449**.

Frozen object-related subtype counts:

| Unit | known tokens | known types | eligible >=20 |
|---|---:|---:|---|
| Lp | 4 | 4 | no |
| Lc | 40 | 40 | yes |
| Lf | 216 | 198 | yes |
| Ln | 64 | 60 | yes |
| Lt | 50 | 47 | yes |
| Ls | 68 | 67 | yes |
| Lz | 37 | 36 | yes |
| La | 7 | 7 | no |

Eligible frozen object units: **6** (`Lc`, `Lf`, `Ln`, `Lt`, `Ls`, `Lz`). The preregistered gate required at least four.

H67: **PASS**.

## Provenance boundary

The admitted candidate explicitly declares `Extracted from LSI_ivtff_0d.txt`. It therefore **does not count as an independent transcription tradition**. H67 only establishes that a richer LSI-derived IVTFF layer exists with enough explicit object-related label subtypes to make a new multiclass confound-controlled experiment feasible.

This does not rescue the historical `Lc` vs `Lf` FAIL, does not satisfy independent replication, and does not establish semantics.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
