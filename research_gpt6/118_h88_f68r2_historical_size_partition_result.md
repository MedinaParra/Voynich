# H88 — f68r2 historical 36+23 size-partition admissibility result

Status: **FAIL_ADMISSIBILITY**.

This records execution of the frozen protocol in `117_h88_f68r2_historical_size_partition_preregistration.md`. Infrastructure, source-integrity, inventory, and grouping gates all passed. The unsupervised size partition was extremely close to the historical 23-small / 36-large prediction but did not satisfy it, so the result is not promoted.

## Execution evidence

- Workflow: `H88 f68r2 historical size partition`.
- Run: **37652456243** (run number 2).
- Job: **112899022404** (`h88-f68r2-historical-size-partition`).
- Experimental branch head executed: `d40acabc8f48d832188802c1f8f162e867a10cb7`.
- PR merge checkout: `1c9ea64e86f6bbcabab490d4521dfcb5c05c6fe9`.
- Artifact: `h88-f68r2-historical-size-partition-results`, ID **11497905290**.
- Artifact ZIP SHA-256: `7b877fcd75f56e7d1ea89e52b693a2833016941cb0f34ba152bfde402b4d4c06`.

Infrastructure: **PASS**.

## Frozen sources and inventory

Both frozen Git blob identities matched exactly:

- `CONFIRMED_ENDPOINTS.tsv`: `e9733f16dc18b32ab5643c6d08a11f395c49a9c1`;
- `F68R2_GROUP_SCOPE.tsv`: `5bcab575377d59147f313acc5929804f84bf02ab`.

Inventory gates:

- valid unique f68r2 stars: **59**;
- HIGH-confidence visual label↔star groups: **24**;
- missing grouped stars: **0**;
- star parse errors: **0**;
- group parse errors: **0**.

All inventory gates: **PASS**.

## Primary size partitions

The preregistered historical prediction was exactly **23 small border stars + 36 large interior stars**, recovered independently by log bounding-box area and log bounding-box diagonal through the global minimum-SSE two-cluster split.

### Area

- optimal split: **24 small / 35 large**;
- optimal total SSE: **2.748678095539523**;
- second-best split: **23 small / 36 large**;
- second-best total SSE: **2.7515572620210706**;
- second/best SSE ratio: **1.0010474731421697**;
- largest small area: **13,546.24**;
- smallest large area: **13,982.16**;
- boundary ratio: **1.0321801474062196**;
- optimum unique: **PASS**.

Historical-count gate: **FAIL**.

### Diagonal

- optimal split: **24 small / 35 large**;
- optimal total SSE: **0.679547416108371**;
- second-best split: **25 small / 34 large**;
- second-best total SSE: **0.6819606105187699**;
- second/best SSE ratio: **1.0035511788481497**;
- largest small diagonal: **164.91367438754116**;
- smallest large diagonal: **167.236150398172**;
- boundary ratio: **1.0140829801971005**;
- optimum unique: **PASS**.

Historical-count gate: **FAIL**.

## Robustness observations frozen as diagnostics

- area and diagonal partition membership agreement: **59 / 59**;
- grouped stars assigned to the small cluster by area: **0**;
- grouped stars assigned to the small cluster by diagonal: **0**;
- therefore all **24/24** HIGH-confidence label-associated stars fall in the common 35-object large cluster.

These diagnostics are strikingly consistent with a label-bearing interior population, but they cannot rescue the preregistered 23/36 size-count criterion.

## Common 24-object small cluster

The exact small set produced identically by both frozen metrics is:

- `HOBJ_f68r2_9B165406AD77`
- `HOBJ_f68r2_EBC81EC14071`
- `HOBJ_f68r2_222319BDB3B7`
- `HOBJ_f68r2_3A47CFE17F40`
- `HOBJ_f68r2_1CF5F57F6301`
- `HOBJ_f68r2_11B515BAA47C`
- `HOBJ_f68r2_F78E01F368AC`
- `HOBJ_f68r2_665E5F11C7FC`
- `HOBJ_f68r2_FDEE7796EE6E`
- `HOBJ_f68r2_07C6E78D42DD`
- `HOBJ_f68r2_FD6FEE3E56A4`
- `HOBJ_f68r2_65E2D78262E2`
- `HOBJ_f68r2_50D2198107DB`
- `HOBJ_f68r2_A4F4A1C7116A`
- `HOBJ_f68r2_9C5B596B5265`
- `HOBJ_f68r2_6D595B71AAAC`
- `HOBJ_f68r2_34D8D73B52BB`
- `HOBJ_f68r2_4C62BFF7A717`
- `HOBJ_f68r2_0BCC383185CE`
- `HOBJ_f68r2_90CEDA9618ED`
- `HOBJ_f68r2_7437D0A5A09A`
- `HOBJ_f68r2_7A528C1AAC25`
- `HOBJ_f68r2_CA59FCCC6F79`
- `HOBJ_f68r2_25982A4DBF9C`.

## Decision

The frozen protocol required both size metrics to recover exactly 23 small + 36 large. Both instead independently recovered the same **24 small + 35 large** partition.

H88: **FAIL_ADMISSIBILITY**.

No size threshold is moved post hoc to force 23/36.

## Conservative interpretation

The historical size description is strongly but not exactly reflected in the modern human boxes: two independent size scalars agree perfectly on membership, all 24 label-associated stars lie in the large population, and the area objective places the historical 23/36 split only ~0.10% above the optimum SSE. Nevertheless, size alone does not identify the exact 36-object interior set under the preregistered rule.

The only legitimate continuation is a separately preregistered spatial test of the historical **border-ring versus interior** distinction using this frozen 24-small / 35-large partition. Such a test must not alter the H88 size threshold or use Voynich token content.

Semantic identification: **NOT_RUN**.
Language identification: **NOT_RUN**.
Translation: **NOT_RUN**.
Decipherment: **NOT_RUN**.
