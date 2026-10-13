# H70 — Prefix-family conditioned internal `a` enrichment — Result

Scientific status: **BLOCKED**

This execution was valid at the infrastructure level, but the preregistered sample threshold was not met. No H70 outcome statistic was evaluated and the threshold is not lowered.

## Execution evidence
- GitHub Actions run: `37641645539`
- Job: `112861863904`
- Head commit executed: `27076b9a9becdb8e9da5fba3506e979c326588d7`
- Artifact: `h70-prefix-family-internal-a-results`
- Artifact ID: `11491733726`
- Artifact SHA-256: `697bfa73b2a50f20fe5acb3e3905aed689d0004b6e0649692cb01e68dc8db1d2`
- Source A blob verified: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob verified: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Frozen sample audit
The exact-prefix, same-folio, same-Currier/hand, exact-length control screen produced `122` aligned control-eligible events before family thresholding.

Prefix-family counts included:
- `ot`: 37
- `ok`: 24
- `ch`: 17
- `ol`: 10
- `da`: 7
- `qo`: 6
- remaining families: < 5 each.

The preregistered >=15-event rule therefore retained exactly three eligible families: `ch`, `ok`, `ot`.

Those families contained **78 paired events across 24 folios**. The preregistration required **>=80** pooled events, >=3 families and >=8 folios. The pooled-event criterion missed by 2 events.

## Decision
**BLOCKED**, not FAIL.

The implementation stopped before computing the confirmatory family-conditioned `a` statistic or its 999-permutation null. The 80-pair threshold is not changed post hoc.

## Interpretation boundary
H70 provides no positive or negative evidence about the family-conditioned internal `a` hypothesis. It only establishes that the preregistered hierarchical family design did not have enough retained observations under its frozen threshold.

Language identification, semantic identification, translation and decipherment remain **NOT_RUN**.
