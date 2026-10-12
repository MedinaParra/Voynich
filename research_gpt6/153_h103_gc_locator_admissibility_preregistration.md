# H103 — GC v101 locator admissibility audit for H91 visual-label family

Status before execution: **NOT_RUN**.

## Purpose
H98 is permanently BLOCKED under its preregistered ordinal bridge (0/153 resolved pairs in repeated runs). H103 does not alter or rescue H98. It asks a prior admissibility question: does the frozen GC v101 transcription contain independently machine-identifiable locator records on the nine H91 folios that could support a *future* prospectively frozen visual→locus bridge?

## Frozen source
GC v101 SHA256: `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f`.
Mismatch => BLOCKED.

Frozen H91 folios: `f14v,f25v,f39r,f40r,f50v,f87r,f8v,f90r1,f95r2`.

## Audit, without lexical opening
Parse every IVTFF record matching `<folio.line,locator> payload`. For each frozen folio report only numeric counts by normalized locator prefix (first ASCII alphabetic character after stripping leading `@+*=`), total parseable records, and total single-token records. Do NOT emit token strings, lengths, or lexical features.

## Decision rule
H103 = PASS iff:
1. source SHA matches;
2. all 9 frozen folios have at least one parseable IVTFF record;
3. at least one identical normalized locator prefix is present on all 9 folios; and
4. that shared prefix has at least 1 single-token record on every folio.
Otherwise H103 = FAIL, except malformed/unreadable source => BLOCKED.

No particular prefix (including `L`) is privileged after preregistration; the shared-prefix set is determined exhaustively from locator syntax only. This is an admissibility audit, not a lexical association test.

## Interpretation firewall
PASS means only that GC exposes a common machine-identifiable locator class potentially usable to design a new independently frozen bridge. It does not validate ordinal correspondence, H98, geometry→lexicon association, semantics, language, translation, or decipherment. FAIL means GC v101 alone does not expose such a common locator class under this frozen syntax audit.

Semantics = NOT_RUN · Language = NOT_RUN · Translation = NOT_RUN · Decipherment = NOT_RUN.
