#!/usr/bin/env python3
"""Exhaustive open-path benchmark for surviving Q20 singulions.

Purpose
-------
Rank all 6! = 720 orders of the six surviving Quire 20 bifolios using
order-independent text representations. This script is deliberately modest:
it reconstructs *adjacency topology*, not reading direction or semantics.

Input
-----
ZL3b/IVTFF corpus text (the frozen corpus used in this project works).

Example
-------
python order_q20_openpath.py ../../data/voynich_eva.txt --json q20_order.json

No Q20 Layfield-Davis order is hard-coded until it is verified from the
primary article. The current physical nesting order is included only as a
benchmark.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

SHEETS: Mapping[str, Tuple[int, int]] = {
    "S1_103|116": (103, 116),
    "S2_104|115": (104, 115),
    "S3_105|114": (105, 114),
    "S4_106|113": (106, 113),
    "S5_107|112": (107, 112),
    "S6_108|111": (108, 111),
}
CURRENT = tuple(SHEETS.keys())
LANG_BLOCK_S = {"S1_103|116", "S5_107|112", "S6_108|111"}
LANG_BLOCK_T = set(SHEETS) - LANG_BLOCK_S

PAGE_HEADER = re.compile(r"^<f(\d+)([rv])>\s")
LOCUS = re.compile(r"^<f(\d+)([rv])\.[^>]+>\s+(.*)$")
COMMENT_INLINE = re.compile(r"<!.*?>")
BRACKET_ALT = re.compile(r"\[([^:\]]+):[^\]]+\]")
BRACE = re.compile(r"\{[^}]*\}")
NON_EVA = re.compile(r"[^a-zA-Z?.'\-]+")


def clean_text(s: str) -> str:
    s = COMMENT_INLINE.sub(" ", s)
    s = BRACKET_ALT.sub(r"\1", s)
    s = BRACE.sub(" ", s)
    s = s.replace("<$>", " ").replace("<%>", " ").replace("<->", " ")
    s = NON_EVA.sub(" ", s)
    return " ".join(s.lower().split())


def load_pages(path: Path) -> Dict[int, str]:
    pages: Dict[int, List[str]] = defaultdict(list)
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LOCUS.match(raw)
        if not m:
            continue
        folio = int(m.group(1))
        if 103 <= folio <= 116 and folio not in (109, 110):
            txt = clean_text(m.group(3))
            if txt:
                pages[folio].append(txt)
    missing = sorted({103,104,105,106,107,108,111,112,113,114,115,116} - set(pages))
    if missing:
        raise ValueError(f"Missing Q20 folios in corpus: {missing}")
    return {k: " ".join(v) for k, v in pages.items()}


def sheet_texts(pages: Mapping[int, str]) -> Dict[str, str]:
    return {name: pages[a] + " " + pages[b] for name, (a, b) in SHEETS.items()}


def token_features(text: str) -> Counter:
    toks = [t for t in text.split() if t and "?" not in t]
    return Counter(toks)


def char_ngram_features(text: str, nmin: int = 3, nmax: int = 5) -> Counter:
    compact = "_".join(t for t in text.split() if t and "?" not in t)
    c = Counter()
    for n in range(nmin, nmax + 1):
        c.update(compact[i:i+n] for i in range(max(0, len(compact)-n+1)))
    return c


def tfidf(counters: Mapping[str, Counter]) -> Dict[str, Dict[str, float]]:
    names = list(counters)
    n_docs = len(names)
    df = Counter()
    for c in counters.values():
        df.update(c.keys())
    out: Dict[str, Dict[str, float]] = {}
    for name, c in counters.items():
        total = sum(c.values()) or 1
        v: Dict[str, float] = {}
        for term, count in c.items():
            tf = count / total
            idf = math.log((1 + n_docs) / (1 + df[term])) + 1.0
            v[term] = tf * idf
        out[name] = v
    return out


def cosine(a: Mapping[str, float], b: Mapping[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    dot = sum(x * b.get(k, 0.0) for k, x in a.items())
    na = math.sqrt(sum(x*x for x in a.values()))
    nb = math.sqrt(sum(x*x for x in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def sim_matrix(vectors: Mapping[str, Mapping[str, float]]) -> Dict[Tuple[str, str], float]:
    names = list(vectors)
    m: Dict[Tuple[str, str], float] = {}
    for a in names:
        for b in names:
            m[(a,b)] = 1.0 if a == b else cosine(vectors[a], vectors[b])
    return m


def zscore_edge_matrices(*matrices: Mapping[Tuple[str,str], float]) -> Dict[Tuple[str,str], float]:
    keys = list(matrices[0].keys())
    offdiag = [k for k in keys if k[0] != k[1]]
    normed = []
    for m in matrices:
        vals = [m[k] for k in offdiag]
        mu = sum(vals) / len(vals)
        sd = math.sqrt(sum((x-mu)**2 for x in vals) / len(vals)) or 1.0
        normed.append({k: (m[k]-mu)/sd for k in keys})
    return {k: sum(mm[k] for mm in normed)/len(normed) for k in keys}


def path_score(order: Sequence[str], sim: Mapping[Tuple[str,str], float]) -> float:
    return sum(sim[(a,b)] for a,b in zip(order, order[1:]))


def canonical(order: Sequence[str]) -> Tuple[str,...]:
    t = tuple(order)
    r = tuple(reversed(t))
    return min(t, r)


def block_transitions(order: Sequence[str]) -> int:
    labels = ["S" if x in LANG_BLOCK_S else "T" for x in order]
    return sum(a != b for a,b in zip(labels, labels[1:]))


def adjacency_set(order: Sequence[str]) -> set:
    return {frozenset((a,b)) for a,b in zip(order, order[1:])}


def rank_all(sim: Mapping[Tuple[str,str], float]):
    scored = []
    seen = set()
    for p in itertools.permutations(SHEETS.keys()):
        c = canonical(p)
        if c in seen:
            continue
        seen.add(c)  # reverse-equivalent: 360 unique undirected paths
        scored.append((path_score(c, sim), c, block_transitions(c)))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", type=Path)
    ap.add_argument("--json", type=Path, default=None)
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--near-opt-frac", type=float, default=0.01,
                    help="retain paths within this fraction of max-min score range from best")
    args = ap.parse_args()

    pages = load_pages(args.corpus)
    sheets = sheet_texts(pages)

    tok = tfidf({k: token_features(v) for k,v in sheets.items()})
    chr_ = tfidf({k: char_ngram_features(v) for k,v in sheets.items()})
    sm_tok = sim_matrix(tok)
    sm_chr = sim_matrix(chr_)
    sm = zscore_edge_matrices(sm_tok, sm_chr)

    ranked = rank_all(sm)
    best = ranked[0][0]
    worst = ranked[-1][0]
    span = best - worst or 1.0
    current_c = canonical(CURRENT)
    current_rank = next(i+1 for i,(_,p,_) in enumerate(ranked) if p == current_c)
    current_score = next(s for s,p,_ in ranked if p == current_c)

    threshold = best - args.near_opt_frac * span
    near = [(s,p,t) for s,p,t in ranked if s >= threshold]
    edge_counts = Counter()
    for _,p,_ in near:
        edge_counts.update(adjacency_set(p))

    result = {
        "status": "TOPOLOGY_ONLY_DIRECTION_UNIDENTIFIED",
        "n_paths_raw": math.factorial(len(SHEETS)),
        "n_paths_reverse_collapsed": len(ranked),
        "current": {
            "order": list(CURRENT),
            "score": current_score,
            "rank_of_reverse_collapsed": current_rank,
            "percentile_higher_is_better": 1.0 - (current_rank - 1) / max(1, len(ranked)-1),
            "block_transitions": block_transitions(CURRENT),
        },
        "best": {
            "order": list(ranked[0][1]),
            "reverse_equivalent": list(reversed(ranked[0][1])),
            "score": ranked[0][0],
            "block_transitions": ranked[0][2],
        },
        "top": [
            {"rank": i+1, "score": s, "order": list(p), "block_transitions": t}
            for i,(s,p,t) in enumerate(ranked[:args.top])
        ],
        "near_optimal": {
            "criterion_fraction_of_score_range": args.near_opt_frac,
            "n": len(near),
            "edge_consensus": [
                {
                    "edge": sorted(tuple(e)),
                    "count": n,
                    "fraction": n / len(near),
                }
                for e,n in edge_counts.most_common()
            ],
        },
        "notes": [
            "Scores combine z-normalized token TF-IDF and EVA character 3-5 gram cosine adjacency.",
            "Reverse paths are collapsed because these scores are symmetric and cannot identify direction.",
            "The missing 109|110 bifolio is not imputed.",
            "No Layfield-Davis Q20 sequence is hard-coded until primary-source verification.",
            "A best path that merely minimizes S/T block transitions is a confound candidate, not a discovery.",
        ],
    }

    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
