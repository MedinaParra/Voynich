# H91c — Generic visual-extractor infrastructure repair

Status at preregistration: **NOT_RUN**

## Purpose
H91b is prospectively frozen but Stage A cannot currently execute because the repository's H76 visual-object extractor is wired specifically to f68r1/f68r2, which H91b excludes. H91c is an infrastructure-only repair. It must not inspect lexical token strings, select folios using lexical information, alter H90/H91/H91b outcomes, or test a geometry→lexical association.

## Frozen scope
Implement a generic wrapper/refactor of the existing H76 visual-object extraction procedure so that it can accept arbitrary folio image/coordinate inputs while preserving the existing image-processing algorithm and thresholds. The repair may change input plumbing, iteration over folios, serialization, provenance recording, and error handling only.

The implementation MUST preserve from the current H76 implementation, without tuning on candidate folios: image preprocessing; thresholding/Otsu procedure; foreground-mask convention; connected-component/object extraction logic; component inclusion/exclusion criteria; geometric measurements; and all numeric thresholds used by H76.

## Lexical firewall
During H91c implementation and validation, lexical token strings are forbidden inputs. Coordinate records may be consumed only in a redacted form containing identifiers/positions needed for later deterministic pairing. No token text, token length, glyph morphology, semantic gloss, language hypothesis, dictionary, translation, or decipherment may be used.

## Validation
Before H91b Stage A may use the generic extractor, H91c must replay the generic implementation on the already-known f68r1/f68r2 H76 inputs solely as an infrastructure equivalence test. For each replayed folio, the generic implementation must reproduce the legacy H76 object count and object geometry/coordinates exactly, subject only to deterministic serialization ordering. Source hashes, code commit SHA, and comparison output must be recorded.

## Classification
- **PASS**: generic implementation exists and exact replay equivalence is demonstrated on both f68r1 and f68r2 with recorded evidence.
- **FAIL**: implementation executes but differs from legacy H76 extraction on either replay folio.
- **BLOCKED**: required legacy inputs/results cannot be retrieved, provenance cannot be reproduced, or infrastructure prevents implementation/equivalence testing.
- **NOT_RUN**: no execution evidence exists.

## Consequence
Only H91c PASS permits H91b Stage A to execute with the generic extractor. H91c itself cannot make H91b PASS and cannot authorize H92. If H91c FAIL or BLOCKED, H91b Stage A remains BLOCKED.

## Anti-flexibility
No threshold or extraction rule may be modified in response to candidate-folio behavior. Any scientifically motivated change to the extractor requires a new preregistration and cannot be represented as this infrastructure repair. f68r1/f68r2 are replay controls only and remain excluded from the H91b confirmatory candidate inventory.