# H102 — Q13 physical-boundary JSD preregistration

Status before execution: NOT_RUN

## Motivation
H101 tested one frozen candidate ordering of the five Q13 bifolios and returned FAIL despite a small reduction in median adjacent-folio character-unigram JSD. H102 asks a different, falsifiable question: is lexical discontinuity specifically concentrated at physical boundaries between bifolios rather than within a physical bifolio?

## Frozen source and physical structure
- Takahashi source SHA256: `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`.
- Frozen Q13 bifolio identities: `(75,84),(76,83),(77,82),(78,81),(79,80)`.
- Frozen candidate bifolio order inherited from H101: `(77,82),(76,83),(75,84),(78,81),(79,80)`.
- No lexical data may be used to alter these identities or this order.

## Unit and metric
Use the 20 folio sides in the frozen candidate sequence. For every adjacent pair, compute character-unigram Jensen-Shannon divergence exactly as in H101.

Classify adjacency *before looking at H102 outcomes*:
1. `WITHIN_LEAF`: recto→verso of the same numbered leaf.
2. `WITHIN_BIFOLIO`: the adjacency joining the two leaves of one frozen bifolio (`a verso -> b recto`).
3. `BETWEEN_BIFOLIO`: adjacency crossing from the end of one frozen bifolio to the start of the next in the frozen candidate order.

Primary contrast: median JSD of `BETWEEN_BIFOLIO` versus the pooled physical-internal set `WITHIN_LEAF + WITHIN_BIFOLIO`.

## Exact randomization test
With the 19 observed adjacency JSD values held fixed, enumerate all `C(19,4)=3876` placements of four BETWEEN_BIFOLIO labels. Test statistic is `median(BETWEEN_BIFOLIO) - median(INTERNAL)`. One-sided exact p-value is the fraction of assignments with statistic >= observed.

## Decision rule
H102 = PASS only if BOTH:
- observed median JSD(BETWEEN_BIFOLIO) > median JSD(INTERNAL), and
- exact one-sided p <= 0.01.
Otherwise H102 = FAIL.

H102 = BLOCKED if source SHA mismatches, the frozen 20-side set is incomplete, there are not exactly 4 BETWEEN_BIFOLIO adjacencies and 15 internal adjacencies, or any JSD is non-finite.

## Controls
Mandatory controls: source SHA identity, frozen candidate identity, 20/20 side coverage, adjacency count 19, between count 4, internal count 15, finite JSD, exact enumeration count 3876. Each is reported strictly PASS/FAIL; a failed mandatory control makes the experiment BLOCKED.

## Interpretation firewall
PASS would support physical-boundary-associated lexical discontinuity in this Q13 candidate reconstruction. It would NOT establish the correct historical order, language, semantics, translation, cipher, or decipherment. FAIL would mean this simple physical-boundary explanation is not supported under the preregistered test. No threshold, order, bifolio identity, endpoint, or adjacency class may be changed after seeing H102 results.
