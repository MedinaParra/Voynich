# H91e — preregistered repair of H91b Stage-A counter-key bug

Status: **PASS** (diagnostic identification + prospective repair preregistration; repaired execution NOT_RUN)

## Trigger

H91d established that all 223 non-excluded H91b records had `candidate_object_count = 0`, including 166 records for which the visual extractor itself returned `PASS`. This impossible-looking signature was audited against the frozen source before any lexical Stage B was opened.

## Exact defect

The frozen H76 extractor returns the count under the JSON/Python key:

`low_text_overlap_component_count`

but H91b Stage A reads:

`r.get("low_text_overlap_components", 0)`

The latter key does not exist. The default `0` therefore deterministically converted every successful extraction into a zero candidate count. This explains the 223/223 all-zero signature without changing any visual threshold, page selection, lexical value, or object geometry.

## Consequence for prior classification

The observed H91b Stage-A result is retained as historical evidence but is **invalid for testing the preregistered candidate-inventory hypothesis because of an implementation defect**. It must not be reinterpreted as evidence against label-object structure. Stage B and H92 remain NOT_RUN.

## Frozen repair

A repaired H91b Stage-A implementation may change **only** the misspelled lookup:

`low_text_overlap_components` -> `low_text_overlap_component_count`

No other code, source revision, exclusion, image source, Otsu procedure, mask margin, connected-component definition, admissibility criterion, >=15 candidate threshold, lexical firewall, or canonical ordering may change.

## Falsifiable validation controls

Before the repaired independent inventory can be interpreted:

1. Static/source control: verify the repaired program differs from the frozen H91b Stage-A program only in that lookup token (apart from optional comments/version metadata that cannot affect execution).
2. Positive-control replay: feed `f68r1` and `f68r2` through the same repaired counter path and require recovered counts to equal the H76/H91c frozen outputs (57 and 89 low-text-overlap components respectively). These pages remain mechanically excluded from the independent candidate inventory.
3. Independent inventory: rerun the same Yale revision `c4d36f4595292c92da8c7428e30cb23b700a019b` over the same canonically ordered records with `f68r1/f68r2` excluded.
4. Freeze and hash the repaired Stage-A manifest before any lexical strings are inspected.

Classification of the repaired run:

- **PASS** only if the controls above pass and at least one independent folio satisfies the already frozen >=15 rule, allowing the next preregistered gate to be evaluated.
- **FAIL** if controls pass but no independent folio satisfies the frozen rule.
- **BLOCKED** if source equivalence, positive controls, acquisition, or manifest freezing fails.
- Stage B remains **NOT_RUN** until a valid repaired Stage A permits it under the existing preregistration.

No semantic, linguistic, translation, or decipherment claim follows from identifying this software defect.
