# H82 — Out-of-sample replication of the fifth-character EVA-a label residual

Status: **NOT_RUN**

## Question
Does the H72 fifth-character EVA-`a` excess replicate in label events that were **not members of the H72 exact-prefix sample**?

H82 is frozen before inspecting any H82 fifth-character outcome. It is intentionally not another jackknife of the same 122 events.

## Frozen sources
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Both hashes must match exactly or H82 is **BLOCKED_SOURCE**.

## Reconstruct and exclude the discovery sample
First recreate the H72 aligned exact-prefix discovery sample exactly:
- same label locus present in both frozen transcriptions;
- identical certain single-token EVA transcription;
- token length >= 5;
- same Currier language and LFD hand in both sources;
- at least one strict `P*` control in **each** source from the same folio, same Currier language, same LFD hand, exact token length, and exact first two EVA characters;
- no `C*`, `R*`, or non-`P*` controls.

This reconstruction must contain exactly **122 events across 27 folios**. Otherwise H82 is **BLOCKED_SAMPLE_DRIFT**.

Every H72 locus is then excluded from H82. No H72 event may re-enter the replication sample.

## H82 held-out sample
Starting from all remaining aligned label loci, retain an event only if:
1. the locus is present in both frozen sources;
2. both sources give the identical certain single-token EVA token;
3. both sources agree on Currier language and LFD hand;
4. token length is >= 5;
5. the locus is not in the reconstructed 122-event H72 sample;
6. each source contains at least one strict `P*` running-text control from the same folio, same Currier language, same LFD hand, and exact token length.

Unlike H72, H82 does **not** require the control token to share the first two EVA characters. This relaxation is fixed in advance solely to obtain a disjoint sample; no token outcome may be used to decide eligibility.

The held-out sample must contain at least **50 events across at least 15 folios**. Otherwise H82 is **BLOCKED_SUPPORT**. These thresholds may not be changed after execution.

## Frozen statistic
For each held-out label event and each source separately:

`residual = I(label t[4] == 'a') - mean[I(length-matched P-control t[4] == 'a')]`

where `t[4]` is the fifth full-token EVA character.

Within each source:
- average event residuals within folio;
- primary statistic = equal-folio mean of the folio residual means.

The target character `a`, token index `4`, control locus `P*`, exact length match, equal-folio weighting, and all sample rules are frozen. No alternative position, character, prefix, control family, or weighting is permitted after execution begins.

## Randomization
For each source independently:
- exactly **999** randomizations;
- Source A seed `20261011`;
- Source B seed `20261012`;
- assign one random sign to each represented H82 folio;
- multiply every event residual in that folio by the shared sign;
- recompute the equal-folio mean;
- one-sided p = `(1 + count(null_mean >= observed_mean)) / 1000`.

## PASS criterion
H82 is **PASS** only if all of the following hold:
1. source hashes match;
2. H72 reconstructs exactly as 122 events / 27 folios;
3. H82 has >=50 held-out events and >=15 held-out folios;
4. H82 has zero locus overlap with H72;
5. Source A equal-folio residual is strictly `> 0` and one-sided `p <= 0.05`;
6. Source B equal-folio residual is strictly `> 0` and one-sided `p <= 0.05`;
7. 999/999 randomizations complete in both sources.

A valid execution missing an inferential PASS gate is **FAIL**. Source mismatch, discovery-sample drift, insufficient held-out support, any locus overlap, or incomplete randomization is **BLOCKED**, not scientific FAIL.

## Interpretation boundary
PASS would provide an out-of-sample replication of the H72 fifth-character EVA-`a` label-versus-running-text difference on previously unused label loci under a preregistered length-matched control rule.

Even PASS would remain a **token-form / functional-locus association**. It would not identify a word, morpheme, phonetic value, pictured object, semantic class, language, plaintext, cipher mechanism, translation, or decipherment. Those remain **NOT_RUN**.
