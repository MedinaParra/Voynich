# Topology-conditioned lexical-anchor falsification result

Status: **FAIL**.

Frozen preregistration: `50_topology_conditioned_lexical_anchor_preregistration.md`.

## Execution evidence
- Branch: `experiment/lexical-anchor-replication`
- Experimental workflow head: `c5e8de3f22136d973d27048e11a21c619729c7c5`
- PR merge checkout: `33f03352abb3c1bf995dde31466b2c0fc46bcc15`
- GitHub Actions run: `37556354280` (run 54), conclusion `success`
- Job: `112583385579` (`topology-conditioned-lexical-anchor`), conclusion `success`
- Artifact: `topology-conditioned-lexical-anchor-results`, ID `11455085840`
- Artifact SHA256: `34cf519c6ae14a58d6779910d6d3c856b8165541bea532369c36c8f59cc54d98`
- Frozen corpus blob: `2a4533ab9bdfa85db9bad602d590978953055df1`
- Raw label rows: 213
- Rows with topology context: 169
- Excluded for no topology context: 44
- Consensus edges: 96
- Permutations: 999/999

## Fold results
| Quire | matched Lc | matched Lf | baseline BA | topology BA | delta BA |
|---|---:|---:|---:|---:|---:|
| O | 13 | 13 | 0.500000 | 0.461538 | -0.038462 |
| S | 17 | 17 | 0.411765 | 0.411765 | 0.000000 |

Aggregate matched held-out examples per class: 30.

## Aggregate result
- baseline balanced accuracy: `0.45`
- topology-conditioned balanced accuracy: `0.43333333333333335`
- `delta_BA`: `-0.016666666666666663`
- Monte Carlo p: `0.643`
- status: **FAIL**

## Frozen decision
The experiment was valid and exceeded the preregistered minimum sample/fold requirements, and all 999 null permutations completed. However, topology did not improve balanced accuracy: delta_BA was negative, topology-conditioned BA was below 0.5, and p=0.643. Therefore the preregistered decision is **FAIL**.

## Conservative interpretation
The independently supported H1-H4 latent topology does not rescue the Lc/Lf lexical-anchor hypothesis under exact token-length control in this test. The original lexical-anchor pilot remains substantially explained by token-length distribution, and adding frozen topology context supplies no detectable independent predictive information for Lc versus Lf here.

This FAIL should close the current Lc/Lf anchor route unless genuinely new independent evidence motivates a separately preregistered hypothesis. It does not negate H1-H4, which test manuscript-internal structural topology rather than Lc/Lf semantics. It also does not show that all labels lack information or that the manuscript lacks semantics.

Translation: **NOT_RUN**.
Semantic identity of Lc/Lf: **NOT_RUN**.
Decipherment: **NOT_RUN**.
