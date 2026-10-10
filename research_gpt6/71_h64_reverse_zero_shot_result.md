# H64 — Reverse zero-shot cross-transcription label-form transfer result

Status: **PASS**.

This records execution of the preregistered protocol in `70_h64_reverse_zero_shot_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- GitHub Actions workflow: `H64 reverse zero-shot cross-transcription`.
- Run: `37612234006` (run number 1), conclusion `success`.
- Job: `112761993325` (`h64-reverse-zero-shot`), conclusion `success`.
- Experimental branch head executed: `1a0312084c7d5745165a6e4573665066d83a8bcc` (PR merge checkout `ce81d621f29567b345ad4ead4934a7a0689e5fea`).
- Frozen training Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.
- Frozen test ZL blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Seed: `20261007`.
- Artifact: `h64-reverse-zero-shot-results`, ID `11477354468`.
- Artifact SHA256: `bdb61276e27e2ce5b44e06bc28071d8b80bc4f4872016334aa8cc4f139ebec29`.

## Frozen samples

Training Takahashi:
- certain single-token L* positives: **669**;
- strict P-only matched pairs: **388**;
- excluded for no match: **281**.

Test ZL:
- certain single-token L* positives: **780**;
- strict P-only matched pairs: **495**;
- represented folios: **34**;
- excluded for no match: **285**.

## Reverse zero-shot result

- Observed balanced accuracy: **0.687878787878788**.
- Null mean balanced accuracy: **0.49865319865319924**.
- Monte Carlo p: **0.001**.
- Permutations: **999/999**.
- Descriptive P-vs-P negative-control BA: **0.4949494949494949** over **495** pairs.
- Takahashi training pairs per held-out ZL folio: min **355**, max **388**.

The preregistered PASS criteria were >=60 ZL test pairs, >=8 represented folios, 999/999 permutations, zero-shot BA > 0.5, and p <= 0.05. All were met.

## Conservative interpretation

A classifier whose standardization and class means are learned only from the frozen Takahashi transcription predicts strict L* label-locus versus P* paragraph-text identity above chance in the frozen Zandbergen-Landini transcription without fitting any parameter on ZL.

Together with H63, this establishes **bidirectional zero-shot transfer** of the frozen five-feature label-versus-paragraph distinction between the two admitted transcription traditions. This materially weakens source-specific refitting and one-way domain-shift explanations.

It does not establish label semantics, language, plaintext, cipher, or translation. Both files describe the same manuscript and use related EVA/IVTFF representation and locus conventions, so a shared representation/annotation mechanism remains an important alternative explanation.

The historical `Lc`-vs-`Lf`, exact-length subtype, topology-conditioned lexical-anchor, and familywise subtype tests remain **FAIL** and are not superseded.

Classification: `REVERSE_ZERO_SHOT_CROSS_TRANSCRIPTION_STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION`.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
