#!/usr/bin/env python3
"""Check arithmetic, coverage, logical controls and exact figure regeneration."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

from render_numeral_duplicate_evidence import render
from test_numeral_hypotheses import eligible_label, tokens


def audit(root, plan, source):
    checks = []

    def check(name, condition):
        checks.append({"check": name, "pass": bool(condition)})
        if not condition:
            raise AssertionError(name)

    a = [f"value-{i}" for i in range(30)]
    b = list(reversed(a))
    ca, cb = collections.Counter(a), collections.Counter(b)
    check("true ordinal list survives any permutation", sum((ca & cb).values()) == 30)
    other = collections.Counter(f"other-{i}" for i in range(30))
    check("disjoint lists have zero exact matches", sum((ca & other).values()) == 0)
    known_a = collections.Counter(a[10:])
    check("omission bound retains true matching possibility", min(30, sum((known_a & cb).values()) + 10) == 30)
    check("primary filter preserves word boundaries", eligible_label("ab.c") != eligible_label("a.bc"))
    check("uncertainty is excluded", eligible_label("ab?c") is None and eligible_label("[a:b]") is None)
    policies = ("dot_full", "dot_comma_full", "dot_left", "dot_comma_left")
    check("drawing gap and comma policies", [tokens("a.b<->c,d<$>", p) for p in policies] == [3, 4, 2, 2])
    with (root / "direct_key_rows.csv").open() as stream:
        rows = list(csv.DictReader(stream))
    with (root / "direct_key_scores.csv").open() as stream:
        for s in csv.DictReader(stream):
            selected = [r for r in rows if r["mode"] == s["mode"] and r["role"] == s["role"]]
            n = sum(int(r[s["policy"]]) == int(r["hypothesized_value"]) for r in selected)
            check("score " + s["mode"] + " " + s["role"] + " " + s["policy"],
                  len(selected) == int(s["total"]) and n == int(s["correct"]))
    labels = json.loads((root / "all_label_records.json").read_text())
    check("299 unique label locus records", len(labels) == 299 and len({(x["folio"], x["locus"]) for x in labels}) == 299)
    check("259 primary eligible labels", sum(x["eligible"] for x in labels) == 259)
    duplicates = json.loads((root / "duplicates.json").read_text())
    for d in duplicates:
        selected = [x for x in labels if x["sign"] == d["sign"] and x["eligible"]]
        norm = lambda x: x["canonical"] if d["mode"] == "preserve_words" else x["canonical"].replace(" ", "")
        check("duplicate " + d["mode"] + " " + d["sign"] + " " + d["label"],
              sum(norm(x) == d["label"] for x in selected) == d["count"])
    with (root / "zodiac_order_free_overlap.csv").open() as stream:
        for r in csv.DictReader(stream):
            check("bound " + r["mode"] + " " + r["sign_a"] + " " + r["sign_b"],
                  0 <= int(r["shared_exact"]) <= int(r["generous_upper_bound"]) <= min(int(r["total_a"]), int(r["total_b"])))
    result = json.loads((root / "result.json").read_text())
    check("f66r not artificially aligned", result["direct_key"]["unaligned_f66r_excluded"])
    check("plan hash matches measured result", hashlib.sha256(plan.read_bytes()).hexdigest() == result["plan_sha256"])
    figure = root / "f73r_duplicate_context.jpg"
    old = hashlib.sha256(figure.read_bytes()).hexdigest()
    render(source, root / "visual_check.json", figure)
    check("figure exactly regenerates", hashlib.sha256(figure.read_bytes()).hexdigest() == old)
    report = {
        "status": "PASS_INTERNAL_CONSISTENCY_AND_LOGICAL_CONTROLS", "check_count": len(checks),
        "failures": sum(not x["pass"] for x in checks), "checks": checks,
        "scope": "Numerical and data integrity, not semantic or palaeographic validation.",
        "exposure_note": "All 26 f49v row word counts were already exported in inventory 55; these are consistency checks, not a fresh blind validation set."
    }
    (root / "checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return {"checks": len(checks), "failures": report["failures"], "figure_sha256": old}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(audit(a.data, a.plan, a.source), indent=2))
