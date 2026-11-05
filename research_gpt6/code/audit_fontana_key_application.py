#!/usr/bin/env python3
"""Independent offline integrity audit of the known-key Fontana packet.

Checks frozen files, crop geometry, exact decoded pixels and review containers.
Does not recognize signs, interpret readings, compare historical references, or
import preparation/reading code. S01's absent original cannot be revalidated.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


CASE_IDS = ("T01", "T02")
SOURCE_IDS = ("S01", "S02")


class Checks:
    def __init__(self):
        self.count = 0
        self.mismatch_count = 0
        self.mismatches = []

    def check(self, name, actual, expected=True):
        self.count += 1
        if actual != expected:
            self.mismatch_count += 1
            if len(self.mismatches) < 50:
                def describe(value):
                    if isinstance(value, bytes):
                        return {"bytes": len(value), "sha256": sha(value)}
                    if isinstance(value, Path):
                        return value.name
                    return value
                self.mismatches.append({"check": name, "actual": describe(actual),
                                        "expected": describe(expected)})
        return actual == expected


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe(base, relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Input must be a safe relative path: " + str(relative))
    result = base / path
    if not result.resolve().is_relative_to(base.resolve()):
        raise ValueError("Input resolves outside its declared directory: " + str(relative))
    return result


def repo_file(repo, relative):
    parts = Path(relative).parts
    if parts and parts[0] == repo.name:
        parts = parts[1:]
    return safe(repo, Path(*parts))


def valid_dimensions(value):
    return (isinstance(value, list) and len(value) == 2 and
            all(type(x) is int and x > 0 for x in value))


def valid_box(box, dimensions):
    return (isinstance(box, list) and len(box) == 4 and
            all(type(x) is int for x in box) and valid_dimensions(dimensions) and
            0 <= box[0] < box[2] <= dimensions[0] and
            0 <= box[1] < box[3] <= dimensions[1])


def box_size(box):
    return [box[2] - box[0], box[3] - box[1]]


def rgb_hash(image):
    return sha(image.tobytes())


def image_input(path, key, hashes):
    with Image.open(path) as image:
        image.load()
        result = image.convert("RGB")
        mode, image_format = image.mode, image.format
    hashes["rgb:" + key] = rgb_hash(result)
    return result, mode, image_format


def indexed(rows, field, name, checks):
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        checks.check(name + "/list_of_objects", False)
        return {}
    checks.check(name + "/identifiers_present", all(field in row for row in rows))
    result = {row[field]: row for row in rows if field in row}
    checks.check(name + "/unique_identifiers", len(result), len(rows))
    return result


def review_records(bundle, checks, hashes):
    records = {}
    available = []
    for reviewer, filename in (("A", "a.json"), ("B", "b.json")):
        path = bundle / "reviews" / filename
        if not path.exists():
            continue
        available.append(reviewer)
        raw = path.read_bytes()
        hashes["reviews/" + filename] = sha(raw)
        review = json.loads(raw)
        prefix = "review/" + reviewer + "/"
        checks.check(prefix + "schema", review.get("schema"), "fontana-key-reading-v1")
        checks.check(prefix + "reviewer", review.get("reviewer"), reviewer)
        cases = indexed(review.get("cases"), "id", prefix + "cases", checks)
        checks.check(prefix + "case_set", sorted(cases), list(CASE_IDS))
        literals = {}
        for case_id in CASE_IDS:
            if case_id not in cases:
                continue
            case = cases[case_id]
            for field in ("literal", "notes"):
                checks.check(prefix + case_id + "/" + field + "_is_string",
                             isinstance(case.get(field), str))
            for field in ("units", "abbreviations"):
                checks.check(prefix + case_id + "/" + field + "_is_array",
                             isinstance(case.get(field), list))
            # Preserve the exact submitted string; no spelling normalization,
            # expansion, semantic scoring or comparison with a reference.
            literals[case_id] = case.get("literal")
        records[reviewer] = {"case_count": len(cases), "literals": literals}
    status = ("NOT_AVAILABLE" if not available else "RECORDS_CHECKED"
              if len(available) == 2 else "PARTIAL_RECORDS_CHECKED")
    return {"status": status, "reviewers_present": available,
            "reviewers_absent": [r for r in ("A", "B") if r not in available],
            "records": records,
            "scope": "Review container structure and verbatim literal strings only; "
                     "units, abbreviation assignments, readings and historical references are not interpreted or validated."}


def audit(repo, bundle):
    checks = Checks()
    hashes = {}
    result = {"schema": "fontana-key-application-integrity-v1",
              "scope": "Offline frozen-file, geometry, decoded-pixel and review-record integrity only. "
                       "PASS is not historical authentication, evidence of prior isolation, "
                       "paleographic validation, or successful reading.",
              "historical_authenticity_validated": False,
              "key_equivalences_validated": False,
              "expert_gold_accuracy_validated": False,
              "historical_reading_success_validated": False,
              "Voynich_translation_validated": False}
    try:
        packet_bytes = (bundle / "packet.json").read_bytes()
        freeze_bytes = (bundle / "pre_review_freeze.json").read_bytes()
        packet, freeze = json.loads(packet_bytes), json.loads(freeze_bytes)
        hashes.update({"packet.json": sha(packet_bytes), "pre_review_freeze.json": sha(freeze_bytes)})
        checks.check("packet/schema", packet.get("schema"), "fontana-key-application-packet-v1")
        checks.check("freeze/schema", freeze.get("schema"), "fontana-key-application-freeze-v1")
        checks.check("freeze/stage", freeze.get("stage"), "BEFORE_FRESH_READERS")
        cases = indexed(packet.get("cases"), "id", "packet/cases", checks)
        sources = indexed(packet.get("sources"), "id", "packet/sources", checks)
        checks.check("packet/case_set", sorted(cases), list(CASE_IDS))
        checks.check("packet/source_set", sorted(sources), list(SOURCE_IDS))

        frozen = indexed(freeze.get("files"), "path", "freeze/files", checks)
        required = {repo / "94_fontana_key_application_protocol.md", bundle / "NOTICE.md",
                    bundle / "packet.json", repo_file(repo, packet["key_file"])}
        for source in sources.values():
            for field in ("stored_tile", "stored_original"):
                if field in source:
                    required.add(safe(bundle, source[field]))
        for case in cases.values():
            required.update(safe(bundle, case[field]) for field in ("native", "display"))
        actual_frozen = {repo_file(repo, path) for path in frozen}
        checks.check("freeze/exact_required_file_set", sorted(str(p.relative_to(repo)) for p in actual_frozen),
                     sorted(str(p.relative_to(repo)) for p in required))
        for relative, record in sorted(frozen.items()):
            path = repo_file(repo, relative)
            exists = checks.check("freeze/" + relative + "/exists", path.is_file())
            if not exists:
                continue
            raw = path.read_bytes()
            actual_sha = sha(raw)
            hashes["file:" + str(path.relative_to(repo))] = actual_sha
            checks.check("freeze/" + relative + "/bytes", len(raw), record.get("bytes"))
            checks.check("freeze/" + relative + "/sha256", actual_sha, record.get("sha256"))
            git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
            checks.check("freeze/" + relative + "/git_blob", git_blob, record.get("git_blob"))

        key_path = repo_file(repo, packet["key_file"])
        checks.check("key/file_sha256", sha(key_path.read_bytes()), packet.get("key_sha256"))
        key_image, key_mode, key_format = image_input(key_path, "key", hashes)
        checks.check("key/format", key_format, "PNG")
        checks.check("key/mode", key_mode, "RGB")
        result["key"] = {"dimensions": list(key_image.size), "rgb_sha256": rgb_hash(key_image),
                         "scope": "Frozen key-image bytes and decoded pixels; not correctness of the printed key."}

        source_images, source_boxes, source_results = {}, {}, {}
        for source_id in SOURCE_IDS:
            source = sources[source_id]
            prefix = "source/" + source_id + "/"
            dimensions = source["original_dimensions"]
            checks.check(prefix + "original_dimensions_valid", valid_dimensions(dimensions))
            original_file_verified = False
            if source_id == "S01":
                path = safe(bundle, source["stored_tile"])
                box = source["stored_tile_original_bbox_xyxy"]
                checks.check(prefix + "tile_original_bounds", valid_box(box, dimensions))
                checks.check(prefix + "full_original_not_preserved_declaration",
                             source.get("full_original_preserved_in_this_bundle"), False)
                checks.check(prefix + "acquisition_pixel_receipt_present",
                             source.get("original_to_tile_pixels_verified_at_acquisition"), True)
            else:
                path = safe(bundle, source["stored_original"])
                box = [0, 0, *dimensions]
                original_file_verified = checks.check(prefix + "full_original_file_sha256",
                                                      sha(path.read_bytes()), source["original_sha256"])
            image, mode, image_format = image_input(path, source_id, hashes)
            checks.check(prefix + "mode", mode, "RGB")
            checks.check(prefix + "format", image_format, "PNG" if source_id == "S01" else "JPEG")
            checks.check(prefix + "stored_dimensions", list(image.size), box_size(box))
            source_images[source_id], source_boxes[source_id] = image, box
            source_results[source_id] = {
                "stored_dimensions": list(image.size), "rgb_sha256": rgb_hash(image),
                "recorded_original_sha256": source["original_sha256"],
                "full_original_file_verified": original_file_verified,
                "acquisition_receipt_only": source_id == "S01",
                "scope": ("Frozen native tile and acquisition declaration only; absent full S01 original is not revalidated."
                          if source_id == "S01" else
                          "Preserved complete scan bytes/pixels; a scan of an 1897 phototypy, not a new direct manuscript photograph.")}
        result["sources"] = source_results

        target_results = {}
        for case_id in CASE_IDS:
            case = cases[case_id]
            source_id = case["source_id"]
            prefix = "case/" + case_id + "/"
            checks.check(prefix + "source_id", source_id, "S02" if case_id == "T01" else "S01")
            source, origin = source_images[source_id], source_boxes[source_id]
            page_box, tile_box = case["original_bbox_xyxy"], case["stored_source_bbox_xyxy"]
            checks.check(prefix + "original_bounds", valid_box(page_box, sources[source_id]["original_dimensions"]))
            checks.check(prefix + "tile_bounds", valid_box(tile_box, list(source.size)))
            checks.check(prefix + "page_to_tile_translation", tile_box,
                         [page_box[0] - origin[0], page_box[1] - origin[1],
                          page_box[2] - origin[0], page_box[3] - origin[1]])
            checks.check(prefix + "stored_source_path", str(safe(bundle, case["stored_source"]).relative_to(bundle)),
                         str(safe(bundle, sources[source_id].get("stored_tile", sources[source_id].get("stored_original"))).relative_to(bundle)))
            native, mode, image_format = image_input(safe(bundle, case["native"]), case["native"], hashes)
            checks.check(prefix + "native_mode", mode, "RGB")
            checks.check(prefix + "native_format", image_format, "PNG")
            checks.check(prefix + "declared_native_dimensions", case["native_dimensions"], box_size(page_box))
            checks.check(prefix + "native_dimensions", list(native.size), box_size(tile_box))
            checks.check(prefix + "native_rgb_sha256", rgb_hash(native), case["native_rgb_sha256"])
            checks.check(prefix + "native_exact_tile_crop_pixels", native.tobytes(), source.crop(tile_box).tobytes())
            display, mode, image_format = image_input(safe(bundle, case["display"]), case["display"], hashes)
            checks.check(prefix + "display_mode", mode, "RGB")
            checks.check(prefix + "display_format", image_format, "PNG")
            scale = case["display_scale_integer"]
            good_scale = checks.check(prefix + "display_scale_positive_integer", type(scale) is int and scale > 0)
            if good_scale:
                dimensions = [native.width * scale, native.height * scale]
                checks.check(prefix + "display_dimensions", list(display.size), dimensions)
                # The frozen display is small. Do not allocate an arbitrary
                # enlargement if a malformed packet specifies excessive size.
                if list(display.size) == dimensions:
                    expected = native.resize(tuple(dimensions), Image.Resampling.NEAREST)
                    checks.check(prefix + "display_exact_integer_nearest_pixels", display.tobytes(), expected.tobytes())
            target_results[case_id] = {"source_id": source_id, "native_dimensions": list(native.size),
                                      "display_dimensions": list(display.size), "display_scale_integer": scale}
        result["targets"] = target_results
        result["counts"] = {"frozen_files": len(frozen), "sources": len(sources), "targets": len(cases)}
        result["reviews"] = review_records(bundle, checks, hashes)
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        # A malformed or absent input must produce FAIL, not an apparent pass
        # after silently dropping a required validation.
        detail = str(exc).replace(str(repo), "<repo>").replace(str(bundle), "<bundle>")
        checks.check("audit/required_input_processing", type(exc).__name__ + ": " + detail, "all required inputs processed")
    result.update({"status": "PASS" if checks.mismatch_count == 0 else "FAIL",
                   "checks": checks.count, "mismatch_count": checks.mismatch_count,
                   "mismatches": checks.mismatches,
                   "input_sha256": dict(sorted(hashes.items())),
                   "input_hash_scope": "Frozen files and JSON use byte hashes; rgb: entries hash decoded RGB pixel bytes. "
                                       "No remote originals are fetched and no historical transcription is scored."})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.repo.resolve(), args.bundle.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "checks", "mismatch_count")}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
