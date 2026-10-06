#!/usr/bin/env python3
"""Audit exact surface-form coverage of the generator published at solvedvoynich.com.

Run: python audit_dickens_generator.py --corpus /path/to/voynich_eva.txt
Uses only Python's standard library. This tests the literal prefix + base +
suffix inventory shown on the public page; it does not assess resemblance or
the author's separate cross-line mutual-information claim.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

PREFIXES = ["", "qo", "o", "y", "sh", "ch", "s", "k", "p", "f", "t", "c", "d"]
BASES = ["l", "r", "k", "ch", "sh", "e", "a", "i", "ol", "al", "or", "ar",
         "ok", "ak", "od", "ed", "ot", "et", "il", "eo", "ee", "ai", "eol",
         "aol", "kor", "kar", "kol", "kal", "dol", "dal", "pol", "pal", "d"]
SUFFIXES = ["", "y", "dy", "ey", "aiy", "eey", "am", "an", "chy", "shy"]

def extract_types(path: Path):
    tokens = []
    lines = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^<[^>]+,\s*[^>]*P[^>]*>\s*(.*)$", line)
        if not m:
            continue
        lines += 1
        body = re.sub(r"<![^>]*>", "", m.group(1))
        body = re.sub(r"\{[^}]*\}", "", body)
        body = re.sub(r"\[[^\]]*\]", " ", body)
        tokens.extend(t for t in re.split(r"[^a-z]+", body.lower()) if t)
    return lines, tokens

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    line_count, tokens = extract_types(args.corpus)
    generated = {p + b + s for p in PREFIXES for b in BASES for s in SUFFIXES}
    observed_types = set(tokens)
    hit_types = observed_types & generated
    hit_tokens = sum(t in generated for t in tokens)
    result = {
        "status": "FAIL_LITERAL_COVERAGE_CLAIM",
        "scope": "Exact surface matching for the published inventory; not a test of visual resemblance or manuscript meaning.",
        "corpus_path": str(args.corpus),
        "transcription_lines": line_count,
        "token_count": len(tokens),
        "observed_type_count": len(observed_types),
        "raw_combinations": len(PREFIXES) * len(BASES) * len(SUFFIXES),
        "unique_generated_forms": len(generated),
        "exact_type_hits": len(hit_types),
        "exact_type_coverage": len(hit_types) / len(observed_types) if observed_types else None,
        "exact_token_hits": hit_tokens,
        "exact_token_coverage": hit_tokens / len(tokens) if tokens else None,
        "limitations": [
            "The author's EVA-Takahashi preprocessing and meaning of 99.6% were not published with a runnable evaluator on the page consulted.",
            "Bracketed uncertain readings are omitted; punctuation/line conventions can change token counts.",
            "This does not test the separate cross-line mutual-information result."
        ]
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")

if __name__ == "__main__":
    main()
