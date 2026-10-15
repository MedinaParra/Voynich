# Strict label-locus vs paragraph-text replication preregistration

Status: **NOT_RUN**.

## Motivation
The completed H58 implementation yielded a strong distinction for L* loci against all non-L* loci, but inspection of the frozen implementation shows that the control pool admitted every non-L locus. IVTFF distinguishes P (paragraph/running text), L (labels), C (circular text), and R (radial text). Therefore the H58 result is retained as an L-vs-non-L result, while the narrower claim L-vs-running-paragraph-text requires an independent strict replication.

## Frozen data and positive set
Use the same frozen corpus/blob `2a4533ab9bdfa85db9bad602d590978953055df1`, the same certain single-token L* positives, and seed `20261007`. No manual recoding.

## Strict control definition
Eligible controls MUST come only from loci whose IVTFF generic locus type is `P` (including P subtypes such as P0/P1/Pb/Pc/Pr/Pt after locus-position markers are stripped). C*, R*, L*, and any unrecognized locus types are excluded from the control pool.

For each positive, match same folio, exact token length, and Currier/hand state. Select one control deterministically. Require >=60 matched pairs and >=8 represented folios, otherwise BLOCKED.

## Predictors and evaluation
Exactly the H58 frozen predictors: fraction o, fraction a, fraction y, starts q, ends y. Absolute length and metadata are prohibited predictors. Leave-one-folio-out; training-fold-only standardization; nearest-class-mean classifier; aggregate balanced accuracy.

## Null
Exactly 999 deterministic within-pair identity swaps, seed `20261007`, refitting the complete LOFO pipeline. Monte Carlo p=(1+count(null_BA>=observed))/1000.

## Negative control
Descriptive only: compare two independently selected P-only running-text tokens from the same folio/exact-length/Currier/hand stratum where possible. It is not part of PASS.

## Decision
PASS iff >=60 pairs, >=8 folios, 999/999 permutations, BA>0.5 and p<=0.05. FAIL if valid execution misses inferential criteria. BLOCKED if strict P-only matching cannot meet frozen sample requirements.

## Interpretation boundary
PASS would show a reproducible token-form distinction between L* label loci and strictly P* paragraph text under local exact-length controls. It would not establish label semantics, language, plaintext, cipher, translation, or decipherment. H58 remains a valid L-vs-non-L execution but must not be described as a strict L-vs-P test.
