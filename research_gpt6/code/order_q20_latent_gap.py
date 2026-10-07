#!/usr/bin/env python3
"""Localize the missing Q20 109|110 as an unscored latent gap.

No text is imputed for the missing bifolium.  We only ask which observed
adjacency in the current principal Q20 candidate is weakest under independent
support diagnostics and therefore most plausibly interrupted by an unseen node.

The diagnostics remain separate:
- residual-bootstrap edge selection frequency;
- full-corpus dialect-controlled residual edge score;
- stable pairwise boundary-direction evidence (support / conflict / absent).

No weighted sum is used.  A Pareto frontier of 'gap weakness' is reported.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CANDIDATE = [
    "S3_105|114",
    "S5_107|112",
    "S4_106|113",
    "S2_104|115",
    "S6_108|111",
    "S1_103|116",
]


def edge(a, b):
    return tuple(sorted((a, b)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bootstrap", type=Path)
    ap.add_argument("controls", type=Path)
    ap.add_argument("pareto", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    b = json.loads(args.bootstrap.read_text(encoding="utf-8"))
    c = json.loads(args.controls.read_text(encoding="utf-8"))
    p = json.loads(args.pareto.read_text(encoding="utf-8"))

    boot = {
        tuple(r["edge"]): float(r["frequency"])
        for r in b["q20_dialect_residual"]["edge_selection_frequency"]
    }
    residual = {
        edge(*r["edge"]): float(r["residual"])
        for r in c["pairwise_combined_sorted_by_residual"]
    }
    arrows = {tuple(x) for x in p["stable_direction_precedence_constraints"]}

    rows = []
    for i, (a, z) in enumerate(zip(CANDIDATE, CANDIDATE[1:]), 1):
        e = edge(a, z)
        if (a, z) in arrows:
            dstate = "supports_candidate_direction"
            dsupport = 2
        elif (z, a) in arrows:
            dstate = "opposes_candidate_direction"
            dsupport = 1
        else:
            dstate = "no_stable_pairwise_arrow"
            dsupport = 0
        rows.append({
            "gap_after_position": i,
            "between": [a, z],
            "edge": list(e),
            "bootstrap_frequency": boot.get(e, 0.0),
            "residual_score": residual[e],
            "direction_state": dstate,
            "direction_support_level": dsupport,
        })

    # For a missing-node hypothesis, lower observed support means a more
    # plausible place to break the observed adjacency.  Direction level is
    # ordered 0 absent < 1 conflict < 2 supports current direction.
    def dominates_gap(a, b):
        keys = ("bootstrap_frequency", "residual_score", "direction_support_level")
        return all(a[k] <= b[k] for k in keys) and any(a[k] < b[k] for k in keys)

    frontier = [
        r for r in rows
        if not any(dominates_gap(q, r) for q in rows if q is not r)
    ]

    min_boot = min(r["bootstrap_frequency"] for r in rows)
    min_resid = min(r["residual_score"] for r in rows)
    min_dir = min(r["direction_support_level"] for r in rows)

    for r in rows:
        r["is_weakest_bootstrap"] = r["bootstrap_frequency"] == min_boot
        r["is_weakest_residual"] = r["residual_score"] == min_resid
        r["has_min_direction_support"] = r["direction_support_level"] == min_dir

    total_boot = sum(r["bootstrap_frequency"] for r in rows)
    total_resid = sum(r["residual_score"] for r in rows)
    for r in rows:
        r["remaining_observed_bootstrap_sum_if_gap_here"] = total_boot - r["bootstrap_frequency"]
        r["remaining_observed_residual_sum_if_gap_here"] = total_resid - r["residual_score"]

    result = {
        "status": "Q20_LATENT_GAP_LOCALIZATION",
        "missing_singulion": "S7_109|110",
        "candidate_order": CANDIDATE,
        "interfaces": rows,
        "gap_weakness_pareto_frontier": frontier,
        "interpretation": {
            "bootstrap_weakest_interface": next(r["between"] for r in rows if r["is_weakest_bootstrap"]),
            "residual_weakest_interface": next(r["between"] for r in rows if r["is_weakest_residual"]),
            "interfaces_without_stable_pairwise_arrow": [r["between"] for r in rows if r["direction_support_level"] == 0],
        },
        "guardrails": [
            "No content is imputed for 109|110.",
            "A weak observed edge can reflect topic/style change rather than a missing bifolium.",
            "Gap localization is conditional on the current principal Q20 order.",
            "Bootstrap frequency, residual score and boundary direction are not combined into an arbitrary weighted scalar.",
            "The inferred gap remains a hypothesis until corroborated by physical/codicological evidence.",
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
