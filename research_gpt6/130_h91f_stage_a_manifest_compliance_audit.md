# H91f — H91b/H91e Stage-A manifest compliance audit

Status: **FAIL**

## Scope
This is a preregistration-compliance audit only. It does not inspect lexical strings and does not modify H90/H91/H91b thresholds.

## Frozen requirement
H91b preregistration requires that, before any lexical exposure, Stage A write and hash a manifest containing source identifiers and SHA-256 hashes, the complete enumerated folio list, exclusions and reasons, **object coordinates/counts, label-coordinate identifiers with token text redacted, pairing rule/version, jitter seed(s), and code commit SHA**.

## Observed H91e artifact
Workflow run 37968534704 on experimental-branch head 0ed46fd6c1ff409e66ce9a2f807eb5757488c253 produced artifact 11633904643 (`h91b-stage-a-manifest`, 25271 bytes, ZIP digest sha256:979a95371f7bf1e7563ebf40b0697fd1e9d7839fcd0c6a2f2075c289e1fbd06c). The manifest reports PASS, candidate_count=168, manifest_sha256=a19ba015a3c997dd37c132be564265a34517d696ebe1a7a20fbb907fc269bdce, and 7,184 candidate objects summed over candidate folios.

However, inspection of the generated manifest schema and the Stage-A runner shows that each successful folio record stores only page/source hashes, candidate_object_count, stage_a_candidate, visual_status, image_sha256, and a redacted ordinal placeholder. It does **not** freeze the actual object coordinates, the actual label-coordinate identifiers, pairing rule/version, jitter seed(s), or the code commit SHA required by H91b.

## Classification
**FAIL** for H91f compliance audit: the produced Stage-A artifact does not satisfy the frozen H91b manifest schema. Consequently the prior descriptive extraction (168 candidate folios; 7,184 candidate objects) remains reproducible evidence about the visual extractor, but it is **not a valid H91b Stage-A freeze for opening lexical Stage B**.

H91b confirmatory Stage B remains **NOT_RUN**. H92 remains **NOT_RUN**.

## Allowed next step
A successor prospective repair must freeze, before any lexical exposure, an exact Stage-A schema/runner that serializes the already-required object coordinates, redacted label-coordinate IDs, pairing rule/version, deterministic jitter seed(s), and executing code commit SHA. It must not change the existing candidate threshold (>=15), exclusions (f68r1/f68r2), visual extractor, Stage-B >=80% stability threshold, family gate (>=2 folios and >=40 stable pairs), or inspect lexical strings while constructing the repaired manifest.

No semantic, language, translation, or decipherment claim is made.
