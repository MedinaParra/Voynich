# H72 — Internal EVA `a` position localization

Status: **NOT_RUN**

## Motivation
H71 passed in both frozen transcriptions: after conditioning on folio, Currier/hand, exact token length and exact first-two-character prefix, `L*` labels retain a positive internal EVA `a` residual relative to strict `P*` paragraph text. H72 asks whether that residual is localized to reproducible absolute positions inside the token rather than being a diffuse composition effect.

## Frozen sources
- Source A: `cesarjz/Voynich` commit `47e6a77dc9d5cd570c375f4aff710fa4a0567278`, `corpus/voynich_eva.txt`, Git blob `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Source B: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, `IT2a-n.txt`, Git blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Seeds: source A `20261007`; source B `20261008`.

## Aligned events and paragraph baseline
Recreate the H71 event set. A label event is eligible only if:
- the complete IVTFF locus is present in both sources;
- both readings are certain single-token generic `L*` loci;
- the cleaned EVA token is identical in both sources;
- Currier and hand metadata agree between sources;
- token length is >=5;
- in **both** sources there is at least one generic `P*` token occurrence on the same folio, same Currier/hand, exact same token length and exact same first two EVA characters.

For each source independently, retain **all** such compatible `P*` occurrences as the local baseline pool; do not sample one control.

## Position definition
For token `t`, the H72 internal region is the same H71 body:

`body(t) = t[2:-1]`

Internal position `k=1` is `t[2]`, `k=2` is `t[3]`, and so on. The final character is never tested.

At a position `k`, an event contributes only when that position exists in the label. Because paragraph controls are exact-length matched, the corresponding position exists in every token in its pool.

For source `s`, define the position residual for event `i`:

`r_i(k) = I(label_i[k] == 'a') - mean_{p in compatible P pool}(I(p[k] == 'a'))`

where the indexing above refers to body position `k`.

## Count-only position eligibility
A body position enters the confirmatory family if, in the common aligned H71 event set, it has:
- >= **60** contributing label events;
- >= **15** represented folios.

Position eligibility uses only token lengths and folio counts, never the `a` outcomes. At least **2** positions must be eligible or H72 is **BLOCKED**. Thresholds must not be changed after outcome inspection.

## Primary statistic
For each eligible position and source:
1. average event residuals within folio;
2. compute the equal-folio-weighted mean residual across represented folios.

This is the observed position statistic.

## Familywise null
Run exactly **999** folio-level sign-flip permutations separately for each source. On a permutation, one random sign (+1/-1) is assigned to each folio and applied jointly to every residual and every eligible position from that folio, preserving within-folio and cross-position dependence.

For each permutation, recompute every eligible position statistic and record the **maximum** statistic across eligible positions. For each observed position `k`, calculate a one-sided max-stat familywise p-value:

`p_FWER(k) = (1 + # {max_null >= observed_k}) / (1 + 999)`.

## PASS criterion
H72 is **PASS** iff:
- both frozen blobs verify exactly;
- >=2 positions satisfy the count-only eligibility rule;
- each source completes 999/999 permutations;
- there is at least **one identical body position `k`** in both sources for which:
  - observed mean residual > 0;
  - `p_FWER(k) <= 0.05` in source A;
  - `p_FWER(k) <= 0.05` in source B.

Otherwise a valid execution is **FAIL**. Blob/sample/position-family failure is **BLOCKED**.

## Secondary descriptive outputs
Report for every eligible position in each source:
- contributing events and folios;
- observed equal-folio-weighted residual;
- event-weighted residual;
- familywise p-value.

Also report the same-prefix family composition of contributing events, descriptively only. No secondary result can rescue a failed primary test.

## Interpretation boundary
PASS would support a reproducible positional localization of the internal EVA `a` excess in labels relative to exact-prefix, exact-length strict paragraph text. It would not establish a morpheme, phonetic value, word class, semantics, language, plaintext, cipher mechanism, translation or decipherment.
