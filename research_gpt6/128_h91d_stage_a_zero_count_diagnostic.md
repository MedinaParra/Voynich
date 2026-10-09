# H91d — Stage-A zero-count diagnostic audit

Status: **PASS** (diagnostic audit only; does not rescue H91b)

## Purpose

After the preregistered H91b Stage A returned **FAIL** with zero qualifying folios, audit the frozen artifact to determine whether the failure was narrowly caused by the >=15 threshold or whether the recorded object counts were identically zero across the independent inventory. This is a post-result diagnostic and is not confirmatory evidence for the lexical-anchor hypothesis.

## Frozen evidence audited

- H91b workflow run: `37917507060`
- H91b artifact: `h91b-stage-a-manifest`
- Artifact ID: `11611220893`
- Artifact digest: `sha256:2ab9cdcaae21da8a8dbeb6bed87fd5a1358f1b585c57615907bd52a29f64b80c`
- Manifest SHA-256: `7d3ad011dfe66e6b7c978c0c2ffe7c29b0a16e3a88eb4b65eb8577cbe54e39c0`

## Audit result

The frozen manifest contains **225 records** total. Two are the mechanically excluded `f68r1` and `f68r2`. Among the remaining **223** records:

- visual status `PASS`: **166**
- visual status `BLOCKED`: **57**
- `candidate_object_count = 0`: **223 / 223**
- `candidate_object_count > 0`: **0 / 223**
- H91b candidates at the frozen >=15 threshold: **0**

Therefore the H91b failure is not a near-threshold outcome (for example, many folios with 10–14 objects). The generalized Stage-A application produced **zero candidate objects on every non-excluded record**, including all 166 records whose visual extraction status was `PASS`.

## Classification and interpretation

**H91d = PASS** as a diagnostic audit because the frozen artifact is internally sufficient to identify this failure signature.

This does **not** change **H91b Stage A = FAIL** and does not permit Stage B or H92. It also does not establish absence of label-object structure in the manuscript.

The all-zero signature is strong evidence that the next scientifically safe step is an infrastructure/data-semantics audit of why the H76/H91c object definition yields positive counts on the legacy f68r1/f68r2 calibration pages but zero counts across every independent record. That audit must remain lexical-blind and must not lower thresholds or select pages based on label strings.

No semantic, linguistic, translation, or decipherment claim follows.
