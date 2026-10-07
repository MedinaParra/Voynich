#!/usr/bin/env python3
"""Enumerate Q20 orders under independent codicological endpoint hypotheses.

No fitted scalar objective is used. We condition on two explicit, externally
motivated *working* endpoint hypotheses:
  - 105|114 first (f105r has section-opening visual features)
  - 103|116 last  (f116 has closing/final-page features)

Among the remaining 4! = 24 orders, report three separate criteria:
  1. sum of Q20 dialect-residual bootstrap edge frequencies;
  2. sum of full-corpus dialect-residual pair scores;
  3. number of stable boundary-direction precedence constraints satisfied.

The Pareto frontier is returned. Endpoint assumptions are not promoted to
facts; a second unconstrained audit reports where Pareto candidates rank among
all 720 directed orders.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

FIRST = "S3_105|114"
LAST = "S1_103|116"
NODES = [
    "S1_103|116", "S2_104|115", "S3_105|114",
    "S4_106|113", "S5_107|112", "S6_108|111",
]

# Stable-sign arrows from the preregistered 4/8/12/16/24-line sweep.
# These are precedence diagnostics, not hard transitions.
ARROWS = [
    ("S6_108|111", "S1_103|116"),
    ("S3_105|114", "S5_107|112"),
    ("S4_106|113", "S5_107|112"),
    ("S4_106|113", "S6_108|111"),
    ("S4_106|113", "S2_104|115"),
    ("S2_104|115", "S1_103|116"),
]


def edge(a, b):
    return tuple(sorted((a, b)))


def load_boot(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    return {
        tuple(r["edge"]): float(r["frequency"])
        for r in d["q20_dialect_residual"]["edge_selection_frequency"]
    }


def load_residual(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for r in d["pairwise_combined_sorted_by_residual"]:
        out[edge(*r["edge"])] = float(r["residual"])
    return out


def metrics(order, boot, resid):
    adj = [edge(a, b) for a, b in zip(order, order[1:])]
    pos = {x: i for i, x in enumerate(order)}
    sat = sum(pos[a] < pos[b] for a, b in ARROWS)
    # Bootstrap JSON only lists edges selected at least once. An omitted edge
    # therefore has observed selection frequency exactly 0 in those replicates.
    boot_vals = [boot.get(e, 0.0) for e in adj]
    return {
        "bootstrap_edge_sum": sum(boot_vals),
        "bootstrap_edge_mean": sum(boot_vals) / len(adj),
        "residual_edge_sum": sum(resid[e] for e in adj),
        "direction_constraints_satisfied": sat,
        "direction_constraints_total": len(ARROWS),
        "edges": [list(e) for e in adj],
    }


def dominates(a, b):
    keys = (
        "bootstrap_edge_sum",
        "residual_edge_sum",
        "direction_constraints_satisfied",
    )
    return all(a[k] >= b[k] for k in keys) and any(a[k] > b[k] for k in keys)


def rank_all(rows, key):
    vals = sorted(
        ((r["metrics"][key], tuple(r["order"])) for r in rows),
        key=lambda x: (-x[0], x[1]),
    )
    return {order: i + 1 for i, (_, order) in enumerate(vals)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bootstrap", type=Path)
    ap.add_argument("controls", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    boot = load_boot(args.bootstrap)
    resid = load_residual(args.controls)

    all_rows = []
    for p in itertools.permutations(NODES):
        all_rows.append({"order": list(p), "metrics": metrics(p, boot, resid)})
    rb = rank_all(all_rows, "bootstrap_edge_sum")
    rr = rank_all(all_rows, "residual_edge_sum")
    rd = rank_all(all_rows, "direction_constraints_satisfied")
    for r in all_rows:
        t = tuple(r["order"])
        r["global_ranks_out_of_720"] = {
            "bootstrap_edge_sum": rb[t],
            "residual_edge_sum": rr[t],
            "direction_constraints_satisfied": rd[t],
        }

    middle = [x for x in NODES if x not in (FIRST, LAST)]
    constrained = []
    for p in itertools.permutations(middle):
        order = (FIRST, *p, LAST)
        constrained.append({"order": list(order), "metrics": metrics(order, boot, resid)})

    frontier = []
    for r in constrained:
        if not any(
            dominates(q["metrics"], r["metrics"])
            for q in constrained if q is not r
        ):
            frontier.append(r)
    frontier.sort(
        key=lambda r: (
            -r["metrics"]["direction_constraints_satisfied"],
            -r["metrics"]["bootstrap_edge_sum"],
            -r["metrics"]["residual_edge_sum"],
            r["order"],
        )
    )
    for r in frontier:
        t = tuple(r["order"])
        r["global_ranks_out_of_720"] = {
            "bootstrap_edge_sum": rb[t],
            "residual_edge_sum": rr[t],
            "direction_constraints_satisfied": rd[t],
        }

    constrained_sorted = {}
    for key in (
        "bootstrap_edge_sum",
        "residual_edge_sum",
        "direction_constraints_satisfied",
    ):
        constrained_sorted[key] = [
            {"rank": i + 1, **r}
            for i, r in enumerate(
                sorted(
                    constrained,
                    key=lambda x: (-x["metrics"][key], x["order"]),
                )
            )
        ][:10]

    result = {
        "status": "Q20_CODICOLOGY_CONSTRAINED_PARETO",
        "endpoint_working_hypotheses": {
            "first": FIRST,
            "last": LAST,
            "n_orders": len(constrained),
        },
        "stable_direction_precedence_constraints": [list(x) for x in ARROWS],
        "pareto_frontier": frontier,
        "top10_by_each_criterion": constrained_sorted,
        "reference_text_candidate": [
            "S3_105|114", "S5_107|112", "S4_106|113",
            "S2_104|115", "S6_108|111", "S1_103|116",
        ],
        "guardrails": [
            "f105r-as-start and f116v-as-end are codicological working hypotheses, not established facts.",
            "No weights combine the three criteria; only Pareto dominance is used.",
            "Direction arrows are pairwise textual boundary preferences, not guaranteed narrative transitions.",
            "The missing 109|110 singulion is absent and can change the solution when modelled.",
            "Bootstrap edge frequencies are stability diagnostics, not posterior historical probabilities.",
            "Bootstrap edges absent from the stored frequency table are assigned observed frequency 0.0.",
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
