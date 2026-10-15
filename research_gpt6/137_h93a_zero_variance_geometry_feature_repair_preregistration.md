# H93a zero-variance geometry-feature repair — preregistration

## Status

**PASS** (infrastructure/mathematical-definition preregistration only). H93 confirmatory execution remains **BLOCKED**; scientific endpoint remains **NOT_RUN**.

## Trigger and evidence

The first H93 workflow execution (run 38026802290) stopped before lexical opening at the geometry-only freeze step with `ValueError: zero global geometry feature standard deviation`. Therefore no token string was read by the H93 runner and no lexical statistic was computed before this repair was frozen.

## Exact allowed repair

The H93 preregistration fixes the visual vector `[log(area), log(width/height), overlap_fraction]` and global standardization. If a frozen feature has population standard deviation exactly zero across all 153 objects, define its standardized coordinate deterministically as `0.0` for every object. Nonzero-variance features remain standardized exactly as preregistered: `(x - mean) / population_sd`, `ddof=0`.

This convention does not drop, replace, tune, reweight, or select a feature using lexical information: a constant feature contributes exactly zero to every Euclidean pair distance. The runner must report which feature indices were constant and retain their raw mean and standard deviation in the artifact.

No other H93 rule changes. Population, pairing, 19,999 within-folio permutations, seed 20261010, one-sided statistic, alpha 0.001, controls, and interpretation ceiling remain frozen.

## Decision rule

- H93a repair implementation: **PASS** only if the sole functional change is deterministic zeroing of exactly-zero-variance standardized coordinates plus reporting their indices.
- H93 scientific result remains **NOT_RUN** until a complete protocol-faithful execution exists.
- Any additional geometry-definition change requires a new prospective preregistration.

Semantics = **NOT_RUN** · Language = **NOT_RUN** · Translation = **NOT_RUN** · Decipherment = **NOT_RUN**.
