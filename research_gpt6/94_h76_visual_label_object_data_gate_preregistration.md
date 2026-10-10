# H76 — Visual label-object data gate preregistration

Status before execution: **NOT_RUN**.

## Motivation

H72 exact local label→paragraph recurrence and H75 prospectively frozen edit-distance-1 recurrence both failed. H69 visual-subtype lexical discrimination also failed. Therefore H76 does **not** enlarge edit distance or tune a new lexical similarity after observing those negatives. It moves to the independently specified E3 label↔object arm of the frozen multimodal protocol.

## Question

Do the frozen public coordinate resources contain enough independently located short-text labels on object-rich Voynich pages to support a later, genuinely visual label↔object experiment without selecting cases from label spelling?

H76 is a **data/admissibility gate only**. It cannot produce a semantic anchor, translation, language identification, or decipherment.

## Frozen external source

- YaleDHLab/voynich coordinate repository revision: `c4d36f4595292c92da8c7428e30cb23b700a019b`.
- Coordinate files: `utils/voynichese/coords/<folio>.json` at that revision.
- Text strings may be used only to establish exact locator/order alignment after page selection; label spelling MUST NOT be used to select pages or visual objects.

## Frozen page family

Primary family: astronomical/cosmological pages containing diagram/star-associated short labels and already represented by coordinate files. The implementation must enumerate eligible pages from the frozen project transcription metadata and the frozen Yale coordinate inventory, not from lexical content.

The previously studied `f68r1`/`f68r2` pages may be included but may not be the sole basis for PASS because they have already been inspected in an external stellar-label geometry analysis.

## Required outputs per page

For every candidate page record:

1. page/folio identifier;
2. whether a Yale coordinate JSON exists at the frozen revision;
3. number of coordinate text boxes;
4. number of transcription label loci eligible for exact occurrence/order alignment;
5. number and fraction uniquely alignable without using lexical similarity to choose among alternatives;
6. whether the page contributes an independent held-out unit beyond `f68r1`/`f68r2`.

No visual class labels may be inferred from EVA strings.

## PASS / FAIL / BLOCKED

**PASS** only if all are true:

- at least **4** eligible object-rich pages have frozen coordinate files;
- at least **3** pages are outside `{f68r1,f68r2}`;
- at least **80** label loci total are uniquely alignable;
- at least **50** uniquely alignable loci are outside `{f68r1,f68r2}`;
- at least **3** independent outside pages each contribute **>=10** uniquely alignable labels.

**FAIL** if the frozen sources execute correctly but any numerical coverage gate above is not met.

**BLOCKED** only for an infrastructure/source-integrity failure that prevents the frozen inventory/alignment audit from being evaluated (missing frozen revision, unparsable source, hash/revision mismatch, or deterministic alignment implementation failure).

Until executed: **NOT_RUN**.

## Consequence

- PASS authorizes a separately preregistered H77 visual-object annotation/association experiment with page/quire holdout and within-page permutation controls.
- FAIL means the current public coordinate route is too sparse for that test and must not be rescued by lowering thresholds post hoc.
- BLOCKED requires infrastructure repair only; thresholds remain frozen.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
