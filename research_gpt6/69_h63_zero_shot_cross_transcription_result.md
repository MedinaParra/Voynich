# H63 — Zero-shot cross-transcription label-form transfer result

Status: **PASS**.

This records execution of the preregistered protocol in `68_h63_zero_shot_cross_transcription_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- GitHub Actions workflow: `H63 zero-shot cross-transcription`.
- Run: `37611770501` (run number 1), conclusion `success`.
- Job: `112760431930` (`h63-zero-shot-cross-transcription`), conclusion `success`.
- Experimental branch head executed: `e0c236cb43632d67c22600d14cea71a8afdff9be` (PR merge checkout `86d7be21a20eed68ffcfc78afc58a71245f6310d`).
- Frozen discovery ZL blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Frozen replication Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.
- Seed: `20261007`.
- Artifact: `h63-zero-shot-cross-transcription-results`, ID `11477473767`.
- Artifact SHA256: `7467d80d60a6c95f586f7bb9f019e8b076cfb18c18c117c340de87aea3040224`.

## Frozen samples

Discovery/training ZL:
- certain single-token L* positives: **780**;
- strict P-only matched pairs: **495**;
- excluded for no match: **285**.

Replication/test Takahashi:
- certain single-token L* positives: **669**;
- strict P-only matched pairs: **388**;
- represented folios: **32**;
- excluded for no match: **281**.

## Zero-shot result

- Observed balanced accuracy: **0.6610824742268041**.
- Null mean balanced accuracy: **0.49978973819180006**.
- Monte Carlo p: **0.001**.
- Permutations: **999/999**.
- Descriptive P-vs-P negative-control BA: **0.518041237113402** over **388** pairs.
- ZL discovery training pairs per held-out Takahashi folio: min **462**, max **495**.

The preregistered PASS criteria were >=60 Takahashi pairs, >=8 represented folios, 999/999 permutations, zero-shot BA > 0.5, and p <= 0.05. All were met.

## Conservative interpretation

A classifier whose standardization and class means are learned only from the frozen Zandbergen-Landini transcription predicts strict L* label-locus versus P* paragraph-text identity above chance in the independently frozen Takahashi transcription without fitting any model parameter on Takahashi.

This is stronger than H62 because it weakens an explanation in which the distinction merely reappears after refitting separately inside each transcription. It still does not rule out shared EVA-family representation, shared manuscript structure, or inherited locus-annotation conventions, because both transcriptions describe the same manuscript and share related transcription conventions.

The historical `Lc`-vs-`Lf`, exact-length subtype, topology-conditioned lexical-anchor, and familywise subtype tests remain **FAIL** and are not superseded.

Classification: `ZERO_SHOT_CROSS_TRANSCRIPTION_STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION`.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
