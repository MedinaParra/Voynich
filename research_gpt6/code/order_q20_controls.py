#!/usr/bin/env python3
"""Controls for Q20 ordering: remove the known S/T dialect-block effect.

This script imports the frozen Q20 representation from order_q20_openpath.py,
then asks which adjacencies remain after subtracting the average similarity
expected purely from edge class (S-S, T-T, S-T). It also compares token-only,
character-ngram-only and combined rankings and enumerates each 3-bifolio
language block independently.

The output is topology-only: all similarity matrices are symmetric, therefore
path direction remains unidentified.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import order_q20_openpath as base


def edge_class(a: str, b: str) -> str:
    aa = "S" if a in base.LANG_BLOCK_S else "T"
    bb = "S" if b in base.LANG_BLOCK_S else "T"
    return "SS" if aa == bb == "S" else "TT" if aa == bb == "T" else "ST"


def class_means(sim):
    vals = defaultdict(list)
    names = list(base.SHEETS)
    for i, a in enumerate(names):
        for b in names[i+1:]:
            vals[edge_class(a,b)].append(sim[(a,b)])
    return {k: sum(v)/len(v) for k,v in vals.items()}


def residualize(sim):
    means = class_means(sim)
    out = {}
    for (a,b), value in sim.items():
        if a == b:
            out[(a,b)] = 0.0
        else:
            out[(a,b)] = value - means[edge_class(a,b)]
    return out, means


def rank_summary(sim, near_frac=0.01):
    ranked = base.rank_all(sim)
    best, worst = ranked[0][0], ranked[-1][0]
    span = best - worst or 1.0
    current_c = base.canonical(base.CURRENT)
    cr = next(i+1 for i,(_,p,_) in enumerate(ranked) if p == current_c)
    cs = next(s for s,p,_ in ranked if p == current_c)
    threshold = best - near_frac * span
    near = [(s,p,t) for s,p,t in ranked if s >= threshold]
    ec = Counter()
    for _,p,_ in near:
        ec.update(base.adjacency_set(p))
    return {
        "n_reverse_collapsed": len(ranked),
        "current_rank": cr,
        "current_score": cs,
        "current_percentile": 1.0 - (cr-1)/max(1,len(ranked)-1),
        "best_score": best,
        "best_order": list(ranked[0][1]),
        "best_reverse": list(reversed(ranked[0][1])),
        "best_block_transitions": ranked[0][2],
        "near_n": len(near),
        "near_edge_consensus": [
            {"edge": sorted(tuple(e)), "count": n, "fraction": n/len(near)}
            for e,n in ec.most_common()
        ],
        "top10": [
            {"rank": i+1, "score": s, "order": list(p), "block_transitions": t}
            for i,(s,p,t) in enumerate(ranked[:10])
        ],
    }, ranked


def conditioned_current_rank(ranked):
    target_t = base.block_transitions(base.CURRENT)
    subset = [(s,p,t) for s,p,t in ranked if t == target_t]
    current_c = base.canonical(base.CURRENT)
    rank = next(i+1 for i,(_,p,_) in enumerate(subset) if p == current_c)
    return {
        "block_transitions": target_t,
        "n_paths": len(subset),
        "rank": rank,
        "percentile": 1.0 - (rank-1)/max(1,len(subset)-1),
    }


def independent_block(block, sim):
    names = sorted(block)
    paths = []
    seen = set()
    for p in itertools.permutations(names):
        c = base.canonical(p)
        if c in seen:
            continue
        seen.add(c)
        paths.append((base.path_score(c, sim), c))
    paths.sort(key=lambda x:(-x[0], x[1]))
    # for a 3-node path the middle node is the one connected to both others
    return [
        {"rank": i+1, "score": s, "order": list(p), "middle": p[1]}
        for i,(s,p) in enumerate(paths)
    ]


def pair_table(raw, residual):
    rows = []
    names = list(base.SHEETS)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            rows.append({
                "edge": [a,b],
                "class": edge_class(a,b),
                "raw": raw[(a,b)],
                "residual": residual[(a,b)],
            })
    return sorted(rows, key=lambda r:(-r["residual"], -r["raw"], r["edge"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    pages = base.load_pages(args.corpus)
    sheets = base.sheet_texts(pages)

    tok = base.tfidf({k: base.token_features(v) for k,v in sheets.items()})
    chr_ = base.tfidf({k: base.char_ngram_features(v) for k,v in sheets.items()})
    sm_tok = base.sim_matrix(tok)
    sm_chr = base.sim_matrix(chr_)
    sm_comb = base.zscore_edge_matrices(sm_tok, sm_chr)

    sm_resid, means = residualize(sm_comb)
    tok_resid, tok_means = residualize(sm_tok)
    chr_resid, chr_means = residualize(sm_chr)

    raw_summary, raw_ranked = rank_summary(sm_comb)
    resid_summary, resid_ranked = rank_summary(sm_resid)
    tok_summary, _ = rank_summary(tok_resid)
    chr_summary, _ = rank_summary(chr_resid)

    # Edges present in the single best path for each representation.
    best_sets = {}
    for label, summary in [
        ("combined_residual", resid_summary),
        ("token_residual", tok_summary),
        ("char_residual", chr_summary),
    ]:
        best_sets[label] = [sorted(tuple(e)) for e in base.adjacency_set(summary["best_order"])]

    edge_votes = Counter()
    for edges in best_sets.values():
        edge_votes.update(tuple(e) for e in edges)

    result = {
        "status": "DIALECT_CONTROLLED_TOPOLOGY_DIRECTION_UNIDENTIFIED",
        "dialect_edge_class_means_combined": means,
        "dialect_edge_class_means_token": tok_means,
        "dialect_edge_class_means_char": chr_means,
        "raw_combined": raw_summary,
        "raw_current_conditioned_on_same_number_of_ST_transitions": conditioned_current_rank(raw_ranked),
        "residual_combined": resid_summary,
        "residual_current_conditioned_on_same_number_of_ST_transitions": conditioned_current_rank(resid_ranked),
        "residual_token_only": tok_summary,
        "residual_char_ngram_only": chr_summary,
        "independent_S_block_residual": independent_block(base.LANG_BLOCK_S, sm_resid),
        "independent_T_block_residual": independent_block(base.LANG_BLOCK_T, sm_resid),
        "pairwise_combined_sorted_by_residual": pair_table(sm_comb, sm_resid),
        "best_path_edge_votes_across_residual_representations": [
            {"edge": list(e), "votes_out_of_3": n}
            for e,n in edge_votes.most_common()
        ],
        "notes": [
            "Residual score subtracts the mean similarity for SS, TT or ST edges; this directly removes the gross known Q20 language-block advantage.",
            "This is a confound control, not a proof of historical adjacency.",
            "Direction is unidentifiable because cosine similarities are symmetric.",
            "The missing 109|110 singulion remains latent and is not imputed.",
        ],
    }

    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
