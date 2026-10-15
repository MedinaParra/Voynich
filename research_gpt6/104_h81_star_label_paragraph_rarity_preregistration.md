# H81 — f68r1 star-label global paragraph-rarity test

Status before execution: **NOT_RUN**.

## Purpose

H79 established a robust one-to-one spatial association between 29 independently annotated f68r1 stars and 29 label positions. H80 then rejected the preregistered hypothesis that neighboring stars carry unusually similar label character forms after exact token-length control.

H81 tests a different, narrower prediction motivated by an **individual-name / panel-local identifier** model:

> Are the f68r1 star-associated label forms unusually rare in running paragraph text, compared with other label forms from the same documentary context and exact token lengths?

The control group is itself composed of label-locus tokens. Therefore a positive result cannot be reduced to the already established generic `label` versus `paragraph` form distinction from H60–H63.

H81 does **not** claim that rare forms are proper names. It tests only a panel-specific rarity prediction.

## Frozen sources

Run the complete test independently in both already admitted frozen transcriptions.

### Zandbergen–Landini

- repository source: `cesarjz/Voynich`
- frozen commit: `47e6a77dc9d5cd570c375f4aff710fa4a0567278`
- path: `corpus/voynich_eva.txt`
- required Git blob SHA-1: `2a4533ab9bdfa85db9bad602d590978953055df1`

### Takahashi IT2a

- repository source: `oklo/voynich_gpt`
- frozen commit: `2d7c61c387ad6962de730caf73c48612bc8f6957`
- path: `IT2a-n.txt`
- required Git blob SHA-1: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Any source hash mismatch is **BLOCKED**.

## Frozen H79/H80 target inventory

H81 freezes the H80-resolved f68r1 star-associated Yale/EVA forms before inspecting their paragraph frequencies in either frozen H81 source.

Use only the 27 target forms whose H80 token lengths are 4 through 8 inclusive. The two singleton-length targets (`odchecthy`, length 9; `toeeodcthy`, length 10) are prospectively excluded because exact-length control sampling would have little or no exchangeability.

Frozen target forms:

- length 4: `otys`, `olor`, `otol`, `otor`;
- length 5: `otydy`, `okeor`, `ockhy`, `ocphy`;
- length 6: `okoaly`, `octhey`, `otcsey`, `otcsdo`, `oiinar`, `okoldy`, `ykchdy`, `okshor`;
- length 7: `okodaly`, `chocphy`, `ytchody`, `otykchs`, `ofcheor`, `ordaiin`;
- length 8: `otcheody`, `cphocthy`, `otochedy`, `okeeodal`, `dolchedy`.

No target may be added, removed, respelled, stemmed, or merged after execution.

## Frozen parsing rules

Use the same IVTFF-style cleaning convention already frozen in H60–H75:

- strip angle/square/curly markup and `@number;` markers;
- lowercase;
- extract only standalone ASCII alphabetic tokens matching `[a-z]{2,}`;
- unresolved `?` material is excluded from label controls;
- page metadata are read from IVTFF page headers where available.

For locus type, remove any leading `@`, `+`, `*`, `=` from the locator and use its first locus letter.

- `L*` loci define the label-control inventory;
- `P*` loci define running paragraph text and the primary recurrence counts.

Other locus types do not contribute paragraph-frequency counts.

## Frozen target admissibility in each source

For each source independently:

1. obtain the page-header metadata `(Q, Currier L, H)` for `f68r1`;
2. for every frozen H81 target form, search the entire source token inventory for that exact string;
3. a target is `source-admitted` iff the exact string occurs at least once anywhere in that frozen source;
4. retain only source-admitted targets for that source.

Source validity requires:

- at least **20 of the 27** frozen target forms are source-admitted;
- at least **4 distinct exact token-length strata** remain represented;
- at least **3 source-admitted targets** in each represented length stratum except that a stratum containing only 1–2 admitted targets may remain only if at least four other strata satisfy the >=3-target rule.

Failure is **BLOCKED**, not FAIL.

No approximate spelling or cross-transcription edit-distance rescue is permitted.

## Frozen matched label-control universe

For each source independently, construct a set of unique control tokens from certain single-token `L*` rows satisfying all of:

1. token matches `^[a-z]{2,}$` exactly after frozen cleaning;
2. row contains no unresolved `?` material;
3. page metadata `(Q, Currier L, H)` are exactly equal to the metadata of `f68r1` in that same source;
4. folio is **not** `f68r1`;
5. token is not one of the 27 frozen H81 target strings;
6. token length is one of the source-admitted target lengths.

Collapse duplicate control token strings so each form enters the control universe once.

Exact-length sampling validity requires, for every represented target length `k`:

`number_of_control_tokens_length_k >= number_of_admitted_targets_length_k`.

Additionally require:

- at least **25 unique matched control tokens** overall;
- at least **4** length strata with at least one target and enough matched controls.

Failure is **BLOCKED**. There is no fallback to looser `(Q,L)` or length-only matching.

## Frozen paragraph-frequency outcome

For each source independently, count exact occurrences of every token string across **all cleaned `P*` paragraph tokens in the complete manuscript**.

For every admitted target/control token define:

`P_count(token) = exact number of occurrences in all P* loci`.

Primary per-token transformed outcome:

`r(token) = log(1 + P_count(token))`

using the natural logarithm.

Primary target statistic:

`T_obs = mean r(token)` over all source-admitted H81 target forms.

Lower values mean greater rarity/absence from running paragraph text.

Also report descriptively:

- median `P_count`;
- fraction with `P_count == 0`;
- raw mean `P_count`.

These descriptive quantities are not additional PASS tests.

## Frozen matched-set null

Use exactly **9,999** random matched control sets per source.

Seeds:

- ZL: `20261012`;
- Takahashi: `20261013`.

For every draw and every exact token-length stratum independently:

1. let `n_k` be the number of source-admitted H81 target forms of length `k`;
2. uniformly sample without replacement exactly `n_k` control forms from the frozen matched control pool of length `k`;
3. combine all sampled length strata;
4. compute the same mean `log(1 + P_count)` statistic.

Thus every null set has exactly the same admitted target count and exact token-length distribution as the star-label target set, while matching the f68r1 `(Q, Currier L, H)` documentary context through the control inventory.

Lower-tail Monte Carlo p:

`p = (1 + count(null_T <= T_obs)) / 10000`.

Also report null mean/SD and `T_obs - null_mean`.

## Frozen familywise decision

The two transcription tests form one conjunction. Bonferroni controls the two source tests at family alpha 0.05, so each source uses `alpha = 0.025`.

H81 = **PASS** only if **both** sources independently:

1. satisfy every integrity/sample/control/permutation gate;
2. have `T_obs < null_mean`;
3. have Monte Carlo `p <= 0.025`;
4. complete exactly 9,999/9,999 matched-set draws.

H81 = **FAIL** if both source tests are valid but either source fails either scientific criterion.

H81 = **BLOCKED** if either source fails source integrity, target admission, documentary matching, exact-length control sufficiency, or execution completeness.

No target list, metadata match, locus definition, transform, seed, or alpha may be changed after viewing output.

## Interpretation boundary

A PASS would support the narrow statement that the **f68r1 star-associated label inventory is unusually paragraph-rare even relative to other labels from the same documentary context and exact length distribution**, replicated in two frozen transcriptions of the same manuscript. This would be compatible with panel-local identifiers or proper-name-like usage, but would not prove either interpretation.

A FAIL would mean the strong H79 object↔label pairing does not extend to this panel-specific paragraph-rarity prediction under the frozen matched-label controls.

A BLOCKED result would mean the public frozen transcriptions do not provide enough exact-string/documentary-matched exchangeability for this test.

Both sources describe the same manuscript and related EVA-family conventions; a PASS is not independent-manuscript replication.

H79 geometric star↔label pairing (A0): **PASS**.
H80 local star-topology label morphology: **FAIL**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
