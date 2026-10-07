# H78 — Major-prefix jackknife robustness of the fifth-character EVA-a residual

Status: **NOT_RUN**

## Question
Is the H72 fifth-character EVA-`a` residual robust to removing any one major two-character label prefix family, or is the effect driven by a single frequent prefix such as `ot`, `ok`, or `ch`?

## Frozen sources
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Both must match exactly or H78 is **BLOCKED**.

## Sample construction
Recreate the H72 aligned exact-prefix sample:
- same label locus present in both frozen transcriptions;
- identical certain single-token EVA label in both;
- token length >= 5;
- at least one strict `P*` control in the same folio, same Currier/hand, exact token length, and exact first two EVA characters in each source;
- no `C*`, `R*`, or non-`P*` controls.

Primary residual is fixed at full-token index `t[4]`:

`I(label t[4] == 'a') - mean[I(P-control t[4] == 'a')]`.

## Major prefixes
A two-character label prefix is a major prefix if, in the aligned sample before outcome testing, it has:
- at least 10 aligned events; and
- at least 5 represented folios.

At least 3 major prefixes must qualify, otherwise H78 is **BLOCKED**. Thresholds may not be changed after counts are observed.

## Jackknife scenarios
Create one scenario per major prefix. In each scenario, remove **all** aligned events whose label begins with that prefix and retain all other events.

Every scenario must retain at least:
- 60 events; and
- 15 folios.

If any preregistered scenario falls below support, H78 is **BLOCKED**.

For each scenario/source, compute the equal-folio mean residual at `t[4]`.

Primary source statistic = the **minimum** equal-folio mean residual across all leave-one-major-prefix-out scenarios. This is a worst-case robustness statistic.

## Randomization
For each source independently:
- exactly 999 randomizations;
- Source A seed `20261007`, Source B seed `20261008`;
- draw one random sign per folio and apply that same sign jointly to the folio contribution in every jackknife scenario;
- for every randomization calculate the minimum scenario mean;
- one-sided p-value = `(1 + count(null_min >= observed_min)) / (1 + 999)`.

Joint signs preserve dependence among overlapping jackknife samples.

## PASS criterion
H78 is **PASS** only if in both frozen transcriptions:
1. at least 3 major prefixes qualify;
2. every jackknife scenario passes support thresholds;
3. the observed worst-case residual is > 0;
4. the one-sided worst-case randomization p <= 0.05;
5. 999/999 randomizations complete.

Otherwise a valid execution is **FAIL**.

## Interpretation boundary
PASS would show that the H72 fifth-character `a` residual is not attributable to any single major two-character prefix family. FAIL would mean this robustness claim is unsupported. It would not by itself identify which prefix is causal.

Language identification, semantic identification, translation, and decipherment remain **NOT_RUN**.
