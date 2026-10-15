#!/usr/bin/env python3
"""H84 preregistered IT↔GC structural transcription-disagreement challenge.

Implements research_gpt6/109_h84_it_gc_label_transcription_disagreement_preregistration.md.
No semantic inference, fuzzy locus alignment, or post-result tuning is performed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Sequence

EXPECTED_SHA256 = {
    "IT": "db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee",
    "GC": "b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f",
}
PAIRING_SEED = 20261016
PERMUTATION_SEED = 20261017
PERMUTATIONS = 9_999
MIN_PAIRS = 60
MIN_FOLIOS = 8
SENSITIVITY_MIN_PAIRS = 30
SENSITIVITY_MIN_FOLIOS = 6


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def known_tokens(payload: str) -> list[str]:
    """Conservative H70-compatible token extraction."""
    text = re.sub(r"<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;", " ", payload)
    pieces = re.split(r"[.\s]+", text)
    out: list[str] = []
    for piece in pieces:
        piece = piece.strip()
        if not piece or "?" in piece:
            continue
        runs = re.findall(r"[A-Za-z0-9]+", piece)
        if len(runs) == 1 and runs[0]:
            out.append(runs[0])
    return out


def parse_records(data: bytes) -> dict[tuple[str, int], dict[str, object]]:
    """Parse exact manuscript locus records using the H70 convention."""
    text = data.decode("utf-8", errors="strict")
    records: dict[tuple[str, int], dict[str, object]] = {}
    page_meta: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        page_header = re.match(r"^<(f\d+[rv]\d*)>\s*<!([^>]*)>", line)
        if page_header:
            metadata = dict(re.findall(r"\$([A-Z])=([^\s>]+)", page_header.group(2)))
            page_meta[page_header.group(1)] = {
                "Q": metadata.get("Q", "?"),
                "L": metadata.get("L", "?"),
                "H": metadata.get("H", "?"),
            }
            continue
        locus = re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$", line)
        if not locus:
            continue
        folio, number, locator, payload = locus.groups()
        key = (folio, int(number))
        records[key] = {
            "folio": folio,
            "number": int(number),
            "locator": locator,
            "payload": payload,
            "tokens": known_tokens(payload),
            "meta": page_meta.get(folio, {"Q": "?", "L": "?", "H": "?"}),
        }
    return records


def generic_locus_type(locator: str) -> str | None:
    """Return only the frozen generic L or P status from the IT locator."""
    loc = re.sub(r"^[@+*=]", "", locator.strip())
    if loc.startswith("L"):
        return "L"
    if loc.startswith("P"):
        return "P"
    return None


def canonical_pattern(token: str) -> tuple[int, ...]:
    mapping: dict[str, int] = {}
    next_id = 0
    pattern: list[int] = []
    for symbol in token:
        if symbol not in mapping:
            mapping[symbol] = next_id
            next_id += 1
        pattern.append(mapping[symbol])
    return tuple(pattern)


def levenshtein(left: Sequence[int], right: Sequence[int]) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[j] + 1,
                    previous[j - 1] + (a != b),
                )
            )
        previous = current
    return previous[-1]


def disagreement(it_token: str, gc_token: str) -> float:
    a = canonical_pattern(it_token)
    b = canonical_pattern(gc_token)
    denominator = max(len(a), len(b), 1)
    return levenshtein(a, b) / denominator


def mean_or_none(values: Iterable[float]) -> float | None:
    values = list(values)
    return statistics.mean(values) if values else None


def median_or_none(values: Iterable[float]) -> float | None:
    values = list(values)
    return statistics.median(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--it", type=Path, required=True)
    parser.add_argument("--gc", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    raw = {"IT": args.it.read_bytes(), "GC": args.gc.read_bytes()}
    observed_hashes = {name: sha256(data) for name, data in raw.items()}
    result: dict[str, object] = {
        "classification": "IT_GC_STRUCTURAL_TRANSCRIPTION_DISAGREEMENT_LABEL_VS_PARAGRAPH_NOT_SEMANTICS",
        "source": {
            "repository": "noah-chelednik/voynich-data",
            "revision": "472ef7366606a799fc8f1044c037e06b413f6ddd",
            "sha256": observed_hashes,
            "expected_sha256": EXPECTED_SHA256,
        },
        "parameters": {
            "pairing_seed": PAIRING_SEED,
            "permutation_seed": PERMUTATION_SEED,
            "permutations_requested": PERMUTATIONS,
            "min_pairs": MIN_PAIRS,
            "min_folios": MIN_FOLIOS,
        },
    }

    bad_hashes = [name for name in EXPECTED_SHA256 if observed_hashes[name] != EXPECTED_SHA256[name]]
    if bad_hashes:
        result.update({"status": "BLOCKED", "reason": "frozen source hash mismatch", "mismatched_sources": bad_hashes})
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    parsed_it = parse_records(raw["IT"])
    parsed_gc = parse_records(raw["GC"])

    eligible: dict[str, list[dict[str, object]]] = {"L": [], "P": []}
    exact_locus_present = {"L": 0, "P": 0}
    for key, it_record in parsed_it.items():
        locus_type = generic_locus_type(str(it_record["locator"]))
        if locus_type not in {"L", "P"}:
            continue
        gc_record = parsed_gc.get(key)
        if gc_record is None:
            continue
        exact_locus_present[locus_type] += 1
        it_tokens = list(it_record["tokens"])  # type: ignore[arg-type]
        gc_tokens = list(gc_record["tokens"])  # type: ignore[arg-type]
        if len(it_tokens) != 1 or len(gc_tokens) != 1:
            continue
        it_token = str(it_tokens[0])
        gc_token = str(gc_tokens[0])
        row = {
            "key": key,
            "folio": key[0],
            "number": key[1],
            "it_token": it_token,
            "gc_token": gc_token,
            "it_length": len(it_token),
            "gc_length": len(gc_token),
            "D": disagreement(it_token, gc_token),
        }
        eligible[locus_type].append(row)

    result["coverage"] = {
        "exact_locus_present": exact_locus_present,
        "single_token_mappable": {kind: len(rows) for kind, rows in eligible.items()},
        "single_token_mappable_folios": {
            kind: len({str(row["folio"]) for row in rows}) for kind, rows in eligible.items()
        },
    }

    # Frozen control matching: same folio and IT token length, without replacement.
    pools: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in eligible["P"]:
        pools[(str(row["folio"]), int(row["it_length"]))].append(row)

    rng_pair = random.Random(PAIRING_SEED)
    for stratum in sorted(pools):
        pools[stratum].sort(key=lambda row: int(row["number"]))
        rng_pair.shuffle(pools[stratum])

    pool_cursor: dict[tuple[str, int], int] = defaultdict(int)
    pairs: list[dict[str, object]] = []
    unmatched_labels = 0
    for label in sorted(eligible["L"], key=lambda row: (str(row["folio"]), int(row["number"]))):
        stratum = (str(label["folio"]), int(label["it_length"]))
        cursor = pool_cursor[stratum]
        controls = pools.get(stratum, [])
        if cursor >= len(controls):
            unmatched_labels += 1
            continue
        control = controls[cursor]
        pool_cursor[stratum] = cursor + 1
        delta = float(label["D"]) - float(control["D"])
        pairs.append(
            {
                "folio": label["folio"],
                "it_length": label["it_length"],
                "label_locus_number": label["number"],
                "paragraph_locus_number": control["number"],
                "label_D": label["D"],
                "paragraph_D": control["D"],
                "delta": delta,
                "label_gc_length": label["gc_length"],
                "paragraph_gc_length": control["gc_length"],
                "label_abs_length_difference": abs(int(label["it_length"]) - int(label["gc_length"])),
                "paragraph_abs_length_difference": abs(int(control["it_length"]) - int(control["gc_length"])),
            }
        )

    represented_folios = sorted({str(pair["folio"]) for pair in pairs})
    sample_gates = {
        "matched_pairs_at_least_60": len(pairs) >= MIN_PAIRS,
        "represented_folios_at_least_8": len(represented_folios) >= MIN_FOLIOS,
    }
    result["matching"] = {
        "matched_pairs": len(pairs),
        "represented_folios": len(represented_folios),
        "folio_ids": represented_folios,
        "unmatched_labels_no_unused_exact_control": unmatched_labels,
        "sample_gates": sample_gates,
    }

    if not all(sample_gates.values()):
        result.update({"status": "BLOCKED", "reason": "preregistered matched-sample gate failed"})
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    label_d = [float(pair["label_D"]) for pair in pairs]
    paragraph_d = [float(pair["paragraph_D"]) for pair in pairs]
    deltas = [float(pair["delta"]) for pair in pairs]
    observed_delta = statistics.mean(deltas)

    by_folio: dict[str, list[float]] = defaultdict(list)
    for pair in pairs:
        by_folio[str(pair["folio"])].append(float(pair["delta"]))

    result["observed"] = {
        "label_mean_D": statistics.mean(label_d),
        "label_median_D": statistics.median(label_d),
        "paragraph_mean_D": statistics.mean(paragraph_d),
        "paragraph_median_D": statistics.median(paragraph_d),
        "Delta": observed_delta,
        "label_exact_pattern_agreement_fraction": sum(value == 0 for value in label_d) / len(label_d),
        "paragraph_exact_pattern_agreement_fraction": sum(value == 0 for value in paragraph_d) / len(paragraph_d),
        "by_folio_mean_delta": {folio: statistics.mean(values) for folio, values in sorted(by_folio.items())},
    }

    rng_null = random.Random(PERMUTATION_SEED)
    null: list[float] = []
    for _ in range(PERMUTATIONS):
        signed = [delta if rng_null.getrandbits(1) else -delta for delta in deltas]
        null.append(statistics.mean(signed))
    p_upper = (1 + sum(value >= observed_delta for value in null)) / (PERMUTATIONS + 1)
    result["null"] = {
        "permutations_requested": PERMUTATIONS,
        "permutations_completed": len(null),
        "seed": PERMUTATION_SEED,
        "null_mean_Delta": statistics.mean(null),
        "null_sd_Delta": statistics.pstdev(null),
        "p_upper": p_upper,
    }

    label_len_diff = [float(pair["label_abs_length_difference"]) for pair in pairs]
    paragraph_len_diff = [float(pair["paragraph_abs_length_difference"]) for pair in pairs]
    result["diagnostics"] = {
        "label_mean_absolute_IT_GC_length_difference": statistics.mean(label_len_diff),
        "paragraph_mean_absolute_IT_GC_length_difference": statistics.mean(paragraph_len_diff),
        "label_equal_IT_GC_length_fraction": sum(value == 0 for value in label_len_diff) / len(label_len_diff),
        "paragraph_equal_IT_GC_length_fraction": sum(value == 0 for value in paragraph_len_diff) / len(paragraph_len_diff),
    }

    sensitivity = [
        pair
        for pair in pairs
        if int(pair["it_length"]) == int(pair["label_gc_length"])
        and int(pair["it_length"]) == int(pair["paragraph_gc_length"])
    ]
    sensitivity_folios = {str(pair["folio"]) for pair in sensitivity}
    if len(sensitivity) >= SENSITIVITY_MIN_PAIRS and len(sensitivity_folios) >= SENSITIVITY_MIN_FOLIOS:
        result["equal_source_length_sensitivity"] = {
            "status": "RUN_DESCRIPTIVE_ONLY",
            "pairs": len(sensitivity),
            "folios": len(sensitivity_folios),
            "label_mean_D": statistics.mean(float(pair["label_D"]) for pair in sensitivity),
            "paragraph_mean_D": statistics.mean(float(pair["paragraph_D"]) for pair in sensitivity),
            "Delta": statistics.mean(float(pair["delta"]) for pair in sensitivity),
        }
    else:
        result["equal_source_length_sensitivity"] = {
            "status": "NOT_RUN_INSUFFICIENT_SAMPLE",
            "pairs": len(sensitivity),
            "folios": len(sensitivity_folios),
            "required_pairs": SENSITIVITY_MIN_PAIRS,
            "required_folios": SENSITIVITY_MIN_FOLIOS,
        }

    # Descriptive P-vs-P negative control from the still-unused controls.
    negative_deltas: list[float] = []
    for pair in pairs:
        stratum = (str(pair["folio"]), int(pair["it_length"]))
        cursor = pool_cursor[stratum]
        controls = pools.get(stratum, [])
        if cursor >= len(controls):
            continue
        second = controls[cursor]
        pool_cursor[stratum] = cursor + 1
        negative_deltas.append(float(pair["paragraph_D"]) - float(second["D"]))
    result["p_vs_p_negative_control"] = {
        "status": "DESCRIPTIVE_ONLY",
        "pairs": len(negative_deltas),
        "mean_delta": mean_or_none(negative_deltas),
        "median_delta": median_or_none(negative_deltas),
    }

    permutations_complete = len(null) == PERMUTATIONS
    scientific_gates = {
        "Delta_positive": observed_delta > 0,
        "p_upper_at_most_0_05": p_upper <= 0.05,
        "permutations_complete": permutations_complete,
    }
    result["scientific_gates"] = scientific_gates
    if not permutations_complete:
        result.update({"status": "BLOCKED", "reason": "preregistered permutation-completion gate failed"})
    elif observed_delta > 0 and p_upper <= 0.05:
        result["status"] = "PASS"
    else:
        result["status"] = "FAIL"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
