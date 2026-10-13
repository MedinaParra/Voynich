# H77 — Length-conditioned morphology generalization — Result

Status: **FAIL**

- Actions run: `37648991371`
- Job: `112887053421`
- Artifact: `h77-length-conditioned-morphology-results`
- Artifact ID: `11496240688`
- Artifact ZIP SHA256: `5c780fdfe23df5d95c2b82d3758381a389c0f1d1ffee2274bebe959154862695`
- Frozen source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Frozen source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Support audit
- aligned exact-prefix events length >=6: 67
- exact length 6: 40 events / 22 folios — eligible
- exact length 7: 18 events / 11 folios — eligible
- exact length 8: 9 events / 8 folios — ineligible under preregistered event threshold
- evaluable held-out folios: 24
- evaluated events: 58
- randomizations: 999/999 in each source

## Source A
- mean rigid MSE: `0.1354677192172436`
- mean length-conditioned MSE: `0.13474140545912658`
- mean delta (rigid - conditioned): `0.0007263137581169795`
- one-sided p: `0.410`

## Source B
- mean rigid MSE: `0.13179398336878476`
- mean length-conditioned MSE: `0.1319437661665031`
- mean delta (rigid - conditioned): `-0.00014978279771832404`
- one-sided p: `0.526`

## Interpretation
The preregistered exact-length-conditioned three-position EVA-`a` residual model does not generalize better across held-out folios than a rigid positional template. This rejects that specific predictive formulation. It does not erase the H72/H73 positional effects, but it prevents treating exact token length as a validated general modifier of the positional profile.

Language identification, semantics, translation, and decipherment remain **NOT_RUN**.
