# H65 — Minimal replicated three-feature L-vs-P model — Result

Scientific status: **FAIL**

Infrastructure status: **SUCCESS**

GitHub Actions:
- run: `37638098210`
- job: `112849514923`
- artifact: `11489899046`
- artifact SHA-256: `50420c6cb5201cd70d4b00114a72155350e04d484dde6453c4c9aea19ede25c4`

## Frozen reconstruction
Both frozen sources and samples matched the preregistration exactly.

Source A:
- 780 positive tokens
- 495 matched pairs
- 34 folios
- 285 unmatched positives

Source B:
- 669 positive tokens
- 388 matched pairs
- 32 folios
- 281 unmatched positives

## Source A
- full five-feature BA: `0.6585858586`
- reduced `{frac_o, frac_a, starts_q}` BA: `0.6636363636`
- reduced minus full BA: `+0.0050505051`
- reduced null mean BA: `0.4997977776`
- reduced Monte Carlo p: `0.001`
- permutations: `999/999`
- excess-over-chance retention: `1.0318471338`
- source status: **PASS**

## Source B
- full five-feature BA: `0.6945876289`
- reduced `{frac_o, frac_a, starts_q}` BA: `0.6314432990`
- reduced minus full BA: `-0.0631443299`
- reduced null mean BA: `0.5001277050`
- reduced Monte Carlo p: `0.001`
- permutations: `999/999`
- excess-over-chance retention: `0.6754966887`
- source status: **FAIL** because preregistered retention threshold was `0.80`.

## Interpretation
The H64 three-component signature is real enough to classify L vs P significantly in both frozen transcriptions, but it is **not sufficient** to account for most of the full H60/H63 classifier signal in both sources. In Source B, approximately one third of the full model's excess-over-chance separation is lost when `frac_y` and `ends_y` are removed, despite those variables not individually meeting H64's replicated familywise criterion.

This suggests that additional multivariate/covariance information, sample composition, transcription-specific treatment, or interactions may contribute to the full separation. H65 does not identify which explanation is correct.

Language identification, semantic identification, translation and decipherment remain **NOT_RUN**.
