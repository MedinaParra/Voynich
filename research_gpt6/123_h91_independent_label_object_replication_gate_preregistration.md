# H91 — Independent label↔object replication gate (preregistration)

Status at preregistration: **NOT_RUN**

## Purpose
H90 on f68r1 was FAIL at the preregistered alpha despite a directional effect. H91 is a prospective data/admissibility gate for a genuinely independent label↔object replication. It is not a rescue analysis of f68r1 or f68r2.

## Frozen exclusions
- f68r1 and f68r2 are excluded from the confirmatory replication set because they have already been inspected repeatedly in H76–H90.
- No H90 parameter, endpoint, alpha, or predictor may be tuned using candidate-folio labels.
- No semantic gloss, star/plant/name identification, dictionary, language hypothesis, or translation is permitted in H91.

## Blind two-stage gate
Stage A must inspect only page/region metadata and visual object geometry, with lexical token strings hidden. Candidate folios must be selected before Stage B exposes their label strings.

A candidate folio is admissible only if all of the following hold:
1. It is not f68r1 or f68r2.
2. It contains at least 15 visually discrete objects with a deterministic one-to-one nearest-label pairing under the same pairing rule used by H79, or a rule frozen before lexical strings are exposed.
3. At least 80% of those pairings remain identical under coordinate jitter of ±5 px in x and y.
4. No object is paired to more than one label and no label to more than one object.
5. The folio and all coordinates/tokens are recoverable from frozen, hash-recorded sources.

Family gate: at least **2 independent admissible folios** and at least **40 total stable pairs** across them are required before any confirmatory geometry→lexical test may run.

## Outcome classification
- **PASS**: all five per-folio conditions are met for at least 2 independent folios and total stable pairs >=40.
- **FAIL**: the complete prespecified candidate inventory can be evaluated and the family gate is not met.
- **BLOCKED**: required images/coordinates/transcriptions cannot be retrieved, provenance cannot be frozen, or infrastructure prevents evaluating the complete candidate inventory.
- **NOT_RUN**: no execution with evidence exists yet.

## If and only if H91 PASS
H92 may be preregistered. H92 must freeze the H90 primary endpoint (label length), predictor family [x,y,r,sin(theta),cos(theta)], leave-one-out evaluation within folio, a folio-stratified identity-permutation null with >=9,999 permutations, and alpha=0.01. The confirmatory claim must require replication across independent folios rather than pooling being driven by one folio.

## Anti-flexibility rules
- A FAIL/BLOCKED H91 cannot be converted to PASS by lowering pair-count or stability thresholds after inspection.
- Candidate folios cannot be dropped because their labels look inconvenient.
- Secondary lexical features cannot rescue failure of the frozen primary endpoint in H92.
- H91/H92 cannot support a semantic, linguistic, translation, or decipherment claim by themselves.

## Required evidence record
Execution must record candidate folios inspected, source URLs/paths and SHA-256 hashes, raw and stable pair counts per folio, stability fractions, exclusions with reasons, total stable pairs, and final PASS/FAIL/BLOCKED status.
