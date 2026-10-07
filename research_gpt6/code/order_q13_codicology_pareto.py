#!/usr/bin/env python3
"""Q13 Pareto test under the soft codicological hypothesis that f76r begins the section.

The independent descriptive evidence at voynich.nu notes that f76r, especially
its ornate initial, may have been the first page of the biological section.
If a singulion is read internally as 76r,76v,83r,83v, this suggests 76|83 as
a possible first singulion.

This script does NOT assert that hypothesis as fact. It asks how expensive it is
for the frozen textual model to satisfy it. Among the 4! = 24 directed orders
starting with 76|83, it keeps the Pareto frontier across:
  1) sum of Q13 bootstrap edge-selection frequencies;
  2) full-corpus frozen combined TF-IDF / EVA char-ngram path score;
  3) stable directional-boundary precedence constraints.
No scalar weights are fitted.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import order_q13_openpath as q13
import order_q20_openpath as feat

FIRST = "Q13_76|83"
NODES = list(q13.SHEETS.keys())

# Only Q13 arrows whose sign survived all 4/8/12/16/24-line windows.
ARROWS = [
    ("Q13_75|84", "Q13_76|83"),
    ("Q13_76|83", "Q13_78|81"),
    ("Q13_78|81", "Q13_79|80"),
]


def edge(a, b):
    return tuple(sorted((a, b)))


def load_boot(path: Path):
    d = json.loads(path.read_text(encoding="utf-8"))
    return {
        tuple(r["edge"]): float(r["frequency"])
        for r in d["q13"]["edge_selection_frequency"]
    }


def full_combined(corpus: Path):
    pages = q13.load_pages(corpus)
    sheets = q13.sheet_texts(pages)
    tok_vec = feat.tfidf({k: feat.token_features(v) for k, v in sheets.items()})
    chr_vec = feat.tfidf({k: feat.char_ngram_features(v) for k, v in sheets.items()})
    return q13.combine(q13.cosine_matrix(tok_vec), q13.cosine_matrix(chr_vec))


def sim_get(sim, a, b):
    return sim.get((a, b), sim.get((b, a)))


def metrics(order, boot, sim):
    adj = [edge(a, b) for a, b in zip(order, order[1:])]
    pos = {x: i for i, x in enumerate(order)}
    sat = sum(pos[a] < pos[b] for a, b in ARROWS)
    return {
        "bootstrap_edge_sum": sum(boot.get(e, 0.0) for e in adj),
        "bootstrap_edge_mean": sum(boot.get(e, 0.0) for e in adj) / len(adj),
        "combined_text_score": sum(sim_get(sim, a, b) for a, b in zip(order, order[1:])),
        "direction_constraints_satisfied": sat,
        "direction_constraints_total": len(ARROWS),
        "edges": [list(e) for e in adj],
    }


def dominates(a, b):
    keys = (
        "bootstrap_edge_sum",
        "combined_text_score",
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
    ap.add_argument("corpus", type=Path)
    ap.add_argument("bootstrap", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    boot = load_boot(args.bootstrap)
    sim = full_combined(args.corpus)

    all_rows = [
        {"order": list(p), "metrics": metrics(p, boot, sim)}
        for p in itertools.permutations(NODES)
    ]
    rank_maps = {
        k: rank_all(all_rows, k)
        for k in ("bootstrap_edge_sum", "combined_text_score", "direction_constraints_satisfied")
    }
    for r in all_rows:
        t = tuple(r["order"])
        r["global_ranks_out_of_120"] = {k: m[t] for k, m in rank_maps.items()}

    remaining = [x for x in NODES if x != FIRST]
    constrained = []
    for tail in itertools.permutations(remaining):
        order = (FIRST, *tail)
        constrained.append({"order": list(order), "metrics": metrics(order, boot, sim)})

    frontier = [
        r for r in constrained
        if not any(dominates(q["metrics"], r["metrics"]) for q in constrained if q is not r)
    ]
    frontier.sort(
        key=lambda r: (
            -r["metrics"]["direction_constraints_satisfied"],
            -r["metrics"]["bootstrap_edge_sum"],
            -r["metrics"]["combined_text_score"],
            r["order"],
        )
    )
    for r in frontier:
        t = tuple(r["order"])
        r["global_ranks_out_of_120"] = {k: m[t] for k, m in rank_maps.items()}

    refs = {
        "layfield_davis": list(q13.LAYFIELD_DAVIS),
        "independent_zl3b": list(q13.REPORTED_HELD_KARP),
    }
    ref_metrics = {
        name: {
            "order": order,
            "starts_with_76_83": order[0] == FIRST,
            "metrics": metrics(order, boot, sim),
            "global_ranks_out_of_120": {
                k: rank_maps[k][tuple(order)] for k in rank_maps
            },
        }
        for name, order in refs.items()
    }

    top_by = {}
    for key in ("bootstrap_edge_sum", "combined_text_score", "direction_constraints_satisfied"):
        top_by[key] = [
            {"rank": i + 1, **r}
            for i, r in enumerate(
                sorted(constrained, key=lambda x: (-x["metrics"][key], x["order"]))[:10]
            )
        ]

    result = {
        "status": "Q13_SOFT_FIRST_PAGE_PARETO",
        "working_hypothesis": {
            "first_singulion": FIRST,
            "motivation": "f76r has an ornate initial and has been independently described as a possible first page of the biological section",
            "n_conditioned_orders": len(constrained),
        },
        "stable_direction_precedence_constraints": [list(x) for x in ARROWS],
        "pareto_frontier": frontier,
        "reference_sequences_unconstrained": ref_metrics,
        "top10_conditioned_by_each_criterion": top_by,
        "guardrails": [
            "The f76r-first observation is a soft codicological clue, not established provenance.",
            "Conditioning 76|83 to be first assumes internal singulion reading begins 76r,76v,83r,83v.",
            "No weights combine criteria; Pareto dominance only.",
            "The first stable boundary arrow 75|84->76|83 conflicts structurally with forcing 76|83 first; that disagreement is intentionally retained.",
            "Bootstrap edge frequencies are stability diagnostics, not historical probabilities.",
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
