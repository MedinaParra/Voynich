#!/usr/bin/env python3
"""Directional boundary test for Q13/Q20 singulion ordering.

Goal
----
Previous ordering experiments use whole-singulion cosine similarity and are
therefore symmetric: A--B == B--A. This experiment instead represents the
*terminal boundary* of A and the *initial boundary* of B, so A->B and B->A
can differ.

Assumed internal reading order of a folded singulion `a|b` is:
    a-r, a-v, b-r, b-v
Thus the external transition is from the tail of b-v to the head of the next
a-r. This assumption is explicit and must be checked codicologically; results
are a directional hypothesis, not proof.

For each ordered pair A->B we combine:
- token TF-IDF cosine(tail(A), head(B));
- EVA character 3-5gram TF-IDF cosine(tail(A), head(B));
- line-initial token distribution similarity;
- line-final token distribution similarity.

All IDF vocabularies are learned over boundary documents only, with fixed
settings. We enumerate every directed Hamiltonian open path, compare candidate
orders and reversals, and report the directional margin.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import order_q20_openpath as base
import order_q13_openpath as q13

Q20_SHEETS = base.SHEETS
Q13_SHEETS = q13.SHEETS

LOCUS = re.compile(r"^<f(\d+)([rv])\.([^>]+)>\s+(.*)$")


def load_page_lines(path: Path, wanted_folios):
    pages = defaultdict(list)
    wanted=set(wanted_folios)
    for raw in path.read_text(encoding="utf-8",errors="replace").splitlines():
        m=LOCUS.match(raw)
        if not m: continue
        f=int(m.group(1)); side=m.group(2)
        if f not in wanted: continue
        txt=base.clean_text(m.group(4))
        if txt:
            pages[(f,side)].append(txt)
    missing=[]
    for f in wanted:
        for side in ("r","v"):
            if not pages[(f,side)]: missing.append(f"{f}{side}")
    if missing:
        raise ValueError(f"Missing pages: {missing}")
    return pages


def take_head(lines,k): return lines[:k]
def take_tail(lines,k): return lines[-k:]


def boundary_docs(pages,sheets,k):
    out={}
    for name,(a,b) in sheets.items():
        # Explicit singulion assumption: starts at a-r, ends at b-v.
        head=take_head(pages[(a,"r")],k)
        tail=take_tail(pages[(b,"v")],k)
        out[name]={"head_lines":head,"tail_lines":tail}
    return out


def first_token_counter(lines):
    c=Counter()
    for ln in lines:
        toks=[t for t in ln.split() if t and "?" not in t]
        if toks: c[toks[0]]+=1
    return c


def last_token_counter(lines):
    c=Counter()
    for ln in lines:
        toks=[t for t in ln.split() if t and "?" not in t]
        if toks: c[toks[-1]]+=1
    return c


def make_vectors(docs,kind):
    counters={}
    for name,d in docs.items():
        lines=d[kind+"_lines"]
        text=" ".join(lines)
        counters[name]=base.token_features(text)
    return base.tfidf(counters)


def make_char_vectors(docs,kind):
    counters={}
    for name,d in docs.items():
        text=" ".join(d[kind+"_lines"])
        counters[name]=base.char_ngram_features(text)
    return base.tfidf(counters)


def tfidf_from_counters(counters):
    return base.tfidf(counters)


def znormalize(values):
    vals=list(values.values())
    mu=sum(vals)/len(vals)
    sd=math.sqrt(sum((x-mu)**2 for x in vals)/len(vals)) or 1.0
    return {k:(v-mu)/sd for k,v in values.items()}


def directed_matrix(docs):
    names=list(docs)
    htok=make_vectors(docs,"head"); ttok=make_vectors(docs,"tail")
    hchr=make_char_vectors(docs,"head"); tchr=make_char_vectors(docs,"tail")
    hfirst=tfidf_from_counters({n:first_token_counter(docs[n]["head_lines"]) for n in names})
    tlast=tfidf_from_counters({n:last_token_counter(docs[n]["tail_lines"]) for n in names})

    components={"token":{},"char":{},"edge_token":{}}
    for a in names:
        for b in names:
            if a==b: continue
            components["token"][(a,b)] = base.cosine(ttok[a],htok[b])
            components["char"][(a,b)] = base.cosine(tchr[a],hchr[b])
            components["edge_token"][(a,b)] = base.cosine(tlast[a],hfirst[b])
    zn={k:znormalize(v) for k,v in components.items()}
    score={pair:sum(zn[k][pair] for k in zn)/len(zn) for pair in zn["token"]}
    return score,components


def path_score(p,score):
    return sum(score[(a,b)] for a,b in zip(p,p[1:]))


def enumerate_directed(names,score):
    rows=[(path_score(p,score),p) for p in itertools.permutations(names)]
    rows.sort(key=lambda x:(-x[0],x[1]))
    return rows


def find_rank(order,rows):
    t=tuple(order)
    for i,(s,p) in enumerate(rows,1):
        if p==t:
            rev=tuple(reversed(t))
            rev_rank=next(j+1 for j,(_,q) in enumerate(rows) if q==rev)
            rev_score=next(ss for ss,q in rows if q==rev)
            return {
                "order":list(t),"score":s,"rank":i,
                "percentile":1-(i-1)/max(1,len(rows)-1),
                "reverse_order":list(rev),"reverse_score":rev_score,
                "reverse_rank":rev_rank,
                "directional_margin_vs_reverse":s-rev_score,
            }
    raise AssertionError(t)


def analyze(label,docs,candidates):
    score,components=directed_matrix(docs)
    rows=enumerate_directed(list(docs),score)
    pair_margins=[]
    names=list(docs)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            pair_margins.append({
                "pair":[a,b],
                "a_to_b":score[(a,b)],
                "b_to_a":score[(b,a)],
                "margin_a_minus_b":score[(a,b)]-score[(b,a)],
            })
    pair_margins.sort(key=lambda r:-abs(r["margin_a_minus_b"]))
    return {
        "label":label,
        "n_directed_paths":len(rows),
        "best":{"score":rows[0][0],"order":list(rows[0][1])},
        "top10":[{"rank":i+1,"score":s,"order":list(p)} for i,(s,p) in enumerate(rows[:10])],
        "candidates":{name:find_rank(order,rows) for name,order in candidates.items()},
        "strongest_pair_direction_margins":pair_margins[:20],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus",type=Path)
    ap.add_argument("--boundary-lines",type=int,default=12)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    f13=sorted({x for p in Q13_SHEETS.values() for x in p})
    f20=sorted({x for p in Q20_SHEETS.values() for x in p})
    p13=load_page_lines(args.corpus,f13)
    p20=load_page_lines(args.corpus,f20)
    d13=boundary_docs(p13,Q13_SHEETS,args.boundary_lines)
    d20=boundary_docs(p20,Q20_SHEETS,args.boundary_lines)

    q13_candidates={
        "current":tuple(Q13_SHEETS),
        "layfield_davis":q13.LAYFIELD_DAVIS,
        "reported_held_karp":q13.REPORTED_HELD_KARP,
        "whole_text_combined_best":("Q13_77|82","Q13_76|83","Q13_78|81","Q13_75|84","Q13_79|80"),
    }
    q20_candidates={
        "current":tuple(Q20_SHEETS),
        "whole_text_raw_best":("S1_103|116","S6_108|111","S5_107|112","S2_104|115","S4_106|113","S3_105|114"),
        "dialect_residual_best":("S2_104|115","S1_103|116","S6_108|111","S4_106|113","S5_107|112","S3_105|114"),
    }

    result={
        "status":"DIRECTIONAL_BOUNDARY_HYPOTHESIS",
        "boundary_lines":args.boundary_lines,
        "internal_reading_assumption":"a-r,a-v,b-r,b-v for singulion a|b",
        "q13":analyze("Q13",d13,q13_candidates),
        "q20":analyze("Q20",d20,q20_candidates),
        "guardrails":[
            "This test depends on the explicit internal reading orientation of each bifolium.",
            "Boundary similarity can reflect scribal/dialect/topic effects rather than narrative continuation.",
            "Q20 109|110 is missing and not modeled.",
            "Use directional results only when they agree across boundary-window sensitivity and codicological evidence.",
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json: args.json.write_text(text+"\n",encoding="utf-8")

if __name__=="__main__": main()
