# H76 — Cross-label-class validation of the fifth-character `a` residual

Status: **NOT_RUN**

## Motivation
H72/H73 identified a replicated label-vs-paragraph EVA `a` enrichment at full-token index `t[4]` (the fifth character). H74 and H75 showed that stronger suffix conditioning and a universal left-vs-penultimate interpretation are not established. H76 therefore tests a different question using an external, pre-existing IVTFF classification rather than a post hoc split of the H75 result: does the fifth-character residual have the same positive direction across two physically and functionally distinct label classes?

IVTFF defines `Lz` as zodiac-element labels and `Lc`/`Lf` as pharmaceutical container/herb-fragment labels. These classes are frozen before H76 outcome inspection.

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Seeds: A `20261007`; B `20261008`.

## Frozen label classes
Exactly two confirmatory classes:
1. **ZODIAC**: complete IVTFF locus subtype `Lz`.
2. **PHARMA**: complete subtype `Lc` or `Lf`.

No other label subtype may enter the confirmatory test.

## Event reconstruction
A label event is eligible only if:
- the complete IVTFF locus occurs in both sources;
- each source has a certain cleaned single-token label reading;
- label subtype is identical between the two sources and belongs to one of the two frozen classes;
- cleaned EVA token is identical between sources;
- Currier and hand metadata agree;
- token length is >=6;
- both sources contain at least one generic `P*` token occurrence on the same folio, same Currier/hand, exact token length and exact first two EVA characters.

For each source independently, **all** compatible `P*` occurrences form the local baseline pool. No individual control is sampled.

## Outcome
At full-token index `t[4]`, for each event/source:

`r_i = I(label_i[4] == 'a') - mean_{p in compatible P pool}(I(p[4] == 'a'))`.

No other position or character is confirmatory.

## Count-only executability
Each frozen class must contain:
- >= **15** events;
- >= **6** represented folios.

Across the two classes combined there must be >= **40** events and >= **12** unique folios. Otherwise H76 is **BLOCKED** and thresholds must not be lowered.

## Class statistics
Within each class and source:
1. average residuals within folio;
2. compute the equal-folio-weighted class mean.

Both class means must be positive for PASS.

## Primary cross-class statistic
The primary statistic is the **equal-class-weighted mean** of the two class means:

`T = (mean_ZODIAC + mean_PHARMA) / 2`.

This prevents the larger class from dominating.

## Null
Run exactly **999 folio-level sign-flip permutations** separately in each source. One random sign is drawn per folio and applied to all residuals from that folio, including across classes if a folio contributes to both. Recompute both class means and `T` for every permutation.

Use a one-sided Monte Carlo p-value for `T > 0`.

## PASS criterion
H76 is **PASS** iff in both frozen sources:
- all sample thresholds are met;
- 999/999 permutations complete;
- ZODIAC class mean >0;
- PHARMA class mean >0;
- primary equal-class statistic `T >0`;
- one-sided Monte Carlo `p <= 0.05`.

Otherwise a valid execution is **FAIL**. Source/sample failure is **BLOCKED**.

## Secondary descriptives
Report within PHARMA the separate `Lc` and `Lf` counts and mean residuals where >=5 events exist; report prefix counts by class. These are descriptive only and cannot rescue PASS/FAIL.

## Interpretation boundary
PASS would support generalization of the fifth-character `a` enrichment across two pre-existing label classes tied to different manuscript contexts. It would not show that the labels have the same semantics or grammatical category, nor establish morphology, phonetics, language, plaintext, cipher mechanism, translation or decipherment.
