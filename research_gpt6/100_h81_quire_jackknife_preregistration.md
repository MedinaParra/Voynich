# H81 — Quire jackknife robustness of the fifth-character EVA-a residual

Status: **NOT_RUN**

## Question
Is the H72 fifth-character EVA-`a` residual robust to removing any one major physical quire (`$Q`), or is it driven by a localized manuscript cluster?

## Frozen sources
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Both must match exactly or H81 is **BLOCKED**.

## Sample construction
Recreate the H72 aligned exact-prefix sample:
- same label locus present in both frozen transcriptions;
- identical certain single-token EVA transcription;
- token length >= 5;
- strict `P*` controls from the same folio, same Currier language, same LFD hand, exact token length, and exact first two EVA characters;
- no `C*`, `R*`, or non-`P*` controls.

Each event inherits the page's IVTFF `$Q` value. Events with missing/unknown `$Q` remain in the global sample but cannot define a major quire.

Primary residual is fixed at full-token index `t[4]`:
`I(label t[4] == 'a') - mean[I(P-control t[4] == 'a')]`.

## Major quires
A quire is major if it contains:
- at least 8 aligned events; and
- at least 3 represented folios.

At least 3 major quires must qualify, otherwise H81 is **BLOCKED**. Thresholds may not be changed after counts are seen.

## Jackknife scenarios
Create one scenario per major quire. In each scenario remove all aligned events from that quire and retain all others.

Every scenario must retain at least:
- 60 events; and
- 15 folios.

Otherwise H81 is **BLOCKED**.

For each scenario/source compute the equal-folio mean residual at `t[4]`.

Primary source statistic = the minimum equal-folio mean residual across all leave-one-major-quire-out scenarios.

## Randomization
For each source independently:
- exactly 999 randomizations;
- Source A seed `20261007`, Source B seed `20261008`;
- one random sign per folio, shared jointly across all overlapping jackknife scenarios;
- calculate the minimum scenario mean for every randomization;
- one-sided p = `(1 + count(null_min >= observed_min)) / 1000`.

## PASS criterion
H81 is **PASS** only if in both frozen transcriptions:
1. at least 3 major quires qualify;
2. every jackknife scenario meets support thresholds;
3. the observed worst-case residual is > 0;
4. worst-case one-sided p <= 0.05;
5. 999/999 randomizations complete.

Otherwise a valid execution is **FAIL**.

## Interpretation boundary
PASS would show that the H72 fifth-character EVA-`a` residual is not attributable to any single major physical quire represented in the local matched sample. FAIL would mean that robustness claim is unsupported. Neither outcome identifies language, semantics, plaintext, cipher mechanism, translation, or decipherment.

Language identification, semantic identification, translation, and decipherment remain **NOT_RUN**.
