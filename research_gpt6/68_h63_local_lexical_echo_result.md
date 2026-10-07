# H63 — Same-folio lexical-echo result

Status: **FAIL**.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Frozen preregistration: `research_gpt6/67_h63_local_lexical_echo_preregistration.md`
- Workflow run: `37613076038`, conclusion `success`
- Job: `112764782310` (`local-lexical-echo-h63`), conclusion `success`
- Artifact: `local-lexical-echo-h63-results`, ID `11478560850`
- Artifact SHA256: `c20c01e14249d6310c9fe23a1d4eb5cfcacffa66c465d6e27708449202a04896`
- Primary IVTFF blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Independent Takahashi blob: `7f491b574b65e5fba6b553e57372c3fa50e10fec`
- Randomizations: 999/999 in each corpus

## Primary IVTFF result
- evaluable source folios: **43** across 7 quires
- mean own-folio echo: **0.12187298098**
- mean matched-control echo: **0.09641002479**
- observed mean delta: **+0.02546295619**
- median delta: **+0.00243608454**
- folios with positive delta: **0.51162790698**
- Monte Carlo p: **0.062**
- status: **FAIL**

The observed aggregate direction was positive but missed the frozen `p <= 0.01` criterion and the required `>55%` positive-folio criterion.

## Independent Takahashi result
- evaluable source folios: **44** across 7 quires
- mean own-folio echo: **0.13425585834**
- mean matched-control echo: **0.09076635016**
- observed mean delta: **+0.04348950818**
- median delta: **+0.00108771770**
- folios with positive delta: **0.50000000000**
- Monte Carlo p: **0.004**
- status: **FAIL**

Although the Takahashi aggregate permutation result was significant at the frozen p threshold, only 50% of evaluable folios had positive delta, below the preregistered >55% requirement. The experiment-level replication gate therefore fails regardless of the aggregate Takahashi p-value.

## Experiment-level decision
**FAIL**. The preregistered replicated local lexical-echo gate is not met in either the strict per-corpus sense required for two-corpus replication.

No threshold is relaxed post hoc. The positive Takahashi aggregate and the positive mean direction in both corpora may be reported descriptively, but they do not license a PASS and should not be used to reopen this exact local-echo route without genuinely new independent evidence and a separately preregistered hypothesis.

## Interpretation
H60-H62 remain valid evidence for a reproducible functional/production-register distinction between label loci and running text. H63 shows that this distinction does **not** currently support the stronger claim that label interiors are consistently echoed in same-folio prose under the frozen matched-folio test.

Therefore the claim ladder remains at **FUNCTIONAL**, not SEMANTIC-CLASS or LEXICAL.

Semantic gloss: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
