# H66 — Symbol-renaming-invariant bidirectional zero-shot result

Status: **PASS**.

This records execution of the preregistered protocol in `74_h66_symbol_renaming_invariant_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- Workflow: `H66 symbol-renaming-invariant zero-shot`.
- Run: `37613066000` (run number 1), conclusion `success`.
- Job: `112764749582` (`h66-symbol-invariant-zero-shot`), conclusion `success`.
- Experimental branch head executed: `370fa62fd8cf77ad25b04b72f190b3f9025ca8ee` (PR merge checkout `268b74edf55b9cb49c264ebb165b1e76586c3810`).
- ZL blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.
- Seed: `20261007`.
- Artifact: `h66-symbol-invariant-zero-shot-results`, ID `11479165376`.
- Artifact SHA256: `7d4d22419399df38fa20c4e1ff78dde0019d9b56b6c18f2f013baf8e07e4c65e`.

Frozen matched sets: ZL **495** pairs; Takahashi **388** pairs.

## Frozen representation

No EVA symbol identity was used. The five features were:

- `unique_fraction`;
- `singleton_type_fraction`;
- `max_frequency_fraction`;
- `adjacent_equal_fraction`;
- `first_last_equal`.

All are exactly invariant under arbitrary bijective renaming of transcription symbols.

## ZL -> Takahashi

- training pairs: **495**;
- test pairs: **388**;
- represented test folios: **32**;
- observed balanced accuracy: **0.654639175257732**;
- null mean BA: **0.49966203316718827**;
- Monte Carlo p: **0.001**;
- Bonferroni alpha: **0.025**;
- permutations: **999/999**;
- descriptive P-vs-P negative control BA: **0.5064432989690721** over **388** pairs;
- status: **PASS**.

## Takahashi -> ZL

- training pairs: **388**;
- test pairs: **495**;
- represented test folios: **34**;
- observed balanced accuracy: **0.6090909090909091**;
- null mean BA: **0.4992982881871776**;
- Monte Carlo p: **0.001**;
- Bonferroni alpha: **0.025**;
- permutations: **999/999**;
- descriptive P-vs-P negative control BA: **0.5060606060606061** over **495** pairs;
- status: **PASS**.

## Decision

Both preregistered directions satisfy the sample gates, 999/999 permutations, BA > 0.5, and the Bonferroni-corrected p <= 0.025 criterion.

H66: **PASS**.

## Conservative interpretation

The strict label-versus-paragraph distinction transfers bidirectionally between the admitted ZL and Takahashi transcriptions even when the classifier has no access to EVA character identity, prefixes, suffixes, lexical identity, or character n-grams. The surviving information is carried by symbol equality/repetition structure inside length-matched tokens.

This materially weakens a simple explanation based on the shared names or identities of EVA symbols. It does **not** eliminate a shared manuscript/layout or locus-annotation mechanism, and it does not establish that labels encode object names or any other semantics.

The historical `Lc`-vs-`Lf`, exact-length subtype, topology-conditioned lexical-anchor, and familywise subtype tests remain **FAIL** and are not superseded.

Classification: `BIDIRECTIONAL_SYMBOL_RENAMING_INVARIANT_ZERO_SHOT_STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION`.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
