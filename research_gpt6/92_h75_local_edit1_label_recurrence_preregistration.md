# H75 — Local edit-distance-1 label-to-paragraph recurrence

Status before execution: **NOT_RUN**.

## Motivation and question

H72 validly rejected the stronger prediction that strict single-token `L*` label forms recur **exactly** in local `P*` paragraph text under documentary/opportunity-matched permutation controls. H75 asks one narrower follow-up question fixed before execution:

> Do eligible label forms have a one-edit morphological neighbour in paragraph text on their own folio more often than expected when the same frozen label forms are reassigned among documentary-, length-, and opportunity-matched folio slots?

H75 does **not** search over stemmers, prefixes, suffixes, edit thresholds, feature weights, object subtypes, or semantic dictionaries. It tests one fixed relation only: Levenshtein edit distance exactly `1`.

## Frozen sources

Run the complete test independently in the same two admitted sources used by H72.

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

## Frozen label population

For each source independently:

1. use the same IVTFF page/header parser and markup cleaning as H72;
2. retain only certain `L*` records containing exactly one lowercase alphabetic token;
3. exclude any label record containing unresolved `?` material;
4. require label-token length **>=4**;
5. collapse duplicate `(folio, label_token)` observations so a form contributes at most one row per folio;
6. retain only folios containing at least one cleaned `P*` paragraph token.

The length >=4 gate is prospective and fixed to prevent one-edit matches among very short strings from dominating the statistic.

No visual subtype (`Lc`, `Lf`, etc.) is used as a predictor, stratum, or semantic interpretation.

## Frozen paragraph target and morphological relation

Only `P*` loci on the same folio count as paragraph text. `L*`, `C*`, `R*`, and other loci are excluded.

Paragraph candidate tokens must be lowercase alphabetic after the same cleaning and have length **>=4**.

For each eligible label row define:

`local_edit1_hit = 1`

iff at least one cleaned local `P*` token has ordinary character-level Levenshtein edit distance **exactly 1** from the label token.

Distance `0` is explicitly excluded, so exact matches tested by H72 do not count. Distances `>=2` do not count. Insertions, deletions, and substitutions each cost one. No transposition special case, glyph-equivalence table, token segmentation, prefix stripping, or learned representation is allowed.

The primary statistic is the mean `local_edit1_hit` over exchangeable label rows. Each label row contributes at most one hit regardless of how many paragraph neighbours it has.

## Frozen documentary/opportunity strata

Use the H72 stratification unchanged. Each row inherits:

- quire `$Q`;
- Currier language `$L`;
- hand `$H`;
- exact label-token length;
- paragraph opportunity quartile.

Paragraph opportunity is the number of cleaned `P*` tokens on the folio. Among eligible folios, deterministic quartiles `1..4` are assigned by rank `(P_token_count, folio_id)` exactly as in H72.

Permutation stratum:

`(Q, Currier, hand, label_token_length, P_opportunity_quartile)`.

A row is exchangeable only if its exact stratum contains label rows from at least **two distinct folios** and at least **4 total label rows**. Nonexchangeable rows are excluded and reported.

## Frozen null

Use exactly **9,999** permutations per source with seed `20261007`.

Within every exchangeable stratum independently:

1. keep folio slots and paragraph text fixed;
2. randomly permute label-token identities among rows;
3. recompute the fixed distance-1 local-hit relation;
4. compute the mean hit rate over all exchangeable rows.

This preserves the label-token multiset, label length, quire, Currier class, hand, paragraph-opportunity quartile, label-slot counts per folio, and each target folio's paragraph text.

Monte Carlo enrichment p:

`p = (1 + count(null_rate >= observed_rate)) / 10000`.

Report observed hits/rate, null mean, observed-minus-null lift, and 9,999-permutation p for each source.

## Frozen validity gates

Each source independently requires:

- >=60 exchangeable unique `(folio,label_token)` rows after the length >=4 filter;
- >=8 represented folios;
- >=5 exchangeable strata;
- at least 1 observed distance-1 local hit;
- exactly 9,999/9,999 permutations completed.

Failure of a validity/exchangeability/execution gate is **BLOCKED**, not FAIL.

## Familywise decision

The two source tests are one frozen family. Bonferroni alpha is `0.025` per source.

H75 = **PASS** only if **both** ZL and Takahashi independently:

- satisfy every validity gate;
- have observed distance-1 local recurrence rate > their own null mean; and
- have Monte Carlo `p <= 0.025`.

H75 = **FAIL** if both source tests are valid but either source fails either scientific criterion.

H75 = **BLOCKED** if either source fails a validity/execution/source-integrity gate.

Until a real execution completes, H75 is **NOT_RUN**.

## Interpretation boundary

A PASS would support replicated **local one-edit morphological-form recurrence** between label loci and paragraph text under the frozen controls. It would justify only a morphological-neighbour/lexical-anchor candidate at this fixed surface relation.

It would **not** identify a stem or morpheme, prove that labels name pictured objects, identify a language, establish a cipher, give a plaintext gloss, translate a token, or decipher the manuscript. Both sources transcribe the same manuscript and substantially share EVA conventions, so a PASS would also require a future cross-alphabet/independent-representation replication before stronger claims.

A FAIL would reject this fixed edit-distance-1 local-recurrence prediction. It would not prove that no morphology exists; it would close this particular prospectively fixed near-match route unless genuinely independent evidence motivates another preregistered representation.

H72 remains **FAIL** regardless of H75.
Historical visual-subtype and `Lc/Lf` results remain unchanged.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
