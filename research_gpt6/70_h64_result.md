# H64 — Bidirectional cross-transcription transfer result

Status: **FAIL**.

Workflow run: `37613497579`.

Frozen sources:
- primary IVTFF blob `2a4533ab9bdfa85db9bad602d590978953055df1`;
- Takahashi blob `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

## Primary -> Takahashi
- balanced accuracy: `0.5820552147239264`
- target pairs: `652`
- evaluable quires: `8`
- quires above 0.5: `7`
- null mean BA: `0.4986320676504722`
- null max BA: `0.5927914110429447`
- Monte Carlo p: `0.015`
- permutations: `999/999`
- decision: **FAIL** (`p > 0.01`).

## Takahashi -> Primary
- balanced accuracy: `0.581151832460733`
- target pairs: `764`
- evaluable quires: `9`
- quires above 0.5: `7`
- null mean BA: `0.5000569941669423`
- null max BA: `0.5896596858638743`
- Monte Carlo p: `0.011`
- permutations: `999/999`
- decision: **FAIL** (`p > 0.01`).

## Interpretation
Both directions are above chance descriptively and broadly consistent across quires, but neither satisfies the preregistered `p <= 0.01` gate. The bidirectional experiment-level decision is therefore **FAIL**. The threshold is not relaxed post hoc.

H60/H61/H62 remain positive functional results, but H64 shows that direct zero-retraining transfer between the two transcriptions is not confirmed under the frozen inferential gate.

This does not establish or refute any semantic gloss, language, cipher, plaintext, translation, or decipherment.
