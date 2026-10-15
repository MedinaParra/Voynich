#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path
from statistics import median

import numpy as np

import h76_visual_object_extraction_admissibility as h76

PAGES = ("f68r1", "f68r2")
EXPECTED = {
    "f68r1": {
        "image_sha256": "a7da74a67a4411dc95e650c270c76ffd1a323dc20f55dc9ab718e6344c263d11",
        "width": 636,
        "height": 900,
        "otsu_threshold": 191,
        "admissible_component_count": 57,
        "low_text_overlap_component_count": 57,
    },
    "f68r2": {
        "image_sha256": "c8ac7f381499fca09cd5c5dd83dd26a0e07d66752d2a0390fb25878ddc1aee60",
        "width": 636,
        "height": 900,
        "otsu_threshold": 182,
        "admissible_component_count": 90,
        "low_text_overlap_component_count": 89,
    },
}
THRESHOLD_DELTAS = (-10, 0, 10)
MASK_MARGINS = (2, 3, 4)
BASE_SETTING = (0, 3)
IOU_MIN = 0.50
CENTROID_DISTANCE_MAX = 12.0
STABLE_MIN_ALTERNATIVES = 6


def bbox_iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ax1, ay1 = ax + aw, ay + ah
    bx1, by1 = bx + bw, by + bh
    ix0, iy0 = max(ax, bx), max(ay, by)
    ix1, iy1 = min(ax1, bx1), min(ay1, by1)
    iw, ih = max(0, ix1 - ix0), max(0, iy1 - iy0)
    inter = iw * ih
    union = aw * ah + bw * bh - inter
    return inter / union if union else 0.0


def centroid_distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def build_masks(height, width, boxes, margin):
    original = np.zeros((height, width), dtype=bool)
    expanded = np.zeros((height, width), dtype=bool)
    for box in boxes:
        h76.apply_rect(original, *box, margin=0)
        h76.apply_rect(expanded, *box, margin=margin)
    return original, expanded


def extract_setting(arr, boxes, base_otsu, delta, margin):
    height, width = arr.shape[:2]
    original_mask, expanded_mask = build_masks(height, width, boxes, margin)
    rgb = arr.astype(np.float64)
    gray = np.rint(
        0.299 * rgb[:, :, 0] +
        0.587 * rgb[:, :, 1] +
        0.114 * rgb[:, :, 2]
    ).clip(0, 255).astype(np.uint8)
    threshold = int(max(0, min(255, base_otsu + delta)))
    foreground = gray < threshold
    foreground[expanded_mask] = False
    all_count, components = h76.component_records(foreground, original_mask)
    low = [c for c in components if c["low_text_overlap"]]
    return {
        "threshold_delta": delta,
        "mask_margin": margin,
        "threshold": threshold,
        "all_connected_component_count": all_count,
        "admissible_component_count": len(components),
        "low_text_overlap_component_count": len(low),
        "foreground_pixels_after_text_mask": int(foreground.sum()),
        "low_components": low,
    }


def greedy_match(base_components, alt_components):
    eligible = []
    for bi, base in enumerate(base_components):
        for ai, alt in enumerate(alt_components):
            iou = bbox_iou(base["bbox"], alt["bbox"])
            if iou < IOU_MIN:
                continue
            dist = centroid_distance(base["centroid"], alt["centroid"])
            if dist > CENTROID_DISTANCE_MAX:
                continue
            eligible.append((
                -iou,
                dist,
                int(base["component_id"]),
                int(alt["component_id"]),
                bi,
                ai,
                iou,
            ))
    eligible.sort()
    used_base = set()
    used_alt = set()
    matches = []
    for _, dist, base_id, alt_id, bi, ai, iou in eligible:
        if bi in used_base or ai in used_alt:
            continue
        used_base.add(bi)
        used_alt.add(ai)
        matches.append({
            "base_index": bi,
            "base_component_id": base_id,
            "alternative_component_id": alt_id,
            "iou": float(iou),
            "centroid_distance": float(dist),
        })
    return matches


def run_page(page, coords_path):
    expected = EXPECTED[page]
    url, data, image, error = h76.download_image(page)
    result = {"page": page, "image_url": url}
    if error:
        result.update({"status": "BLOCKED", "reason": "image acquisition/decoding failed", "error": error})
        return result

    image_hash = h76.sha256_bytes(data)
    arr = np.asarray(image, dtype=np.uint8)
    height, width = arr.shape[:2]
    result.update({
        "image_sha256": image_hash,
        "width": int(width),
        "height": int(height),
    })
    if image_hash != expected["image_sha256"]:
        result.update({"status": "BLOCKED", "reason": "frozen H76 image hash mismatch"})
        return result

    boxes = h76.load_boxes(coords_path)
    rgb = arr.astype(np.float64)
    gray = np.rint(
        0.299 * rgb[:, :, 0] +
        0.587 * rgb[:, :, 1] +
        0.114 * rgb[:, :, 2]
    ).clip(0, 255).astype(np.uint8)
    base_otsu = h76.otsu_threshold(gray)

    settings = {}
    for delta in THRESHOLD_DELTAS:
        for margin in MASK_MARGINS:
            key = f"delta_{delta:+d}_margin_{margin}"
            settings[key] = extract_setting(arr, boxes, base_otsu, delta, margin)

    base_key = "delta_+0_margin_3"
    base = settings[base_key]
    base_components = base.pop("low_components")

    reproduction = {
        "dimensions_match": width == expected["width"] and height == expected["height"],
        "otsu_threshold_match": base_otsu == expected["otsu_threshold"],
        "admissible_component_count_match": base["admissible_component_count"] == expected["admissible_component_count"],
        "low_text_overlap_component_count_match": base["low_text_overlap_component_count"] == expected["low_text_overlap_component_count"],
    }

    match_summaries = {}
    per_base = [{
        "component_id": int(c["component_id"]),
        "bbox": c["bbox"],
        "centroid": c["centroid"],
        "area": int(c["area"]),
        "successful_matches": [],
    } for c in base_components]

    alternative_counts_ok = True
    for key, setting in settings.items():
        if key == base_key:
            continue
        alt_components = setting.pop("low_components")
        if setting["low_text_overlap_component_count"] < 10:
            alternative_counts_ok = False
        matches = greedy_match(base_components, alt_components)
        match_summaries[key] = {
            "matched_base_component_count": len(matches),
            "alternative_low_text_component_count": len(alt_components),
        }
        for m in matches:
            per_base[m["base_index"]]["successful_matches"].append({
                "setting": key,
                "alternative_component_id": m["alternative_component_id"],
                "iou": m["iou"],
                "centroid_distance": m["centroid_distance"],
            })

    stable_components = []
    base_output = []
    for rec in per_base:
        n = len(rec["successful_matches"])
        ious = [m["iou"] for m in rec["successful_matches"]]
        dists = [m["centroid_distance"] for m in rec["successful_matches"]]
        stable = n >= STABLE_MIN_ALTERNATIVES
        out_rec = {
            "component_id": rec["component_id"],
            "bbox": rec["bbox"],
            "centroid": rec["centroid"],
            "area": rec["area"],
            "successful_alternative_count": n,
            "stable": stable,
            "median_successful_iou": float(median(ious)) if ious else None,
            "median_successful_centroid_distance": float(median(dists)) if dists else None,
        }
        base_output.append(out_rec)
        if stable:
            stable_components.append(out_rec)

    stable_count = len(stable_components)
    stable_fraction = stable_count / len(base_components) if base_components else 0.0
    stable_median_ious = [c["median_successful_iou"] for c in stable_components if c["median_successful_iou"] is not None]
    page_median_iou = float(median(stable_median_ious)) if stable_median_ious else None

    gates = {
        "image_hash_matches_h76": image_hash == expected["image_sha256"],
        "base_reproduces_h76": all(reproduction.values()),
        "all_alternative_settings_have_at_least_10_low_text_candidates": alternative_counts_ok,
        "stable_component_count_at_least_15": stable_count >= 15,
        "stable_fraction_at_least_0_50": stable_fraction >= 0.50,
        "median_stable_component_median_iou_at_least_0_60": page_median_iou is not None and page_median_iou >= 0.60,
    }
    status = "PASS" if all(gates.values()) else "BLOCKED"

    result.update({
        "coordinate_box_count": len(boxes),
        "base_otsu_threshold": int(base_otsu),
        "h76_reproduction": reproduction,
        "settings": settings,
        "alternative_match_summaries": match_summaries,
        "base_low_text_components": base_output,
        "stable_component_count": stable_count,
        "stable_fraction": stable_fraction,
        "median_stable_component_median_iou": page_median_iou,
        "gates": gates,
        "status": status,
    })
    if status == "BLOCKED":
        result["reason"] = "preregistered visual-component stability gate failed"
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coords-f68r1", type=Path, required=True)
    ap.add_argument("--coords-f68r2", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    pages = {
        "f68r1": run_page("f68r1", args.coords_f68r1),
        "f68r2": run_page("f68r2", args.coords_f68r2),
    }
    overall = "PASS" if all(v.get("status") == "PASS" for v in pages.values()) else "BLOCKED"
    out = {
        "classification": "VISUAL_COMPONENT_PERTURBATION_STABILITY_NOT_SEMANTICS",
        "coordinate_source_revision": "c4d36f4595292c92da8c7428e30cb23b700a019b",
        "threshold_deltas": list(THRESHOLD_DELTAS),
        "mask_margins": list(MASK_MARGINS),
        "base_setting": {"threshold_delta": 0, "mask_margin": 3},
        "matching": {
            "iou_min": IOU_MIN,
            "centroid_distance_max_pixels": CENTROID_DISTANCE_MAX,
            "stable_min_alternatives": STABLE_MIN_ALTERNATIVES,
        },
        "pages": pages,
        "status": overall,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
