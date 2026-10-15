# External-referent admissibility audit after H79/H80

Status: **BLOCKED_SEMANTIC_OPENING**.

This is an audit of an already-published external, label-blind experiment. It is **not** a new preregistered confirmatory test and must not be presented as one.

## Why this audit is needed

H79 established a reproducible A0 geometric pairing between the 29 independently annotated f68r1 star centres and the frozen Yale stellar-label position block. H80 then **FAIL**ed the prospectively frozen prediction that labels attached to robustly adjacent stars would have unusually similar character forms.

The remaining defensible route toward semantics is therefore not to retune token similarity on the same 29 labels, but to ask whether an external historical referent can be fixed **without looking at the Voynich label strings**. Only then would a held-out comparison between external names/attributes and Voynich labels be scientifically admissible.

## External source audited

Repository: `seeton/Voynich-public`

Frozen revision already used for the independent star centres:

`8920f2e506fce4c2c5a1245fb21a312f25655f1b`

Relevant files:

- `docs/stellar-catalogue-match-contract.md`
- `docs/stellar-catalogue-match.md`
- `analysis/annotations/f68r_star_centres.csv`
- `analysis/semantics/stellar_catalogue_match.py`
- `analysis/results/stellar_catalogue_match/manifest.json`

The external contract explicitly requires the external referent to be identified from star-object count/geometry before opening the Voynich label strings.

## f68r1 external-catalogue result

The external experiment tested all Ptolemy V/61 constellations with exactly 29 catalogue entries. The exact-count family consisted of:

- Hercules — 29
- Perseus — 29
- Ophiuchus — 29
- Canis Major — 29

The family-best observed pairwise-distance-spectrum score was Hercules, RMSE **0.060723**.

The preregistered radius/angle-preserving null had:

- null mean **0.059450**;
- lower-tail `p = 0.592620`.

The uniform-angle sensitivity null had:

- null mean **0.052001**;
- lower-tail `p = 0.835708`.

Across 1,000 ±35 px annotation-jitter draws, **0/1000** crossed the primary null 5% threshold.

The external experiment therefore did **not** identify a Ptolemaic 29-star referent for f68r1.

This is a valid negative result, not evidence that the objects are not astronomical and not evidence that the labels are not names.

## Detectability caveat

The same external pipeline recovered the source constellation identity in synthetic controls for 4/4 exact-count candidates, but its formal gate passed only 3/4 under the specified jitter; Hercules was underpowered in that condition.

Therefore the negative f68r1 result should not be inflated into a universal rejection of Ptolemaic-style or historical sky diagrams. It is sufficient, however, to enforce the external contract's label-opening rule: the tested external referent was not fixed.

## f68r2 / 36-item route

The external source reports 36 large interior star-like objects plus 23 smaller border objects on f68r2, but its preregistered automatic/manual segmentation was judged insufficiently reliable and the proposed 36 coordinates were discarded rather than retained post hoc.

The historical 36-decan inventory therefore remains only a **count-level candidate**. There is no unique frozen 36-point external sky catalogue or independently validated object correspondence that would justify opening labels as decan names.

## Admissibility decision

Current evidence permits the following:

- H79 A0 spatial object↔label-position association: **PASS**.
- H80 local topology↔character-morphology relation: **FAIL**.
- Ptolemy exact-29 external referent: **NOT_SUPPORTED** by the external preregistered geometry test.
- f68r2 36-decan relation: **COUNT_ONLY_CANDIDATE**.
- label-blind external referent sufficient to open semantics: **BLOCKED**.

Therefore a direct star-name/decan-name/string matching experiment on the current f68r labels would be methodologically premature. It would select the semantic candidate after seeing the same material and would substantially increase researcher degrees of freedom.

## Next admissible experiment

A new semantic test should be opened only after one of these prospective conditions is met:

1. an independent historical manuscript/catalogue supplies a sufficiently specific object layout and known labels, and a token-blind point/object correspondence can be frozen before examining Voynich strings; or
2. f68r2 receives a genuinely independent, label-blind object annotation that reproducibly separates the relevant 36-object interior inventory from border objects, followed by an externally fixed ordering/grouping hypothesis rather than a free 36-name permutation; or
3. an independently defined visual object attribute on the H79 29-star set (for example a reproducible discrete visual class) is frozen without consulting token strings, and a new prospective held-out morphology/class test is preregistered.

Until one of those conditions is satisfied, semantic identification remains **BLOCKED**, and translation/decipherment remain **NOT_RUN**.

## Interpretation boundary

This audit does not alter H79 or H80 and does not add a positive semantic claim. Its purpose is to prevent post-hoc semantic fishing after a strong spatial A0 association.

H79 geometric star↔label pairing: **PASS**.
H80 topology↔label morphology: **FAIL**.
External semantic referent admissibility: **BLOCKED**.
Semantic identification A1+: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
