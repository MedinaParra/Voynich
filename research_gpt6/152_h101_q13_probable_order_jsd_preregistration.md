# H101 — Q13 probable-order consecutive-folio JSD test

Status: **PASS** (preregistration only). Execution: **NOT_RUN**.

## Motivation
H96/H97/H100 show a persistent excess of real consecutive-folio character-unigram JSD relative to the tested generators. The user requested testing a probable bifolio order rather than silently assuming current binding order.

This experiment does **not** claim that the candidate is the historical order. It asks only whether the already-existing Q13 candidate materially changes the observed consecutive-folio heterogeneity inside Q13.

## Frozen candidate before H101
The candidate was discovered in H73 and prospectively frozen/tested in H74, before H101:

`77|82 -> 76|83 -> 75|84 -> 78|81 -> 79|80`

H74 independently tested it in GC/v101: candidate score 0.7182146753922127 versus current 0.6734273220203645, but exact p=0.08333333333333333, hence H74 = FAIL. Therefore throughout H101 it must be called **probable/candidate order**, never correct/original order.

Frozen current physical nesting order:

`75|84 -> 76|83 -> 77|82 -> 78|81 -> 79|80`

## Frozen transcription
Use the same Takahashi IT2a-n source identity inherited from H96/H100:
SHA-256 `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`.
Mismatch => **BLOCKED**.

## Reading-sequence construction
For each ordered bifolio `a|b`, expand deterministically as:
`fa r, fa v, fb r, fb v`, retaining only folio sides present in the frozen transcription.
No orientation, side order, or bifolio direction may be optimized using lexical statistics.

Construct exactly two Q13 sequences using the same expansion rule:
1. current physical nesting order;
2. frozen H73/H74 candidate order.

If any folio side required for a fair paired comparison is unavailable, restrict both sequences to the identical intersection and report coverage. If fewer than 16 common folio sides remain, H101 = **BLOCKED**.

## Primary statistic
For every adjacent pair in each sequence compute character-unigram Jensen-Shannon divergence using the same character normalization/JSD implementation as H96/H100.

Primary summaries:
- median consecutive-folio JSD in current order;
- median consecutive-folio JSD in candidate order;
- delta = candidate median - current median.

## Frozen decision rule
H101 = **PASS** iff candidate-order median JSD is at least 20% lower than current-order median JSD:

`candidate_median <= 0.80 * current_median`.

Otherwise H101 = **FAIL**.

The 20% threshold is frozen before execution. No p-value rescue, alternate order, orientation search, metric substitution, endpoint dropping, or threshold change is permitted.

## Mandatory controls
- source SHA identity = PASS;
- candidate identity exactly matches H74 = PASS;
- current-order identity exactly matches H73/H74 = PASS;
- identical folio-side set in both comparisons = PASS;
- common coverage >=16 sides = PASS;
- same H96/H100 character normalization/JSD = PASS;
- finite JSD for every compared adjacency = PASS.

Any mandatory control failure => **BLOCKED**.

## Diagnostics only
Report full adjacency JSD vectors and which adjacencies change. These cannot rescue the primary rule.

## Interpretation ceiling
PASS would show only that the pre-existing Q13 candidate substantially reduces local consecutive-folio character-distribution discontinuity relative to current nesting under this fixed metric. It would not establish historical order, semantics, language, cipher key, translation, or decipherment.

FAIL would show that this specific probable/candidate Q13 ordering does not reduce the local discontinuity enough to meet the frozen effect-size criterion.

Semantics = **NOT_RUN**. Language = **NOT_RUN**. Translation = **NOT_RUN**. Decipherment = **NOT_RUN**.
