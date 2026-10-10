# H62 — Independent-transcription strict label-vs-paragraph replication result

Status: **PASS**.

This records execution of the preregistered protocol in `66_h62_independent_transcription_label_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- GitHub Actions workflow: `H62 independent-transcription label replication`.
- Run: `37611318914` (run number 1), conclusion `success`.
- Job: `112758964982` (`h62-independent-transcription-label`), conclusion `success`.
- Experimental branch head executed: `dd5b94ac57ffe367ad6ccde01c8b9787ff5e397f` (PR merge checkout `afebd20c92320958d59b19713972d7581688b887`).
- Immutable replication source: `oklo/voynich_gpt` commit `2d7c61c387ad6962de730caf73c48612bc8f6957`, path `IT2a-n.txt`.
- Replication Git blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.
- Seed: `20261007`.
- Artifact: `h62-independent-transcription-label-results`, ID `11478127459`.
- Artifact SHA256: `e8afb90834fb5a9ce24d7818e79eb23a468ebd250e5980ae7b9fb9965e1af25f`.

## Frozen-sample result

- Certain single-token L* positives: **669**.
- Exact folio + Currier/hand + token-length matched strict P-only pairs: **388**.
- Represented folios: **32**.
- Excluded for no strict P match: **281**.
- Observed balanced accuracy: **0.6945876288659794**.
- Null mean balanced accuracy: **0.5008410472327995**.
- Monte Carlo p: **0.001**.
- Permutations: **999/999**.
- Descriptive P-vs-P negative-control BA: **0.5347938144329897** over **388** pairs.

The preregistered PASS criteria were >=60 pairs, >=8 folios, 999/999 permutations, BA > 0.5 and p <= 0.05. All were met.

## Conservative interpretation

The strict label-vs-paragraph token-form distinction observed in H60 on the frozen Zandbergen-Landini discovery transcription replicates in the independently frozen Takahashi IT2a-n transliteration under the same five token-form predictors, exact-length/local matching, and leave-one-folio-out evaluation.

This materially weakens the explanation that H60/H61 are an idiosyncrasy of one transcription file. It does not eliminate shared EVA-family encoding conventions, shared manuscript-level structure, or shared locus annotation conventions as explanations.

The historical `Lc`-vs-`Lf`, exact-length subtype, topology-conditioned lexical-anchor, and familywise subtype tests remain **FAIL** and are not superseded.

Classification: `INDEPENDENT_TRANSCRIPTION_STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION`.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
