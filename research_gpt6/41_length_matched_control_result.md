# Lc vs Lf exact-length matched negative control — result

Status: **FAIL**.

Evidence source: GitHub Actions run `37545052680`, job `lexical-anchor-length-matched` (`112546944819`), artifact `lexical-anchor-length-matched-results` (`11449892106`), workflow head `3e9f48e668751b91b9000e2e191c15a00c13d36b` (PR merge checkout `fb75b7ac32fbedf77ea6dbb696b84cfbf81e33cf`).

Frozen preregistration: `40_length_matched_control_preregistration.md`.

## Observed

- Eligible source rows before matching: Lc = 36; Lf = 177; total = 213.
- Held-out quire O after exact-length matching: Lc = 18; Lf = 18; balanced accuracy = **0.500000**. Retained lengths 4–9.
- Held-out quire S after exact-length matching: Lc = 17; Lf = 17; balanced accuracy = **0.500000**. Retained lengths 6–9.
- Both folds satisfy the preregistered minimum of at least 10 observations per class.
- Aggregate mean balanced accuracy = **0.500000**.
- Restricted permutations completed = **999**.
- Monte Carlo p = **0.993**.
- Artifact SHA-256 = `8cbac832ff6d8e2ac0a76d91a46040c7fe47fcc26c95fdbf1a599463181da713`.

## Decision

The frozen PASS criterion required valid matched folds, aggregate balanced accuracy > 0.5, and Monte Carlo p <= 0.05. The execution is valid but both inferential thresholds fail. Therefore the preregistered result is **FAIL**.

## Conservative interpretation

After balancing Lc and Lf exactly by token length inside each held-out quire, the original six-feature nearest-centroid classifier falls to chance in both folds. Together with the preceding length-ablation FAIL, this materially weakens the claim that the original Lc-vs-Lf pilot detected robust lexical/morphological structure independent of token length. The original pilot remains a real reproducible association under its original feature set, but it should now be treated as substantially confounded by token-length distribution rather than as a lexical anchor.

This does **not** establish that Lc/Lf lack all linguistic information; it rejects this specific preregistered classifier/evidence path under the exact-length control. It is not translation and not decipherment.

## Ledger

- workflow execution: **PASS**
- exact-length matched scientific control: **FAIL**
- original Lc/Lf lexical-anchor interpretation: downgraded / not supported as length-independent evidence
- translation: **NOT_RUN**
- semantic identity: **NOT_RUN**
- independent replication on fresh manuscript strata: **NOT_RUN**
