#!/usr/bin/env python3
"""Adversarial control for specificity of the physical reading interface.

Protocol: research_gpt6/35_reading_interface_specificity_protocol.md
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

IT2A_SHA256 = base.IT2A_SHA256
WINDOWS = base.WINDOWS
MODES = {
    "TH": ("tail", "head"),
    "HH": ("head", "head"),
    "TT": ("tail", "tail"),
    "HT": ("head", "tail"),
}
COMPLETE = scan.QUIRES
B_NAME = "B_f9-f16_partial"
B_PAIRS = qb.PAIRS


def interface_matrix(pages, folios, window, source_edge, target_edge):
    src = {f: base.window_tokens(pages[f"f{f}v"], source_edge, window) for f in folios}
    dst = {f: base.window_tokens(pages[f"f{f}r"], target_edge, window) for f in folios}
    tok_docs = {f"S{f}": base.token_counter(src[f]) for f in folios}
    tok_docs.update({f"D{f}": base.token_counter(dst[f]) for f in folios})
    chr_docs = {f"S{f}": base.char_counter(src[f]) for f in folios}
    chr_docs.update({f"D{f}": base.char_counter(dst[f]) for f in folios})
    tok_vec = base.tfidf(tok_docs)
    chr_vec = base.tfidf(chr_docs)
    comps = {"token_tfidf": {}, "char35_tfidf": {}, "token_jaccard": {}}
    for a in folios:
        for b in folios:
            if a == b:
                continue
            p = (a, b)
            comps["token_tfidf"][p] = base.cosine(tok_vec[f"S{a}"], tok_vec[f"D{b}"])
            comps["char35_tfidf"][p] = base.cosine(chr_vec[f"S{a}"], chr_vec[f"D{b}"])
            comps["token_jaccard"][p] = base.jaccard(src[a], dst[b])
    z = {k: base.znorm(v) for k, v in comps.items()}
    return {p: sum(z[k][p] for k in z) / len(z) for p in z["token_tfidf"]}


def rank_complete(pairs, matrix):
    labels = tuple(scan.label(p) for p in pairs)
    rows = scan.enumerate_nestings(labels, matrix)
    idx = next(i for i, (_, p, _) in enumerate(rows) if p == labels)
    return idx + 1


def rank_partial(matrix):
    rows = qb.enumerate_partial_nestings(qb.CURRENT, matrix)
    idx = next(i for i, (_, p, _) in enumerate(rows) if p == qb.CURRENT)
    return idx + 1


def analyse_quire(pages, pairs, sigs, partial=False):
    folios = sorted({x for p in pairs for x in p})
    n_candidates = 6 if partial else 24
    out = {}
    for mode, (source_edge, target_edge) in MODES.items():
        raw_ranks = []
        exact_ranks = []
        for w in WINDOWS:
            raw = interface_matrix(pages, folios, w, source_edge, target_edge)
            exact, _ = meta_ctl.residualize(raw, lambda p: (sigs[p[0]], sigs[p[1]]))
            if partial:
                raw_ranks.append(rank_partial(raw))
                exact_ranks.append(rank_partial(exact))
            else:
                raw_ranks.append(rank_complete(pairs, raw))
                exact_ranks.append(rank_complete(pairs, exact))
        out[mode] = {"raw_ranks": raw_ranks, "exact_metadata_ranks": exact_ranks}
    return n_candidates, out


def normalized_median(zl_ranks, it_ranks, n_candidates):
    vals = [(r - 1) / (n_candidates - 1) for r in zl_ranks + it_ranks]
    return median(vals)


def sign_test_one_sided(xs, ys):
    wins = sum(x < y for x, y in zip(xs, ys))
    losses = sum(x > y for x, y in zip(xs, ys))
    ties = len(xs) - wins - losses
    n = wins + losses
    if n == 0:
        return {"wins": wins, "losses": losses, "ties": ties, "n_non_tie": 0, "p_one_sided": 1.0}
    p = sum(math.comb(n, k) for k in range(wins, n + 1)) / (2 ** n)
    return {"wins": wins, "losses": losses, "ties": ties, "n_non_tie": n, "p_one_sided": p}


def evaluate_control(per_quire, control_key):
    summaries = {}
    for mode in MODES:
        vals = [per_quire[q][control_key][mode] for q in per_quire]
        summaries[mode] = {"quire_medians": vals, "global_median": median(vals)}

    th = summaries["TH"]["quire_medians"]
    best_wrong = [
        min(summaries["HH"]["quire_medians"][i], summaries["TT"]["quire_medians"][i], summaries["HT"]["quire_medians"][i])
        for i in range(len(th))
    ]
    wins_best_wrong = sum(x < y for x, y in zip(th, best_wrong))
    global_condition = all(summaries["TH"]["global_median"] < summaries[m]["global_median"] for m in ("HH", "TT", "HT"))
    if wins_best_wrong >= 6 and global_condition:
        status = "PASS_EDGE_SPECIFIC_EXPLORATORY"
    elif wins_best_wrong <= 3:
        status = "FAIL_EDGE_SPECIFIC"
    else:
        status = "INCONCLUSIVE"

    signs = {m: sign_test_one_sided(th, summaries[m]["quire_medians"]) for m in ("HH", "TT", "HT")}
    signs["best_wrong"] = sign_test_one_sided(th, best_wrong)
    return {
        "status": status,
        "mode_summary": summaries,
        "best_wrong_quire_medians": best_wrong,
        "TH_wins_vs_best_wrong": wins_best_wrong,
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

    definitions = list(COMPLETE.items()) + [(B_NAME, B_PAIRS)]
    per_quire = {}
    details = {}
    for qname, pairs in definitions:
        partial = qname == B_NAME
        folios = sorted({x for p in pairs for x in p})
        sigs = meta_ctl.signatures(metadata, folios)
        required = [f"f{n}{s}" for n in folios for s in ("r", "v")]
        mz = [x for x in required if not zlpages.get(x)]
        mi = [x for x in required if not itpages.get(x)]
        if mz or mi:
            raise SystemExit(f"{qname}: missing pages ZL={mz} IT2a={mi}")
        nz, z = analyse_quire(zlpages, pairs, sigs, partial=partial)
        ni, t = analyse_quire(itpages, pairs, sigs, partial=partial)
        if nz != ni:
            raise RuntimeError("candidate count mismatch")

        q_primary = {}
        q_exact = {}
        q_detail = {"candidate_count": nz, "ZL3b": z, "IT2a": t}
        for mode in MODES:
            q_primary[mode] = normalized_median(z[mode]["raw_ranks"], t[mode]["raw_ranks"], nz)
            q_exact[mode] = normalized_median(z[mode]["exact_metadata_ranks"], t[mode]["exact_metadata_ranks"], nz)
        per_quire[qname] = {"raw": q_primary, "exact_metadata": q_exact}
        details[qname] = q_detail

    primary = evaluate_control(per_quire, "raw")
    secondary = evaluate_control(per_quire, "exact_metadata")

    result = {
        "status": primary["status"],
        "protocol": "research_gpt6/35_reading_interface_specificity_protocol.md",
        "primary": primary,
        "secondary_exact_metadata": secondary,
        "quire_order": list(per_quire.keys()),
        "per_quire_normalized_medians": per_quire,
        "details": details,
        "parser_audit": {"ZL3b": zlaudit, "IT2a": itaudit},
        "guardrails": [
            "This is a post-result adversarial control preregistered before wrong-interface execution.",
            "TH is the only physically motivated reading interface; HH, TT and HT are negative controls.",
            "The ten transcription-window ranks within a quire are correlated and are summarized by one median.",
            "Q13 and Q20 are excluded because they motivated nonstandard-order hypotheses.",
            "Whole-page windows are intentionally retained from the frozen model and are non-specific to head/tail orientation.",
            "ZL3b and IT2a are independent transcriptions of the same manuscript, not independent manuscripts.",
            "No semantic, language, translation or decipherment claim is tested here."
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
