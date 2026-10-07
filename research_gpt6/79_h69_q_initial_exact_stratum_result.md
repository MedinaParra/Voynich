# H69 — Exact-stratum q-initial conditional permutation result

Status: **PASS_EXACT_STRATUM_Q_DEPLETION**.

Frozen preregistration: `78_h69_q_initial_exact_stratum_preregistration.md`.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Experimental head tested: `5f8d2dfd5d3ac23338624a690e3466e96ca67916`
- PR merge checkout: `2b3318a16491d69954b21afcfbc1eede1e7264f8`
- GitHub Actions run: `37656914066`
- Job: `112914210343` (`q-initial-exact-stratum-h69`), conclusion `success`
- Artifact: `q-initial-exact-stratum-h69-results`, ID `11499465622`
- Artifact SHA-256: `c4207ac6f48759da6b2d317706ebb795eb2ec2a0d5489489a09279e285b3be3b`
- Primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Primary IVTFF
- included exact strata: **209**
- included labels: **732**
- included running-token instances: **4,136**
- evaluable quires: **9**
- observed conditional `D`: **`-0.08020448576438176`**
- negative quires: **8/9**
- null mean `D`: `0.00006294013145944481`
- null maximum absolute `D`: `0.03785475898842547`
- two-sided Monte Carlo p: **0.001**
- permutations: **999/999**
- status: **POSITIVE**

Per-quire conditional D: H `+0.0899813`, I `-0.0664376`, J `-0.0101010`, K `-0.0065476`, L `-0.0322924`, M `-0.2691311`, N `-0.0142024`, O `-0.1496864`, S `-0.1115484`.

## Independent Takahashi
- included exact strata: **192**
- included labels: **625**
- included running-token instances: **3,997**
- evaluable quires: **8**
- observed conditional `D`: **`-0.08983906993460483`**
- negative quires: **7/8**
- null mean `D`: `0.00008285198731711143`
- null maximum absolute `D`: `0.0338390699346048`
- two-sided Monte Carlo p: **0.001**
- permutations: **999/999**
- status: **POSITIVE**

Per-quire conditional D: H `+0.0951118`, I `-0.0719005`, J `-0.0058824`, K `-0.0035971`, L `-0.0273993`, M `-0.2635543`, O `-0.1603063`, S `-0.1131137`.

## Frozen decision
Both frozen transcriptions satisfy the support gate, `D <= -0.05`, two-sided p <= 0.01, at least three negative quires, and 999/999 permutations. H69 therefore **PASS_EXACT_STRATUM_Q_DEPLETION**.

## Conservative interpretation
The q-initial depletion found in H68 survives removal of the one-control sampling choice. It remains present when every eligible running-token instance is used and label assignment is permuted conditionally within exact `(folio, Currier, hand, token length)` strata. This substantially weakens the hypothesis that H68 arose from a particular control draw or those matched covariates.

The effect is not perfectly homogeneous: quire H is positive in both transcriptions. That heterogeneity is reported rather than tuned away and should be challenged explicitly in later tests.

This is an orthographic/functional-register constraint only. It does not identify what EVA `q` means, whether labels name depicted objects, manuscript language, cipher/plaintext mechanism, semantic gloss, translation, or decipherment.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
