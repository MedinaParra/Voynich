# H87 — Leave-one-folio-out equality-pattern codebook recurrence result

Status: **FAIL**.

This records execution of the frozen protocol in `115_h87_heldout_equality_pattern_codebook_preregistration.md`. Both corpus arms were valid and adequately sampled, all permutations completed, and both arms failed in the direction opposite to the preregistered prediction.

## Execution evidence

- Workflow: `H87 held-out equality-pattern codebook`.
- Run: **37650458886** (run number 1).
- Job: **112892127144** (`h87-heldout-equality-pattern-codebook`).
- Experimental branch head executed: `cae5310502b8796533845e3fa01996750fc7f5eb`.
- PR merge checkout: `5babe146e42fcfa7abf4ebb4ea1230a92716a24d`.
- Artifact: `h87-heldout-equality-pattern-codebook-results`, ID **11495723570**.
- Artifact ZIP SHA-256: `0d52167719819070a9479efe7bc2ef098006a9b3a927f982c1082756cafe63a7`.

Infrastructure: **PASS**.

Frozen source blobs matched exactly:

- ZL: `2a4533ab9bdfa85db9bad602d590978953055df1`.
- Takahashi: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Familywise alpha was 0.05 with Bonferroni **0.025 per arm**.

## ZL arm

### Sample

- eligible label tokens: **780**;
- P token occurrences: **33,951**;
- matched pairs before codebook gate: **426**;
- excluded labels without unused exact control: **354**;
- excluded pair without same-length training codebook: **1**;
- evaluable pairs: **425**;
- evaluable folios: **34**;
- controls without replacement: PASS.

### Primary result

- equal-folio mean `Delta`: **-0.3783677157236635**;
- label mean recurrence score: **2.625689963213629**;
- control mean recurrence score: **2.8677602730528737**;
- label seen-pattern fraction: **0.84**;
- control seen-pattern fraction: **0.8729411764705882**;
- unique label patterns: **119**;
- unique control patterns: **104**;
- fraction of folios with `Delta > 0`: **0.29411764705882354**.

Null:

- permutations: **9,999 / 9,999**;
- seed: `20261026`;
- null mean `Delta`: **0.0003283655231691104**;
- null SD: **0.1490284989773955**;
- upper-tail `p`: **0.9962**.

The frozen prediction was `Delta > 0`. The observed effect is negative.

ZL status: **FAIL**.

## Takahashi arm

### Sample

- eligible label tokens: **669**;
- P token occurrences: **33,931**;
- matched pairs before codebook gate: **380**;
- excluded labels without unused exact control: **289**;
- excluded pair without same-length training codebook: **1**;
- evaluable pairs: **379**;
- evaluable folios: **32**;
- controls without replacement: PASS.

### Primary result

- equal-folio mean `Delta`: **-0.25254425128756797**;
- label mean recurrence score: **2.470152425569041**;
- control mean recurrence score: **2.718683249440144**;
- label seen-pattern fraction: **0.8522427440633246**;
- control seen-pattern fraction: **0.8786279683377308**;
- unique label patterns: **113**;
- unique control patterns: **98**;
- fraction of folios with `Delta > 0`: **0.28125**.

Null:

- permutations: **9,999 / 9,999**;
- seed: `20261027`;
- null mean `Delta`: **-0.00042180746171347817**;
- null SD: **0.13323709953018495**;
- upper-tail `p`: **0.9714**.

The frozen prediction was `Delta > 0`. The observed effect is negative.

Takahashi status: **FAIL**.

## Decision

Both arms were valid and both fail the preregistered directional/inferential criteria.

H87 overall: **FAIL**.

## Conservative interpretation

The robust symbol-renaming-invariant label-versus-paragraph distinction established earlier does **not** reduce to stronger reuse of a small out-of-folio codebook of exact equality/repetition templates. Under the pooled unlabelled leave-one-folio-out reference, matched paragraph controls actually show greater exact-template recurrence than labels in both transcriptions.

This narrows the surviving mechanism: the H66 signal is distributed and structural, but it is not explained by simple preferential recurrence of exact canonical repetition templates. This result does not identify semantics, a language, a cipher, plaintext, translation, or decipherment.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
