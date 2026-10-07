# H71 — q-initial running-text line-position mechanism test

Status: **NOT_RUN**.

## Motivation
H70 failed its preregistered magnitude gate after restricting the running comparator to line-initial tokens, despite a residual negative label contrast in both transcriptions. This suggests that line position may explain a substantial part of the H68/H69 q effect. H71 tests that mechanism directly using **running text only**, without labels.

This is an adaptive structural test motivated by H70. It cannot rescue H70 and is not a semantic experiment.

## Frozen sources
- primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`;
- independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Sources are parsed independently.

## Frozen running-text construction
For each certain non-label running-text locus containing >=1 alphabetic token:
- the first token is assigned position class **INITIAL**;
- every subsequent token is assigned position class **INTERNAL**.

Loci containing `?` are excluded. Label loci are excluded entirely.

Define exact stratum `(folio, Currier, hand, token_length)`. Include only strata containing at least one INITIAL and at least one INTERNAL token instance. Retain all token instances in included strata.

## Frozen feature
Sole feature: `starts_q(token)`.

## Primary statistic
For stratum s:
- `nI_s` = INITIAL token count;
- `nT_s` = INITIAL + INTERNAL token count;
- `qI_s` = q-initial INITIAL count;
- `qT_s` = q-initial total count.

Expected q-initial INITIAL tokens under within-stratum position exchangeability:
`E[qI_s] = nI_s * qT_s / nT_s`.

Primary statistic:
`D_pos = sum_s(qI_s - E[qI_s]) / sum_s(nI_s)`.

Positive `D_pos` means q-initial tokens are enriched at running-line beginnings after exact control for folio, Currier, hand, and token length.

## Null
Exactly 999 deterministic conditional permutations per transcription. Within each exact stratum, choose exactly `nI_s` token instances as pseudo-INITIAL, preserving position-class counts, total q count, folio, Currier, hand, and length.

Seeds:
- IVTFF `20261013`;
- Takahashi `20261014`.

Two-sided Monte Carlo p:
`(1 + count(abs(D_null) >= abs(D_obs))) / 1000`.

## Support gate
Each transcription requires:
- >=200 included INITIAL tokens;
- >=50 exact strata;
- >=4 evaluable quires, each with >=20 included INITIAL tokens;
- 999/999 permutations.

Only strata belonging to evaluable quires enter inference.

## Frozen decision
A transcription is **POSITIVE** iff:
1. support gate passes;
2. `D_pos >= 0.05`;
3. p <= 0.01;
4. >=3 evaluable quires have `D_pos > 0`.

Overall **PASS_REPLICATED_Q_LINE_INITIAL_ENRICHMENT** iff both transcriptions are POSITIVE.

**FAIL** if both execute validly but the joint gate is missed.

**BLOCKED** if either source fails support/infrastructure requirements.

No threshold, position class, stratum, feature, source, or direction may be changed after result inspection.

## Interpretation ceiling
PASS would establish a replicated structural fact: EVA q-initial tokens are enriched at running-line beginnings under exact covariate conditioning. This would provide a concrete non-semantic mechanism for part of the attenuation observed from H69 to H70 and would constrain future generative models of Voynichese.

It would not establish what `q` means, label semantics, language, cipher/plaintext, translation, or decipherment.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
