# H86 — Triangular replication of inverse label stability result

Overall status: **BLOCKED**.

This records execution of the prospectively directional protocol in `113_h86_triangular_label_stability_replication_preregistration.md`. Infrastructure and all frozen-source checks passed. The ZL↔IT arm was adequately sampled and gave a valid **FAIL** in the opposite direction from the H85 inverse observation. The ZL↔GC arm failed its frozen sample gate, so the H86 conjunction is **BLOCKED**.

## Execution evidence

- Workflow: `H86 triangular label stability replication`.
- Run: **37649217523** (run number 2).
- Job: **112887837496** (`h86-triangular-label-stability-replication`).
- Experimental branch head executed: `71e4538b2799d1718b777384b5dcf524c3b3f1f9`.
- PR merge checkout: `1f6303a4fe0b3c955c69a879ba24be0ab59a29d7`.
- ZL Git blob SHA-1: `2a4533ab9bdfa85db9bad602d590978953055df1` — matched.
- IT SHA-256: `db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee` — matched.
- GC SHA-256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f` — matched.
- Artifact: `h86-triangular-label-stability-replication-results`, ID **11496610625**.
- Artifact ZIP SHA-256: `4399a858f094d79244126ae46c5aeb07f70c861bc94fb115f41161b3e55487bf`.

Infrastructure: **PASS**.

## Arm A — ZL↔IT

### Coverage / matching

- exact P records present in both: **4,118**;
- P records nonempty in both: **4,116**;
- P records with equal cleaned token count: **3,122**;
- ordinal P token candidates: **24,956**;
- single-token-mappable labels: **403** across **44** folios;
- matched label–P pairs: **237**;
- represented folios: **30**;
- distinct P records used: **237**.

All frozen sample gates passed.

### Primary result

- label mean structural disagreement D: **0.05293014533520862**;
- label median D: **0.0**;
- paragraph mean D: **0.021688098586832766**;
- paragraph median D: **0.0**;
- `Delta = mean(D_label - D_paragraph)`: **+0.03124204674837586**.

Exact equality-pattern agreement:

- labels: **0.8354430379746836**;
- paragraphs: **0.9324894514767933**.

The prospectively frozen H86 prediction was `Delta < 0`. This arm instead points in the opposite direction.

### Null

- paired sign-flip permutations: **9,999 / 9,999**;
- pairing seed: `20261020`;
- null seed: `20261021`;
- null mean Delta: **0.00016047365234815627**;
- null SD: **0.010496305062543437**;
- preregistered lower-tail `p_lower`: **0.9985**.

Arm A status: **FAIL**.

The equal-source-length descriptive sensitivity retained **209 pairs across 30 folios** and also had positive Delta:

- label mean D: **0.031197311460469355**;
- paragraph mean D: **0.007055517581833371**;
- Delta: **+0.024141793878635985**.

This diagnostic is descriptive only.

## Arm B — ZL↔GC

### Coverage / matching

- exact P records present in both: **4,119**;
- P records nonempty in both: **3,220**;
- P records with equal cleaned token count: only **19**;
- ordinal P token candidates: **56**;
- single-token-mappable labels: **112** across **34** folios;
- matched label–P pairs: **2**;
- represented folios: **2** (`f67r2`, `f99v`);
- distinct P records used: **2**.

Frozen gates required >=60 pairs and >=8 folios. Both failed.

Arm B status: **BLOCKED**.

No inferential Delta or permutation p-value was allowed for this arm.

## Conjunction

The preregistered H86 conjunction required both arms to PASS.

- ZL↔IT: **FAIL**;
- ZL↔GC: **BLOCKED**;
- H86 overall: **BLOCKED**.

## Conservative interpretation

H86 does not replicate H85's previously unregistered inverse observation as a general cross-transcription property of labels. On the adequately powered ZL↔IT edge, the direction reverses again: labels are structurally *less* stable than matched paragraph tokens under this protocol.

Therefore the negative Delta seen in H85 IT↔GC should not be promoted as a manuscript-level discovery. The evidence now indicates that cross-transcription stability depends materially on which transcription traditions and tokenization conventions are compared.

The ZL↔GC arm additionally exposes a strong documentary compatibility problem: despite 4,119 exact P records sharing record keys, only 19 nonempty records preserved equal cleaned token counts under the frozen H86 rule. That makes ordinal token alignment inadmissible at useful scale for this pair under the preregistered protocol.

The proper conclusion is narrower but stronger methodologically: the existing strict label-vs-paragraph signal is **not explained by a single universal direction of cross-transcription ambiguity**. H85 weakened the hypothesis “labels are always less stable”; H86 also rejects the post-hoc opposite generalization “labels are always more stable.”

This does not establish semantics, plaintext, a language, or decipherment.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
