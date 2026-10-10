# 33. High-impact paper plan: from structural signal to falsifiable semantic anchors
Date: 2026-10-06

## Principle
We cannot guarantee fame. We can maximize scientific impact by making a narrow, surprising, reproducible claim that survives adversarial tests and predicts held-out data.

## Current competitive landscape
Recent work already covers: visual semantic page profiling; cross-validated morphology without lexical recovery; Currier A/B quantitative recovery; directional/positional constraints; dynamic/self-copy generation hypotheses; null-calibrated critiques of semantic cribs. Therefore a paper that only reports section classification, label morphology, or generic multimodality is insufficiently novel.

## Proposed central claim
Test whether object-associated Voynich labels contain a reproducible lexical component that predicts the visual class of previously unseen objects/pages after controlling for section, Currier state, hand attribution, quire, word length, initial glyph family and local page context.

This is deliberately weaker than translation and stronger than structural clustering.

## Primary preregistered test
Data unit: each IVTFF label with a recognized object-position code (plant, pharma fragment/container, human/nymph, tube/bath, star, zodiac, astronomical/cosmological object).

Representation tournament:
1. full EVA token;
2. first 1-3 glyphs;
3. last 1-3 glyphs;
4. prefix-stripped token (especially ot/ok families);
5. character n-grams;
6. unsupervised prefix-core-suffix segmentation learned on training folds only.

Evaluation:
- grouped holdout by quire;
- stricter leave-one-section-family-out tests where meaningful;
- balanced accuracy and macro-F1;
- conditional mutual information;
- 9,999 stratified permutations.

Adversarial nulls preserve, progressively:
A. label length;
B. Currier x hand;
C. section;
D. first-glyph/prefix family;
E. local folio;
F. token-frequency spectrum.

PASS_LEXICAL_ANCHOR requires:
1. held-out prediction above all preregistered baselines;
2. Monte Carlo p <= 0.001 in the primary test;
3. effect survives at least nulls A-D;
4. effect replicates on an alternate transcription;
5. same latent component recurs in running text in contexts consistent with the object class;
6. no semantic gloss is assigned until the above passes.

## Internal Rosetta test
Use documented same-plant/same-root correspondences between herbal and pharmaceutical folios as independent constraints. Learn candidate label components only from pharmaceutical labels, then test whether those components are enriched in running text of the matched herbal folio relative to matched controls. The plant identity annotation itself is not accepted as ground truth; use only high-confidence internal visual correspondences and report sensitivity to disputed pairs.

## Codicological test
Repeat continuity/semantic analyses under current binding and independently reconstructed singulion order. Do not optimize order on the test set. A positive result is publishable only if the external codicological reconstruction improves held-out textual/visual continuity relative to physically valid permutations.

## Strong negative-result value
If labels lose predictive power after prefix-family or local-folio controls, report that apparent semantic signal is explained by positional/generative morphology. This directly constrains decipherment claims and remains scientifically useful.

## Paper architecture
Working title: "From Labels to Lexical Anchors: A Preregistered Multimodal Test of Semantic Information in the Voynich Manuscript"

Main figures:
1. blind pipeline and leakage barriers;
2. label morphology by object class;
3. observed vs 9,999 stratified nulls;
4. prefix/core/suffix ablation;
5. herbal-pharma internal Rosetta replication;
6. current vs reconstructed physical order;
7. independent-transcription replication.

## Publication standard
No claim of decipherment unless a frozen mapping predicts unseen labels/passages and an independent analyst can reproduce it. Distinguish STRUCTURAL, FUNCTIONAL, SEMANTIC-CLASS, LEXICAL and TRANSLATION claims in every result table.

## Status
Literature differentiation: PASS.
Protocol/preregistration: PASS.
Existing corpus/transcription: PASS.
Primary 9,999-permutation execution: NOT_RUN.
Object-label dataset extraction: NOT_RUN.
Internal Rosetta enrichment test: NOT_RUN.
Alternate-transcription replication: NOT_RUN.
Lexical recovery: UNKNOWN.
Translation: UNKNOWN.
