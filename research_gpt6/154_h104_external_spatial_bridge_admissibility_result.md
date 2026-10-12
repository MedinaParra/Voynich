# H104 — External spatial bridge admissibility audit

Status: **BLOCKED**

## Question
After H98 was BLOCKED and H103 FAILed, can a newly identified, independently produced public spatial transcription provide a non-post-hoc visual→token bridge for the frozen H91 family?

## Frozen H91 target family
The nine independently admissible H91 folios are:
`f14v, f25v, f39r, f40r, f50v, f87r, f8v, f90r1, f95r2`.
The target remains the 153 stable H91 object↔label pairs. No target page or pair is changed.

## External source audited
Repository: `alessandroplaca-uro/voynich-spatial-data` (public, independently authored).
Audit date: 2026-10-12.
The repository advertises machine-readable positioned transliteration. The spatial directory currently exposes the Nine Rosettes foldout dataset, including `rosettes/overlay_f85v_86r.json` and `rosettes/tokens_f85v_86r.csv`; GitHub blob SHAs observed at audit were respectively `b91d62bda137a6058f59aa36b621885fe5062a10` and `a5311d1b40d53731fc0453d5ecfbee456c4e2b9a`.

## Prospective admissibility rule
PASS requires an independently authored spatial/token-coordinate dataset covering at least one frozen H91 folio with token coordinates sufficient to define a deterministic visual→token pairing rule without inspecting lexical association outcomes. If there is zero overlap with the frozen H91 folios, status is BLOCKED and no lexical endpoint is run.

## Result
The positioned dataset identified in the audited external source is for the Nine Rosettes foldout `f85v–f86r`. Intersection with the frozen H91 folios is **0/9**.

Controls:
- independent_external_source: PASS
- machine_readable_token_coordinates_exist: PASS
- frozen_H91_family_unchanged: PASS
- H91_folio_overlap_ge_1: FAIL

Therefore **H104 = BLOCKED**. No visual→token mapping was fitted, no lexical statistic was computed, and no alternative H91 folios were substituted after seeing coverage.

## Interpretation
This is a data-availability block, not evidence against a visual–lexical relationship. The newly identified spatial resource is promising for future independently preregistered experiments on its own covered folio, but it cannot legitimately rescue H98 because it does not overlap the frozen H91 replication family.

Semantics = NOT_RUN · Language = NOT_RUN · Translation = NOT_RUN · Decipherment = NOT_RUN
