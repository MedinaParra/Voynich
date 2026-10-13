# H82 — Out-of-sample replication of the fifth-character EVA-a label residual — Result

Status: **FAIL**

## Frozen execution
- Actions run: `37651721209`
- Job: `112896454269`
- Head commit: `1d90bda7527ab78b1d05b23cf347aff705a33f7b`
- Artifact: `h82-out-of-sample-label-replication-results`
- Artifact ID: `11496004792`
- Artifact ZIP SHA-256: `23144d4cb9e4d6fdb929da6b7048471bd9b800d2e3592c0604c89261be8cee6f`
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Randomizations: `999/999` in each source

## Sample gates
The H72 discovery sample reconstructed exactly:
- **122 events**
- **27 folios**

Before control matching there were 398 aligned label events. After excluding all 122 H72 loci and applying the frozen same-folio / same-Currier / same-hand / exact-length `P*` control requirement, H82 retained:
- **108 held-out events**
- **29 held-out folios**
- **0 locus overlap with H72**

Therefore all frozen source, sample-drift, support, and independence gates passed. H82 is a valid scientific **FAIL**, not a blocked run.

## Source A
- equal-folio mean residual: **-0.0092315321**
- event-weighted residual: `+0.0259335488`
- one-sided p: **0.589**
- 999/999 randomizations completed

## Source B
- equal-folio mean residual: **-0.0091277136**
- event-weighted residual: `+0.0281711018`
- one-sided p: **0.558**
- 999/999 randomizations completed

## Frozen decision
H82 is **FAIL**. The fifth-character EVA-`a` excess discovered in H72 did **not** replicate in a disjoint set of previously unused aligned label loci under the preregistered length-matched `P*` control rule. The primary equal-folio statistic is slightly negative in both frozen transcriptions and far from the one-sided significance gate.

## Consequence for the evidence ladder
H72/H79/H80/H81 show that the positive effect is robust **within the exact-prefix-matched 122-event sample** to Currier×hand, label-subtype, and single-folio deletion tests. H82 shows that this is not presently a general label-wide fifth-character effect under a looser exact-length control rule.

This materially lowers the scope of the claim. The current defensible statement is that a reproducible fifth-character EVA-`a` contrast exists in a specific tightly matched prefix-conditioned subset; generalization beyond that subset is **not demonstrated**.

The next useful test should distinguish two explanations without changing H82: (1) the exact-prefix conditioning is necessary because it controls a genuine orthographic confound, versus (2) the H72 effect is selection-specific and does not generalize.

No lexical meaning, semantic class, language, plaintext, translation, or decipherment is established. Those remain **NOT_RUN**.
