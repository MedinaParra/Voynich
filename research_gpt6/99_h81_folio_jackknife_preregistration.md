# H81 — Leave-one-folio-out robustness of the fifth-character EVA-a residual

Status: **NOT_RUN**

## Question
Is the H72 fifth-character EVA-`a` residual robust to removing any single represented folio, or can one folio account for the replicated positive effect?

H81 is frozen before any H81 outcome is inspected. It is a robustness test of the already localized H72 signal, not a new search over characters or positions.

## Frozen sources
- Source A blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Source B blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`

Both hashes must match exactly or H81 is **BLOCKED**.

## Frozen parent sample
Recreate the H72/H79 aligned exact-prefix sample without changing any extraction rule:
- same label locus present in both frozen transcriptions;
- identical certain single-token EVA transcription;
- token length >= 5;
- strict `P*` controls from the same folio, same Currier language, same LFD hand, exact token length, and exact first two EVA characters;
- no `C*`, `R*`, or non-`P*` controls.

The reconstructed parent sample must contain exactly **122 aligned events across 27 folios**, as frozen by H72. Any mismatch is **BLOCKED_SAMPLE_DRIFT** and no inferential result may be reported.

The primary residual remains fixed at full-token index `t[4]`:
`I(label t[4] == 'a') - mean[I(P-control t[4] == 'a')]`.

No alternative character, token position, prefix length, control pool, or weighting rule may be substituted after execution begins.

## Leave-one-folio-out scenarios
Create exactly one scenario for each of the 27 represented folios. In scenario `f`, remove every aligned event from folio `f` and retain all other events.

Every scenario must retain at least:
- **90 events**; and
- **25 folios**.

If any scenario falls below either frozen threshold, H81 is **BLOCKED_CONCENTRATION**. Thresholds may not be relaxed after counts are seen.

For each scenario and each source, compute the residual for every retained event, average residuals within folio, then average the retained folio means equally.

Primary source statistic = the **minimum equal-folio mean residual** across all 27 leave-one-folio-out scenarios.

## Randomization
For each source independently:
- exactly **999** randomizations;
- Source A seed `20261009`;
- Source B seed `20261010`;
- for each randomization assign one random sign to each of the 27 parent-sample folios;
- reuse that same joint sign assignment across all 27 leave-one-folio-out scenarios;
- compute every scenario mean and retain the minimum scenario mean for that randomization;
- one-sided p = `(1 + count(null_min >= observed_min)) / 1000`.

This joint minimum-statistic null explicitly accounts for selecting the worst leave-one-folio-out scenario.

## PASS criterion
H81 is **PASS** only if, in **both** frozen transcriptions:
1. the reconstructed parent sample is exactly 122 events / 27 folios;
2. all 27 leave-one-folio-out scenarios satisfy the frozen support thresholds;
3. the observed worst-case residual is strictly `> 0`;
4. the worst-case one-sided p is `<= 0.05`;
5. 999/999 randomizations complete.

A valid execution missing any inferential PASS gate is **FAIL**. Source mismatch, sample drift, insufficient scenario support, or incomplete randomization is **BLOCKED**, not scientific FAIL.

## Interpretation boundary
PASS would show that the H72 fifth-character EVA-`a` residual is not attributable to any single represented folio in the frozen matched sample and survives a joint leave-one-folio-out stress test in both frozen transcriptions.

PASS would **not** establish a lexical meaning, morpheme, phonetic value, language, plaintext, cipher mechanism, visual-object mapping, translation, or decipherment. Those claims remain **NOT_RUN**.
