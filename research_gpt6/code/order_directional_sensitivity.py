#!/usr/bin/env python3
"""Sensitivity sweep for directional singulion boundary ordering.

Runs the directional boundary model at multiple head/tail window sizes and
reports which pairwise arrow signs remain stable. It deliberately separates
undirected adjacency evidence from directional evidence.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import order_directional_boundaries as d
import order_q13_openpath as q13
import order_q20_openpath as q20

WINDOWS=(4,8,12,16,24)

Q13_EDGES={
    "75|84--78|81":("Q13_75|84","Q13_78|81"),
    "76|83--77|82":("Q13_76|83","Q13_77|82"),
    "75|84--76|83":("Q13_75|84","Q13_76|83"),
    "76|83--78|81":("Q13_76|83","Q13_78|81"),
    "78|81--79|80":("Q13_78|81","Q13_79|80"),
}
Q20_EDGES={
    "103|116--108|111":("S1_103|116","S6_108|111"),
    "106|113--107|112":("S4_106|113","S5_107|112"),
    "106|113--108|111":("S4_106|113","S6_108|111"),
    "104|115--106|113":("S2_104|115","S4_106|113"),
    "103|116--104|115":("S1_103|116","S2_104|115"),
}


def score_pair(matrix,a,b):
    ab=matrix[(a,b)]; ba=matrix[(b,a)]
    return {"a_to_b":ab,"b_to_a":ba,"margin_a_minus_b":ab-ba,
            "preferred":f"{a}->{b}" if ab>ba else f"{b}->{a}" if ba>ab else "TIE"}


def summarize_edge_sweep(rows, edges):
    out={}
    for label,(a,b) in edges.items():
        observations=[]; signs=[]
        for win,matrix in rows:
            x=score_pair(matrix,a,b)
            m=x["margin_a_minus_b"]
            sign=1 if m>0 else -1 if m<0 else 0
            signs.append(sign)
            observations.append({"window":win,**x})
        nonzero=[s for s in signs if s]
        stable=bool(nonzero) and len(set(nonzero))==1
        mean_margin=sum(o["margin_a_minus_b"] for o in observations)/len(observations)
        out[label]={
            "a":a,"b":b,
            "stable_sign_all_windows":stable,
            "preferred_direction_if_stable": observations[0]["preferred"] if stable else None,
            "mean_margin_a_minus_b":mean_margin,
            "observations":observations,
        }
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("corpus",type=Path)
    ap.add_argument("--json",type=Path)
    args=ap.parse_args()

    f13=sorted({x for p in q13.SHEETS.values() for x in p})
    f20=sorted({x for p in q20.SHEETS.values() for x in p})
    p13=d.load_page_lines(args.corpus,f13)
    p20=d.load_page_lines(args.corpus,f20)

    rows13=[]; rows20=[]; best13=[]; best20=[]
    for w in WINDOWS:
        docs13=d.boundary_docs(p13,q13.SHEETS,w)
        docs20=d.boundary_docs(p20,q20.SHEETS,w)
        m13,_=d.directed_matrix(docs13)
        m20,_=d.directed_matrix(docs20)
        r13=d.enumerate_directed(list(docs13),m13)
        r20=d.enumerate_directed(list(docs20),m20)
        rows13.append((w,m13)); rows20.append((w,m20))
        best13.append({"window":w,"score":r13[0][0],"order":list(r13[0][1])})
        best20.append({"window":w,"score":r20[0][0],"order":list(r20[0][1])})

    q13_edges=summarize_edge_sweep(rows13,Q13_EDGES)
    q20_edges=summarize_edge_sweep(rows20,Q20_EDGES)

    result={
        "status":"DIRECTION_SENSITIVITY",
        "windows":list(WINDOWS),
        "q13":{"best_by_window":best13,"candidate_edges":q13_edges},
        "q20":{"best_by_window":best20,"candidate_edges":q20_edges},
        "acceptance_rule":"Do not call a direction stable unless its pairwise margin has the same non-zero sign at all tested boundary windows; even then treat it as a textual-direction candidate requiring codicological corroboration.",
        "guardrails":[
            "Internal reading assumption remains a-r,a-v,b-r,b-v.",
            "Stable sign does not establish historical sequence by itself.",
            "Q20 missing 109|110 remains unmodeled.",
        ],
    }
    text=json.dumps(result,ensure_ascii=False,indent=2)
    print(text)
    if args.json: args.json.write_text(text+"\n",encoding="utf-8")

if __name__=="__main__": main()
