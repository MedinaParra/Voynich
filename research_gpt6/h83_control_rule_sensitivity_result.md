# H83 — Control-rule sensitivity of the H72 fifth-character EVA-a residual — Result

Status: **PASS**

## Frozen execution
- Actions run: `37652090485`
- Job: `112897733180`
- Head commit: `e49d85e9cc2a74426f3b17170077eb24f651b87a`
- Artifact: `h83-control-rule-sensitivity-results`
- Artifact ID: `11497425322`
- Artifact ZIP SHA-256: `36f489ab7e2fc867fb098c331bea9cd80ad93afa6c97b4485fe5f81fbbccfc6a`
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

## Sample gates
The H72 sample reconstructed exactly:
- **122 events**
- **27 folios**
- all **122/122** events had both exact-prefix and length-only `P*` control pools

No blocking gate fired.

## Source A
Exact-prefix equal-folio residual: `+0.1016808295`

Length-only equal-folio residual: **+0.1246130580**
- one-sided p: **0.002**
- 999/999 primary randomizations

Paired `exact-prefix - length-only` equal-folio difference: `-0.0229322285`
- paired one-sided p for a positive delta: `0.551`
- 999/999 delta randomizations

## Source B
Exact-prefix equal-folio residual: `+0.0940730052`

Length-only equal-folio residual: **+0.1211169773**
- one-sided p: **0.003**
- 999/999 primary randomizations

Paired `exact-prefix - length-only` equal-folio difference: `-0.0270439721`
- paired one-sided p for a positive delta: `0.644`
- 999/999 delta randomizations

## Frozen decision
H83 is **PASS** with diagnostic classification **CONTROL_RULE_ROBUST**.

Removing the exact first-two-character prefix restriction from the running-text control pool does **not** remove the H72 fifth-character EVA-`a` contrast on the same 122 label events. In fact, the length-only residual is numerically larger in both sources. The paired diagnostic gives no evidence that exact-prefix conditioning artificially increases the contrast.

## Joint interpretation with H82
H82's out-of-sample **FAIL** therefore cannot be explained simply by the relaxed length-only control rule. The dominant difference is the **event set**: the 122 H72 events show the contrast under either control rule, while the disjoint 108 H82 events do not.

This narrows the next scientific question to sample composition / functional-locus structure: what objective, externally defensible property distinguishes the H72 event subset from the held-out H82 event subset?

This remains structural. No lexical meaning, semantic class, language, plaintext, translation, or decipherment is established; those remain **NOT_RUN**.
