#!/usr/bin/env python3
"""H78 segmentation-free local visual-context stability gate.

Protocol: research_gpt6/98_h78_local_visual_context_stability_preregistration.md
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import urllib.request
from pathlib import Path
from statistics import median

import numpy as np
from PIL import Image
from scipy import ndimage

PAGES = ("f68r1", "f68r2")
IMAGE_URL = "http://www.voynichese.com/2/data/folio/image/glance/color/large/{page}.jpg"
EXPECTED = {
    "f68r1": {
        "sha256": "a7da74a67a4411dc95e650c270c76ffd1a323dc20f55dc9ab718e6344c263d11",
        "width": 636,
        "height": 900,
        "coordinate_box_count": 65,
    },
    "f68r2": {
        "sha256": "c8ac7f381499fca09cd5c5dd83dd26a0e07d66752d2a0390fb25878ddc1aee60",
        "width": 636,
        "height": 900,
        "coordinate_box_count": 81,
    },
}
RADII = (24, 32, 40)
MASK_MARGINS = (2, 3, 4)
BASE_SETTING = (32, 3)
MIN_VALID_PIXELS = 600
MIN_MEAN_GRADIENT = 4.0
MIN_COSINE = 0.90
MIN_SUCCESSFUL_ALTERNATIVES = 6


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_image(page: str):
    url = IMAGE_URL.format(page=page)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Voynich-H78/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
        image = Image.open(io.BytesIO(data)).convert("RGB")
        image.load()
        return url, data, image, None
    except Exception as exc:
        return url, None, None, f"{type(exc).__name__}: {exc}"


def load_boxes(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError("unexpected Yale coordinate JSON structure")
    rows = raw[1]
    out = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 5:
            continue
        index, x, y, w, h = row[:5]
        out.append({
            "source_index": int(index),
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
        })
    return out


def rect_inside(box, width, height):
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    return x >= 0 and y >= 0 and w >= 0 and h >= 0 and x + w <= width and y + h <= height


def apply_rect(mask, box, margin):
    height, width = mask.shape
    x0 = max(0, box["x"] - margin)
    y0 = max(0, box["y"] - margin)
    x1 = min(width, box["x"] + box["w"] + margin)
    y1 = min(height, box["y"] + box["h"] + margin)
    if x1 > x0 and y1 > y0:
        mask[y0:y1, x0:x1] = True


def gray_and_gradients(arr: np.ndarray):
    rgb = arr.astype(np.float64)
    gray = np.rint(0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]).clip(0, 255).astype(np.uint8)
    gray_f = gray.astype(np.float64)
    gx = ndimage.sobel(gray_f, axis=1, mode="reflect")
    gy = ndimage.sobel(gray_f, axis=0, mode="reflect")
    mag = np.hypot(gx, gy) / 8.0
    ori = np.mod(np.arctan2(gy, gx), math.pi)
    return gray, mag, ori


def normalized_hist(values, bins, weights=None):
    hist, _ = np.histogram(values, bins=bins, weights=weights)
    hist = hist.astype(np.float64)
    total = float(hist.sum())
    if total > 0:
        hist /= total
    return hist


def descriptor_for_anchor(box, radius, text_mask, gray, mag, ori):
    height, width = gray.shape
    x0 = max(0, box["x"] - radius)
    y0 = max(0, box["y"] - radius)
    x1 = min(width, box["x"] + box["w"] + radius)
    y1 = min(height, box["y"] + box["h"] + radius)
    valid = ~text_mask[y0:y1, x0:x1]
    n_valid = int(valid.sum())
    if n_valid < MIN_VALID_PIXELS:
        return {"valid": False, "valid_pixels": n_valid}

    g = gray[y0:y1, x0:x1][valid].astype(np.float64)
    m = mag[y0:y1, x0:x1][valid].astype(np.float64)
    o = ori[y0:y1, x0:x1][valid].astype(np.float64)

    gray_hist = normalized_hist(g, np.linspace(0.0, 256.0, 9))
    mag_hist = normalized_hist(m, np.array([0.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0, np.inf]))
    ori_hist = normalized_hist(o, np.linspace(0.0, math.pi, 9), weights=m)
    desc = np.concatenate([gray_hist, mag_hist, ori_hist])
    mean_gradient = float(m.mean()) if len(m) else 0.0
    return {
        "valid": True,
        "valid_pixels": n_valid,
        "mean_gradient": mean_gradient,
        "descriptor": desc,
    }


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def setting_key(radius, margin):
    return f"R{radius}_M{margin}"


def run_page(page: str, coords_path: Path):
    expected = EXPECTED[page]
    url, data, image, error = download_image(page)
    result = {"page": page, "image_url": url}
    if error:
        result.update({"status": "BLOCKED", "reason": "image acquisition/decoding failed", "error": error})
        return result

    digest = sha256_bytes(data)
    arr = np.asarray(image, dtype=np.uint8)
    height, width = arr.shape[:2]
    boxes = load_boxes(coords_path)
    inside = [b for b in boxes if rect_inside(b, width, height)]

    integrity = {
        "sha256_match": digest == expected["sha256"],
        "dimensions_match": width == expected["width"] and height == expected["height"],
        "coordinate_count_match": len(boxes) == expected["coordinate_box_count"],
        "all_coordinates_inside": len(inside) == len(boxes),
    }
    result.update({
        "image_sha256": digest,
        "width": int(width),
        "height": int(height),
        "coordinate_box_count": len(boxes),
        "coordinate_boxes_inside": len(inside),
        "integrity_gates": integrity,
    })
    if not all(integrity.values()):
        result.update({"status": "BLOCKED", "reason": "source/H76 reproduction gate failed"})
        return result

    gray, mag, ori = gray_and_gradients(arr)
    setting_records = {}
    per_setting_anchor = {}
    for radius in RADII:
        for margin in MASK_MARGINS:
            mask = np.zeros((height, width), dtype=bool)
            for box in boxes:
                apply_rect(mask, box, margin)
            key = setting_key(radius, margin)
            anchors = {}
            valid_count = 0
            signal_count = 0
            for i, box in enumerate(boxes):
                rec = descriptor_for_anchor(box, radius, mask, gray, mag, ori)
                if rec.get("valid"):
                    valid_count += 1
                    if rec.get("mean_gradient", 0.0) >= MIN_MEAN_GRADIENT:
                        signal_count += 1
                anchors[i] = rec
            per_setting_anchor[key] = anchors
            setting_records[key] = {
                "radius": radius,
                "text_mask_margin": margin,
                "valid_anchor_count": valid_count,
                "visual_signal_anchor_count": signal_count,
            }

    base_key = setting_key(*BASE_SETTING)
    base_records = per_setting_anchor[base_key]
    admitted_indices = [
        i for i, rec in base_records.items()
        if rec.get("valid") and rec.get("mean_gradient", 0.0) >= MIN_MEAN_GRADIENT
    ]

    challenge_keys = [k for k in setting_records if k != base_key]
    anchor_results = []
    stable_count = 0
    stable_medians = []
    for i in admitted_indices:
        base = base_records[i]
        sims = []
        successful = 0
        alternative_records = {}
        for key in challenge_keys:
            alt = per_setting_anchor[key][i]
            if alt.get("valid"):
                sim = cosine(base["descriptor"], alt["descriptor"])
                ok = sim >= MIN_COSINE
                if ok:
                    successful += 1
                    sims.append(sim)
                alternative_records[key] = {
                    "valid": True,
                    "valid_pixels": alt["valid_pixels"],
                    "cosine_to_base": sim,
                    "recovered": ok,
                }
            else:
                alternative_records[key] = {
                    "valid": False,
                    "valid_pixels": alt.get("valid_pixels", 0),
                    "recovered": False,
                }
        stable = successful >= MIN_SUCCESSFUL_ALTERNATIVES
        med_sim = float(median(sims)) if sims else None
        if stable:
            stable_count += 1
            if med_sim is not None:
                stable_medians.append(med_sim)
        box = boxes[i]
        anchor_results.append({
            "anchor_list_index": i,
            "source_index": box["source_index"],
            "bbox": [box["x"], box["y"], box["w"], box["h"]],
            "base_valid_pixels": base["valid_pixels"],
            "base_mean_gradient": base["mean_gradient"],
            "successful_alternative_count": successful,
            "stable": stable,
            "median_successful_cosine": med_sim,
            "alternatives": alternative_records,
        })

    admitted_count = len(admitted_indices)
    stable_fraction = stable_count / admitted_count if admitted_count else 0.0
    page_median_stable_cosine = float(median(stable_medians)) if stable_medians else None
    gates = {
        "base_admitted_anchors_at_least_15": admitted_count >= 15,
        "stable_anchors_at_least_10": stable_count >= 10,
        "stable_fraction_at_least_0_50": stable_fraction >= 0.50,
        "median_stable_cosine_at_least_0_93": page_median_stable_cosine is not None and page_median_stable_cosine >= 0.93,
    }
    status = "PASS" if all(gates.values()) else "BLOCKED"
    result.update({
        "base_setting": {"radius": BASE_SETTING[0], "text_mask_margin": BASE_SETTING[1]},
        "settings": setting_records,
        "base_admitted_anchor_count": admitted_count,
        "stable_anchor_count": stable_count,
        "stable_fraction": stable_fraction,
        "page_median_stable_anchor_median_cosine": page_median_stable_cosine,
        "gates": gates,
        "anchors": anchor_results,
        "status": status,
    })
    if status == "BLOCKED":
        result["reason"] = "local visual-context stability gate failed"
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
        "classification": "LOCAL_VISUAL_CONTEXT_STABILITY_NOT_SEMANTICS",
        "coordinate_source_revision": "c4d36f4595292c92da8c7428e30cb23b700a019b",
        "radii_pixels": list(RADII),
        "text_mask_margins_pixels": list(MASK_MARGINS),
        "base_setting": {"radius": BASE_SETTING[0], "text_mask_margin": BASE_SETTING[1]},
        "minimum_valid_pixels": MIN_VALID_PIXELS,
        "minimum_base_mean_gradient": MIN_MEAN_GRADIENT,
        "minimum_cosine": MIN_COSINE,
        "minimum_successful_alternatives": MIN_SUCCESSFUL_ALTERNATIVES,
        "pages": pages,
        "status": overall,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
