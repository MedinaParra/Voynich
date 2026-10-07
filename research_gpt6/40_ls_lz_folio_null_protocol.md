# Folio-level Ls/Lz confound test

Status: PREREGISTERED EXPLORATORY HARDENING / NOT A TRANSLATION

Date frozen: 2026-10-07
Corpus: cesarjz/Voynich commit 47e6a77dc9d5cd570c375f4aff710fa4a0567278
Expected Git blob: 2a4533ab9bdfa85db9bad602d590978953055df1

## Motivation
The prior label-pair audit produced an apparent Ls/Lz balanced accuracy near 0.69, but zero labels were exchangeable within folio. Therefore the within-folio null was blocked. This protocol changes the randomization unit to the folio and is frozen before seeing the new result.

## Frozen hypothesis
H0: the apparent Ls/Lz token signal is no stronger than an arbitrary assignment of the observed Ls/Lz folio classes, conditional on the manuscript stratum used by these labels.

H1: label-token morphology predicts the held-out folio class more strongly than folio-level randomized class assignments.

No natural-language gloss is tested.

## Data and exclusions
Use the same conservative certain-single-token label parser as label_pair_anchor_audit.py. Restrict to Ls and Lz. Collapse duplicate folio/subtype/token rows. A folio must have exactly one of the two classes; mixed-class folios are excluded and reported. Frozen corpus hash must match.

## Primary model
Character 1-3 gram set features and the same Naive Bayes implementation as the preceding audit. Evaluation is leave-one-folio-out. Balanced accuracy is computed over all held-out label predictions.

## Controls
Report length-only and edge-only baselines. The primary null permutes Ls/Lz class assignments at the FOLIO level, preserving the observed number of folios in each class. Permutation is performed within Currier|hand strata when a stratum contains both classes and at least two folios per class; otherwise all eligible Ls/Lz folios are permuted together and this fallback is explicitly reported. Tokens never move between folios.

Seed: 20261007.
Exploratory permutations: 999.

## Frozen gate
PASS_EXPLORATORY only if all conditions hold:
1. observed balanced accuracy > 0.60;
2. observed balanced accuracy exceeds both length-only and edge-only controls;
3. empirical one-sided Monte Carlo p <= 0.01;
4. recall for both Ls and Lz > 0.50;
5. at least 5 held-out folios from each class are evaluable.

Otherwise FAIL. If fewer than 5 folios exist in either class, or a valid folio-level permutation cannot be formed, BLOCKED.

A PASS is only evidence for a folio-generalizing visual-class association in this transcription. It is not a lexical gloss and not a translation.
