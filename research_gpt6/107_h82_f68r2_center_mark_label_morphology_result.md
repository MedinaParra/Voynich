# H82 — f68r2 centre-mark ↔ label-morphology result

Status: **FAIL_EXPLORATORY**.

This records the completed execution of the prospectively frozen exploratory protocol in `106_h82_f68r2_center_mark_label_morphology_preregistration.md`.

The workflow, source-integrity, sample, exchangeability, and permutation gates all completed successfully. The preregistered scientific criteria did not.

Because the external source table had been inspected during hypothesis selection and its own annotation was not fully blind, H82 was prospectively capped at exploratory status regardless of outcome.

H82 is a visual-class ↔ character-form test only. It does not identify semantics, a celestial catalogue, star names, language, plaintext, translation, or decipherment.

## Execution evidence

- Branch: `experiment/h58-strict-l-vs-p`.
- Workflow: `H82 f68r2 center-mark label morphology`.
- Run: `37645427621` (run number 2), conclusion `success`.
- Job: `112874811506` (`h82-f68r2-center-mark-label-morphology`), conclusion `success`.
- Experimental head: `27b1813c0e48974518456154920fc7cba27afae9`.
- PR merge checkout: `74451f492de66618a52060d2c0cc235ae1a9b475`.
- Artifact: `h82-f68r2-center-mark-label-morphology-results`, ID `11494721529`.
- Artifact SHA256: `a2aeb2aa83e98379f7834b3bbc0b7e05b938e386bebffeab2edc4ed0de314587`.
- Artifact size: 1,564 bytes.

Infrastructure: **PASS**.

## Frozen source integrity

External source:

- repository: `RN-Top/Voynich`;
- revision: `1eb6c0d1e98fb56acaadc0095c4d88a4a1c5bed0`;
- path: `analyses/star_centres_f68r2_r3.csv`;
- expected Git blob SHA-1: `b19bbeae51334ab124f05f081b5dc6e07ef2ae42`;
- observed Git blob SHA-1: `b19bbeae51334ab124f05f081b5dc6e07ef2ae42`.

Source-integrity gate: **PASS**.

## Frozen mechanical filtering

Raw f68r2 rows: **23**.

Three rows failed the prospectively frozen exact lowercase-ASCII token rule and were excluded without repair:

- star 1: `o@167olchchy` — contains the encoded special/gallows marker;
- star 19: `odair.chol` — contains punctuation/multiple-token structure;
- star 23: `ok[eeee]or` — contains bracketed editorial material.

No marker decoding, punctuation removal, bracket expansion, fuzzy spelling correction, or hand-reading substitution was permitted.

Valid sample:

- total: **20**;
- marked centre (`ring`/`dot`): **5**;
- plain centre: **15**;
- distinct exact token lengths: **6** (`5,6,7,8,9,10`);
- star IDs unique: yes.

All frozen sample gates passed.

## Exact-length exchangeability

Exact-length class inventory:

| Length | Marked | Plain | Mixed |
|---:|---:|---:|:---:|
| 5 | 1 | 2 | yes |
| 6 | 1 | 7 | yes |
| 7 | 1 | 1 | yes |
| 8 | 1 | 3 | yes |
| 9 | 1 | 1 | yes |
| 10 | 0 | 1 | no |

- mixed exact-length strata: **5**;
- movable positions: **19**;
- movable marked positions: **5**.

Frozen requirements were >=10 movable positions, >=3 mixed strata and >=4 movable marked positions.

Exact-length exchangeability gate: **PASS**.

## Observed morphology separation

Frozen distance: ordinary character-level Levenshtein distance divided by the longer token length.

Observed means:

- marked↔plain, `D_between`: **0.7208941798941798**;
- marked↔marked, `D_marked`: **0.7049603174603175**;
- plain↔plain, `D_plain`: **0.7190249433106577**;
- frozen within-class mean, `D_within`: **0.7119926303854875**;
- primary statistic `S = D_between - D_within`: **+0.008901549508692264**.

Thus the raw statistic is in the preregistered positive direction, but the magnitude is very small.

Descriptive token lengths:

- marked mean length: **7.0**;
- plain mean length: **6.8**.

## Null A — unrestricted visual-class assignment

- seed: `20261014`;
- permutations: **19,999/19,999**;
- null mean `S`: **-0.000017098256651306254**;
- null SD: **0.03151548081108239**;
- observed `S`: **0.008901549508692264**;
- upper-tail Monte Carlo p: **0.35665**.

Frozen criterion: `p <= 0.025`.

Unrestricted criterion: **FAIL**.

## Null B — exact-length-preserving visual-class assignment

- seed: `20261015`;
- permutations: **19,999/19,999**;
- null mean `S`: **0.006403218819293184**;
- null SD: **0.028327555472623882**;
- observed `S`: **0.008901549508692264**;
- upper-tail Monte Carlo p: **0.40225**.

Frozen criterion: `p <= 0.025`.

Exact-length-preserving criterion: **FAIL**.

The observed separation is especially unremarkable under the exact-length-preserving null: its value lies close to the null centre.

## Frozen decision

H82 required the conjunction:

1. `S > 0` — **PASS**;
2. unrestricted `p <= 0.025` — **FAIL**;
3. exact-length-preserving `p <= 0.025` — **FAIL**;
4. all 19,999 permutations in both nulls complete — **PASS**.

H82: **FAIL_EXPLORATORY**.

## Conservative interpretation

The externally annotated f68r2 centre class (`ring`/`dot` versus `plain`) does not show the preregistered separation in attached label character form.

The small positive raw contrast is compatible with random reassignment under both the unrestricted and exact-token-length-preserving nulls. In particular, exact length does not conceal a strong character-form association: `p=0.40225` after preserving exact length within every movable stratum.

Together with H80, this gives two different negative morphology results on the astronomical foldout: local star adjacency on f68r1 did not organize label character similarity, and the discrete centre-mark class on f68r2 did not separate label forms under the frozen test.

This does **not** show that the visual marks lack meaning, that the labels are arbitrary, or that they are not names. It rejects only the tested prediction that these visual relations/classes are encoded by gross character-form similarity under ordinary normalized Levenshtein distance.

Do not tune alternative glyph equivalences, stem rules, visual-class merges, distances, or row repairs on this same f68r2 sample to rescue the result.

Infrastructure: **PASS**.
H79 geometric star↔label pairing (A0): **PASS**.
H80 local star-topology label morphology: **FAIL**.
H81 star-label paragraph rarity: **BLOCKED** (valid ZL arm **FAIL**).
H82 f68r2 centre-mark ↔ label morphology: **FAIL_EXPLORATORY**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
