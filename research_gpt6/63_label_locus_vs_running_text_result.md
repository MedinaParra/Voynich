# Label-locus vs running-text falsification result

Status: **PASS**.

This records the completed execution of the preregistered protocol in `58_label_locus_vs_running_text_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- GitHub Actions run: `37609859377` (run number 77), overall conclusion `success`.
- Job: `112754218281` (`label-locus-vs-running-text`), conclusion `success`.
- Experimental branch head executed: `ff1c662e84dcf92c6e1fb34590d299edf5e9a2c3` (PR merge checkout `0b18020ac8a54f34f2f53fc9ed23eb390aca4be2`).
- Frozen corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Seed: `20261007`.
- Artifact: `label-locus-vs-running-text-results`, ID `11477556403`.
- Artifact SHA256: `83ee59fce49966464c76dcf4270c9e739caa34ca87e7509d9e9793f0fda44f29`.

## Frozen-sample result

- Certain single-token L* positives: **780**.
- Exact folio + Currier/hand + token-length matched running-text pairs: **766**.
- Represented folios: **49**.
- Excluded for no eligible match: **14**.
- Observed balanced accuracy: **0.6553524804177546**.
- Null mean balanced accuracy: **0.5006494745398138**.
- Monte Carlo p: **0.001**.
- Permutations: **999/999**.
- Descriptive running-text negative-control BA: **0.4680156657963447**.

The preregistered PASS criteria were >=60 pairs, >=8 folios, 999/999 permutations, BA > 0.5 and p <= 0.05. All were met.

## Interpretation

The execution supports a reproducible **token-form distinction between annotated L* label loci and locally matched running text** under the frozen five-feature classifier and leave-one-folio-out evaluation.

This agrees in direction with H60's stricter P-only replication. It does **not** rescue the failed `Lc` versus `Lf` lexical-anchor hypothesis, does not show that label subclasses encode object identity, and does not identify what any label means. The topology-conditioned and familywise subtype routes remain **FAIL**.

Classification: `LABEL_LOCUS_VS_RUNNING_TEXT_NOT_TRANSLATION`.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
