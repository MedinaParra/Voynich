# H79 — Currier-language × LFD-hand jackknife robustness

Status: **NOT_RUN**

## Question
Is the H72 fifth-character EVA-`a` residual robust to removing any one major `(Currier language, LFD hand)` page-metadata cell, or is it driven by a single scribal/textual regime?

IVTFF page variables are used exactly as encoded in the frozen transcriptions: `$L` = Currier language and `$H` = LFD hand.

## Frozen sources
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Both must match exactly or H79 is **BLOCKED**.

## Sample construction
Recreate the H72 aligned exact-prefix sample:
- identical certain single-token label at the same locus in both frozen transcriptions;
- token length >= 5;
- strict `P*` controls only;
- controls from the same folio, same `$L`, same `$H`, exact token length, and exact first two EVA characters;
- no `C*`, `R*`, or non-`P*` controls.

Primary residual is fixed at full-token index `t[4]`:
`I(label t[4] == 'a') - mean[I(P-control t[4] == 'a')]`.

## Major metadata cells
A `(Currier language, LFD hand)` cell is major if it contains:
- at least 10 aligned events; and
- at least 5 represented folios.

At least 2 major cells must qualify, otherwise H79 is **BLOCKED**. Thresholds may not be changed after counts are seen.

## Jackknife scenarios
Create one scenario per major metadata cell. In each scenario remove all aligned events belonging to that cell and retain all other events.

Every scenario must retain at least:
- 60 events; and
- 15 folios.

Otherwise H79 is **BLOCKED**.

For each scenario/source compute the equal-folio mean residual at `t[4]`.

Primary source statistic = the minimum equal-folio mean residual across all leave-one-major-cell-out scenarios.

## Randomization
For each source independently:
- exactly 999 randomizations;
- Source A seed `20261007`, Source B seed `20261008`;
- one random sign per folio, applied jointly to that folio's contribution in all overlapping jackknife scenarios;
- calculate the minimum scenario mean for each randomization;
- one-sided p = `(1 + count(null_min >= observed_min)) / 1000`.

## PASS criterion
H79 is **PASS** only if in both frozen transcriptions:
1. at least 2 major metadata cells qualify;
2. every jackknife scenario meets support thresholds;
3. the worst-case residual is > 0;
4. the worst-case one-sided p <= 0.05;
5. 999/999 randomizations complete.

Otherwise a valid execution is **FAIL**.

## Interpretation boundary
PASS would show that the H72 fifth-character `a` residual is not attributable to any single major Currier-language × LFD-hand regime represented in the matched sample. FAIL would mean that robustness claim is unsupported. Neither outcome identifies language, semantics, plaintext, cipher, translation, or decipherment.

Language identification, semantic identification, translation, and decipherment remain **NOT_RUN**.
