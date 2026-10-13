# 35. Label-object lexical anchor experiment

Date: 2026-10-06
Status: PREREGISTERED / NOT_RUN

## Motivation
The completed section holdout produced only a marginal section signal after Currier x hand conditioned permutations (balanced accuracy 0.258125; null mean 0.237270; Monte Carlo p=0.049), while Currier A/B was almost perfectly recoverable (balanced accuracy 0.991150). Therefore section classification is not promoted as semantic evidence. The next test targets labels tied to external visual referents.

## Claim under test
Voynich label morphology contains information about its IVTFF visual-referent subtype beyond documentary confounds.

H0: after conditioning on documentary/morphological controls, label morphology does not predict object class out of sample.
H1: at least one train-only learned morphological representation predicts held-out object class and survives adversarial nulls.

## Frozen classes
Use only IVTFF label subtypes with explicit object relation:
- Lp plant
- Lc pharmaceutical container
- Lf pharmaceutical herb fragment
- Ln nymph/human
- Lt tube/tub/bath
- Ls star
- Lz zodiac
- La astronomical/cosmological object

Do not infer new visual labels from the Voynich text itself.

## Data hygiene
- Frozen IVTFF corpus blob: 2a4533ab9bdfa85db9bad602d590978953055df1.
- Exclude uncertain/unreadable labels in the primary analysis.
- Primary unit is one label with one explicit referent subtype.
- Duplicate identical locus/transcription rows are collapsed before splitting.
- No feature vocabulary or segmentation may be learned from the held-out quire.

## Representation tournament
1. length-only negative control;
2. full EVA token;
3. first 1/2/3 glyphs;
4. last 1/2/3 glyphs;
5. character 1/2/3-grams;
6. first-glyph-masked n-grams;
7. ot/ok-family-stripped n-grams;
8. train-only prefix/core/suffix segmentation.

## Primary split
Leave-one-quire-out. Report per-class recall, balanced accuracy, macro-F1, confusion matrix, number of labels and number of evaluable folds. Random label-level CV is diagnostic only and cannot establish PASS.

## Baselines
- majority class per training fold;
- length-only classifier;
- prefix-only classifier;
- suffix-only classifier;
- full-token memorization baseline where vocabulary overlap permits.

## Adversarial null hierarchy
Run 9,999 permutations for the final test. Preserve progressively:
A. class counts;
B. Currier x hand;
C. Currier x hand x quire where exchangeability remains;
D. token-length bin;
E. first-glyph/prefix family;
F. local folio when at least two object classes coexist.

If a stratum has no exchangeable class labels, it contributes no permutation evidence and coverage must be reported rather than silently relaxed.

## PASS_LEXICAL_ANCHOR gate
All conditions are required:
1. grouped held-out balanced accuracy exceeds majority, length, prefix and suffix controls;
2. primary adversarial Monte Carlo p <= 0.001;
3. effect survives at least controls A-D;
4. result is not driven by a single object class;
5. a candidate component learned without the validation folios recurs in running text in contexts compatible with the visual class;
6. effect replicates using an alternate independent transcription.

Passing this gate permits the phrase `lexical anchor candidate`; it does not permit a natural-language gloss or a claim of decipherment.

## Failure interpretation
If predictive power disappears after prefix-family, Currier, hand, quire, length or local-folio controls, apparent semantic signal is attributed to register/generative/documentary structure until contrary evidence is produced.

## Relation to completed experiments
TimesFM structural forecasting: PASS_EXECUTED, but not semantic evidence.
Weak section holdout: EXECUTED; marginal p=0.049, not promoted.
Currier control: very strong recoverability; mandatory confound control for all subsequent experiments.
Label-object lexical anchor: NOT_RUN.
Translation: UNKNOWN.
