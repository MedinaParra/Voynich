#!/usr/bin/env python3
"""H91c infrastructure-only generic wrapper for frozen H76 extraction.

No lexical strings are accepted or inspected. The frozen H76 run_page implementation
is reused directly, so image processing, thresholds, masking, connected components,
and geometry are unchanged.
"""
import argparse
import json
from pathlib import Path

from h76_visual_object_extraction_admissibility import run_page


def parse_input(spec: str):
    if "=" not in spec:
        raise ValueError("--input must be PAGE=COORDS_JSON")
    page, path = spec.split("=", 1)
    page = page.strip()
    if not page:
        raise ValueError("empty page identifier")
    return page, Path(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", action="append", required=True, help="PAGE=COORDS_JSON; lexical strings forbidden")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    pages = {}
    for spec in args.input:
        page, coords = parse_input(spec)
        if page in pages:
            raise ValueError(f"duplicate page: {page}")
        pages[page] = run_page(page, coords)

    overall = "PASS" if pages and all(v.get("status") == "PASS" for v in pages.values()) else "BLOCKED"
    out = {
        "classification": "H91C_GENERIC_VISUAL_EXTRACTOR_INFRASTRUCTURE_ONLY",
        "implementation": "delegates unchanged extraction to h76_visual_object_extraction_admissibility.run_page",
        "lexical_inputs": "FORBIDDEN",
        "pages": pages,
        "status": overall,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
