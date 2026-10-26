#!/usr/bin/env python3
"""Descriptive, source-linked inventory. No glyph decoding or dating estimator."""
import argparse
import calendar
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for row in rows for k in row)))
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()})


def parse_ivtff(path):
    rows = []
    for line in Path(path).read_text().splitlines():
        m = re.match(r"<f([^.,>]+)\.(\d+),([^>]+)>\s*(.*)", line)
        if m:
            folio, number, kind, text = m.groups()
            rows.append(dict(folio=folio, locus=int(number), kind=kind, text=text))
    return rows


def strip_comments(text):
    return re.sub(r"<[^>]*>", "", text).strip()


def word_count(text, comma_is_boundary):
    # Counts editorial tokens, NOT translated words. Keep alternatives as one token.
    text = re.sub(r"<->", ".", text)
    text = strip_comments(text)
    return len([x for x in re.split(r"[.,]" if comma_is_boundary else r"\.", text) if x])


def run(spec_path, corpus_path, scans, output, receipts_path, download_missing=False):
    from PIL import Image, ImageDraw, ImageFont

    spec = json.loads(spec_path.read_text())
    if sha256(corpus_path) != spec["corpus_sha256"]:
        raise ValueError("Corpus hash does not match frozen source")
    output.mkdir(parents=True, exist_ok=True)
    (output / "crops").mkdir(exist_ok=True)
    (output / "figures").mkdir(exist_ok=True)
    rows = parse_ivtff(corpus_path)
    by_folio = defaultdict(list)
    for row in rows:
        by_folio[row["folio"]].append(row)

    # Pairing follows the IVTFF locus order: a label immediately precedes a text line.
    f49 = by_folio["49v"]
    labels = [r for r in f49 if r["kind"].endswith("L0")]
    running = [r for r in f49 if r["kind"].endswith("P0")]
    if len(labels) != 26 or len(running) != 26:
        raise ValueError("Unexpected f49v locus coverage")
    associations = []
    for i, (label, text) in enumerate(zip(labels, running), 1):
        if label["locus"] + 1 != text["locus"]:
            raise ValueError("Label/text pairing is not adjacent")
        digit = i - 1 if 2 <= i <= 6 else None
        associations.append(dict(
            physical_line=i, label_locus=label["locus"], text_locus=text["locus"],
            marginal_sign=strip_comments(label["text"]), visible_arabic_digit=digit,
            tokens_dot=word_count(text["text"], False),
            tokens_dot_or_comma=word_count(text["text"], True),
        ))
    digit_rows = [r for r in associations if r["visible_arabic_digit"] is not None]
    for case in [c for c in spec["cases"] if c["kind"] == "CIFRA_MARGINAL"]:
        row = associations[case["physical_line"] - 1]
        if (row["visible_arabic_digit"], row["marginal_sign"]) != (case["value"], case["paired_transliteration"]):
            raise ValueError("Curated image association and ZL disagree")

    # Ring f57v.3: editorial dot-delimited groups, not necessarily indivisible glyphs.
    ring = next(r for r in by_folio["57v"] if r["locus"] == 3)
    ring_groups = strip_comments(ring["text"]).split(".")
    if len(ring_groups) != 68:
        raise ValueError("Ring group segmentation changed")
    blocks = [ring_groups[i:i + 17] for i in range(0, 68, 17)]
    stable_positions = [i + 1 for i in range(17) if len({b[i] for b in blocks}) == 1]

    zodiac = []
    for item in spec["zodiac"]:
        found = [r for r in by_folio[item["folio"]] if r["kind"].endswith("Lz")]
        zodiac.append({**item, "labels_in_zl": len(found), "catalogue_agrees_with_zl": len(found) == item["labels_reported"]})
    totals = defaultdict(lambda: {"labels": 0, "figures_reported": 0, "folios": []})
    for item in zodiac:
        sign = totals[item["sign"]]
        sign["labels"] += item["labels_in_zl"]
        sign["figures_reported"] += item["figures_reported"]
        sign["folios"].append(item["folio"])
        sign["month"] = item["month"]
        # Only March-December are represented; no February/leap-year ambiguity.
        sign["civil_month_days"] = calendar.monthrange(2025, item["month"])[1]

    receipts = json.loads(receipts_path.read_text())["images"]
    receipt_map = {r["canvas_id"].split("/")[-1]: r for r in receipts}
    if download_missing:
        import urllib.request
        scans.mkdir(parents=True, exist_ok=True)
        for cid in sorted({c["canvas"] for c in spec["cases"]}):
            target = scans / (cid + ".jpg")
            if target.exists():
                continue
            receipt = receipt_map[cid]
            url = receipt["source_url"]
            if not url.startswith("https://collections.library.yale.edu/iiif/2/"):
                raise ValueError("Unexpected image host")
            with urllib.request.urlopen(url, timeout=45) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != receipt["source_sha256"]:
                raise ValueError("Downloaded source changed; stop rather than replace frozen evidence")
            target.write_bytes(data)
    image_sources = []
    seen = set()
    catalog = []
    for case in spec["cases"]:
        path = scans / (case["canvas"] + ".jpg")
        receipt = receipt_map[case["canvas"]]
        if sha256(path) != receipt["source_sha256"]:
            raise ValueError("Image differs from acquisition receipt: " + case["canvas"])
        im = Image.open(path)
        x0, y0, x1, y1 = case["crop"]
        if not (0 <= x0 < x1 <= im.width and 0 <= y0 < y1 <= im.height):
            raise ValueError("Out-of-bounds crop: " + case["id"])
        crop_path = output / "crops" / (case["id"] + ".jpg")
        im.crop(case["crop"]).save(crop_path, quality=92)
        catalog.append({**case, "crop_file": "crops/" + crop_path.name, "source_url": receipt["source_url"], "source_sha256": receipt["source_sha256"]})
        if case["canvas"] not in seen:
            image_sources.append({"canvas": case["canvas"], "source_url": receipt["source_url"], "source_sha256": receipt["source_sha256"], "size": list(im.size)})
            seen.add(case["canvas"])

    # A larger context crop is essential: shows digits, signs, and running text together.
    Image.open(scans / "1006171.jpg").crop((300, 190, 1230, 680)).save(output / "figures/f49v_alignment.jpg", quality=94)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 21)
    for folio, ann in spec["manual_head_points"].items():
        im = Image.open(scans / (ann["canvas"] + ".jpg")).copy()
        im.thumbnail((1200, 1500))
        d = ImageDraw.Draw(im)
        number = 0
        for group in ("inner", "outer"):
            for px, py in ann[group]:
                number += 1
                x = px / ann["reference_size"][0] * im.width
                y = py / ann["reference_size"][1] * im.height
                d.ellipse((x - 8, y - 8, x + 8, y + 8), outline="#087A8E", width=3)
                d.rectangle((x + 9, y - 30, x + 45, y - 5), fill="white")
                d.text((x + 11, y - 31), str(number), font=font, fill="#075666")
        if number != 15:
            raise ValueError("Manual point count differs from review")
        im.save(output / "figures" / (folio + "_counted.jpg"), quality=91)

    repeats = {s: [r["physical_line"] for r in associations if r["marginal_sign"] == s] for s, n in Counter(r["marginal_sign"] for r in associations).items() if n > 1}
    result = {
        "status": "DESCRIPTIVE_FIRST_INVENTORY_NO_DECIPHERMENT",
        "scope": spec["scope"], "date": spec["date"], "review": spec["review"],
        "case_count": len(catalog), "case_kinds": dict(Counter(c["kind"] for c in catalog)),
        "corpus_sha256": sha256(corpus_path), "spec_sha256": sha256(spec_path),
        "f49v": {"running_lines": len(running), "marginal_signs": len(labels), "digit_rows": digit_rows,
            "repeated_sign_positions": repeats,
            "digit_equals_line_token_count": {key: sum(r["visible_arabic_digit"] == r[key] for r in digit_rows) for key in ("tokens_dot", "tokens_dot_or_comma")},
            "unique_absolute_line_number_hypothesis": "INCOMPATIBLE_WITH_REPEATED_IDENTICAL_SIGNS_UNDER_FIXED_ONE_TO_ONE_MAPPING",
            "interpretation": "Partial enumeration/annotation plausible. Local alignment does not validate a numeral key, dosage, or word-count meaning."},
        "f57v": {"locus": "f57v.3", "editorial_groups": len(ring_groups), "block_size": 17,
            "blocks": blocks, "invariant_positions": stable_positions, "variable_positions": [i for i in range(1, 18) if i not in stable_positions],
            "interpretation": "Repetition of sign groups; not proof of a numerical base or a numeral sequence."},
        "zodiac": {"diagrams": len(zodiac), "signs": len(totals), "all_label_counts_match_catalogue": all(r["catalogue_agrees_with_zl"] for r in zodiac),
            "total_labels": sum(r["labels_in_zl"] for r in zodiac), "total_figures_reported": sum(r["figures_reported"] for r in zodiac),
            "by_sign": dict(totals),
            "signs_with_30_labels": sum(r["labels"] == 30 for r in totals.values()),
            "signs_with_30_figures_reported": sum(r["figures_reported"] == 30 for r in totals.values()),
            "signs_labels_equal_civil_month_days": sum(r["labels"] == r["civil_month_days"] for r in totals.values()),
            "signs_figures_equal_civil_month_days": sum(r["figures_reported"] == r["civil_month_days"] for r in totals.values()),
            "independence": "Catalogue and ZL share authorship/source history; agreement is a consistency check, not independent replication.",
            "interpretation": "A 30-unit zodiac scheme is a useful hypothesis. Strict one-item-per-civil-day reading does not fit all represented months; a schematic calendar remains possible."},
        "image_sources": image_sources, "limits": spec["interpretation_limits"],
    }
    dump(output / "result.json", result)
    dump(output / "catalog.json", catalog)
    write_csv(output / "catalog.csv", catalog)
    write_csv(output / "f49v_alignment.csv", associations)
    write_csv(output / "zodiac_counts.csv", zodiac)
    checks = {"status": "PASS_INTERNAL_CONSISTENCY", "scope": "Coverage, coordinates, source hashes, transcript pairing and bibliography count consistency. Not verification of semantic interpretations.",
        "unique_case_ids": len({c["id"] for c in catalog}) == len(catalog), "source_images_hash_checked": len(image_sources), "crop_bounds_checked": len(catalog),
        "f49v_pairs_checked": len(associations), "numeral_pairings_checked": len(digit_rows), "zodiac_label_counts_checked": len(zodiac),
        "manual_figure_counts": {k: len(v["inner"]) + len(v["outer"]) for k, v in spec["manual_head_points"].items()}}
    dump(output / "checks.json", checks)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--scans", type=Path, required=True)
    p.add_argument("--receipts", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--download-missing", action="store_true", help="Download only missing selected scans, with exact source-hash verification")
    a = p.parse_args()
    r = run(a.spec, a.corpus, a.scans, a.output, a.receipts, a.download_missing)
    print(json.dumps({"status": r["status"], "cases": r["case_count"], "f49v": r["f49v"]["digit_rows"], "f57v": {k: v for k, v in r["f57v"].items() if k != "blocks"}, "zodiac": {k: v for k, v in r["zodiac"].items() if k != "by_sign"}}, ensure_ascii=False, indent=2))
