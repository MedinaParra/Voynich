#!/usr/bin/env python3
"""Reproduce notebook 74's STA1 parsing and f57v glyph counts.

The notebook's chance calculations are reported for comparison but explicitly
flagged as post-selection, since the candidates were identified from this
corpus and the model treats atom locations as exchangeable independent draws.
"""
from __future__ import annotations

import argparse
import os

from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = Path(os.environ.get("VOYNICH_CORPUS", str(ROOT / "corpus" / "voynich_sta.txt")))
ATOM_RE = re.compile(r"[A-Z][a-z0-9]*")
CANDIDATES = ["X1", "X2", "Xd", "Xf", "Pc", "Ea", "Eb", "Ja"]
EXCLUSIVE_CORE = ["X2", "Xd", "Xf", "Pc", "Ea"]


def main() -> None:
    global CORPUS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus", type=Path,
        default=CORPUS,
        help="Path to corpus/voynich_sta.txt from the source repository; can also be set with VOYNICH_CORPUS.",
    )
    args = parser.parse_args()
    CORPUS = args.corpus.expanduser().resolve()
    if not CORPUS.is_file():
        parser.error(f"STA1 corpus not found: {CORPUS}. Pass --corpus or set VOYNICH_CORPUS.")
    all_lines = []
    with CORPUS.open(encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"<(f\d+[rv]\d?)\.(\d+)[,>]([^>]*)>\s*(.*)", line)
            if not m:
                continue
            folio, line_num, tag, content = m.groups()
            content = content.strip()
            if not content or content.startswith("<!") or content.startswith("$"):
                continue
            atoms = ATOM_RE.findall(content.replace(".", "").replace(",", ""))
            all_lines.append({"folio": folio, "line_num": int(line_num),
                              "tag": tag.strip(), "content": content,
                              "atoms": atoms})

    per_folio: dict[str, Counter[str]] = defaultdict(Counter)
    global_counts: Counter[str] = Counter()
    for row in all_lines:
        per_folio[row["folio"]].update(row["atoms"])
        global_counts.update(row["atoms"])
    n_all = sum(global_counts.values())
    n_f57v = sum(per_folio["f57v"].values())
    folio_n = len(per_folio)

    candidate_stats = {}
    for glyph in CANDIDATES:
        total = global_counts[glyph]
        count = per_folio["f57v"][glyph]
        if not total:
            continue
        candidate_stats[glyph] = {
            "global_count": total,
            "f57v_count": count,
            "share_in_f57v_pct": 100 * count / total,
            "enrichment_x": (count / n_f57v) / (total / n_all),
            "folios_with_glyph": sum(bool(c[glyph]) for c in per_folio.values()),
        }

    all_exclusive = []
    for glyph, total in global_counts.items():
        if total < 2:
            continue
        for folio, counts in per_folio.items():
            if counts[glyph] == total:
                all_exclusive.append({"glyph": glyph, "folio": folio, "count": total})

    p_share = n_f57v / n_all
    x2_k = global_counts["X2"]
    result = {
        "source": str(CORPUS),
        "sha256": sha256(CORPUS.read_bytes()).hexdigest(),
        "parser": "74_f57v_private_subalphabet.ipynb cells 2, 4, 6 (faithful port)",
        "corpus": {"parsed_lines": len(all_lines), "folios": folio_n,
                   "atoms": n_all, "f57v_atoms": n_f57v,
                   "f57v_share": p_share},
        "candidates": candidate_stats,
        "non_singleton_exclusive_glyph_folio_pairs": len(all_exclusive),
        "all_exclusive_examples_first_30": sorted(all_exclusive, key=lambda x: (x["folio"], x["glyph"]))[:30],
        "notebook_null_reproduction": {
            "assumption": "Each occurrence is independently and uniformly assigned to corpus atoms, after selecting candidates/folio from this same dataset.",
            "x2_p_unadjusted": p_share ** x2_k,
            "five_glyphs_k": sum(global_counts[g] for g in EXCLUSIVE_CORE),
            "five_glyphs_p_unadjusted": p_share ** sum(global_counts[g] for g in EXCLUSIVE_CORE),
            "status": "descriptive only; not a calibrated inferential p-value",
        },
        "selection_note": "Candidate glyphs and exceptional folio are identified from the same corpus. The reported p**k omits post-selection/multiplicity, dependence, section/quire effects and transcription uncertainty.",
    }
    out = ROOT / "research_gpt6" / "results" / "f57v_reproduction.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nSaved: {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
