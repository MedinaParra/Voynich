# H69 — Documentary-stratified visual-subtype morphology screen result

Status: **FAIL**.

This records execution of the preregistered protocol in `80_h69_stratified_visual_subtype_screen_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- Workflow: `H69 stratified visual-subtype screen`.
- Run: `37614192607` (run number 1), conclusion `success`.
- Job: `112768464700` (`h69-stratified-visual-subtype-screen`), conclusion `success`.
- Experimental branch head executed: `e9b86e0250d0ef262875e17fd814480914fbb02f` (PR merge checkout `5dcfb505d8f674409fbaaacca91970a219082177`).
- Frozen source Git blob SHA-1: `4201d762a4bd6e9014e0e796d72dd5c3efb597da`.
- Frozen source SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee`.
- Seed: `20261007`.
- Permutations: **9999/9999** with full model refit under every paired null permutation.
- Familywise alpha: **0.001**.
- Artifact: `h69-stratified-visual-subtype-screen-results`, ID `11479277813`.
- Artifact SHA256: `ad6c8af678a5ef8b4726deb0b5b54f52f73216ad2d366453ac79fb92e0340a7a`.

## Lc vs Lf

Frozen exact strata: `O|A|1` and `S|A|1`.

After exact `(Q,L,H,folio,token_length)` matching:
- matched pairs: **25**;
- represented folios: **9**;
- unmatched exclusions: `Lc` **15**, `Lf` **191**;
- observed balanced accuracy: **0.52**;
- null mean BA: **0.4999219921992157**;
- raw Monte Carlo p: **0.4928**;
- familywise max-stat p: **0.7433**;
- status: **FAIL**.

## Ln vs Lt

Frozen exact stratum: `M|B|2`.

After exact `(Q,L,H,folio,token_length)` matching:
- matched pairs: **20**;
- represented folios: **7**;
- unmatched exclusions: `Ln` **44**, `Lt` **30**;
- observed balanced accuracy: **0.65**;
- null mean BA: **0.5010876087608783**;
- raw Monte Carlo p: **0.0971**;
- familywise max-stat p: **0.1067**;
- status: **FAIL**.

## Decision

Both frozen contrasts passed the preregistered sample-validity gates and all 9999 permutations completed. Neither contrast reached the frozen familywise criterion `p <= 0.001`.

H69: **FAIL**.

## Conservative interpretation

Under exact documentary and token-length matching, leave-one-folio-out evaluation, alphabet-renaming-invariant morphology, and a full-refit paired permutation null, this source does not provide preregistered evidence for a visual-subtype morphology candidate.

The `Ln` vs `Lt` descriptive BA of 0.65 is not promoted because its raw p=0.0971 and familywise p=0.1067 are not statistically sufficient. It must not be used as a post-hoc semantic claim.

The `Lc` vs `Lf` result independently remains consistent with the historical negative route rather than rescuing it.

No visual-subtype morphology candidate is promoted from H69.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
