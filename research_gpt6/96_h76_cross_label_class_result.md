# H76 — Cross-label-class validation result

Status: **BLOCKED**

## Frozen execution
- Run: `37647474949`
- Job: `112881904341`
- Head commit: `c30aaf1319b07eec7f17a27afa9c64377b80fb81`
- Artifact: `11493734145`
- Artifact SHA-256: `294e6f790ffc3b1dbce293d79cd19f89f0dee598fe206d969eceebd83386513b`

## Count-only sample audit
PHARMA (`Lc`/`Lf`):
- events: **33**
- folios: **12**
- subtype counts: `Lc=7`, `Lf=26`

ZODIAC (`Lz`):
- events: **0**
- folios: **0**

Total confirmatory events: 33 across 12 unique folios.

The preregistration required each class to have >=15 events and >=6 folios, with >=40 total events and >=12 total folios. These thresholds were not met because no zodiac event had a strict same-folio paragraph (`P*`) baseline satisfying the exact-prefix/length/metadata controls in both frozen transcriptions.

## Conclusion
H76 is **BLOCKED**, not FAIL. No `a` outcomes, class statistics or permutations were evaluated after the sample audit failed.

The absence of eligible `Lz` events reflects incompatibility between the H71 same-folio paragraph-control design and the zodiac-page layout; it is not evidence that zodiac labels lack the H72/H73 effect. The same-folio rule must not be relaxed retrospectively to rescue H76.

Language identification, semantic identification, translation and decipherment remain **NOT_RUN**.
