# 36. Label-object audit result and feasibility gate

Date: 2026-10-06
Run: GitHub Actions #10, label-object-audit
Status: PASS_EXECUTED for audit; primary 8-class lexical-anchor test BLOCKED by design confounding.

## Frozen-corpus result
Corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`.
Raw IVTFF label rows detected: 729.
Primary single, certain labels: 633.

Counts before any classifier was inspected:
- Lp plant: 1, across 1 quire, Currier/hand A|1.
- Lc pharmaceutical container: 36, across 2 quires, A|1.
- Lf pharmaceutical fragment: 177, across 2 quires, A|1.
- Ln nymph/human: 59, across 1 quire, B|2.
- Lt tube/bath: 39, across 1 quire, B|2.
- Ls star: 69, across 1 quire, ?|4.
- Lz zodiac: 249, across 3 quires, ?|4.
- La astro/cosmo: 3, across 1 quire, ?|4.

## Critical finding
The proposed global 8-class classifier is not a clean semantic test. Object subtype is strongly entangled with documentary strata and quire coverage. Lp and La are too sparse for independent grouped validation. Ln/Lt and Ls are each confined to a single quire, making the preregistered leave-one-quire-out gate impossible for those classes. A high global accuracy could therefore be a section/hand/quire detector rather than an object-referent detector.

This is a scientifically useful negative feasibility result and must not be bypassed post hoc.

## Valid next tests without changing the preregistered claim
1. Pharmaceutical within-register contrast Lc vs Lf is the strongest immediate test: both are A|1 and both span two quires. Run leave-one-quire-out, length/prefix/suffix controls, and label permutations within quire. This asks whether morphology distinguishes container labels from herb-fragment labels inside the same documentary register.
2. Ln vs Lt may be explored only with grouped folio holdout inside B|2; it cannot satisfy the primary leave-one-quire-out lexical-anchor gate and must be labelled exploratory.
3. Ls vs Lz may be explored only where folio/quire support permits exchangeability; Ls single-quire confinement prevents a clean primary cross-quire claim.
4. Lp and La are descriptive only in this corpus version.

## Decision
Do not run or report the global 8-class accuracy as semantic evidence. Primary next execution is the preregistered-compatible Lc-vs-Lf pharmaceutical contrast. The original PASS_LEXICAL_ANCHOR requirements remain unchanged; a positive pharmaceutical contrast is only a lexical-anchor candidate and still requires recurrence in running text plus alternate-transcription replication.

Artifact evidence: `label-object-audit-results`, artifact ID 11439491989, run 37520607412.
