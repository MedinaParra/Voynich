# H62 — Edge-ablation functional-role replication result

Status: **PASS_EDGE_ABLATED_REPLICATION**.

## Frozen protocol
Preregistration: `65_h62_edge_ablation_preregistration.md`.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Workflow: `Voynich H62 edge-ablation replication`
- GitHub Actions run: `37611393201`, conclusion `success`
- Job: `112759213070` (`edge-ablation-h62`), conclusion `success`
- Artifact: `edge-ablation-h62-results`, ID `11477398475`
- Artifact SHA256: `8b40241ab334bc7aa4ec49ef0103ef45229f2829ffcb14e1286f37c44932cd8e`
- Seed: `20261007`
- Permutations: 999/999 independently in each corpus

## Primary IVTFF corpus
- blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- evaluable pairs: 764
- evaluable quires: 9
- edge-ablated balanced accuracy: `0.5857329842931938`
- held-out quires above 0.5: 7
- null mean BA: `0.49994562625452654`
- null max BA: `0.5425392670157068`
- Monte Carlo p: `0.001`
- edge-only diagnostic BA: `0.5399214659685864`
- status: **PASS_EDGE_ABLATED**

## Independent Takahashi corpus
- blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- evaluable pairs: 652
- evaluable quires: 8
- edge-ablated balanced accuracy: `0.5782208588957055`
- held-out quires above 0.5: 7
- null mean BA: `0.5000445230506585`
- null max BA: `0.5460122699386503`
- Monte Carlo p: `0.001`
- edge-only diagnostic BA: `0.5636503067484663`
- status: **PASS_EDGE_ABLATED**

## Frozen decision
Both corpora satisfy the preregistered gate: BA > 0.55, p <= 0.01, >=3 held-out quires above chance, adequate sample size and 999/999 permutations. Therefore H62 is **PASS_EDGE_ABLATED_REPLICATION**.

## Conservative interpretation
The functional label/object-locus signal survives removal of the original first and final glyphs and therefore is not reducible to the explicit starts-`q` / ends-`y` edge cues. The surviving effect is weaker than H60/H61, so token edges carry part of the signal, but a statistically reproducible interior-composition component remains in both frozen transcriptions.

This strengthens a functional-register / production-grammar interpretation. It does **not** identify semantic classes, lexical glosses, language, cipher, plaintext, or translation.

Semantic identity: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
