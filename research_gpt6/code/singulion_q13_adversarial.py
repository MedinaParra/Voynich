#!/usr/bin/env python3
"""Adversarial robustness audit for the preregistered Q13 singulion test.

This does not change the preregistered primary decision. It reports exact ranks
for all metrics under the 5! fixed-orientation null, then broadens the null to
5! * 2^5 = 3840 sequences by allowing each bifolium's two leaves to exchange
order. This is a sensitivity test, not a claim about codicological orientation.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import singulion_q13_order as base

ALL_METRICS = (
    "tfidf_cosine_all",
    "char3_cosine_all",
    "token_jaccard_all",
    "char_js_similarity_all",
    "edge_tfidf_cosine_all",
)
BOUNDARY_METRICS = (
    "tfidf_cosine_boundary",
    "char3_cosine_boundary",
    "token_jaccard_boundary",
    "char_js_similarity_boundary",
    "edge_tfidf_cosine_boundary",
)


def swapped_sequence(order, mask):
    seq = []
    labels = []
    for i, (a, b) in enumerate(order):
        flip = bool((mask >> i) & 1)
        x, y = (b, a) if flip else (a, b)
        seq.extend((f"f{x}r", f"f{x}v", f"f{y}r", f"f{y}v"))
        labels.append(f"{x}|{y}")
    return seq, labels


def summarize(value, vals):
    r = base.rank_info(value, vals, True)
    return {
        "observed": value,
        "null_min": min(vals),
        "null_mean": base.mean(vals),
        "null_max": max(vals),
        **r,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    data = a.corpus.read_bytes()
    blob = base.git_blob_sha1(data)
    if blob != base.SOURCE_BLOB:
        raise SystemExit(f"Corpus blob mismatch: {blob}")
    pages, meta, audit = base.parse_pages(data.decode("utf-8"))
    ids = base.q13_page_ids()
    missing = [p for p in ids if not pages.get(p)]
    if missing:
        raise SystemExit(f"Missing/empty Q13 pages: {missing}")
    idf, tf, cg = base.page_vectors(pages, ids)

    proposed_seq = base.singulion_sequence(base.LAYFIELD_DAVIS)
    proposed = base.full_scores(proposed_seq, pages, idf, tf, cg, True)
    current = base.full_scores(base.current_sequence(), pages, idf, tf, cg, False)

    fixed = []
    for perm in itertools.permutations(base.BIFOLIA):
        s = base.full_scores(base.singulion_sequence(perm), pages, idf, tf, cg, True)
        fixed.append(s)

    expanded = []
    best_primary = None
    for perm in itertools.permutations(base.BIFOLIA):
        for mask in range(1 << len(base.BIFOLIA)):
            seq, labels = swapped_sequence(perm, mask)
            s = base.full_scores(seq, pages, idf, tf, cg, True)
            expanded.append(s)
            candidate = (s[base.PRIMARY], labels, mask, s)
            if best_primary is None or candidate[0] > best_primary[0]:
                best_primary = candidate

    fixed_ranks = {
        m: summarize(proposed[m], [x[m] for x in fixed])
        for m in ALL_METRICS + BOUNDARY_METRICS
    }
    expanded_ranks = {
        m: summarize(proposed[m], [x[m] for x in expanded])
        for m in ALL_METRICS + BOUNDARY_METRICS
    }

    beats_current = {
        m: {
            "current": current[m],
            "proposed": proposed[m],
            "delta": proposed[m] - current[m],
            "fraction_fixed_null_beating_current": sum(x[m] > current[m] for x in fixed) / len(fixed),
        }
        for m in ALL_METRICS
    }

    # Consensus across metrics: count in how many all-page metrics the proposed
    # sequence reaches at least the 95th percentile of the exact fixed null.
    robust_metric_hits = sum(fixed_ranks[m]["percentile"] > 95.0 for m in ALL_METRICS)
    boundary_hits = sum(fixed_ranks[m]["percentile"] > 95.0 for m in BOUNDARY_METRICS)

    result = {
        "classification": "Q13_SINGULION_ADVERSARIAL_ROBUSTNESS_NOT_DECIPHERMENT",
        "status": "ROBUST_SIGNAL" if robust_metric_hits >= 3 else "NO_ROBUST_ORDER_SIGNAL",
        "source_blob": blob,
        "layfield_davis_order": [f"{a}|{b}" for a,b in base.LAYFIELD_DAVIS],
        "fixed_null_size": len(fixed),
        "expanded_leaf_swap_null_size": len(expanded),
        "all_page_metric_exact_ranks_fixed_null": {m: fixed_ranks[m] for m in ALL_METRICS},
        "boundary_metric_exact_ranks_fixed_null": {m: fixed_ranks[m] for m in BOUNDARY_METRICS},
        "all_page_metric_exact_ranks_expanded_null": {m: expanded_ranks[m] for m in ALL_METRICS},
        "boundary_metric_exact_ranks_expanded_null": {m: expanded_ranks[m] for m in BOUNDARY_METRICS},
        "comparison_to_current_binding": beats_current,
        "metrics_above_95pct_fixed_null": robust_metric_hits,
        "boundary_metrics_above_95pct_fixed_null": boundary_hits,
        "best_expanded_primary": {
            "score": best_primary[0],
            "order": best_primary[1],
            "leaf_swap_mask": best_primary[2],
            "scores": best_primary[3],
        },
        "interpretation_guardrail": "Expanded leaf-swap null is adversarial sensitivity only; it does not assert that all 3840 sequences are codicologically feasible.",
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
