# H61 — Strict label-vs-paragraph cross-context generalization result

Status: **PASS**.

This records the completed execution of the preregistered protocol in `64_h61_label_cross_context_preregistration.md`. No semantic, language, plaintext, cipher, translation, or decipherment claim is made.

## Execution evidence

- GitHub Actions workflow: `H61 label cross-context`.
- Run: `37610823641` (run number 1), conclusion `success`.
- Job: `112757376844` (`h61-label-cross-context`), conclusion `success`.
- Experimental branch head executed: `4e986af24e340a511d5f1e589bb903b1bd1fb780` (PR merge checkout `4f6c7332b2d72dde500e076f8a00ad56d0189873`).
- Frozen corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Seed: `20261007`.
- Artifact: `h61-label-cross-context-results`, ID `11478146477`.
- Artifact SHA256: `26e4ff4f9f7c418447557a231ea127ba204e53c07cf1bfcaa0f3beac101e08be`.

## Frozen pair set

- Certain single-token L* positives: **780**.
- Strict P-only exact folio + Currier/hand + token-length matched pairs: **495**.
- Excluded for no strict P match: **285**.
- Permutations: **999/999**.

## View A — leave-one-hand-out

Eligible hands (>=10 pairs): `1`, `2`, `4`, `5`.

Pair counts:
- hand 1: **208**;
- hand 2: **98**;
- hand 4: **171**;
- hand 5: **18**.

Aggregate result:
- eligible pairs: **495**;
- observed balanced accuracy: **0.6313131313131313**;
- null mean balanced accuracy: **0.5004873560429116**;
- Monte Carlo p: **0.001**;
- status: **PASS**.

Held-out hand BAs:
- hand 1: **0.6153846153846154**;
- hand 2: **0.7193877551020409**;
- hand 4: **0.6052631578947368**;
- hand 5: **0.5833333333333334**.

All eligible held-out hands are above 0.5 descriptively.

## View B — leave-one-quire-out

Eligible quires (>=10 pairs): `H`, `I`, `M`, `N`, `O`, `S`.

All quire counts before eligibility filtering:
- A: **1**;
- B: **1**;
- H: **18**;
- I: **73**;
- M: **98**;
- N: **98**;
- O: **71**;
- S: **135**.

Aggregate result:
- eligible pairs: **493**;
- observed balanced accuracy: **0.6470588235294118**;
- null mean balanced accuracy: **0.49983959618848034**;
- Monte Carlo p: **0.001**;
- status: **PASS**.

Held-out quire BAs:
- H: **0.5833333333333334**;
- I: **0.5410958904109588**;
- M: **0.7142857142857143**;
- N: **0.6275510204081632**;
- O: **0.6901408450704225**;
- S: **0.6555555555555556**.

All eligible held-out quires are above 0.5 descriptively.

## Decision

The preregistered conjunction required both the hand-out and quire-out views to meet sample thresholds, complete 999/999 permutations, achieve BA > 0.5, and p <= 0.05. Both views satisfy all frozen criteria.

H61: **PASS**.

## Conservative interpretation

The strict H60 label-vs-paragraph token-form distinction is not confined to a single eligible scribal hand or a single eligible physical quire in this frozen corpus. The five frozen token-form predictors retain above-chance cross-context discrimination when entire eligible hands or quires are held out.

This materially weakens a simple explanation in which the H60 result is produced solely by a shared-hand or shared-quire artifact. It does **not** establish that labels are nouns, names, semantic object identifiers, or plaintext words. The failed `Lc`-vs-`Lf`, familywise subtype, exact-length subtype, and topology-conditioned lexical-anchor results remain **FAIL** and are not superseded.

Classification: `STRICT_LABEL_VS_PARAGRAPH_CROSS_CONTEXT_NOT_TRANSLATION`.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
