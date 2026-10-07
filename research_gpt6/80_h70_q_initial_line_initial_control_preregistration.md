# H70 — q-initial depletion against line-initial running text

Status: **NOT_RUN**.

## Motivation
H69 showed q-initial depletion in labels after exact conditioning on folio, Currier, hand, and token length using all running-token instances. A remaining non-semantic explanation is positional grammar: EVA `q` may be associated with particular positions in running lines, while label loci are structurally separate. H70 therefore uses the running-text position most plausibly enriched for a leading glyph: the **first certain token of each running-text locus/line**.

H70 is an adversarial positional-confound test. It is adaptive to H69 and cannot establish semantics.

## Frozen sources
- primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`;
- independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

The corpora are parsed and tested separately.

## Frozen construction
For each transcription:
1. label token = certain single alphabetic token of length >=2 at a locus marked `L...`;
2. running comparator = **only the first token** from each certain non-label text locus that contains at least one token;
3. define exact stratum `(folio, Currier, hand, token_length)`;
4. include a stratum only if it contains >=1 label token and >=1 line-initial running token;
5. retain all labels and all eligible line-initial running token instances in included strata.

A locus containing `?` is excluded from both label and running constructions. No token identity, other prefix/suffix, interior glyph, section interpretation, illustration, or semantic hypothesis is used.

## Frozen feature and statistic
Sole feature: `starts_q(token)`.

Use the H69 conditional statistic:
`D = sum_s(qL_s - nL_s*qT_s/nT_s) / sum_s(nL_s)`
where the total tokens in each stratum contain the included labels plus line-initial running comparators only.

Negative D means q-initial tokens are depleted among labels relative to exactly matched line-initial running text.

## Null
Exactly 999 conditional permutations per transcription. Within each exact stratum choose exactly `nL_s` of all stratum token instances as pseudo-labels, preserving stratum membership, label count, total q count, folio, Currier, hand, length, and comparator position class.

Seeds:
- IVTFF: `20261011`;
- Takahashi: `20261012`.

Two-sided Monte Carlo p:
`(1 + count(abs(D_null) >= abs(D_obs))) / 1000`.

## Support gate
For each transcription:
- >=50 included label instances;
- >=4 evaluable quires, each with >=8 included labels;
- >=20 included exact strata;
- 999/999 permutations.

Only strata from evaluable quires enter inference.

## Frozen decision
A transcription is **POSITIVE** iff:
1. support gate passes;
2. `D <= -0.05`;
3. two-sided p <= 0.01;
4. >=3 evaluable quires have D < 0.

Overall **PASS_LINE_INITIAL_Q_DEPLETION** iff both transcriptions are POSITIVE.

**FAIL** if both execute validly but the joint gate is missed.

**BLOCKED** if either source fails the support/infrastructure gate.

No threshold, positional class, matching rule, source, direction, or feature may change after inspection.

## Interpretation ceiling
PASS would reject the simple explanation that H68/H69 q depletion is produced merely because labels are being compared with arbitrary running positions while q is concentrated at the beginning of running lines. It would show depletion even against line-initial running tokens under exact matching.

It would not establish the meaning of `q`, label-object identity, language, cipher/plaintext, semantic gloss, translation, or decipherment.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
