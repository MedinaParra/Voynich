# H112 — Independent held-out visual–lexical replication: source admissibility preregistration

Status at registration: **NOT_RUN**.

## Motivation
H105 was positive on Rosettes, but H106–H110 failed increasingly strict controls and H111 failed to construct an independent H91→L* bridge. The stopping rule forbids further tuning on those same observations. H112 therefore asks a prior, falsifiable question: does a genuinely held-out public spatial source contain enough independently specified object↔label pairs to support a confirmatory lexical-anchor replication?

## Frozen candidate sources
Public external mappings not used to fit H105–H111:
- `https://vigibygg-cmyk.github.io/voynich-research/data/folio_maps/f69v_mapping.json`
- `https://vigibygg-cmyk.github.io/voynich-research/data/folio_maps/f75r_mapping.json`

These files are treated only as candidate measurement sources. Their authors' semantic/decipherment claims are not accepted or tested here.

## Lexical firewall
The admissibility decision MUST NOT use Voynich token spelling, token length, glyph identity, frequency, proposed translation, or any association statistic. Only metadata/provenance and explicit pair-level spatial annotation structure may be inspected.

## Required gates
A candidate held-out source is admissible only if all are true:
1. source downloads and parses as machine-readable JSON;
2. folio is outside the H105 Rosettes cohort;
3. source exposes explicit pair-level object↔label records or enough explicit per-pair coordinates/IDs to reconstruct them without lexical content;
4. at least 30 total independently addressable object↔label pairs across admitted sources;
5. at least 2 independently defined visual object classes/subtypes with >=10 pairs each;
6. pairing does not require semantic interpretation, token-informed matching, manual repair, or post-hoc offset choice.

## Decision rule
- **PASS**: all six gates pass. Then freeze source hashes and pair IDs before any lexical values are opened, and preregister a single held-out lexical contrast.
- **FAIL**: infrastructure/source access works, but the public candidate data do not satisfy the frozen admissibility gates.
- **BLOCKED**: source cannot be fetched/parsed or required provenance cannot be evaluated for infrastructural reasons.
- Lexical replication result remains **NOT_RUN** unless H112 admissibility = PASS.

## Stopping rule
If H112 = FAIL, do not infer lexical absence and do not manufacture pairs from narrative descriptions. A future replication requires a new external dataset with explicit pair-level spatial annotations.
