# H73 — Length-stratified left-anchor test for H72 position 3

Status: **NOT_RUN**

## Motivation
H72 localized the replicated internal EVA `a` excess to body position 3, i.e. full-token index `t[4]` (the fifth EVA character). However, that absolute position has different suffix-relative meanings at different token lengths: in exact length 6 it is the penultimate character; in exact length 7 it is the antepenultimate character. H73 asks whether the positive residual survives in both exact-length strata, which would favor an absolute-left positional interpretation over a single fixed suffix-relative explanation.

## Frozen sources
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1` from `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`.
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec` from `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`.

Seeds: A `20261007`, B `20261008`.

## Event reconstruction
Recreate the H71/H72 exact-prefix aligned event set. A label event must have an identical certain single-token `L*` reading in both sources, identical Currier/hand metadata, length >=5, and at least one strict `P*` occurrence in both sources from the same folio, same Currier/hand, exact length and exact first two EVA characters. Use all compatible `P*` occurrences as the local baseline in each source.

## Frozen exact-length strata
H73 tests exactly two strata selected from the H72 count audit before inspecting length-specific outcomes:
- exact token length **6**;
- exact token length **7**.

At both lengths the tested absolute-left position is `t[4]`. At length 6 this equals the penultimate character; at length 7 it equals the antepenultimate character.

H73 is executable only if:
- length 6 has >= **30** events and >= **8** represented folios;
- length 7 has >= **15** events and >= **8** represented folios.

Otherwise H73 is **BLOCKED** and thresholds must not be lowered.

## Residual
For each event and source, at full-token index `t[4]` define:

`r_i = I(label_i[4] == 'a') - mean_{p in exact-prefix P pool}(I(p[4] == 'a'))`.

Within each exact-length stratum, first average residuals within folio, then calculate the equal-folio-weighted stratum mean.

## Primary combined statistic
The primary statistic is the equal-stratum-weighted mean of the two stratum means:

`T = (mean_len6 + mean_len7) / 2`.

Thus the larger length-6 sample cannot dominate the length-7 sample.

## Null
Run exactly **999** folio-level sign-flip permutations separately in each source. One sign is drawn per folio and applied jointly to every event from that folio in both length strata. Recompute both stratum means and `T` on every permutation. Use a one-sided Monte Carlo p-value for `T > 0`.

## PASS criterion
H73 is **PASS** iff, in both frozen sources:
- both sample thresholds are met;
- 999/999 permutations complete;
- the length-6 stratum mean is >0;
- the length-7 stratum mean is >0;
- combined `T > 0`;
- one-sided Monte Carlo `p <= 0.05`.

Otherwise a valid execution is **FAIL**. Source/sample failure is **BLOCKED**.

## Interpretation boundary
PASS would support positive `a` residual at the same absolute fifth EVA character across two token lengths where that character occupies different positions relative to the end. This would favor, but not prove, a left-anchored positional constraint. It would not establish morphology, phonetics, semantics, language, plaintext, cipher mechanism, translation or decipherment.
