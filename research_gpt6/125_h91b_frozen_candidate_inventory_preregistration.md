# H91b — Frozen candidate-inventory repair for independent label↔object replication

Status at preregistration: **NOT_RUN**

## Purpose
H91 was BLOCKED because its required “complete prespecified candidate inventory” was not itself frozen. H91b repairs only that prospective inventory defect. It does not modify H90/H91 results and cannot rescue them.

## Frozen exclusions
- Exclude f68r1 and f68r2 from all confirmatory candidate sets.
- Do not inspect lexical token strings when constructing Stage A candidate inventory.
- No semantic gloss, object naming, dictionary, language hypothesis, translation, or decipherment is permitted.

## Deterministic Stage A inventory rule
Starting from the frozen transcription/image sources already used by the repository, enumerate folios in canonical folio order. A folio enters the Stage A inventory if, without reading lexical strings, the existing visual-object extraction pipeline identifies at least 15 spatially discrete candidate objects and the source provides recoverable coordinate metadata sufficient to apply a deterministic one-to-one nearest-label-coordinate pairing. f68r1 and f68r2 are removed mechanically after enumeration.

Before any lexical string is exposed, Stage A must write and hash a manifest containing: source identifiers and SHA-256 hashes, complete enumerated folio list, exclusions and mechanical reasons, object coordinates/counts, label-coordinate identifiers with token text redacted, pairing rule/version, jitter seed(s), and code commit SHA. That manifest hash freezes the inventory.

## Stage B admissibility gate
Only after the Stage A manifest is committed may token strings be exposed. Per folio:
1. raw deterministic one-to-one pairs >=15;
2. >=80% of pair identities stable under ±5 px x/y coordinate jitter using the frozen procedure;
3. no object or label coordinate used more than once;
4. provenance and hashes reproduce;
5. no post-Stage-A folio addition/deletion is allowed based on lexical content.

Family PASS requires >=2 admissible independent folios and >=40 stable pairs total.

## Classification
- **PASS**: Stage A manifest is frozen before lexical exposure and Stage B family gate is met.
- **FAIL**: complete frozen inventory is evaluated and family gate is not met.
- **BLOCKED**: Stage A cannot be deterministically enumerated/frozen from available sources, provenance is unavailable, or infrastructure prevents completion.
- **NOT_RUN**: no execution evidence exists.

## If and only if PASS
A separate H92 preregistration may test the H90 primary endpoint without tuning: label length; predictors [x,y,r,sin(theta),cos(theta)]; leave-one-out within folio; folio-stratified identity permutation null >=9,999 permutations; alpha=0.01; replication must not be driven by one folio.

## Anti-flexibility
Thresholds, exclusions, pairing rules, predictor family, endpoint and alpha cannot be changed after Stage A freeze. H91b/H92 alone cannot support semantic, linguistic, translation, or decipherment claims.
