# H64 — Replicated five-feature decomposition of strict label vs paragraph signal

Status at registration: **NOT_RUN**.

## Question
Which, if any, of the five token-form variables frozen before H60 individually distinguish strict IVTFF label loci (L*) from paragraph loci (P*) in **both** the discovery transcription and an immutable independent transcription after familywise error control?

This is a decomposition of the already replicated H60/H63 effect. It is not a translation experiment.

## Frozen sources

### Source A — discovery transcription
- repository: `cesarjz/Voynich`
- commit: `47e6a77dc9d5cd570c375f4aff710fa4a0567278`
- path: `corpus/voynich_eva.txt`
- required Git blob SHA-1: `2a4533ab9bdfa85db9bad602d590978953055df1`

### Source B — independent transcription
- repository: `oklo/voynich_gpt`
- commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- path: `IT2a-n.txt`
- required Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Any blob mismatch => **BLOCKED**.

## Sample reconstruction
For each source independently, recreate the strict H60/H63 sample exactly:
- positive: certain single-token `L*` loci;
- control: tokens only from generic IVTFF `P*` loci;
- exact match on folio, Currier/hand metadata, and token length;
- deterministic control draw with seed `20261007` after sorting positives by `(folio, token, currier, hand)`;
- uncertain `?` label lines excluded as in H60/H63.

Expected reconstruction checks:
- Source A: 780 positive candidates, 495 matched pairs, 34 represented folios, 285 unmatched positives.
- Source B: 669 positive candidates, 388 matched pairs, 32 represented folios, 281 unmatched positives.

If either source has <60 matched pairs or <8 represented folios, or its reconstruction differs from the frozen counts above, H64 is **BLOCKED** rather than retuned.

## Five preregistered variables
For token `t`, exactly the H60 feature definitions:
1. `frac_o = count(o)/len(t)`
2. `frac_a = count(a)/len(t)`
3. `frac_y = count(y)/len(t)`
4. `starts_q = 1[t starts with q]`
5. `ends_y = 1[t ends with y]`

No absolute length, metadata, vocabulary identity, n-grams, or newly selected predictors enter H64.

## Effect statistic
For each source and feature, compute paired differences
`d_i = feature(L_i) - feature(P_i)`.
Report the raw mean paired difference and its sign.

The inferential statistic is the absolute paired studentized mean:
`T = |mean(d)| / (sd(d)/sqrt(n))` using sample standard deviation (`n-1`).
If all differences are identical and zero, `T=0`; otherwise a zero standard error is treated as an infinite statistic and reported explicitly.

## Familywise null
For each source separately:
- exactly **999** randomizations;
- seed `20261007` for Source A and `20261008` for Source B;
- on every randomization independently swap L/P identity within each matched pair, equivalently multiply each entire five-feature difference vector by `+1` or `-1`;
- recompute all five studentized statistics;
- retain the maximum absolute statistic across the five features.

For feature `j`, familywise Monte-Carlo p-value:
`p_FWER_j = (1 + count(maxT_null >= T_obs_j)) / 1000`.

This max-stat null controls selection among all five preregistered variables within each transcription.

## Replication criterion
A feature is a **replicated component** iff all are true:
1. raw mean difference is non-zero and has the same sign in Source A and Source B;
2. `p_FWER <= 0.05` in Source A;
3. `p_FWER <= 0.05` in Source B;
4. both sources complete 999/999 randomizations.

H64 overall **PASS** iff at least one of the five features is a replicated component.
H64 overall **FAIL** iff both source samples are valid and 999/999 randomizations complete, but no feature satisfies the replication criterion.
H64 is **BLOCKED** for source/sample/reconstruction/infrastructure failures.

## Interpretation boundary
PASS would identify one or more reproducible token-form components of the L-vs-P distinction. It does **not** establish what labels mean, whether a component is linguistic vs scribal/orthographic, the manuscript language, plaintext, cipher, translation, or decipherment.

Language identification: **NOT_RUN**  
Semantic identification: **NOT_RUN**  
Translation: **NOT_RUN**  
Decipherment: **NOT_RUN**
