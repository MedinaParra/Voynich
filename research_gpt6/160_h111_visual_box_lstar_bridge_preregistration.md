# H111 — H91 visual-box ↔ IVTFF L* bridge admissibility

Status: PREREGISTERED / NOT_RUN

## Motivation
H110 closed further subdivision of the Rosettes H105 effect. H92 independently failed to replicate a geometry→lexical-length anchor, while H98 was blocked because its GC-v101 representation supplied zero usable labels for the nine-folio bridge. H67 nevertheless established that the frozen IVTFF source contains a non-trivial L* label population. H111 therefore tests only whether an independently specified, auditable bridge between the existing H91 visual inventory and IVTFF L* records is feasible. It does **not** test meaning, language, translation, or decipherment.

## Frozen inputs
1. The H91/H91b visual inventory already present in this branch and its recorded folio/page coordinates and visual boxes. No boxes may be added, deleted, moved, or reclassified after inspecting IVTFF token strings.
2. The same frozen IVTFF source and parser used by H67. No token normalization beyond the already-defined H67 normalization is permitted.
3. Only folios represented in both frozen inputs are eligible.

## Bridge rule (token-blind)
The bridge must be constructed without using Voynich token spelling, token length, glyph identity, edit distance, frequency, or any downstream lexical statistic. Candidate textual records are restricted by metadata only: folio/page identity, L* locus/class, and ordinal/locator information exposed by the frozen IVTFF representation. Candidate visual records are restricted by the pre-existing H91 box geometry/ordering only.

Within each common folio/page, establish deterministic visual reading order from the H91 coordinates using the already-recorded page orientation: primary key top-to-bottom centroid position, secondary key left-to-right centroid position, with stable box identifier as the final tie-breaker. Establish textual order only from IVTFF locator/ordinal metadata. Pair by ordinal rank **only when the counts on that folio/page are exactly equal**. Folios/pages with unequal counts are excluded rather than repaired, trimmed, duplicated, manually reassigned, or optimized.

No token string may be inspected to decide whether a pair is retained.

## Primary admissibility endpoint
Let `N_exact` be the number of paired records contributed by folio/pages satisfying exact count equality, and `F_exact` the number of distinct contributing folio/pages.

H111 = **PASS** iff all of the following hold before any lexical outcome is inspected:
- `F_exact >= 3`;
- `N_exact >= 30`;
- at least two admissible IVTFF L* classes are represented among the paired records;
- every retained pair is reproducible solely from the frozen metadata/order rules above;
- zero manual/token-informed repairs are required.

Otherwise H111 = **FAIL** if the pipeline executes correctly but the admissibility thresholds are not met. H111 = **BLOCKED** only for an infrastructure/source failure that prevents evaluating the frozen rule. H111 = **NOT_RUN** until an actual execution with evidence exists.

## Mandatory controls / evidence
The runner must emit:
- commit SHA and source hashes/identifiers for both frozen inputs;
- common folio/page count;
- per-folio/page `n_visual`, `n_Lstar`, equality flag, and retained-pair count;
- `F_exact`, `N_exact`, represented L* classes;
- a bridge table containing only metadata identifiers/coordinates/ordinals plus token values in a separately sealed output column that is not read by the admissibility logic;
- machine-readable final status PASS/FAIL/BLOCKED;
- explicit assertions that no lexical field is imported into the pairing function and that input boxes were not mutated.

## Stopping rule
- If H111 FAILS, do not relax equality, thresholds, ordering, or use nearest-neighbour/token similarity to rescue the bridge. Seek a genuinely independent source with explicit visual↔text locators.
- If H111 PASSES, freeze the resulting pair IDs and hashes before preregistering **one** lexical-anchor statistic. H111 PASS alone is not evidence of semantics.

## Interpretation guardrail
PASS means only that a sufficiently sized token-blind visual↔text bridge can be built under the frozen rules. FAIL means this bridge design is inadmissible at the preregistered scale. Neither outcome licenses a translation or semantic assignment.
