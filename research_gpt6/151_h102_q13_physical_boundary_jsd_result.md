# H102 — Q13 physical-boundary JSD result

Scientific status: **FAIL**  
Infrastructure: **PASS**

## Execution evidence
- Workflow run: `38236696962`
- Job: `114769031033`
- PR merge commit executed: `96e46062e06055833722a0074182cd2c94c01cda` (branch head `9f8a02b6eef3fcb944f98c9b7d63f55bbfae9faa` merged into audit base)
- Artifact: `h102-q13-physical-boundary-jsd`, ID `11741570846`, size 1131 bytes
- Artifact ZIP SHA256: `450ff61afaac888c099535a6947c0941c13ea9e8d740b8b6a2a6bfeed7ecee00`
- Frozen Takahashi SHA256 matched: `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`

## Mandatory controls
All **PASS**:
- source SHA identity
- candidate identity
- coverage 20/20
- adjacency count 19
- BETWEEN_BIFOLIO count 4
- internal count 15
- finite JSD
- exact enumeration count 3876

## Frozen primary test
Candidate bifolio order:
`77|82 -> 76|83 -> 75|84 -> 78|81 -> 79|80`

- median JSD(BETWEEN_BIFOLIO) = `0.01162803894117407`
- median JSD(INTERNAL) = `0.010049132988957637`
- observed difference = `+0.0015789059522164327`
- exact one-sided randomization p = `0.2835397316821465`
- extreme-or-equal assignments = `1099 / 3876`

Preregistered PASS required BOTH a positive difference and `p <= 0.01`. The direction was positive, but the exact p-value was far above the frozen threshold. Therefore **H102 = FAIL**.

## Conservative interpretation
Under the frozen Q13 candidate reconstruction, boundaries between bifolios have a somewhat higher median character-unigram JSD than physical-internal adjacencies, but the effect is not statistically unusual under the preregistered exact randomization test. H102 therefore does not support the simple hypothesis that the unresolved between-folio heterogeneity is concentrated at bifolio boundaries.

This result must not be used to optimize a new Q13 order post hoc. It does not establish historical order, semantics, language, translation, cipher, or decipherment.

Semantics = **NOT_RUN** · Language = **NOT_RUN** · Translation = **NOT_RUN** · Decipherment = **NOT_RUN**
