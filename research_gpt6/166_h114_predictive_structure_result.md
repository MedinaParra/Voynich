# H114 — Held-out predictive structure beyond frozen generative controls: result

## Strict classification
**H114 = FAIL**

Infrastructure = **PASS**. GitHub Actions run `38750335513`, job `116474765554`, completed successfully. All frozen controls reported PASS: source hash, partition hash, non-empty train/test, and exactly 200 null replicas.

## Frozen provenance
- Experimental branch: `experiment/h58-strict-l-vs-p`
- Workflow head SHA: `dc8680a7dda04c406c3ff275b11fa83fa6d21e94`
- Actions PR merge execution SHA: `b85b9be4e7d72e479ce8138a27960df36d8b404b`
- Takahashi source SHA-256: `32b11a0b584a75bbe9817c96a316a246f82d02d69996d789bc2cb908190bab77`
- Partition hash: `50c82d6b48da54c3e2a1b70f14743f4c41bb2112ba74976de7185147d9d1766c`
- Primary frozen null: H96 `token_markov1`
- Null replicas: 200
- Null seed: 96002
- Additive alpha: 0.5
- Artifact ID: `11981491947`
- Artifact ZIP SHA-256: `b67d9344185a0d4ca70a594f8b1bc6aec63e0ca94d53cf73cf18f74094056f38`
- Statistics hash: `00804ad0b41558601f50aa80e802f8fe80b789ec6ba90c24f4dee3baf25be682`

## Primary results
Eligible held-out prediction positions: **8046**.

Observed pooled held-out NLL (nats/token):
- UNIGRAM: **7.4082648321**
- TOKEN_M1: **8.3694834058**
- TOKEN_M2: **8.4840575143**

Frozen increments:
- `D10 = NLL_UNIGRAM - NLL_TOKEN_M1 = -0.9612185737`
- `D21 = NLL_TOKEN_M1 - NLL_TOKEN_M2 = -0.1145741085`

Frozen null summaries:
- D10 median: **-0.0665994803**
- D10 99th percentile: **-0.0029633353**
- D21 median: **-0.5190018228**
- D21 99th percentile: **-0.4910927284**

Preregistered gates:
- D10 > 0 and > null p99: **FAIL**
- D21 > 0 and > null p99: **FAIL**

Therefore H114 = **FAIL** by the preregistered conjunctive rule.

## Secondary diagnostics (non-decisional)
- Eligible folios: 200
- Development folios: 160
- Holdout folios: 40
- Vocabulary size including `<UNK>`: 6871
- Held-out `<UNK>` rate: **0.1512552821**
- Fraction of held-out folios with D10 > 0: **0.025**
- Fraction of held-out folios with D21 > 0: **0.075**

## Scientific interpretation
Under the exact frozen tokenization, smoothing, H96 partition, and token-Markov controls, adding one-token or two-token lexical context did **not** improve held-out token prediction over the unigram baseline. In fact, pooled held-out NLL worsened from unigram to first-order and again from first-order to second-order.

This falsifies the specific H114 claim that this frozen token-level sequential representation contains out-of-sample predictive structure exceeding the preregistered H96 token-Markov-1 null under the specified models.

It does **not** show that the manuscript lacks structure or language. The result is representation- and estimator-specific. The relatively high held-out `<UNK>` rate (~15.1%) and very large development vocabulary are useful diagnostics, but they were observed after execution and therefore must not be used to retune H114 or convert this FAIL into another test post hoc.

Any future character/subtoken/morphological predictive experiment must be independently motivated and preregistered before execution, with a new held-out firewall; it is not a repair of H114.

Semantics: **NOT_RUN**
Language identification: **NOT_RUN**
Translation: **NOT_RUN**
Decipherment: **NOT_RUN**
