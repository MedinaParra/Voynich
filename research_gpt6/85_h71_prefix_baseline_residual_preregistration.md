# H71 — Exact-prefix paragraph-baseline residual test

Status: **NOT_RUN**

## Motivation and registration status
H70 was **BLOCKED** before outcome evaluation because its hierarchical >=15-events-per-family rule left 78 pooled events against a frozen threshold of 80. Its sample audit nevertheless established, without evaluating the H70 outcome, that 122 aligned label events have at least one strict-P control with the same folio, Currier/hand, exact token length and exact first two EVA characters in both frozen transcriptions.

H71 is a new estimator, not a lowered H70 threshold. It uses every compatible paragraph token to estimate a local exact-prefix baseline, then performs inference at the folio level. The hypothesis, statistic and PASS criterion below are frozen before any H71 residual is inspected.

## Question
After conditioning on folio, Currier/hand, exact token length and exact first two EVA characters, do aligned `L*` labels still contain more **internal EVA `a`** than the local strict paragraph-text (`P*`) baseline?

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, `corpus/voynich_eva.txt`, Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, `IT2a-n.txt`, Git blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Seeds: source A `20261007`; source B `20261008`.

## Aligned labels
A label event is eligible only if:
- the complete IVTFF locus occurs in both sources;
- each source has one certain cleaned single-token `L*` reading;
- the EVA token is identical between sources;
- Currier and hand metadata are identical between sources;
- token length is >=5.

## Exact-prefix strict-P baseline
For an eligible label token `t`, construct a strict-P comparison pool independently in each source from **all token occurrences** satisfying:
- generic locus type `P*` only;
- same folio;
- same Currier metadata;
- same hand metadata;
- exact same token length;
- exact same first two EVA characters as `t`;
- token length >=5.

The label event enters H71 only if this pool is non-empty in **both** sources. No single control is sampled.

For any token `x`, define:

`body(x) = x[2:-1]`

`internal_a(x) = count('a' in body(x)) / len(body(x))`

For each label event and source, define the local paragraph baseline as the arithmetic mean `internal_a` over **all token occurrences** in its compatible P pool. The event residual is:

`r_i = internal_a(label_i) - mean_P_compatible(internal_a)`.

## Independence unit and primary statistic
To prevent pages with many labels from dominating inference, first average event residuals within folio. The primary statistic is the **equal-folio-weighted mean** of those folio residual means.

Also report the event-weighted mean residual as descriptive context.

## Null
Run exactly **999 folio-level sign-flip permutations** separately in each source. In each permutation, multiply every residual from a given folio by the same randomly selected +1 or -1 sign, preserving all within-folio dependence.

Recompute the equal-folio-weighted primary statistic each time. Use a one-sided Monte Carlo p-value for positive enrichment.

## Sample threshold
H71 is executable only if the common exact-prefix sample contains:
- >= **100 aligned label events**;
- >= **15 represented folios** in both sources;
- both frozen blobs verify exactly.

Otherwise H71 is **BLOCKED**. These thresholds must not be changed after outcome inspection.

## PASS criterion
H71 is **PASS** iff in both frozen sources:
- sample thresholds are met;
- 999/999 folio-level permutations complete;
- equal-folio-weighted mean residual > 0;
- one-sided Monte Carlo p <= 0.05.

Otherwise a valid execution is **FAIL**.

## Secondary descriptive outputs
Without affecting PASS/FAIL, report:
- event-weighted mean residual;
- counts and mean residuals by exact two-character prefix for prefixes with >=5 aligned events;
- number of compatible P occurrences contributing to each source overall.

No secondary component may rescue a failed primary test.

## Interpretation boundary
PASS would support a replicated internal-`a` difference between labels and strict paragraph text after conditioning on initial two-character family, folio, Currier/hand and exact length. It would not establish that `a` is a morpheme, its phonetic value, semantics, a language, plaintext, cipher mechanism, translation, or decipherment.
