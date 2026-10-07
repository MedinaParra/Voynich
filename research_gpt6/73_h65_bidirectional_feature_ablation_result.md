# H65 — Bidirectional zero-shot leave-one-feature-out robustness result

Status: **PASS**.

This records execution of the preregistered protocol in `72_h65_bidirectional_feature_ablation_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- GitHub Actions workflow: `H65 bidirectional feature ablation`.
- Run: `37612497779` (run number 1).
- Job: `112762884861` (`h65-bidirectional-feature-ablation`).
- Experimental branch head executed: `640549a2e5e91c13b4aa0387ef091fe868bba297` (PR merge checkout `22d7350d1f4a0f1a46200711a4b380faf94979ee`).
- ZL blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.
- Seed: `20261007`.
- Artifact: `h65-bidirectional-feature-ablation-results`, ID `11478064236`.
- Artifact SHA256: `343930029fd524293d8c7e3e28c3acc82e2edc5cdbc22ae198c3e0957242c41e`.

Frozen matched sets: ZL **495** pairs; Takahashi **388** pairs.

## ZL -> Takahashi

All five preregistered ablations completed 999/999 permutations and PASS:

- minus `frac_o`: BA **0.6082474226804124**, p **0.001**;
- minus `frac_a`: BA **0.6314432989690721**, p **0.001**;
- minus `frac_y`: BA **0.654639175257732**, p **0.001**;
- minus `starts_q`: BA **0.6172680412371134**, p **0.001**;
- minus `ends_y`: BA **0.6597938144329897**, p **0.001**.

Direction status: **PASS**.

## Takahashi -> ZL

All five preregistered ablations completed 999/999 permutations and PASS:

- minus `frac_o`: BA **0.6070707070707071**, p **0.001**;
- minus `frac_a`: BA **0.601010101010101**, p **0.001**;
- minus `frac_y`: BA **0.6565656565656566**, p **0.001**;
- minus `starts_q`: BA **0.6787878787878788**, p **0.001**;
- minus `ends_y`: BA **0.6878787878787879**, p **0.001**.

Direction status: **PASS**.

## Decision

The preregistered conjunction required all 10 direction x ablation cells to achieve BA > 0.5 and p <= 0.05 with valid samples and 999/999 permutations. All 10 cells satisfy the criterion.

H65: **PASS**.

## Conservative interpretation

The bidirectional zero-shot strict label-versus-paragraph distinction does not require any single one of the five frozen EVA token-form predictors by itself. Removing any one of `frac_o`, `frac_a`, `frac_y`, `starts_q`, or `ends_y` still leaves above-chance cross-transcription transfer in both directions under the frozen model family.

This supports a distributed token-form distinction rather than a result driven solely by one frozen character/position feature. It does **not** show invariance to arbitrary representations and does not rule out a distributed EVA/IVTFF convention or another shared annotation mechanism.

The historical `Lc`-vs-`Lf`, exact-length subtype, topology-conditioned lexical-anchor, and familywise subtype tests remain **FAIL** and are not superseded.

Classification: `BIDIRECTIONAL_ZERO_SHOT_LEAVE_ONE_FEATURE_OUT_NOT_TRANSLATION`.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
