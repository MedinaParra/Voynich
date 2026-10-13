# H74 — Suffix-conditioned fifth-character `a` test

Status: **NOT_RUN**

## Motivation
H72/H73 localized the replicated label-vs-paragraph EVA `a` excess to full-token index `t[4]` (the fifth character) and showed positive direction at exact lengths 6 and 7. H69 showed that globally matching the final character reduced the broader internal-`a` signal. H74 therefore asks the focused question: does the fifth-character effect itself survive conditioning on the final character?

## Frozen sources
- Source A blob `2a4533ab9bdfa85db9bad602d590978953055df1` from `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`.
- Source B blob `7f491b574b65e5fba6b553e57372c3fa50e10fec` from `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`.

Seeds: A `20261007`; B `20261008`.

## Aligned labels
A label event is eligible only if the complete IVTFF locus occurs in both sources, each source has a certain single-token `L*` reading, the cleaned EVA token is identical in both sources, Currier and hand metadata agree, and token length is >=6.

## Strict paragraph baseline with boundary conditioning
For each eligible label and source independently, the comparison pool contains **all** generic `P*` token occurrences satisfying:
- same folio;
- same Currier and hand;
- exact same token length;
- exact same first two EVA characters;
- exact same **final EVA character**;
- length >=6.

The event enters H74 only if the conditioned pool is non-empty in **both** sources. No individual control is sampled.

## Sole confirmatory outcome
At full-token index `4` (fifth EVA character), define:

`r_i = I(label_i[4] == 'a') - mean_{p in conditioned P pool}(I(p[4] == 'a'))`.

No other character, position, feature, prefix or suffix statistic is tested confirmatorily.

## Primary statistic
Average event residuals within folio, then compute the equal-folio-weighted mean residual across represented folios.

## Sample threshold
H74 is executable only if the common conditioned sample contains:
- >= **25** aligned events;
- >= **10** represented folios.

Otherwise H74 is **BLOCKED**. Thresholds must not be changed after outcome inspection.

## Null
Run exactly **999** folio-level sign-flip permutations separately in each source. One random sign is assigned per folio and applied to all residuals from that folio. Recompute the equal-folio statistic for every permutation. Use a one-sided Monte Carlo p-value for positive enrichment.

## PASS criterion
H74 is **PASS** iff in both frozen sources:
- sample thresholds are met;
- 999/999 permutations complete;
- equal-folio-weighted mean residual >0;
- one-sided Monte Carlo `p <= 0.05`.

Otherwise a valid execution is **FAIL**. Blob/sample failure is **BLOCKED**.

## Secondary descriptives
Report event-weighted residual and exact-length-specific residual means for lengths with >=5 events. These do not alter PASS/FAIL.

## Interpretation boundary
PASS would show that the fifth-character EVA `a` excess is not explained simply by differences in the first-two-character family or final-character distribution. It would still not establish a morpheme, phonetic value, semantics, language, plaintext, cipher mechanism, translation or decipherment.
