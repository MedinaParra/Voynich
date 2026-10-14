#!/usr/bin/env python3
"""Pinned, non-training Kraken layout pilot. Count proxies are not OCR accuracy."""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib.metadata as metadata
import io
import json
import os
import platform
import random
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw
from scipy.optimize import linear_sum_assignment


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def bbox_iou(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0., x1 - x0) * max(0., y1 - y0)
    area_a = max(0., a[2] - a[0]) * max(0., a[3] - a[1])
    area_b = max(0., b[2] - b[0]) * max(0., b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union else 0.


def match_boxes(pred, truth, threshold=0.5):
    if not 0 < threshold <= 1:
        raise ValueError("IoU threshold must be in (0, 1]")
    matches = []
    if pred and truth:
        matrix = np.array([[bbox_iou(a, b) for b in truth] for a in pred])
        # Maximize eligible cardinality first, then IoU. Duplicates cannot
        # claim the same truth line or inflate recall.
        score = (matrix >= threshold) * (min(len(pred), len(truth)) + 1) + matrix
        rows, cols = linear_sum_assignment(-score)
        matches = [{"pred": int(i), "truth": int(j), "iou": float(matrix[i, j])}
                   for i, j in zip(rows, cols) if matrix[i, j] >= threshold]
    tp = len(matches)
    precision = tp / len(pred) if pred else (1. if not truth else 0.)
    recall = tp / len(truth) if truth else (1. if not pred else 0.)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.
    return {"tp": tp, "fp": len(pred) - tp, "fn": len(truth) - tp,
            "precision": precision, "recall": recall, "f1": f1,
            "iou_threshold": threshold, "pairs": matches,
            "pred_count": len(pred), "truth_count": len(truth)}


def boxer_rows(data, folios):
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    out = {f: [] for f in folios}
    seen = set()
    for row in rows:
        f = row.get("folio", "").strip()
        if f not in out:
            continue
        par, line = int(row["par"]), int(row["line"])
        key = (f, par, line)
        if key in seen:
            raise ValueError("Duplicate physical line in Boxer CSV: " + repr(key))
        seen.add(key)
        tokens = [row[k] for k in row if k and k.startswith("t") and k[1:].isdigit()
                  and row[k] and row[k] != "$"]
        if tokens:
            out[f].append({"folio": f, "paragraph": par, "line": line, "tokens": tokens})
    for f in folios:
        if not out[f]:
            raise ValueError("No block-text reference rows for " + f)
    return out


def page_truth(data):
    root = ET.fromstring(data)
    page = next(e for e in root.iter() if e.tag.rsplit("}", 1)[-1] == "Page")
    w, h = int(page.attrib["imageWidth"]), int(page.attrib["imageHeight"])
    if min(w, h) <= 0:
        raise ValueError("Invalid PAGE-XML dimensions")
    boxes = []
    for elem in root.iter():
        if elem.tag.rsplit("}", 1)[-1] != "TextLine":
            continue
        coords = next((e for e in elem if e.tag.rsplit("}", 1)[-1] == "Coords"), None)
        if coords is None or not coords.attrib.get("points"):
            raise ValueError("Annotated TextLine has no geometry")
        points = [[float(v) for v in xy.split(",")] for xy in coords.attrib["points"].split()]
        xs, ys = zip(*points)
        boxes.append([min(xs)/w, min(ys)/h, max(xs)/w, max(ys)/h])
    if not boxes:
        raise ValueError("PAGE-XML has no annotated text lines")
    return boxes, (w, h)


def serialize_lines(seg, size):
    w, h = size
    records = []
    for idx, line in enumerate(seg.lines or []):
        boundary = getattr(line, "boundary", None)
        baseline = getattr(line, "baseline", None)
        box = getattr(line, "bbox", None)
        if box is None:
            if not boundary:
                raise ValueError("Detected baseline has no boundary")
            xs, ys = zip(*boundary)
            box = [min(xs), min(ys), max(xs), max(ys)]
        box = [float(x) for x in box]
        if not np.isfinite(box).all() or box[2] <= box[0] or box[3] <= box[1]:
            raise ValueError("Invalid detected line box")
        records.append({
            "index": idx, "bbox_pixels": box,
            "bbox_normalized": [box[0]/w, box[1]/h, box[2]/w, box[3]/h],
            "boundary": [[float(x), float(y)] for x, y in boundary] if boundary else None,
            "baseline": [[float(x), float(y)] for x, y in baseline] if baseline else None,
        })
    return records


def fetch_bytes(url, dest, acquired, expected_blob=None):
    response = None
    for attempt in range(2):
        try:
            response = requests.get(url, timeout=(10, 50),
                                    headers={"User-Agent": "Voynich-Kraken-research-pilot/1.0"})
            if response.status_code in (429, 500, 502, 503, 504) and attempt == 0:
                time.sleep(2)
                continue
            response.raise_for_status()
            break
        except requests.RequestException:
            if response is not None and response.status_code < 500 and response.status_code != 429:
                raise
            if attempt:
                raise
            time.sleep(2)
    data = response.content
    got = git_blob_sha(data)
    if expected_blob and got != expected_blob:
        raise ValueError("Frozen source blob mismatch: " + url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    acquired.append({"url": url, "final_url": response.url, "http_status": response.status_code,
                     "bytes": len(data), "sha256": sha256(data), "git_blob_sha": got,
                     "local": str(dest), "content_type": response.headers.get("Content-Type")})
    return data


def resized(im, width):
    height = max(1, round(im.height * width / im.width))
    return im.resize((width, height), Image.Resampling.LANCZOS)


def count_loss(records, expected, method, width):
    selected = {r["folio"]: r for r in records
                if r["method"] == method and r["width"] == width and r["status"] == "EXECUTED"}
    if set(selected) != set(expected):
        return None
    total = sum(expected.values())
    errors = {f: abs(selected[f]["line_count"] - expected[f]) for f in expected}
    return {"absolute_errors": errors, "total_reference_lines": total,
            "sum_absolute_error": sum(errors.values()),
            "relative_absolute_count_error": sum(errors.values()) / total}


def proxy_gate(result, plan):
    expected = {p["folio"]: p["expected_boxer_lines"] for p in plan["pages"]}
    methods = plan["methods"]
    primary = plan["widths"]["primary"]
    robust = plan["widths"]["robustness"]
    for method in methods:
        for width in (primary, robust):
            rows = [r for r in result["cases"] if r["method"] == method and r["width"] == width
                    and r["status"] == "EXECUTED"]
            if {r["folio"] for r in rows} != set(expected) or len(rows) != len(expected):
                return "BLOCKED_DATA_OR_RUNTIME"
    blanks = result.get("blank_controls", {})
    if any(m not in blanks or blanks[m].get("status") not in ("EXECUTED", "REJECTED_EMPTY_IMAGE")
           for m in methods):
        return "BLOCKED_DATA_OR_RUNTIME"
    neural = count_loss(result["cases"], expected, methods[0], primary)
    stable = all(x["absolute_count_change"] <= plan["gates"]["max_line_count_change_each_page"]
                 for x in result["robustness"] if x["method"] == methods[0])
    if len([x for x in result["robustness"] if x["method"] == methods[0]]) != len(expected):
        return "BLOCKED_DATA_OR_RUNTIME"
    passed = (neural["relative_absolute_count_error"] <= plan["gates"]["count_proxy_max_loss"]
              and stable and blanks[methods[0]].get("line_count") == 0)
    return "PASS_COUNT_PROXY_ONLY" if passed else "FAIL_COUNT_PROXY"


def overlay(im, lines):
    out = im.convert("RGB").copy()
    draw = ImageDraw.Draw(out)
    for line in lines:
        if line["boundary"]:
            pts = [tuple(p) for p in line["boundary"]]
            draw.line(pts + [pts[0]], fill="#d52b49", width=3)
        else:
            draw.rectangle(line["bbox_pixels"], outline="#d52b49", width=3)
        if line["baseline"]:
            draw.line([tuple(p) for p in line["baseline"]], fill="#007d9a", width=3)
    return out


def emit_result(result, out):
    result_path = out / "kraken_pilot_result.json"
    text = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result_path.write_text(text + "\n")
    summary = {"status": result["status"], "execution_commit": result.get("execution_commit"),
               "plan_sha256": result.get("plan_sha256"), "count_metrics": result.get("count_metrics"),
               "comparison": result.get("comparison"), "blank_controls": result.get("blank_controls"),
               "positive_control": result.get("positive_control"),
               "case_counts": [{"folio": r["folio"], "method": r["method"], "width": r["width"],
                                "status": r["status"], "lines": r.get("line_count")}
                               for r in result["cases"]],
               "robustness": result.get("robustness"), "failures": result["failures"],
               "recognition": result["recognition"], "translation": result["translation"],
               "training": result["training"]}
    (out / "kraken_pilot_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    (out / "sha256_manifest.json").write_text(json.dumps(
        {str(p.relative_to(out)): sha256(p.read_bytes()) for p in sorted(out.rglob("*"))
         if p.is_file() and p.name != "sha256_manifest.json"}, indent=2) + "\n")
    print("KRAKEN_SUMMARY_JSON=" + json.dumps(summary, ensure_ascii=False, separators=(",", ":")), flush=True)
    print("KRAKEN_RESULT_SHA256=" + sha256(result_path.read_bytes()), flush=True)
    print("KRAKEN_RESULT_JSON=" + text, flush=True)
    for folio in ("1r", "1v"):
        path = out / "overlays" / (folio + "_default_neural_baselines_1800.jpg")
        if path.exists():
            with Image.open(path) as im:
                preview = resized(im, 750)
                buf = io.BytesIO()
                preview.save(buf, format="JPEG", quality=65, optimize=True)
            print("KRAKEN_PREVIEW_" + folio.upper() + "_JPEG_BASE64=" +
                  base64.b64encode(buf.getvalue()).decode(), flush=True)


def run(plan_path, out):
    out.mkdir(parents=True, exist_ok=True)
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    result = {"schema_version": 1, "experiment": plan["experiment"], "status": "BLOCKED_DATA_OR_RUNTIME",
              "execution_commit": os.environ.get("GITHUB_SHA"), "run_id": os.environ.get("GITHUB_RUN_ID"),
              "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"), "plan_sha256": sha256(plan_bytes),
              "code_sha256": sha256(Path(__file__).read_bytes()), "started_unix": time.time(),
              "recognition": plan["recognition"], "translation": plan["translation"],
              "training": plan["training"], "cases": [], "failures": [], "acquired": [],
              "count_metrics": {}, "robustness": [], "blank_controls": {}}
    started = time.perf_counter()
    try:
        import torch
        from importlib import resources
        from kraken import blla, binarization, pageseg
        from kraken.lib.vgsl import TorchVGSLModel
        from packaging.version import Version

        if Version(metadata.version("kraken")) != Version(plan["kraken"]["release"]):
            raise ValueError("Installed Kraken differs from pinned version")
        random.seed(plan["runtime"]["seed"])
        np.random.seed(plan["runtime"]["seed"])
        torch.manual_seed(plan["runtime"]["seed"])
        torch.set_num_threads(plan["runtime"]["threads"])
        result["environment"] = {
            "python": platform.python_version(), "platform": platform.platform(), "device": "cpu",
            "torch": torch.__version__, "torch_threads": torch.get_num_threads(),
            "packages": {d.metadata["Name"]: d.version for d in metadata.distributions()
                         if d.metadata.get("Name")},
            "cuda_used": False,
        }
        model_path = Path(str(resources.files("kraken").joinpath("blla.mlmodel")))
        model_data = model_path.read_bytes()
        if git_blob_sha(model_data) != plan["kraken"]["segmentation_model"]["git_blob_sha"]:
            raise ValueError("Bundled default segmentation model differs from fixed upstream blob")
        result["model"] = {"path": str(model_path), "bytes": len(model_data),
                           "sha256": sha256(model_data), "git_blob_sha": git_blob_sha(model_data)}
        net = TorchVGSLModel.load_model(str(model_path))

        def segment_case(im, method, label, width, allow_blank=False):
            tick = time.perf_counter()
            try:
                if method == "default_neural_baselines":
                    seg = blla.segment(im, model=net, device="cpu", raise_on_error=True)
                elif method == "legacy_boxes_nlbin":
                    seg = pageseg.segment(binarization.nlbin(im))
                else:
                    raise ValueError("Unrecognized method")
                lines = serialize_lines(seg, im.size)
                return {"folio": label, "method": method, "width": width,
                        "image_size": list(im.size), "status": "EXECUTED",
                        "line_count": len(lines), "lines": lines,
                        "seconds": time.perf_counter() - tick}
            except Exception as exc:
                empty = (allow_blank and method == "legacy_boxes_nlbin"
                         and type(exc).__name__ == "KrakenInputException"
                         and "empty" in str(exc).lower())
                return {"folio": label, "method": method, "width": width,
                        "image_size": list(im.size),
                        "status": "REJECTED_EMPTY_IMAGE" if empty else "BLOCKED",
                        "line_count": 0 if empty else None, "lines": [],
                        "error": type(exc).__name__ + ": " + str(exc),
                        "seconds": time.perf_counter() - tick}

        src = plan["sources"]["boxer"]
        url = ("https://raw.githubusercontent.com/" + src["repository"] + "/" +
               src["commit"] + "/" + src["path"])
        raw = fetch_bytes(url, out / "sources/boxer_vms.csv", result["acquired"], src["git_blob_sha"])
        refs = boxer_rows(raw, [p["folio"] for p in plan["pages"]])
        result["boxer_reference_counts"] = {f: len(rows) for f, rows in refs.items()}
        if result["boxer_reference_counts"] != {p["folio"]: p["expected_boxer_lines"] for p in plan["pages"]}:
            raise ValueError("Independent transcript counts differ from preregistration")
        (out / "sources/boxer_selected_lines.json").write_text(json.dumps(refs, ensure_ascii=False, indent=2))

        mapping = plan["sources"]["image_mapping"]
        mapping_url = ("https://raw.githubusercontent.com/" + mapping["repository"] + "/" +
                       mapping["commit"] + "/" + mapping["path"])
        map_data = fetch_bytes(mapping_url, out / "sources/image_mapping.csv",
                               result["acquired"], mapping["git_blob_sha"])
        map_rows = list(csv.DictReader(io.StringIO(map_data.decode())))
        for p in plan["pages"]:
            candidates = [r for r in map_rows if r["folio"] == p["folio"]]
            if len(candidates) != 1 or candidates[0]["image_service_url"] != p["service_url"]:
                raise ValueError("Frozen image mapping disagrees for " + p["folio"])

        for p in plan["pages"]:
            folio = p["folio"]
            try:
                image_url = p["service_url"] + "/full/" + str(plan["widths"]["primary"]) + ",/0/default.jpg"
                data = fetch_bytes(image_url, out / ("images/" + folio + ".jpg"), result["acquired"])
                with Image.open(io.BytesIO(data)) as source:
                    original = source.convert("RGB")
                if abs(original.width - plan["widths"]["primary"]) > 2:
                    raise ValueError("Unexpected IIIF requested width")
                for width in plan["widths"].values():
                    im = resized(original, width)
                    for method in plan["methods"]:
                        case = segment_case(im, method, folio, width)
                        result["cases"].append(case)
                        print("KRAKEN_CASE_JSON=" + json.dumps({k:v for k,v in case.items()
                              if k != "lines"}, separators=(",", ":")), flush=True)
                        if case["status"] == "EXECUTED":
                            path = out / "overlays" / (folio + "_" + method + "_" + str(width) + ".jpg")
                            path.parent.mkdir(exist_ok=True)
                            overlay(im, case["lines"]).save(path, quality=85)
                        else:
                            result["failures"].append({"phase": "segmentation", "folio": folio,
                                                       "method": method, "width": width,
                                                       "error": case["error"]})
            except Exception as exc:
                result["failures"].append({"phase": "image", "folio": folio,
                                           "error": type(exc).__name__ + ": " + str(exc)})

        blank = Image.new("L", (1000, 1400), 255)
        for method in plan["methods"]:
            b = segment_case(blank, method, "blank", 1000, allow_blank=True)
            result["blank_controls"][method] = {k:v for k,v in b.items() if k != "lines"}

        positive = plan["sources"]["positive"]
        try:
            root = "https://raw.githubusercontent.com/mittagessen/kraken/" + positive["upstream_commit"] + "/"
            jpg = fetch_bytes(root + positive["image_path"], out / "control/positive.jpg",
                              result["acquired"], positive["image_blob_sha"])
            xml = fetch_bytes(root + positive["xml_path"], out / "control/positive.xml",
                              result["acquired"], positive["xml_blob_sha"])
            truth, xml_size = page_truth(xml)
            with Image.open(io.BytesIO(jpg)) as source:
                raw_im = source.convert("RGB")
            ratio_error = abs((raw_im.width/raw_im.height)/(xml_size[0]/xml_size[1]) - 1)
            if ratio_error > 0.02:
                raise ValueError("Positive-control image/XML aspect mismatch")
            im = resized(raw_im, plan["widths"]["primary"])
            result["positive_control"] = {"status": "EXECUTED", "xml_dimensions": list(xml_size),
                                          "source_image_dimensions": list(raw_im.size),
                                          "aspect_relative_error": ratio_error,
                                          "truth_boxes": truth, "methods": {}}
            for method in plan["methods"]:
                r = segment_case(im, method, "positive", im.width)
                entry = {"status": r["status"], "line_count": r["line_count"], "lines": r["lines"],
                         "seconds": r["seconds"]}
                if r["status"] == "EXECUTED":
                    entry["matching"] = match_boxes([x["bbox_normalized"] for x in r["lines"]], truth)
                    overlay(im, r["lines"]).save(out / ("control/" + method + ".jpg"), quality=85)
                else:
                    entry["error"] = r["error"]
                result["positive_control"]["methods"][method] = entry
        except Exception as exc:
            result["positive_control"] = {"status": "BLOCKED", "error": type(exc).__name__ + ": " + str(exc)}
            result["failures"].append({"phase": "positive_control", "error": str(exc)})

        expected = result["boxer_reference_counts"]
        primary = plan["widths"]["primary"]
        for method in plan["methods"]:
            result["count_metrics"][method] = count_loss(result["cases"], expected, method, primary)
            for p in plan["pages"]:
                pair = [next((r for r in result["cases"] if r["folio"] == p["folio"]
                              and r["method"] == method and r["width"] == width
                              and r["status"] == "EXECUTED"), None)
                        for width in plan["widths"].values()]
                if all(pair):
                    stability = match_boxes([x["bbox_normalized"] for x in pair[0]["lines"]],
                                            [x["bbox_normalized"] for x in pair[1]["lines"]])
                    result["robustness"].append({"folio": p["folio"], "method": method,
                        "absolute_count_change": abs(pair[0]["line_count"] - pair[1]["line_count"]),
                        "cross_resolution_box_f1": stability["f1"], "matching": stability})
        metrics = [result["count_metrics"].get(m) for m in plan["methods"]]
        if all(metrics):
            result["comparison"] = {"neural_minus_legacy_count_loss":
                metrics[0]["relative_absolute_count_error"] - metrics[1]["relative_absolute_count_error"],
                "scope": "Descriptive count comparison; not a significance test or CER."}
        result["status"] = proxy_gate(result, plan)
    except Exception as exc:
        result["status"] = "BLOCKED_DATA_OR_RUNTIME"
        result["failures"].append({"phase": "initialization", "error": type(exc).__name__ + ": " + str(exc),
                                   "traceback": traceback.format_exc()})
    result["duration_seconds"] = time.perf_counter() - started
    emit_result(result, out)
    return 2 if result["status"] == "BLOCKED_DATA_OR_RUNTIME" else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    sys.exit(run(args.plan, args.out))
