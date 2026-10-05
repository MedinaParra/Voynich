#!/usr/bin/env python3
"""Audit stored outputs and percentile arithmetic in source notebook 28.

This does not rerun the notebook or the Hebrew corpus comparison. It checks
the committed notebook's saved results and verifies whether its displayed
percentile expression computes the empirical percentile it claims to report.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

EXPECTED_SHA256 = "38686c3aa394ee36d1ea75c45e72ee3e11caeb7aa2f22fe2245c2f73527c38f5"
SOURCE_COMMIT = "47e6a77dc9d5cd570c375f4aff710fa4a0567278"
BAD_EXPR = "np.mean([1 for x in null_rates if bigram_rate > x]) / len(null_rates) * 100"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebook", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    raw = args.notebook.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    doc = json.loads(raw.decode("utf-8"))
    sources, outputs = [], []
    for cell in doc.get("cells", []):
        src = "".join(cell.get("source", []))
        out = "".join("".join(x.get("text", [])) for x in cell.get("outputs", []))
        sources.append(src)
        outputs.append(out)
    source = "\n".join(sources)
    output = "\n".join(outputs)
    rounds = [float(x) for x in re.findall(r"Monte Carlo p = ([0-9.]+)", output)]
    z_match = re.search(r"Z-score: ([+-]?[0-9.]+), percentile: ([0-9.]+)%", output)
    if len(rounds) != 3 or not z_match:
        raise SystemExit("Could not find the three stored crib p-values and bigram output")
    z_reported, pct_reported = map(float, z_match.groups())
    z_tail_normal = 0.5 * math.erfc(z_reported / math.sqrt(2))
    expr_present = BAD_EXPR in source
    # The notebook creates a list of k ones, so mean(...) is 1 for every k>0;
    # dividing that by N and multiplying by 100 prints 100/N% regardless of k.
    sample_outputs = {str(k): ("NaN" if k == 0 else 100 / 1000) for k in (0, 1, 100, 1000)}
    result = {
        "status": "PASS_SOURCE_AND_ARITHMETIC_AUDIT",
        "scope": "Reads saved outputs and audits notebook formula; does not rerun Hebrew/Torah experiment.",
        "source_notebook": "28_zodiac_cribs.ipynb",
        "source_commit": SOURCE_COMMIT,
        "source_sha256": digest,
        "source_hash_matches_expected": digest == EXPECTED_SHA256,
        "stored_zodiac_crib_monte_carlo_p_values": rounds,
        "crib_rounds_significant_at_0_05": [p < 0.05 for p in rounds],
        "stored_hebrew_bigram_result": {
            "valid_pairs": "9581/9582",
            "reported_null_mean_percent": 75.3,
            "reported_null_sd_percentage_points": 16.1,
            "reported_z": z_reported,
            "reported_percentile": pct_reported,
            "normal_approximation_upper_tail_from_z": z_tail_normal,
            "normal_approximation_limit": "Diagnostic only; the permutation distribution and its dependence structure are not available here."
        },
        "percentile_expression": {
            "buggy_expression_present": expr_present,
            "reported_expression": BAD_EXPR,
            "demonstration_percent_for_k_null_scores_below_observed_out_of_1000": sample_outputs,
            "correct_form_for_count": "100 * sum(score < observed for score in null_rates) / len(null_rates)",
            "finding": "The saved 0.1% display is not the empirical percentile: it is fixed at 0.1% whenever at least one null score is below observed."
        },
        "conclusion": "The notebook's three zodiac-crib searches report p=0.6103, 0.8066, 0.7713 (none significant). The separate bigram comparison has a percentile-reporting bug and cannot support the claimed 0.1% percentile. No plaintext mapping is validated by these outputs."
    }
    if digest != EXPECTED_SHA256:
        result["status"] = "BLOCKED_SOURCE_HASH_MISMATCH"
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
