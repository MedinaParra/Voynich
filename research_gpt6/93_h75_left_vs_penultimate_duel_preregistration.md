# H75 — Fifth-character versus penultimate-position duel

Status: **NOT_RUN**

## Motivation
H72 localized a replicated label-vs-paragraph EVA `a` excess to full-token index `t[4]`. H73 showed that this absolute-left position remains positive at exact lengths 6 and 7 even though its suffix-relative location changes. H74, which additionally forced exact final-character matching, retained a positive point estimate but failed its p<=0.05 criterion. H75 does not attempt to rescue H74. It directly compares the H72 left-anchored candidate against a suffix-relative competitor within the same tokens and the same exact-prefix paragraph baselines.

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Seeds: A `20261007`; B `20261008`.

## Event reconstruction
Recreate the H71 exact-prefix aligned label sample. A label event must have:
- the same complete IVTFF locus in both sources;
- a certain cleaned single-token generic `L*` reading in each source;
- identical EVA token in both sources;
- identical Currier and hand metadata;
- token length **>=7**;
- at least one generic `P*` token occurrence in both sources from the same folio, same Currier/hand, exact token length and exact first two EVA characters.

For each source independently, use **all** compatible `P*` occurrences as the baseline pool. No single control is sampled.

The >=7 restriction is count/design based: at length 6 `t[4]` is itself penultimate, so the two hypotheses cannot be distinguished. H72's count audit showed 27 events / 14 folios at body position 4, which corresponds to token length >=7, before this duel outcome was defined.

## Competing positions
For event `i` and source `s`, define two residuals:

**Left-anchor candidate**
`L_i = I(label_i[4] == 'a') - mean_P I(P[4] == 'a')`

**Suffix-relative competitor**
`R_i = I(label_i[-2] == 'a') - mean_P I(P[-2] == 'a')`

The primary paired contrast is:

`D_i = L_i - R_i`.

For length 7, `t[4]` is antepenultimate and `t[-2]` is penultimate. For longer words the two positions remain distinct.

## Sample threshold
H75 is executable only if the common sample has:
- >= **25** events;
- >= **10** represented folios.

Otherwise H75 is **BLOCKED** and the thresholds must not be lowered.

## Primary statistic
Average `D_i` within each folio, then compute the equal-folio-weighted mean contrast `T` across represented folios.

Also report equal-folio and event-weighted means for `L` and `R` separately as descriptives.

## Null
Run exactly **999** folio-level sign-flip permutations separately in each source. One random sign is assigned to each folio and multiplied by every `D_i` in that folio. Recompute `T` on each permutation. Use a one-sided Monte Carlo p-value for `T > 0`.

## PASS criterion
H75 is **PASS** iff in both frozen sources:
- sample thresholds are met;
- 999/999 permutations complete;
- equal-folio left residual `L > 0`;
- primary contrast `T = L-R > 0`;
- one-sided Monte Carlo `p <= 0.05`.

Otherwise a valid execution is **FAIL**. Blob/sample failure is **BLOCKED**.

## Secondary descriptives
Report by exact token length (for lengths represented by >=5 events):
- event count;
- mean `L`;
- mean `R`;
- mean `D`.

These do not change PASS/FAIL.

## Interpretation boundary
PASS would support the fifth EVA character as a better locus of the label-specific `a` enrichment than the generic penultimate position among length>=7 labels, favoring a left-anchored morphotactic interpretation. It would not establish a morpheme boundary, phonetic value, semantics, language, plaintext, cipher mechanism, translation or decipherment.
