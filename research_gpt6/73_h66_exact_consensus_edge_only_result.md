# H66 — Exact-consensus edge-only functional test result

Status: **PASS_EDGE_ONLY_CONSENSUS_SIGNAL**.

Frozen execution evidence:
- GitHub Actions run: `37614795914`
- job: `112770426941`
- workflow head SHA: `eea02e7e74f590a88bd162acba0949984f962a48`
- artifact: `consensus-edge-only-h66-results`, ID `11479308373`
- artifact SHA-256: `c04d2faed41b3506e4e474c7bb2d2cc1d05feeffde093dd14593656d148fa4f6`
- primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Frozen support
- common loci: 5,213
- exact-consensus loci: 2,283
- metadata disagreements: 0
- consensus positive loci: 482
- evaluable matched pairs: 246
- evaluable quires: H, I, M, O, S
- 999/999 permutations completed
- predictors: `starts_q`, `ends_y` only

## Primary result
- observed balanced accuracy: **0.5772357724**
- null mean BA: **0.5000956241**
- null max BA: **0.5813008130**
- Monte Carlo p: **0.002**
- quires above chance: **4/5**
- per-quire BA: H 0.3636364, I 0.5363636, M 0.6474359, O 0.6551724, S 0.5342466

The preregistered gate required >=4 evaluable quires, >=80 pairs, 999/999 permutations, BA > 0.55, p <= 0.01, and >=3 quires above 0.5. All gates pass.

## Interpretation
H66 shows that the strict exact-consensus subset retains a statistically reproducible functional label-vs-running-text distinction using only the two previously frozen token-edge indicators (`q`-initial and `y`-final). In conjunction with H65 FAIL on edge-ablated interior features, this localizes the robust signal on this strict subset toward token-edge behavior rather than providing evidence for lexical meaning.

This is a functional-register result only. It does not identify what labels mean, whether they name pictured objects, the underlying language/cipher/plaintext, any gloss, translation, or decipherment.
