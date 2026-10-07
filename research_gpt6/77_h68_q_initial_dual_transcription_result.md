# H68 — Dual-transcription q-initial paired-prevalence result

Status: **PASS_REPLICATED_Q_REGISTER**.

Frozen preregistration: `76_h68_q_initial_dual_transcription_preregistration.md`.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Experimental head tested: `823bd88d31a69a19238a5a28d6c06f6fae54c820`
- PR merge checkout: `e359cf1885ae4a6440d721c003e1f2b56f3cff88`
- GitHub Actions run: `37652274126`
- Job: `112898379161` (`q-initial-dual-transcription-h68`), conclusion `success`
- Artifact: `q-initial-dual-transcription-h68-results`, ID `11497870074`
- Artifact SHA-256: `b666acfb2f416d210cb34b2163ee276bca8751b0d5edf8605f4bec87b5fb1228`
- Primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Primary IVTFF
- evaluable pairs: **764**
- evaluable quires: **9**
- label q-initial prevalence: `0.014397905759162303`
- matched running-text control q-initial prevalence: `0.11125654450261781`
- `delta_q = label - control`: **`-0.0968586387434555`**
- same-direction quires: **7**
- permutations: **999/999**
- two-sided Monte Carlo p: **0.001**
- status: **POSITIVE**

## Independent Takahashi
- evaluable pairs: **652**
- evaluable quires: **8**
- label q-initial prevalence: `0.015337423312883436`
- matched running-text control q-initial prevalence: `0.1058282208588957`
- `delta_q = label - control`: **`-0.09049079754601227`**
- same-direction quires: **6**
- permutations: **999/999**
- two-sided Monte Carlo p: **0.001**
- status: **POSITIVE**

The effect direction agrees across both frozen transcriptions: EVA `q`-initial tokens are substantially less frequent among the selected label loci than among same-folio, same-Currier, same-hand, exact-length running-text controls.

## Frozen decision
Both transcription-specific support and inferential gates pass, `abs(delta_q) >= 0.05`, both p-values are <=0.01, sufficient quires agree in direction, and the signs agree. H68 therefore **PASS_REPLICATED_Q_REGISTER**.

## Interpretation ceiling
This is a replicated orthographic/register difference, not a semantic identification. It strengthens the conclusion that the robust H66/H67 functional distinction is concentrated in q-initial behavior and is not an artifact of the exact-consensus subset or the nearest-class-mean classifier.

It does **not** establish what EVA `q` means, whether labels name depicted objects, the manuscript language, a cipher/plaintext mechanism, any semantic gloss, translation, or decipherment.

A next adversarial test should remove the one-control sampling choice entirely by conditioning on the full same-folio/same-Currier/same-hand/exact-length token stratum and permuting label status while preserving label counts within each stratum.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
