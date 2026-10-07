#!/usr/bin/env python3
"""Preregistered partial-nesting test for Voynich Quire B.

Protocol: research_gpt6/33_quire_b_partial_nesting_protocol.md

The surviving physical bifolia are 9|16, 10|15, 11|14.  The expected central
bifolium 12|13 is absent, so candidate nestings are scored only on observed
adjacencies that do not cross the missing-center gap.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from statistics import median

import order_quire_c_nesting as base
import order_regular_quires_nesting_scan as scan
import order_regular_quires_metadata_control as meta_ctl

IT2A_SHA256 = base.IT2A_SHA256
WINDOWS = base.WINDOWS
PAIRS = ((9, 16), (10, 15), (11, 14))
CURRENT = tuple(scan.label(p) for p in PAIRS)


def observed_transitions(nesting_labels):
    """Four true observed adjacencies, excluding the missing-center interface."""
    pairs = [scan.parse_label(x) for x in nesting_labels]
    (a1, b1), (a2, b2), (a3, b3) = pairs
    return [(a1, a2), (a2, a3), (b3, b2), (b2, b1)]


def enumerate_partial_nestings(pair_labels, matrix):
    rows = []
    for nesting in itertools.permutations(pair_labels):
        edges = observed_transitions(nesting)
        score = sum(matrix[e] for e in edges)
        rows.append((score, nesting, edges))
    rows.sort(key=lambda x: (-x[0], x[1]))
    return rows


def rank_current(pair_labels, matrix):
    rows = enumerate_partial_nestings(pair_labels, matrix)
    idx = next(i for i, (_, p, _) in enumerate(rows) if p == pair_labels)
    cur = rows[idx]
    best = rows[0]
    second = rows[1]
    return {
        "current_rank": idx + 1,
        "current_score": cur[0],
        "current_exact_uniform_rank_p": (idx + 1) / 6.0,
        "current_observed_transitions": [f"{a}->{b}" for a, b in cur[2]],
        "best_nesting_outer_to_inner": list(best[1]),
        "best_observed_transitions": [f"{a}->{b}" for a, b in best[2]],
        "best_score": best[0],
        "second_score": second[0],
        "best_margin_over_second": best[0] - second[0],
        "current_is_best": idx == 0,
    }


def analyse_one(pages, sigs):
    folios = sorted({x for p in PAIRS for x in p})
    by_window = []
    for w in WINDOWS:
        raw = scan.directed_transition_matrix(pages, folios, w)
        currier, currier_groups = meta_ctl.residualize(
            raw, lambda p: (sigs[p[0]][1], sigs[p[1]][1])
        )
        exact, exact_groups = meta_ctl.residualize(
            raw, lambda p: (sigs[p[0]], sigs[p[1]])
        )
        by_window.append({
            "boundary_tokens": "whole_page" if w == 0 else w,
            "raw": rank_current(CURRENT, raw),
            "currier_residual": rank_current(CURRENT, currier),
            "hand_currier_residual": rank_current(CURRENT, exact),
            "n_currier_transition_classes": len(currier_groups),
            "n_hand_currier_transition_classes": len(exact_groups),
        })

    summary = {}
    for control in ("raw", "currier_residual", "hand_currier_residual"):
        ranks = [row[control]["current_rank"] for row in by_window]
        summary[control] = {
            "current_ranks": ranks,
            "median_rank": median(ranks),
            "top1_windows": sum(r == 1 for r in ranks),
            "top2_windows": sum(r <= 2 for r in ranks),
            "worst_rank": max(ranks),
        }
    return {"by_window": by_window, "summary": summary}


def classify(zl, it):
    z = zl["summary"]["hand_currier_residual"]
    t = it["summary"]["hand_currier_residual"]
    pass_ok = (
        z["median_rank"] <= 2
        and t["median_rank"] <= 2
        and z["top1_windows"] >= 3
        and t["top1_windows"] >= 3
        and z["worst_rank"] <= 4
        and t["worst_rank"] <= 4
    )
    if pass_ok:
        return "PASS_PREDICTIVE_EXPLORATORY"
    fail = (
        z["median_rank"] >= 4
        or t["median_rank"] >= 4
        or (z["top1_windows"] + t["top1_windows"] == 0)
    )
    if fail:
        return "FAIL_PREDICTIVE"
    return "INCONCLUSIVE"


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
    folios = sorted({x for p in PAIRS for x in p})
    sigs = meta_ctl.signatures(metadata, folios)

    required = [f"f{n}{s}" for n in folios for s in ("r", "v")]
    missing_zl = [x for x in required if not zlpages.get(x)]
    missing_it = [x for x in required if not itpages.get(x)]
    if missing_zl or missing_it:
        raise SystemExit(f"missing pages ZL={missing_zl} IT2a={missing_it}")

    zl = analyse_one(zlpages, sigs)
    it = analyse_one(itpages, sigs)
    decision = classify(zl, it)

    result = {
        "status": decision,
        "protocol": "research_gpt6/33_quire_b_partial_nesting_protocol.md",
        "target": "relative outer-to-inner order of surviving Quire B bifolia",
        "known_surviving_bifolia_current_order": list(CURRENT),
        "missing_central_bifolium": "12|13",
        "candidate_orders": 6,
        "scored_edges_per_candidate": 4,
        "excluded_gap_edge_rule": "never score a3v->b3r because missing 12|13 intervenes",
        "primary_control": "hand_currier_residual",
        "ZL3b": zl,
        "IT2a": it,
        "folio_metadata_signatures": {
            str(n): {"H": list(sigs[n][0]), "L": list(sigs[n][1])} for n in folios
        },
        "parser_audit": {"ZL3b": zlaudit, "IT2a": itaudit},
        "guardrails": [
            "Decision thresholds were frozen before this script was executed.",
            "Quire B was previously used in a physical-pairing experiment, but not in the A/C/D/E/F/G nesting-order scans.",
            "Only four observed adjacencies are scored; the missing-center interface is never imputed.",
            "Five windows are correlated and are not independent p-values.",
            "With six possible orders, rank 1 has exact uniform rank probability 1/6; PASS is operational predictive consistency, not alpha-0.05 significance.",
            "ZL3b and IT2a are independent transcriptions of the same manuscript, not independent manuscripts.",
            "No semantic, linguistic, translation, or decipherment claim follows from this test."
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
