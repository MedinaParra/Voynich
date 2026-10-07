#!/usr/bin/env python3
"""Exhaustive open-path benchmark for Quire 13 singulions.

Tests all 5! = 120 orders (60 after reverse collapse) using the same frozen
ZL3b corpus and feature families used for Q20. The published Layfield-Davis
sequence and the previously reported independent Held-Karp sequence are
benchmarks only; neither is used to fit the representation.

Similarity is symmetric, so this script identifies topology/adjacency but not
direction. A path and its reverse are therefore treated as equivalent.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import order_q20_openpath as feat

SHEETS = {
    "Q13_75|84": (75,84),
    "Q13_76|83": (76,83),
    "Q13_77|82": (77,82),
    "Q13_78|81": (78,81),
    "Q13_79|80": (79,80),
}

CURRENT = tuple(SHEETS.keys())
LAYFIELD_DAVIS = (
    "Q13_77|82",
    "Q13_78|81",
    "Q13_75|84",
    "Q13_76|83",
    "Q13_79|80",
)
REPORTED_HELD_KARP = (
    "Q13_79|80",
    "Q13_78|81",
    "Q13_75|84",
    "Q13_76|83",
    "Q13_77|82",
)

LOCUS = re.compile(r"^<f(\d+)([rv])\.[^>]+>\s+(.*)$")


def load_pages(path: Path):
    pages = defaultdict(list)
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LOCUS.match(raw)
        if not m:
            continue
        f = int(m.group(1))
        if 75 <= f <= 84:
            txt = feat.clean_text(m.group(3))
            if txt:
                pages[f].append(txt)
    missing = sorted(set(range(75,85)) - set(pages))
    if missing:
        raise ValueError(f"Missing Q13 folios in corpus: {missing}")
    return {k:" ".join(v) for k,v in pages.items()}


def sheet_texts(pages):
    return {name: pages[a] + " " + pages[b] for name,(a,b) in SHEETS.items()}


def cosine_matrix(vectors):
    return feat.sim_matrix(vectors)


def combine(tok, char):
    return feat.zscore_edge_matrices(tok,char)


def canonical(order):
    t=tuple(order); r=tuple(reversed(t)); return min(t,r)


def edges(order):
    return {frozenset((a,b)) for a,b in zip(order,order[1:])}


def score(order, sim):
    return sum(sim[(a,b)] for a,b in zip(order,order[1:]))


def rank_all(sim):
    rows=[]; seen=set()
    for p in itertools.permutations(SHEETS):
        c=canonical(p)
        if c in seen: continue
        seen.add(c)
        rows.append((score(c,sim),c))
    rows.sort(key=lambda x:(-x[0],x[1]))
    return rows


def benchmark(order, ranked):
    c=canonical(order)
    for i,(s,p) in enumerate(ranked,1):
        if p==c:
            return {
                "order": list(order),
                "reverse_equivalent": list(reversed(order)),
                "score": s,
                "rank": i,
                "percentile_higher_is_better": 1-(i-1)/max(1,len(ranked)-1),
            }
    raise AssertionError(order)


def summarize(sim, near_frac=0.01):
    ranked=rank_all(sim)
    best,worst=ranked[0][0],ranked[-1][0]
    span=best-worst or 1
    threshold=best-near_frac*span
    near=[x for x in ranked if x[0]>=threshold]
    counts=Counter()
    for _,p in near: counts.update(edges(p))
    return {
        "n_paths_raw": math.factorial(len(SHEETS)),
        "n_paths_reverse_collapsed": len(ranked),
        "best": benchmark(ranked[0][1], ranked),
        "current": benchmark(CURRENT, ranked),
        "layfield_davis": benchmark(LAYFIELD_DAVIS, ranked),
        "reported_held_karp": benchmark(REPORTED_HELD_KARP, ranked),
        "near_optimal_n": len(near),
        "near_edge_consensus": [
            {"edge": sorted(tuple(e)), "count":n, "fraction":n/len(near)}
            for e,n in counts.most_common()
        ],
        "top10": [
            {"rank":i+1,"score":s,"order":list(p),"reverse":list(reversed(p))}
            for i,(s,p) in enumerate(ranked[:10])
        ],
    }, ranked


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus",type=Path)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    pages=load_pages(args.corpus)
    sheets=sheet_texts(pages)
    tok_vec=feat.tfidf({k:feat.token_features(v) for k,v in sheets.items()})
    chr_vec=feat.tfidf({k:feat.char_ngram_features(v) for k,v in sheets.items()})
    sm_tok=cosine_matrix(tok_vec)
    sm_chr=cosine_matrix(chr_vec)
    sm_comb=combine(sm_tok,sm_chr)

    combined,_=summarize(sm_comb)
    token,_=summarize(sm_tok)
    char,_=summarize(sm_chr)

    # Robust edge votes across the best path of the three representations.
    votes=Counter()
    for summary in (combined,token,char):
        votes.update(edges(summary["best"]["order"]))

    result={
        "status":"Q13_TOPOLOGY_DIRECTION_UNIDENTIFIED",
        "combined":combined,
        "token_only":token,
        "char_ngram_only":char,
        "best_path_edge_votes_across_3_representations":[
            {"edge":sorted(tuple(e)),"votes_out_of_3":n}
            for e,n in votes.most_common()
        ],
        "predeclared_core_edges":[
            ["Q13_78|81","Q13_75|84"],
            ["Q13_75|84","Q13_76|83"],
        ],
        "notes":[
            "Layfield-Davis and reported Held-Karp orders are evaluated, not fitted.",
            "Reverse paths are equivalent because all adjacency scores are symmetric.",
            "A robust local core is stronger evidence than a unique total order when endpoints vary.",
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json: args.json.write_text(text+"\n",encoding="utf-8")

if __name__=="__main__": main()
