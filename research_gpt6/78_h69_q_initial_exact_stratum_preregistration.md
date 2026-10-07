# H69 — Exact-stratum q-initial conditional permutation preregistration

Status: **NOT_RUN**.

## Motivation
H68 replicated a large negative q-initial label-vs-running-text contrast in both frozen transcriptions using one deterministic same-folio, same-Currier, same-hand, exact-length control per label. H69 attacks the remaining one-control sampling choice directly. It uses every token instance in each frozen matching stratum and asks whether q-initial labels are still depleted after conditioning exactly on the full stratum.

H69 is adaptive to H68. It is a confound/sampling robustness test, not an independent manuscript sample and not a semantic test.

## Frozen sources
- primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`;
- independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`.

Parse the two corpora separately. No exact-consensus filtering is used.

## Frozen token construction
For each transcription independently:
1. a label token is a locus marked `L...` with exactly one certain alphabetic token of length >=2;
2. running-text token instances are all certain alphabetic tokens at non-label loci;
3. define the exact stratum `s = (folio, Currier, hand, token_length)`;
4. retain a label only through strata that contain at least one running-text token;
5. retain **all** token instances in an included stratum; there is no single-control draw, token-identity matching, prefix/suffix matching, or illustration/semantic information.

## Frozen feature
The sole measured feature remains:
- `starts_q(token)` = 1 iff the EVA token begins with `q`, otherwise 0.

No other glyph feature is tested.

## Primary conditional statistic
For every included stratum `s`, let:
- `nL_s` = number of label-token instances;
- `nT_s` = total label + running-token instances;
- `qL_s` = q-initial label count;
- `qT_s` = q-initial total-token count.

Under exchangeability of label status inside the exact stratum, expected q-initial labels are
`E[qL_s] = nL_s * qT_s / nT_s`.

The primary effect is
`D = sum_s(qL_s - E[qL_s]) / sum_s(nL_s)`.

Negative D means q-initial tokens are depleted among labels relative to the exact-stratum expectation.

Report also raw label and running q prevalence as descriptive diagnostics. They are not decision statistics.

## Quire support and directional replication
Count included label instances by quire. A quire is evaluable if it contains >=10 included labels. Only strata from evaluable quires enter the inferential statistic.

Report per-quire conditional D. H69 is frozen to the **negative direction observed in H68**; at least 3 evaluable quires must have D < 0 in each transcription.

## Null
For each transcription separately, run exactly **999** deterministic conditional permutations.

Within every included exact stratum on every permutation, randomly choose exactly `nL_s` of the `nT_s` token instances as pseudo-labels, thereby preserving the label count, folio, Currier, hand, token-length distribution, and total q count of every stratum exactly.

Seeds:
- primary: `20261009`;
- independent: `20261010`.

For each permutation recompute D. Two-sided Monte Carlo p:
`p = (1 + count(abs(D_null) >= abs(D_obs))) / 1000`.

## Frozen support gate
Each transcription must have:
- >=80 included label instances across evaluable quires;
- >=4 evaluable quires;
- >=20 included exact strata;
- 999/999 completed permutations.

## Frozen decision
A transcription is **POSITIVE** iff:
1. support gate passes;
2. `D <= -0.05`;
3. two-sided Monte Carlo `p <= 0.01`;
4. >=3 evaluable quires have per-quire D < 0.

Experiment-level **PASS_EXACT_STRATUM_Q_DEPLETION** iff both frozen transcriptions are POSITIVE.

**FAIL** if both execute validly but the joint gate is missed.

**BLOCKED** if either source cannot meet support/infrastructure requirements.

No threshold, stratum, feature, direction, source, or exclusion may change after result inspection.

## Interpretation ceiling
PASS would show that the replicated H68 q-initial depletion does not depend on choosing one running-text control and survives exact conditioning on folio, Currier, hand, and token length using all matched token instances.

It would remain an orthographic/functional-register constraint only. It would not identify what `q` means, label semantics, depicted-object identity, language, cipher, plaintext, translation, or decipherment.

Semantic gloss: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
