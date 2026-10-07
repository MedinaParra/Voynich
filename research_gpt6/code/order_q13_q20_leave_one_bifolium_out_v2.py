#!/usr/bin/env python3
"""Corrected strict Q13/Q20 leave-one-bifolium-out audit.

Corrections relative to v1:
- Q20 principal reference is frozen to the current candidate
  105|114 -> 106|113 -> 107|112 -> 104|115 -> 108|111 -> 103|116.
- f116v is allowed to be text-empty; unit_tokens() already handles absent sides
  as an empty list, so no information is imputed.

All scoring/fitting functions are imported unchanged from v1.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import order_q13_q20_leave_one_bifolium_out as core

core.REFERENCES["Q20_principal"] = [
    "105|114", "106|113", "107|112", "104|115", "108|111", "103|116"
]

ALLOWED_EMPTY_PAGES = {"f116v"}


def analyse_transcription(raw: str):
    pages, audit = core.parse_pages(raw)
    required = sorted({f for p in list(core.Q13.values()) + list(core.Q20.values()) for f in p})
    missing = [
        f"f{f}{s}" for f in required for s in ("r", "v")
        if not pages.get(f"f{f}{s}") and f"f{f}{s}" not in ALLOWED_EMPTY_PAGES
    ]
    if missing:
        raise RuntimeError(f"missing required nonempty pages: {missing}")

    out = {"parser_audit": audit, "allowed_empty_pages": sorted(ALLOWED_EMPTY_PAGES)}
    out["Q13_independent"] = core.analyse_reference(
        pages, core.Q13, core.REFERENCES["Q13_independent"]
    )
    out["Q13_layfield_davis"] = core.analyse_reference(
        pages, core.Q13, core.REFERENCES["Q13_layfield_davis"]
    )
    out["Q13_current"] = core.analyse_reference(
        pages, core.Q13, core.REFERENCES["Q13_current"]
    )
    out["Q20_principal_raw"] = core.analyse_reference(
        pages, core.Q20, core.REFERENCES["Q20_principal"]
    )
    out["Q20_principal_residual_ST"] = core.analyse_reference(
        pages, core.Q20, core.REFERENCES["Q20_principal"], True
    )
    out["Q20_current_raw"] = core.analyse_reference(
        pages, core.Q20, core.REFERENCES["Q20_current"]
    )
    out["Q20_current_residual_ST"] = core.analyse_reference(
        pages, core.Q20, core.REFERENCES["Q20_current"], True
    )
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zl", type=Path, required=True)
    ap.add_argument("--it", type=Path, required=True)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    zl_raw = args.zl.read_text(encoding="utf-8", errors="replace")
    it_bytes = args.it.read_bytes()
    it_sha = hashlib.sha256(it_bytes).hexdigest()
    if it_sha != core.IT2A_SHA256:
        raise SystemExit(f"IT2a SHA256 mismatch: {it_sha}")
    it_raw = it_bytes.decode("utf-8", errors="replace")

    zl = analyse_transcription(zl_raw)
    it = analyse_transcription(it_raw)
    keys = [k for k in zl if k not in {"parser_audit", "allowed_empty_pages"}]
    cross = {k: core.cross_summary(zl, it, k) for k in keys}

    result = {
        "status": "Q13_Q20_STRICT_LEAVE_ONE_BIFOLIUM_OUT_V2",
        "corrections_from_v1": [
            "allow text-empty f116v without imputation",
            "freeze Q20 principal to current six-survivor candidate",
        ],
        "method": {
            "unit": "complete physical bifolium; absent f116v contributes zero tokens",
            "idf_fit": "all manuscript pages except both held-out folios",
            "heldout_transform": "frozen training IDF; unseen held-out features ignored",
            "component_normalization": "training target-quire pair similarities only",
            "components": [
                "token TF-IDF cosine",
                "character 3-5gram TF-IDF cosine",
                "token Jaccard",
            ],
            "placement": "rank every insertion slot into each frozen reference order",
            "Q20_control": "training-only S/T block-pair mean residualization",
        },
        "references": core.REFERENCES,
        "ZL3b": zl,
        "IT2a": it,
        "cross_transcription": cross,
        "guardrails": [
            "This is metric-generalization/self-consistency, not independent historical validation.",
            "Reference orders were discovered or proposed using related manuscript evidence.",
            "ZL3b and IT2a are independent transcriptions of the same physical manuscript.",
            "The missing Q20 bifolium 109|110 is not imputed or scored.",
            "No folio number, current distance, image feature, or material defect enters the similarity metric.",
            "f116v is treated as genuinely text-empty, not synthetically filled.",
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    print(text, end="")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
