#!/usr/bin/env python3
"""Independent Q20 directional-boundary audit using Glen Claston's v101 file.

This script intentionally tests only the five surviving Q20 singulions whose
start and end boundaries are present symmetrically in GC2a:
  S2=104|115, S3=105|114, S4=106|113, S5=107|112, S6=108|111.

For singulion a|b, the assumed internal reading orientation is a-r,a-v,b-r,b-v;
therefore its external boundary is tail(b-v) -> head(next a-r).

Unlike the EVA-oriented scripts, v101 words and glyphs are parsed natively:
period/comma/vertical bar are boundary separators, @nnn; is one glyph unit,
and all other v101 symbols are preserved.

The experiment reports directed pair margins for four previously proposed Q20
precedence arrows, sensitivity across 2..8 boundary lines, full 5! path ranks,
and a token+glyph ablation because exact edge-token matching is sparse in v101.
It does not decipher Voynichese and does not equate pairwise precedence with
immediate adjacency.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

NODES = {
    "S2_104|115": (104, 115),
    "S3_105|114": (105, 114),
    "S4_106|113": (106, 113),
    "S5_107|112": (107, 112),
    "S6_108|111": (108, 111),
}
ARROWS = [
    ("S3_105|114", "S5_107|112"),
    ("S4_106|113", "S5_107|112"),
    ("S4_106|113", "S6_108|111"),
    ("S4_106|113", "S2_104|115"),
]
CANDIDATE = (
    "S3_105|114", "S4_106|113", "S5_107|112",
    "S2_104|115", "S6_108|111",
)
LOCUS = re.compile(r"^<f(\d+)([rv])\.\d+,[^>]+>\s+(.*)$")
ATCODE = re.compile(r"@\d+;")

def load_pages(path: Path):
    pages = defaultdict(list)
    wanted = {x for pair in NODES.values() for x in pair}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LOCUS.match(raw)
        if not m:
            continue
        f, side, text = int(m.group(1)), m.group(2), m.group(3)
        if f not in wanted:
            continue
        text = text.replace("<%>", "").replace("<$>", "").replace("<->", "|")
        text = re.sub(r"<[^>]*>", "", text)
        pages[(f, side)].append(text.strip())
    missing = []
    for a, b in NODES.values():
        for key in ((a, "r"), (b, "v")):
            if not pages.get(key):
                missing.append(f"f{key[0]}{key[1]}")
    if missing:
        raise RuntimeError(f"Missing required GC boundaries: {missing}")
    return pages

def words(line: str):
    line = line.replace(r"\.", "§DOT§").replace(r"\,", "§COMMA§")
    return [x for x in re.split(r"[.,|]+", line) if x]

def glyph_units(word: str):
    out = []
    i = 0
    while i < len(word):
        if word.startswith("§DOT§", i):
            out.append("<DOT>"); i += 5; continue
        if word.startswith("§COMMA§", i):
            out.append("<COMMA>"); i += 7; continue
        if word[i] == "@":
            m = ATCODE.match(word, i)
            if m:
                out.append(m.group(0)); i = m.end(); continue
        out.append(word[i]); i += 1
    return out

def token_counter(lines):
    return Counter(w for ln in lines for w in words(ln))

def glyph_ngram_counter(lines):
    seq = []
    for ln in lines:
        for w in words(ln):
            seq.extend(glyph_units(w)); seq.append("<WB>")
    if seq and seq[-1] == "<WB>":
        seq.pop()
    c = Counter()
    for n in (3, 4, 5):
        for i in range(len(seq) - n + 1):
            c[tuple(seq[i:i+n])] += 1
    return c

def first_counter(lines):
    c = Counter()
    for ln in lines:
        ws = words(ln)
        if ws: c[ws[0]] += 1
    return c

def last_counter(lines):
    c = Counter()
    for ln in lines:
        ws = words(ln)
        if ws: c[ws[-1]] += 1
    return c

def tfidf(counters):
    names = list(counters)
    df = Counter()
    for c in counters.values():
        df.update(c.keys())
    n = len(names)
    idf = {k: math.log((1+n)/(1+d)) + 1.0 for k, d in df.items()}
    out = {}
    for name, c in counters.items():
        total = sum(c.values()) or 1
        out[name] = {k: (v/total)*idf[k] for k, v in c.items()}
    return out

def cosine(a, b):
    if len(a) > len(b):
        a, b = b, a
    dot = sum(v*b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v*v for v in a.values()))
    nb = math.sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na and nb else 0.0

def zscore(d):
    vals = list(d.values())
    mu = sum(vals)/len(vals)
    sd = math.sqrt(sum((x-mu)**2 for x in vals)/len(vals)) or 1.0
    return {k: (v-mu)/sd for k, v in d.items()}

def score_window(pages, k):
    token_docs, glyph_docs, edge_docs = {}, {}, {}
    for node, (a, b) in NODES.items():
        head = pages[(a, "r")][:k]
        tail = pages[(b, "v")][-k:]
        token_docs["H"+node] = token_counter(head)
        token_docs["T"+node] = token_counter(tail)
        glyph_docs["H"+node] = glyph_ngram_counter(head)
        glyph_docs["T"+node] = glyph_ngram_counter(tail)
        edge_docs["H"+node] = first_counter(head)
        edge_docs["T"+node] = last_counter(tail)
    tv, gv, ev = tfidf(token_docs), tfidf(glyph_docs), tfidf(edge_docs)
    comps = {"token": {}, "glyph": {}, "edge_token": {}}
    for a in NODES:
        for b in NODES:
            if a == b: continue
            comps["token"][(a,b)] = cosine(tv["T"+a], tv["H"+b])
            comps["glyph"][(a,b)] = cosine(gv["T"+a], gv["H"+b])
            comps["edge_token"][(a,b)] = cosine(ev["T"+a], ev["H"+b])
    z = {name: zscore(d) for name, d in comps.items()}
    combined = {pair: sum(z[name][pair] for name in z)/len(z) for pair in z["token"]}
    token_glyph = {pair: (z["token"][pair] + z["glyph"][pair])/2 for pair in z["token"]}
    return z, combined, token_glyph

def rank_path(score, path):
    rows = []
    for p in itertools.permutations(NODES):
        s = sum(score[(a,b)] for a,b in zip(p,p[1:]))
        rows.append((s,p))
    rows.sort(key=lambda x: (-x[0], x[1]))
    rank = next(i+1 for i,(_,p) in enumerate(rows) if p == tuple(path))
    rev = tuple(reversed(path))
    rev_rank = next(i+1 for i,(_,p) in enumerate(rows) if p == rev)
    return rank, rev_rank, rows[0]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gc", type=Path)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()
    pages = load_pages(args.gc)
    windows = {}
    arrow_summary = {f"{a}->{b}": [] for a,b in ARROWS}
    for k in range(2, 9):
        z, combined, token_glyph = score_window(pages, k)
        full_rank, full_rev, full_best = rank_path(combined, CANDIDATE)
        tg_rank, tg_rev, tg_best = rank_path(token_glyph, CANDIDATE)
        windows[str(k)] = {
            "candidate_full_rank_out_of_120": full_rank,
            "candidate_full_reverse_rank_out_of_120": full_rev,
            "candidate_token_glyph_rank_out_of_120": tg_rank,
            "candidate_token_glyph_reverse_rank_out_of_120": tg_rev,
            "best_full_path": list(full_best[1]),
            "best_token_glyph_path": list(tg_best[1]),
        }
        for a,b in ARROWS:
            rec = {"window_lines": k}
            for name in z:
                rec[f"{name}_margin"] = z[name][(a,b)] - z[name][(b,a)]
            rec["combined_margin"] = combined[(a,b)] - combined[(b,a)]
            rec["token_glyph_margin"] = token_glyph[(a,b)] - token_glyph[(b,a)]
            arrow_summary[f"{a}->{b}"].append(rec)
    summary = {}
    for key, rows in arrow_summary.items():
        pfull = sum(r["combined_margin"] > 0 for r in rows)
        ptg = sum(r["token_glyph_margin"] > 0 for r in rows)
        summary[key] = {
            "windows": rows,
            "positive_combined_windows": pfull,
            "positive_token_glyph_windows": ptg,
            "robust_positive_all_windows": pfull == len(rows) and ptg == len(rows),
        }
    result = {
        "status": "Q20_GC_V101_INDEPENDENT_DIRECTION_AUDIT",
        "source_header_expected_prefix": "#=IVTFF v101",
        "nodes": {k:list(v) for k,v in NODES.items()},
        "candidate_five_node": list(CANDIDATE),
        "arrows": summary,
        "path_sensitivity": windows,
        "interpretation": {
            "robust_gc_arrows": [k for k,v in summary.items() if v["robust_positive_all_windows"]],
            "warning": "A replicated pairwise directional preference is precedence evidence only; it is not immediate adjacency.",
        },
        "guardrails": [
            "GC/v101 is independent of the EVA/Takahashi lineage and uses a different alphabet.",
            "Exact last-token/first-token matching is sparse in v101; token+glyph ablation is reported.",
            "Robustness across 2..8 lines is a sensitivity diagnostic, not a historical probability.",
            "S1=103|116 terminal arrows are excluded because this audit focuses on boundaries symmetrically available for S2-S6.",
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
