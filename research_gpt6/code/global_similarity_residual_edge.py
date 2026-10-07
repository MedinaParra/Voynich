#!/usr/bin/env python3
"""Residual local-edge specificity after removing global page similarity.

Protocol: research_gpt6/37_global_similarity_residual_protocol.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median

import order_quire_c_nesting as base
import order_regular_quires_nesting_scan as scan
import order_regular_quires_metadata_control as meta_ctl
import order_quire_b_partial_nesting as qb
import reading_interface_specificity as iface

IT2A_SHA256 = base.IT2A_SHA256
LOCAL_WINDOWS = (25, 50, 100, 200)
MODES = iface.MODES

DEFINITIONS = [
    ("A_f1-f8", scan.QUIRES["A_f1-f8"], False),
    ("B_f9-f16_partial", qb.PAIRS, True),
    ("C_f17-f24", scan.QUIRES["C_f17-f24"], False),
    ("D_f25-f32", scan.QUIRES["D_f25-f32"], False),
    ("E_f33-f40", scan.QUIRES["E_f33-f40"], False),
    ("F_f41-f48", scan.QUIRES["F_f41-f48"], False),
    ("G_f49-f56", scan.QUIRES["G_f49-f56"], False),
]


def orthogonalize(local, global_score):
    keys = sorted(local)
    xs = [global_score[k] for k in keys]
    ys = [local[k] for k in keys]
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    beta = 0.0 if vx == 0 else cov / vx
    alpha = my - beta * mx
    residual = {k: local[k] - (alpha + beta * global_score[k]) for k in keys}
    corr = 0.0 if vx == 0 or vy == 0 else cov / math.sqrt(vx * vy)
    return residual, {
        "alpha": alpha,
        "beta": beta,
        "pearson_local_global": corr,
        "var_global_sum_sq": vx,
        "var_local_sum_sq": vy,
        "n_directed_pairs": len(keys),
    }


def rank_matrix(pairs, matrix, partial):
    if partial:
        rows = qb.enumerate_partial_nestings(qb.CURRENT, matrix)
        idx = next(i for i, (_, p, _) in enumerate(rows) if p == qb.CURRENT)
        return idx + 1
    labels = tuple(scan.label(p) for p in pairs)
    rows = scan.enumerate_nestings(labels, matrix)
    idx = next(i for i, (_, p, _) in enumerate(rows) if p == labels)
    return idx + 1


def analyse_one(pages, pairs, sigs, partial):
    folios = sorted({x for p in pairs for x in p})
    global_score = iface.interface_matrix(pages, folios, 0, "tail", "head")
    modes = {}
    for mode, (source_edge, target_edge) in MODES.items():
        rows = []
        for w in LOCAL_WINDOWS:
            local = iface.interface_matrix(pages, folios, w, source_edge, target_edge)
            residual, audit = orthogonalize(local, global_score)
            exact, exact_groups = meta_ctl.residualize(
                residual, lambda p: (sigs[p[0]], sigs[p[1]])
            )
            rows.append({
                "boundary_tokens": w,
                "global_residual_rank": rank_matrix(pairs, residual, partial),
                "global_plus_exact_metadata_rank": rank_matrix(pairs, exact, partial),
                "regression": audit,
                "n_hand_currier_transition_classes": len(exact_groups),
            })
        modes[mode] = rows
    return modes


def normalized_median(ranks, n_candidates):
    return median([(r - 1) / (n_candidates - 1) for r in ranks])


def sign_test_one_sided(xs, ys):
    wins = sum(x < y for x, y in zip(xs, ys))
    losses = sum(x > y for x, y in zip(xs, ys))
    ties = len(xs) - wins - losses
    n = wins + losses
    if n == 0:
        return {"wins": wins, "losses": losses, "ties": ties, "n_non_tie": 0, "p_one_sided": 1.0}
    p = sum(math.comb(n, k) for k in range(wins, n + 1)) / (2 ** n)
    return {"wins": wins, "losses": losses, "ties": ties, "n_non_tie": n, "p_one_sided": p}


def evaluate(per_quire, key):
    summaries = {}
    for mode in MODES:
        vals = [per_quire[q][key][mode] for q, _, _ in DEFINITIONS]
        summaries[mode] = {"quire_medians": vals, "global_median": median(vals)}
    th = summaries["TH"]["quire_medians"]
    wrong_modes = ("HH", "TT", "HT")
    best_wrong = [min(summaries[m]["quire_medians"][i] for m in wrong_modes) for i in range(len(th))]
    wins = sum(x < y for x, y in zip(th, best_wrong))
    global_condition = all(summaries["TH"]["global_median"] < summaries[m]["global_median"] for m in wrong_modes)
    if wins >= 6 and global_condition:
        status = "PASS_LOCAL_EDGE_SPECIFIC_EXPLORATORY"
    elif wins <= 3:
        status = "FAIL_LOCAL_EDGE_SPECIFIC"
    else:
        status = "INCONCLUSIVE"
    signs = {m: sign_test_one_sided(th, summaries[m]["quire_medians"]) for m in wrong_modes}
    signs["best_wrong"] = sign_test_one_sided(th, best_wrong)
    return {
        "status": status,
        "mode_summary": summaries,
        "best_wrong_quire_medians": best_wrong,
        "TH_wins_vs_best_wrong": wins,
        "global_condition_TH_better_than_each_wrong": global_condition,
        "sign_tests_secondary": signs,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zl", type=Path, required=True)
    ap.add_argument("--it", type=Path, required=True)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    zlraw = args.zl.read_text(encoding="utf-8", errors="replace")
    itbytes = args.it.read_bytes()
    itsha = hashlib.sha256(itbytes).hexdigest()
    if itsha != IT2A_SHA256:
        raise SystemExit(f"IT2a SHA256 mismatch: {itsha}")
    itraw = itbytes.decode("utf-8", errors="replace")

    zlpages, zlaudit = base.parse_pages(zlraw)
    itpages, itaudit = base.parse_pages(itraw)
    metadata = meta_ctl.parse_metadata(zlraw)

    per_quire = {}
    details = {}
    for qname, pairs, partial in DEFINITIONS:
        folios = sorted({x for p in pairs for x in p})
        sigs = meta_ctl.signatures(metadata, folios)
        required = [f"f{n}{s}" for n in folios for s in ("r", "v")]
        mz = [x for x in required if not zlpages.get(x)]
        mi = [x for x in required if not itpages.get(x)]
        if mz or mi:
            raise SystemExit(f"{qname}: missing pages ZL={mz} IT2a={mi}")

        z = analyse_one(zlpages, pairs, sigs, partial)
        t = analyse_one(itpages, pairs, sigs, partial)
        n_candidates = 6 if partial else 24
        q_primary = {}
        q_secondary = {}
        for mode in MODES:
            primary_ranks = [r["global_residual_rank"] for r in z[mode]] + [r["global_residual_rank"] for r in t[mode]]
            secondary_ranks = [r["global_plus_exact_metadata_rank"] for r in z[mode]] + [r["global_plus_exact_metadata_rank"] for r in t[mode]]
            q_primary[mode] = normalized_median(primary_ranks, n_candidates)
            q_secondary[mode] = normalized_median(secondary_ranks, n_candidates)
        per_quire[qname] = {
            "global_residual": q_primary,
            "global_plus_exact_metadata": q_secondary,
        }
        details[qname] = {
            "candidate_count": n_candidates,
            "ZL3b": z,
            "IT2a": t,
            "folio_metadata_signatures": {
                str(n): {"H": list(sigs[n][0]), "L": list(sigs[n][1])} for n in folios
            },
        }

    primary = evaluate(per_quire, "global_residual")
    secondary = evaluate(per_quire, "global_plus_exact_metadata")

    result = {
        "status": primary["status"],
        "protocol": "research_gpt6/37_global_similarity_residual_protocol.md",
        "local_windows": list(LOCAL_WINDOWS),
        "whole_page_excluded_from_local_test": True,
        "primary_global_similarity_residual": primary,
        "secondary_global_plus_exact_metadata": secondary,
        "quire_order": [q for q, _, _ in DEFINITIONS],
        "per_quire_normalized_medians": per_quire,
        "details": details,
        "parser_audit": {"ZL3b": zlaudit, "IT2a": itaudit},
        "guardrails": [
            "Protocol and decision thresholds were frozen before execution.",
            "Global nuisance similarity uses full verso(source) versus full recto(target) over all directed folio pairs and never uses the correct candidate order during fitting.",
            "The full-page predictor contains local edges, making this a conservative residualization that may remove some genuine local signal.",
            "Whole-page is excluded from the local endpoint because local and nuisance scores coincide there.",
            "The eight ranks per quire are correlated and summarized by one median.",
            "Q13 and Q20 remain excluded because they motivated nonstandard-order hypotheses.",
            "A primary FAIL closes the current edge-specific ordering interpretation for this program unless independent evidence motivates a new metric.",
            "No semantic, language, translation or decipherment claim is tested."
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
