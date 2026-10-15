# H72 — Local exact label-to-paragraph recurrence

Status before execution: **NOT_RUN**.

## Question

Do strict single-token `L*` label forms recur **exactly** in `P*` paragraph text on their own folio more often than expected when the same frozen label forms are reassigned among documentary- and opportunity-matched folios?

This test is deliberately different from the failed `Lc` vs `Lf` morphology route. It does not use visual subtype codes at all. It tests local lexical reuse of label forms into paragraph text.

## Frozen sources

Run the complete test independently in both already admitted transcription sources:

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

Any hash mismatch is **BLOCKED**.

## Frozen label population

For each source independently:

1. parse page metadata from IVTFF page headers;
2. retain only certain `L*` records containing exactly one lowercase alphabetic token of length >=2 after the same markup cleaning used in H60-H66;
3. exclude any label record containing unresolved `?` material;
4. collapse duplicate `(folio, label_token)` observations so one exact label form on one folio contributes at most one row;
5. retain only folios containing at least one `P*` paragraph token after cleaning.

No visual subtype (`Lc`, `Lf`, etc.) is used as a predictor, stratum, or interpretation.

## Frozen paragraph target

Only `P*` loci on the same folio count as paragraph text. `L*`, `C*`, `R*`, and other loci are excluded from the target corpus.

For every eligible label row define the observed binary outcome:

`local_hit = 1` iff the exact label token occurs at least once among cleaned `P*` tokens on that same folio; otherwise `0`.

The primary statistic is the mean `local_hit` across exchangeable label rows (local exact-recurrence rate). Binary recurrence is used prospectively so repeated occurrences of a very frequent form cannot dominate the statistic.

## Frozen documentary/opportunity strata

Each label row inherits:

- quire `$Q` from the page header;
- Currier language `$L`;
- hand `$H`;
- exact label-token length;
- paragraph opportunity quartile.

Paragraph opportunity is the total number of cleaned `P*` tokens on that folio. Within each transcription independently, rank eligible folios by this count and assign deterministic quartiles `1..4` using rank order `(P_token_count, folio_id)`, splitting the ranked folio list into four groups whose sizes differ by at most one.

The exact permutation stratum is:

`(Q, Currier, hand, label_token_length, P_opportunity_quartile)`.

A row is `exchangeable` only if its exact stratum contains label rows from at least **two distinct folios** and at least **4 total label rows**. Nonexchangeable rows are excluded before computing the observed statistic and are reported.

## Frozen null

Use exactly **9,999** permutations per transcription with seed `20261007`.

Within every exact exchangeable stratum independently:

1. keep the folio slots fixed;
2. randomly permute the label-token identities among those rows;
3. recompute whether each permuted token occurs in the fixed target folio's `P*` text;
4. compute the mean local-hit rate across all exchangeable rows.

Thus every permutation preserves:

- the complete label-token multiset;
- global paragraph frequency of each token;
- number of label slots per folio;
- quire;
- Currier class;
- hand;
- label length;
- paragraph-text opportunity quartile.

No classifier, token feature model, edit distance, fuzzy matching, or semantic dictionary is used.

Monte Carlo p for enrichment is:

`p = (1 + count(null_rate >= observed_rate)) / 10000`.

Also report the null mean rate and observed-minus-null-mean recurrence lift.

## Frozen validity gates

Each transcription independently requires:

- >=60 exchangeable unique `(folio,label_token)` rows;
- >=8 represented folios;
- >=5 exact permutation strata;
- at least 1 observed exact local hit;
- exactly 9,999/9,999 permutations completed.

Failure of a sample/exchangeability gate is **BLOCKED**, not FAIL.

## Familywise decision

The two transcription tests form one frozen family. Bonferroni controls the two primary tests at `alpha = 0.05`, so each source must satisfy `p <= 0.025`.

H72 = **PASS** only if **both** ZL and Takahashi independently satisfy all validity gates and show:

- observed local exact-recurrence rate > null mean; and
- Monte Carlo `p <= 0.025`.

H72 = **FAIL** if both tests are valid but either source fails either scientific criterion.

H72 = **BLOCKED** if either source cannot satisfy the frozen validity/execution requirements.

Before execution H72 remains **NOT_RUN**.

## Interpretation boundary

A PASS would support **local exact lexical reuse between label loci and paragraph text** under strong documentary, length, opportunity, and token-frequency-preserving controls, replicated in two frozen transcriptions.

It would still not identify what any repeated token means, prove that a label names its illustrated object, establish a natural language, identify a cipher, translate text, or decipher the manuscript. Because both sources transcribe the same manuscript, a PASS would also not constitute independent-manuscript replication.

A FAIL would mean the strong label-vs-paragraph form distinction from H60-H66 does not extend to this specific exact local-reuse prediction under the frozen controls.

Historical `Lc`/`Lf` and visual-subtype FAIL results remain unchanged regardless of H72.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
