# H60 — Strict label vs paragraph replication result

Status: **PASS**.

This is the confirmatory result for the preregistered protocol in `60_strict_label_vs_paragraph_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- GitHub Actions run: `37601860517` (run number 76), overall conclusion `success`.
- H60 job: `112727887862` (`strict-label-vs-paragraph`), conclusion `success`.
- Experimental branch head executed: `c2de08ee11f4c95b2d9c468b5c04ab14cf09d6be` (PR merge checkout `223aec30c377ec92605ce6d1444935236248edf2`).
- Frozen corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Seed: `20261007`.
- Artifact: `strict-label-vs-paragraph-h60-results`, ID `11472748580`.
- Artifact SHA256: `66f1a3881a2300d196fddc871fcd1dd564594738571b87480c2c8fd52ef03315`.

## Frozen-sample result

- Certain single-token L* positives: **780**.
- Exact folio + Currier/hand + token-length matched P-only pairs: **495**.
- Represented folios: **34**.
- Excluded for no strict P match: **285**.
- Observed balanced accuracy: **0.6585858585858586**.
- Null mean balanced accuracy: **0.49960263293596635**.
- Monte Carlo p: **0.001**.
- Permutations: **999/999**.
- Descriptive P-vs-P negative-control BA: **0.45151515151515154** over **495** pairs.

The preregistered PASS criteria were >=60 pairs, >=8 folios, 999/999 permutations, BA > 0.5 and p <= 0.05. All were met.

## Interpretation

H60 supports a reproducible **token-form distinction between certain single-token L* label loci and strictly P* paragraph/running-text loci**, after local exact-length, folio and Currier/hand matching, using the five frozen token-form predictors and leave-one-folio-out evaluation.

This strengthens the narrower interpretation that the H58 signal was not merely caused by pooling circular/radial loci into the control class. It does **not** identify what labels mean, whether they are nouns/names, what language is present, whether the manuscript is enciphered, or how to translate/decipher it.

Classification: `STRICT_LABEL_VS_PARAGRAPH_NOT_TRANSLATION`.
