# H77 — Length-conditioned morphology generalization

Status: **NOT_RUN**

## Question
Does allowing the label-vs-paragraph positional EVA-`a` residual profile to vary by exact token length improve prediction on held-out folios relative to a single rigid positional profile?

This is a confirmatory follow-up to H72/H73/H74/H75. It is not a translation test.

## Frozen sources
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Source A and B must both match exactly or the experiment is **BLOCKED**.

## Sample construction
Use only label loci that:
1. are present in both frozen transcriptions at the same locus;
2. have identical certain single-token EVA transcription in both sources;
3. have token length >= 6;
4. have at least one strict paragraph (`P*`) comparison token in the same folio, same Currier/hand, exact token length, and exact first two EVA characters, separately in both sources.

No `C*`, `R*`, or non-`P*` comparison loci are allowed.

## Eligible exact-length strata
For each exact token length, count aligned events before looking at the H77 score. A length stratum is eligible only if it has:
- at least 15 aligned events; and
- at least 8 represented folios.

At least 2 exact-length strata must be eligible, otherwise H77 is **BLOCKED**. Thresholds may not be lowered after seeing the counts.

## Frozen feature family
For every aligned event and source, construct a three-dimensional residual vector using the first three body positions after the two-character prefix:
- body position 1 = full-token index `t[2]`
- body position 2 = `t[3]`
- body position 3 = `t[4]`

At each position the residual is:

`I(label character == 'a') - mean[I(P-control character == 'a')]`

where the mean is over all compatible strict-`P*` controls in that source.

No other characters, n-grams, suffixes, metadata, token length as a numeric predictor, semantic labels, or manuscript images enter H77.

## Models
Evaluation is leave-one-folio-out (LOFO).

For each held-out folio, fit templates using training folios only.

### Rigid model
One 3-position residual template shared across all eligible token lengths. The training template is computed with equal-folio weighting.

### Length-conditioned model
One separate 3-position residual template for each eligible exact token length. Each template is computed with equal-folio weighting within that length.

For every held-out event, predict its residual vector using the corresponding template. Compute mean squared error (MSE). Within a held-out folio, average event MSEs first so every folio has equal weight.

Primary fold statistic:

`delta_folio = MSE_rigid - MSE_length_conditioned`

Positive values favor the length-conditioned morphology model.

Primary source statistic is the equal-folio mean of `delta_folio`.

## Randomization test
For each source independently:
- exactly 999 randomizations;
- deterministic seeds: Source A `20261007`, Source B `20261008`;
- one joint random sign per evaluable held-out folio applied to its `delta_folio`;
- one-sided p-value for mean delta > 0 using `(1 + exceedances)/(1 + 999)`.

This tests whether the held-out improvement is systematically positive across folios rather than being driven by a few dense pages.

## Minimum evaluation support
H77 requires:
- at least 2 eligible exact-length strata;
- at least 12 evaluable held-out folios;
- 999/999 randomizations in each source.

Otherwise **BLOCKED**.

## PASS criterion
H77 is **PASS** only if all of the following hold in both frozen transcriptions:
1. the primary equal-folio mean `delta_folio` is > 0;
2. one-sided p <= 0.05;
3. all minimum support thresholds above are met;
4. 999/999 randomizations complete.

Otherwise a valid execution is **FAIL**.

## Interpretation boundary
PASS would support a length-conditioned positional morphology difference between labels and locally matched paragraph text that generalizes across held-out folios. FAIL would reject that specific predictive formulation. Neither outcome identifies language, semantics, plaintext, cipher mechanism, translation, or decipherment.

- Language identification: **NOT_RUN**
- Semantic identification: **NOT_RUN**
- Translation: **NOT_RUN**
- Decipherment: **NOT_RUN**
