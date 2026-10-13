# H83 — Control-rule sensitivity of the H72 fifth-character EVA-a residual

Status: **NOT_RUN**

## Motivation
H72/H79/H80/H81 established a positive fifth-character EVA-`a` residual inside the 122-event exact-prefix-matched sample. H82 then failed on 108 disjoint label events when controls were matched only on exact token length rather than exact first-two-character prefix.

H83 is a preregistered diagnostic designed to separate **sample generalization** from **control-rule sensitivity**. It asks whether the original H72 122-event sample itself remains positive when the prefix requirement is removed from the control pool.

H83 is frozen before inspecting its length-only outcome.

## Frozen sources
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Any mismatch => **BLOCKED_SOURCE**.

## Frozen sample
Reconstruct the H72 sample exactly:
- aligned certain single-token label locus in both sources;
- identical EVA label token in both sources;
- identical Currier language and LFD hand metadata in both sources;
- token length >= 5;
- at least one strict `P*` control in each source from same folio, same Currier language, same LFD hand, exact token length, and exact first two EVA characters.

The reconstructed sample must be exactly **122 events / 27 folios** or H83 is **BLOCKED_SAMPLE_DRIFT**.

The H83 sample is this same frozen set of 122 label events. No events may be added or removed based on fifth-character outcome.

## Two frozen control rules
For each H72 label event and each source, construct:

1. **Exact-prefix control**: same H72 rule — same folio, Currier, hand, exact token length, exact first two EVA characters, strict `P*` only.
2. **Length-only control**: same folio, Currier, hand, exact token length, strict `P*` only; no prefix restriction.

Every event already has an exact-prefix pool by construction. Because the length-only pool is a superset, every event must also have a length-only pool. Any exception => **BLOCKED_CONTROL_CONSTRUCTION**.

## Frozen target
Target remains full-token index `t[4]` and EVA character `a`.

For each event and each control rule:
`residual = I(label t[4] == 'a') - mean[I(P-control t[4] == 'a')]`.

Within each source:
- average event residuals within folio;
- then average folio means equally.

Primary H83 statistic = equal-folio mean residual under the **length-only** rule.

Secondary diagnostic = equal-folio mean of the paired event-level difference:
`exact-prefix residual - length-only residual`.
Positive secondary values mean exact-prefix conditioning increases the estimated label contrast.

No other token position, character, prefix length, control locus, metadata rule, or weighting may be substituted after execution begins.

## Randomization
Exactly **999** folio-level sign-flip randomizations per source.

For the primary length-only residual:
- Source A seed `20261013`
- Source B seed `20261014`
- one random sign per represented folio;
- reuse sign for every event in that folio;
- one-sided p = `(1 + count(null >= observed)) / 1000`.

For the secondary paired-difference diagnostic:
- Source A seed `20261015`
- Source B seed `20261016`
- same folio-level sign-flip method;
- report one-sided p for positive `exact-prefix minus length-only` difference.

## PASS criterion
H83 is **PASS** only if in both frozen sources:
1. sample reconstructs exactly as 122 events / 27 folios;
2. all 122 events have both control pools;
3. primary length-only equal-folio residual is strictly `> 0`;
4. primary one-sided `p <= 0.05`;
5. 999/999 primary randomizations complete.

Otherwise a valid execution is **FAIL**. Source mismatch, sample drift, missing control pools, or incomplete randomization is **BLOCKED**.

The secondary paired-difference p-value is diagnostic and does not alter PASS/FAIL.

## Interpretation matrix
- **PASS**: H72's positive t[4]=`a` signal survives removal of prefix matching on the same 122 events. H82's failure then points mainly toward lack of generalization to the disjoint event sample.
- **FAIL + positive/significant paired delta**: the H72 signal is materially dependent on exact-prefix conditioning; control construction is a major explanation for the contrast between H72 and H82.
- **FAIL without positive paired delta**: neither simple explanation is sufficient; the discrepancy likely reflects event-set composition and requires a different diagnostic.

Regardless of outcome, H83 is structural/diagnostic only. It does not establish lexical meaning, semantics, language, plaintext, translation, or decipherment; those remain **NOT_RUN**.
