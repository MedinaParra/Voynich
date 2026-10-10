#!/usr/bin/env python3
import argparse
import hashlib
import io
import json
import urllib.request
from pathlib import Path
from statistics import median

import numpy as np
from PIL import Image
from scipy import ndimage

PAGES = ("f68r1", "f68r2")
IMAGE_URL = "http://www.voynichese.com/2/data/folio/image/glance/color/large/{page}.jpg"
MASK_MARGIN = 3
LOW_TEXT_OVERLAP_MAX = 0.10


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def otsu_threshold(gray_u8: np.ndarray) -> int:
    hist = np.bincount(gray_u8.ravel(), minlength=256).astype(np.float64)
    total = hist.sum()
    indices = np.arange(256, dtype=np.float64)
    sum_total = float((indices * hist).sum())
    sum_b = 0.0
    weight_b = 0.0
    max_var = -1.0
    threshold = 0
    for t in range(256):
        weight_b += hist[t]
        if weight_b == 0:
            continue
        weight_f = total - weight_b
        if weight_f == 0:
            break
        sum_b += t * hist[t]
        mean_b = sum_b / weight_b
        mean_f = (sum_total - sum_b) / weight_f
        between = weight_b * weight_f * (mean_b - mean_f) ** 2
        if between > max_var:
            max_var = between
            threshold = t
    return int(threshold)


def download_image(page: str):
    url = IMAGE_URL.format(page=page)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Voynich-H76/1.0"})
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
    boxes = raw[1]
    out = []
    for row in boxes:
        if not isinstance(row, list) or len(row) < 5:
            continue
        _, x, y, w, h = row[:5]
        out.append((int(x), int(y), int(w), int(h)))
    return out


def rect_inside(x, y, w, h, width, height):
    return x >= 0 and y >= 0 and w >= 0 and h >= 0 and x + w <= width and y + h <= height


def apply_rect(mask, x, y, w, h, margin=0):
    height, width = mask.shape
    x0 = max(0, x - margin)
    y0 = max(0, y - margin)
    x1 = min(width, x + w + margin)
    y1 = min(height, y + h + margin)
    if x1 > x0 and y1 > y0:
        mask[y0:y1, x0:x1] = True


def component_records(foreground: np.ndarray, original_text_mask: np.ndarray):
    structure = np.ones((3, 3), dtype=np.uint8)
    labels, n = ndimage.label(foreground, structure=structure)
    objects = ndimage.find_objects(labels)
    records = []
    for label_id, slc in enumerate(objects, 1):
        if slc is None:
            continue
        ys, xs = slc
        y0, y1 = ys.start, ys.stop
        x0, x1 = xs.start, xs.stop
        h, w = y1 - y0, x1 - x0
        component_mask = labels[ys, xs] == label_id
        area = int(component_mask.sum())
        touches_border = x0 == 0 or y0 == 0 or x1 == foreground.shape[1] or y1 == foreground.shape[0]
        admissible = (
            area >= 40 and
            w >= 5 and h >= 5 and
            w <= 160 and h <= 160 and
            not touches_border
        )
        if not admissible:
            continue
        coords = np.argwhere(component_mask)
        cy_local, cx_local = coords.mean(axis=0)
        bbox_area = w * h
        text_overlap_fraction = float(original_text_mask[y0:y1, x0:x1].sum() / bbox_area) if bbox_area else 1.0
        records.append({
            "component_id": int(label_id),
            "bbox": [int(x0), int(y0), int(w), int(h)],
            "area": area,
            "centroid": [float(x0 + cx_local), float(y0 + cy_local)],
            "text_bbox_overlap_fraction": text_overlap_fraction,
            "low_text_overlap": text_overlap_fraction <= LOW_TEXT_OVERLAP_MAX,
        })
    return int(n), records


def run_page(page: str, coords_path: Path):
    url, data, image, error = download_image(page)
    result = {"page": page, "image_url": url}
    if error:
        result.update({"status": "BLOCKED", "reason": "image acquisition/decoding failed", "error": error})
        return result

    arr = np.asarray(image, dtype=np.uint8)
    height, width = arr.shape[:2]
    boxes = load_boxes(coords_path)
    inside = sum(rect_inside(*b, width, height) for b in boxes)
    inside_fraction = inside / len(boxes) if boxes else 0.0

    result.update({
        "image_sha256": sha256_bytes(data),
        "width": int(width),
        "height": int(height),
        "coordinate_box_count": len(boxes),
        "coordinate_boxes_fully_inside": int(inside),
        "coordinate_inside_fraction": inside_fraction,
    })

    coordinate_gate = width >= 500 and height >= 700 and inside_fraction >= 0.95
    if not coordinate_gate:
        result.update({"status": "BLOCKED", "reason": "coordinate compatibility gate failed"})
        return result

    original_text_mask = np.zeros((height, width), dtype=bool)
    expanded_text_mask = np.zeros((height, width), dtype=bool)
    for b in boxes:
        apply_rect(original_text_mask, *b, margin=0)
        apply_rect(expanded_text_mask, *b, margin=MASK_MARGIN)

    rgb = arr.astype(np.float64)
    gray = np.rint(0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]).clip(0, 255).astype(np.uint8)
    threshold = otsu_threshold(gray)
    foreground = gray < threshold
    foreground[expanded_text_mask] = False

    all_count, components = component_records(foreground, original_text_mask)
    low = [c for c in components if c["low_text_overlap"]]
    low_fraction = len(low) / len(components) if components else 0.0
    med_area = float(median([c["area"] for c in low])) if low else None

    gates = {
        "candidate_count_at_least_15": len(low) >= 15,
        "low_text_overlap_fraction_at_least_0_80": low_fraction >= 0.80,
        "median_low_text_overlap_area_at_least_60": med_area is not None and med_area >= 60.0,
    }
    status = "PASS" if all(gates.values()) else "BLOCKED"
    result.update({
        "otsu_threshold": threshold,
        "foreground_pixels_after_text_mask": int(foreground.sum()),
        "all_connected_component_count": all_count,
        "admissible_component_count": len(components),
        "low_text_overlap_component_count": len(low),
        "low_text_overlap_fraction": low_fraction,
        "median_low_text_overlap_component_area": med_area,
        "gates": gates,
        "components": components,
        "status": status,
    })
    if status == "BLOCKED":
        result["reason"] = "visual-candidate adequacy gate failed"
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
        "classification": "BLIND_VISUAL_OBJECT_EXTRACTION_ADMISSIBILITY_NOT_SEMANTICS",
        "coordinate_source_revision": "c4d36f4595292c92da8c7428e30cb23b700a019b",
        "mask_margin_pixels": MASK_MARGIN,
        "low_text_overlap_max": LOW_TEXT_OVERLAP_MAX,
        "pages": pages,
        "status": overall,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
