#!/usr/bin/env python3
"""Apply the frozen Currier/hand confound control to all regular complete quires.

This generalizes the Quire F control without retuning anything.  For each of
A,C,D,E,F,G, each transcription (ZL3b and Takahashi IT2a), and each frozen
boundary window (25,50,100,200,whole page), enumerate the same 24 possible
outer->inner nestings of the four known physical bifolia and rank the *current*
nesting under three matrices:

  raw                 frozen boundary-continuity score;
  currier_residual    raw score minus ordered source/target Currier-L class mean;
  hand_currier_residual
                      raw score minus ordered exact (Davis-H,Currier-L)
                      source/target class mean.

Metadata are taken only from frozen ZL headers and reused as nuisance labels for
IT2a.  Physical nesting labels never enter residualization.  This is a confound
control, not a decipherment or a proof of historical order.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import median

import order_quire_c_nesting as base
import order_regular_quires_nesting_scan as scan

IT2A_SHA256 = base.IT2A_SHA256
WINDOWS = base.WINDOWS
QUIRES = scan.QUIRES


def parse_metadata(raw: str):
    meta = {}
    for line in raw.splitlines():
        m = re.match(r"^<([^>.,]+)>\s*<!", line)
        if not m:
            continue
        meta[m.group(1)] = dict(re.findall(r"\$([A-Z])=([^\s>]+)", line))
    return meta


def folio_sig(meta, n, key):
    vals = []
    for side in ("r", "v"):
        v = meta.get(f"f{n}{side}", {}).get(key)
        if v is not None:
            vals.append(v)
    return tuple(sorted(set(vals)))


def signatures(meta, folios):
    return {n: (folio_sig(meta, n, "H"), folio_sig(meta, n, "L")) for n in folios}


def residualize(matrix, key_fn):
    groups = defaultdict(list)
    for pair, value in matrix.items():
        groups[key_fn(pair)].append((pair, value))
    out = {}
    group_summary = {}
    for key, rows in groups.items():
        mu = sum(v for _, v in rows) / len(rows)
        group_summary[repr(key)] = {"mean": mu, "n_edges": len(rows)}
        for pair, value in rows:
            out[pair] = value - mu
    return out, group_summary


def enumerate_nestings(pair_labels, matrix):
    rows = []
    for nesting in itertools.permutations(pair_labels):
        leaves = scan.leaf_sequence(nesting)
        score = sum(matrix[(a, b)] for a, b in zip(leaves, leaves[1:]))
        rows.append((score, nesting, leaves))
    rows.sort(key=lambda x: (-x[0], x[1]))
    return rows


def rank_current(pair_labels, matrix):
    rows = enumerate_nestings(pair_labels, matrix)
    idx = next(i for i, (_, p, _) in enumerate(rows) if p == pair_labels)
    cur = rows[idx]
    best = rows[0]
    return {
        "current_rank": idx + 1,
        "current_score": cur[0],
        "current_exact_p_ge": (idx + 1) / 24.0,
        "best_nesting_outer_to_inner": list(best[1]),
        "best_leaf_reading_order": best[2],
        "best_score": best[0],
        "current_is_best": idx == 0,
    }


def analyse_quire(pages, pairs, sigs):
    folios = sorted({x for p in pairs for x in p})
    pair_labels = tuple(scan.label(p) for p in pairs)
    by_window = []
    for w in WINDOWS:
        raw = scan.directed_transition_matrix(pages, folios, w)
        currier, currier_groups = residualize(
            raw, lambda p: (sigs[p[0]][1], sigs[p[1]][1])
        )
        exact, exact_groups = residualize(
            raw, lambda p: (sigs[p[0]], sigs[p[1]])
        )
        by_window.append({
            "boundary_tokens": "whole_page" if w == 0 else w,
            "raw": rank_current(pair_labels, raw),
            "currier_residual": rank_current(pair_labels, currier),
            "hand_currier_residual": rank_current(pair_labels, exact),
            "n_currier_transition_classes": len(currier_groups),
            "n_hand_currier_transition_classes": len(exact_groups),
        })

    summary = {}
    for control in ("raw", "currier_residual", "hand_currier_residual"):
        ranks = [row[control]["current_rank"] for row in by_window]
        bests = [row[control]["best_nesting_outer_to_inner"] for row in by_window]
        summary[control] = {
            "current_ranks": ranks,
            "current_median_rank": median(ranks),
            "current_top1_windows": sum(r == 1 for r in ranks),
            "current_top3_windows": sum(r <= 3 for r in ranks),
            "current_worst_rank": max(ranks),
            "best_nestings_by_window": bests,
        }
    return {"by_window": by_window, "summary": summary}


def classify(raw_med, cur_med, exact_med, exact_top3, exact_worst):
    """Descriptive status only; not a statistical decision rule."""
    if exact_med <= 3 and exact_top3 >= 3:
        return "CURRENT_ORDER_COMPATIBLE_AFTER_METADATA_CONTROL"
    if raw_med >= 12 and exact_med <= 8:
        return "RAW_ANOMALY_MATERIALLY_COLLAPSES_AFTER_METADATA_CONTROL"
    if raw_med >= 12 and exact_med >= 12 and exact_worst >= 18:
        return "ANOMALY_SURVIVES_METADATA_CONTROL_REVIEW_REQUIRED"
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
    meta = parse_metadata(zlraw)

    results = {}
    global_ranks = {k: [] for k in ("raw", "currier_residual", "hand_currier_residual")}
    for qname, pairs in QUIRES.items():
        folios = sorted({x for p in pairs for x in p})
        sigs = signatures(meta, folios)
        zl = analyse_quire(zlpages, pairs, sigs)
        it = analyse_quire(itpages, pairs, sigs)
        cross = {}
        for control in ("raw", "currier_residual", "hand_currier_residual"):
            ranks = zl["summary"][control]["current_ranks"] + it["summary"][control]["current_ranks"]
            global_ranks[control].extend(ranks)
            cross[control] = {
                "current_ranks_across_10_tests": ranks,
                "median_rank": median(ranks),
                "top1_tests": sum(r == 1 for r in ranks),
                "top3_tests": sum(r <= 3 for r in ranks),
                "worst_rank": max(ranks),
            }
        status = classify(
            cross["raw"]["median_rank"],
            cross["currier_residual"]["median_rank"],
            cross["hand_currier_residual"]["median_rank"],
            cross["hand_currier_residual"]["top3_tests"],
            cross["hand_currier_residual"]["worst_rank"],
        )
        results[qname] = {
            "known_physical_bifolia": [scan.label(p) for p in pairs],
            "folio_metadata_signatures": {
                str(n): {"H": list(sigs[n][0]), "L": list(sigs[n][1])} for n in folios
            },
            "ZL3b": zl,
            "IT2a": it,
            "cross_transcription": cross,
            "descriptive_status": status,
        }

    global_summary = {}
    for control, ranks in global_ranks.items():
        global_summary[control] = {
            "n_correlated_tests": len(ranks),
            "median_current_rank_out_of_24": median(ranks),
            "top1_tests": sum(r == 1 for r in ranks),
            "top3_tests": sum(r <= 3 for r in ranks),
            "worst_rank": max(ranks),
        }

    result = {
        "status": "REGULAR_QUIRE_NESTING_METADATA_CONTROL_NOT_DECIPHERMENT",
        "method_frozen_from": "Quire F Currier/hand confound control, itself using the frozen Quire C boundary model",
        "controls": ["raw", "ordered Currier-L transition-class centering", "ordered exact Davis-H plus Currier-L transition-class centering"],
        "quires": results,
        "global_summary": global_summary,
        "parser_audit": {"ZL3b": zlaudit, "IT2a": itaudit},
        "guardrails": [
            "Descriptive status labels are summaries, not preregistered hypothesis tests.",
            "The scoring model, windows and metadata residualization are fixed before this all-quire run.",
            "Exact H/L centering may remove genuine historical sequence signal if that signal is correlated with scribe/language changes.",
            "Physical nesting labels are used only to identify the current candidate rank, never in residualization.",
            "The 10 tests per quire are strongly correlated and must not be counted as independent evidence.",
            "IT2a and ZL3b are independent transcriptions of the same manuscript, not independent manuscripts.",
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
