#!/usr/bin/env python3
"""H85 preregistered IT↔GC exact-record ordinal-token disagreement challenge."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence

EXPECTED_SHA256 = {
    "IT": "db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee",
    "GC": "b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f",
}
PAIRING_SEED = 20261018
PERMUTATION_SEED = 20261019
PERMUTATIONS = 9_999
MIN_PAIRS = 60
MIN_FOLIOS = 8
SENSITIVITY_MIN_PAIRS = 30
SENSITIVITY_MIN_FOLIOS = 6


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def known_tokens(payload: str) -> list[str]:
    text = re.sub(r"<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;", " ", payload)
    out: list[str] = []
    for piece in re.split(r"[.\s]+", text):
        piece = piece.strip()
        if not piece or "?" in piece:
            continue
        runs = re.findall(r"[A-Za-z0-9]+", piece)
        if len(runs) == 1 and runs[0]:
            out.append(runs[0])
    return out


def parse_records(data: bytes) -> dict[tuple[str, int], dict[str, object]]:
    records: dict[tuple[str, int], dict[str, object]] = {}
    for line in data.decode("utf-8", errors="strict").splitlines():
        locus = re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$", line)
        if not locus:
            continue
        folio, number, locator, payload = locus.groups()
        records[(folio, int(number))] = {
            "folio": folio,
            "number": int(number),
            "locator": locator,
            "tokens": known_tokens(payload),
        }
    return records


def generic_locus_type(locator: str) -> str | None:
    loc = re.sub(r"^[@+*=]", "", locator.strip())
    if loc.startswith("L"):
        return "L"
    if loc.startswith("P"):
        return "P"
    return None


def canonical_pattern(token: str) -> tuple[int, ...]:
    mapping: dict[str, int] = {}
    out: list[int] = []
    for symbol in token:
        if symbol not in mapping:
            mapping[symbol] = len(mapping)
        out.append(mapping[symbol])
    return tuple(out)


def levenshtein(left: Sequence[int], right: Sequence[int]) -> int:
    previous = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        current = [i]
        for j, b in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (a != b)))
        previous = current
    return previous[-1]


def disagreement(it_token: str, gc_token: str) -> float:
    left, right = canonical_pattern(it_token), canonical_pattern(gc_token)
    return levenshtein(left, right) / max(len(left), len(right), 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--it", type=Path, required=True)
    ap.add_argument("--gc", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    raw = {"IT": args.it.read_bytes(), "GC": args.gc.read_bytes()}
    hashes = {name: sha256(data) for name, data in raw.items()}
    result: dict[str, object] = {
        "classification": "IT_GC_ORDINAL_TOKEN_STRUCTURAL_DISAGREEMENT_LABEL_VS_PARAGRAPH_NOT_SEMANTICS",
        "source": {
            "repository": "noah-chelednik/voynich-data",
            "revision": "472ef7366606a799fc8f1044c037e06b413f6ddd",
            "sha256": hashes,
            "expected_sha256": EXPECTED_SHA256,
        },
        "parameters": {
            "pairing_seed": PAIRING_SEED,
            "permutation_seed": PERMUTATION_SEED,
            "permutations_requested": PERMUTATIONS,
            "min_pairs": MIN_PAIRS,
            "min_folios": MIN_FOLIOS,
            "max_controls_per_P_record": 1,
        },
    }
    bad = [name for name in EXPECTED_SHA256 if hashes[name] != EXPECTED_SHA256[name]]
    if bad:
        result.update({"status": "BLOCKED", "reason": "frozen source hash mismatch", "mismatched_sources": bad})
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    it_records = parse_records(raw["IT"])
    gc_records = parse_records(raw["GC"])

    labels: list[dict[str, object]] = []
    p_candidates: list[dict[str, object]] = []
    p_exact_records = 0
    p_nonempty_both = 0
    p_equal_count_records = 0
    p_equal_count_distribution: Counter[int] = Counter()

    for key, it_record in it_records.items():
        kind = generic_locus_type(str(it_record["locator"]))
        if kind not in {"L", "P"}:
            continue
        gc_record = gc_records.get(key)
        if gc_record is None:
            continue
        it_tokens = list(it_record["tokens"])  # type: ignore[arg-type]
        gc_tokens = list(gc_record["tokens"])  # type: ignore[arg-type]

        if kind == "L":
            if len(it_tokens) == 1 and len(gc_tokens) == 1:
                it_token, gc_token = str(it_tokens[0]), str(gc_tokens[0])
                labels.append({
                    "folio": key[0],
                    "number": key[1],
                    "record_key": key,
                    "it_token": it_token,
                    "gc_token": gc_token,
                    "it_length": len(it_token),
                    "gc_length": len(gc_token),
                    "D": disagreement(it_token, gc_token),
                })
            continue

        p_exact_records += 1
        if not it_tokens or not gc_tokens:
            continue
        p_nonempty_both += 1
        if len(it_tokens) != len(gc_tokens):
            continue
        p_equal_count_records += 1
        p_equal_count_distribution[len(it_tokens)] += 1
        for ordinal, (it_raw, gc_raw) in enumerate(zip(it_tokens, gc_tokens), 1):
            it_token, gc_token = str(it_raw), str(gc_raw)
            p_candidates.append({
                "folio": key[0],
                "number": key[1],
                "record_key": key,
                "ordinal": ordinal,
                "it_token": it_token,
                "gc_token": gc_token,
                "it_length": len(it_token),
                "gc_length": len(gc_token),
                "D": disagreement(it_token, gc_token),
            })

    result["coverage"] = {
        "label_single_token_mappable": len(labels),
        "label_folios": len({str(row["folio"]) for row in labels}),
        "P_exact_records_present_in_both": p_exact_records,
        "P_records_nonempty_in_both": p_nonempty_both,
        "P_records_equal_known_token_count": p_equal_count_records,
        "P_ordinal_token_candidates": len(p_candidates),
        "P_equal_token_count_record_size_distribution": {str(k): v for k, v in sorted(p_equal_count_distribution.items())},
    }

    pools: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in p_candidates:
        pools[(str(row["folio"]), int(row["it_length"]))].append(row)
    rng_pair = random.Random(PAIRING_SEED)
    for stratum in sorted(pools):
        pools[stratum].sort(key=lambda row: (int(row["number"]), int(row["ordinal"])))
        rng_pair.shuffle(pools[stratum])

    cursors: dict[tuple[str, int], int] = defaultdict(int)
    used_p_records: set[tuple[str, int]] = set()
    pairs: list[dict[str, object]] = []
    unmatched_labels = 0
    for label in sorted(labels, key=lambda row: (str(row["folio"]), int(row["number"]))):
        stratum = (str(label["folio"]), int(label["it_length"]))
        candidates = pools.get(stratum, [])
        cursor = cursors[stratum]
        chosen: dict[str, object] | None = None
        while cursor < len(candidates):
            candidate = candidates[cursor]
            cursor += 1
            record_key = candidate["record_key"]  # type: ignore[assignment]
            if record_key in used_p_records:
                continue
            chosen = candidate
            used_p_records.add(record_key)  # type: ignore[arg-type]
            break
        cursors[stratum] = cursor
        if chosen is None:
            unmatched_labels += 1
            continue
        pairs.append({
            "folio": label["folio"],
            "it_length": label["it_length"],
            "label_locus_number": label["number"],
            "paragraph_locus_number": chosen["number"],
            "paragraph_ordinal": chosen["ordinal"],
            "label_D": label["D"],
            "paragraph_D": chosen["D"],
            "delta": float(label["D"]) - float(chosen["D"]),
            "label_gc_length": label["gc_length"],
            "paragraph_gc_length": chosen["gc_length"],
            "label_abs_length_difference": abs(int(label["it_length"]) - int(label["gc_length"])),
            "paragraph_abs_length_difference": abs(int(chosen["it_length"]) - int(chosen["gc_length"])),
        })

    folios = sorted({str(pair["folio"]) for pair in pairs})
    sample_gates = {
        "matched_pairs_at_least_60": len(pairs) >= MIN_PAIRS,
        "represented_folios_at_least_8": len(folios) >= MIN_FOLIOS,
        "distinct_P_records_equals_pair_count": len(used_p_records) == len(pairs),
    }
    result["matching"] = {
        "matched_pairs": len(pairs),
        "represented_folios": len(folios),
        "folio_ids": folios,
        "distinct_P_records_used": len(used_p_records),
        "unmatched_labels_no_unused_record_control": unmatched_labels,
        "sample_gates": sample_gates,
    }
    if not all(sample_gates.values()):
        result.update({"status": "BLOCKED", "reason": "preregistered matched-sample gate failed"})
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    label_d = [float(pair["label_D"]) for pair in pairs]
    p_d = [float(pair["paragraph_D"]) for pair in pairs]
    deltas = [float(pair["delta"]) for pair in pairs]
    observed_delta = statistics.mean(deltas)
    by_folio: dict[str, list[float]] = defaultdict(list)
    for pair in pairs:
        by_folio[str(pair["folio"])].append(float(pair["delta"]))

    result["observed"] = {
        "label_mean_D": statistics.mean(label_d),
        "label_median_D": statistics.median(label_d),
        "paragraph_mean_D": statistics.mean(p_d),
        "paragraph_median_D": statistics.median(p_d),
        "Delta": observed_delta,
        "label_exact_pattern_agreement_fraction": sum(v == 0 for v in label_d) / len(label_d),
        "paragraph_exact_pattern_agreement_fraction": sum(v == 0 for v in p_d) / len(p_d),
        "by_folio_mean_delta": {folio: statistics.mean(values) for folio, values in sorted(by_folio.items())},
    }

    rng_null = random.Random(PERMUTATION_SEED)
    null: list[float] = []
    for _ in range(PERMUTATIONS):
        null.append(statistics.mean(delta if rng_null.getrandbits(1) else -delta for delta in deltas))
    p_upper = (1 + sum(value >= observed_delta for value in null)) / (PERMUTATIONS + 1)
    result["null"] = {
        "permutations_requested": PERMUTATIONS,
        "permutations_completed": len(null),
        "seed": PERMUTATION_SEED,
        "null_mean_Delta": statistics.mean(null),
        "null_sd_Delta": statistics.pstdev(null),
        "p_upper": p_upper,
    }

    label_len = [int(pair["label_abs_length_difference"]) for pair in pairs]
    p_len = [int(pair["paragraph_abs_length_difference"]) for pair in pairs]
    result["diagnostics"] = {
        "label_mean_absolute_IT_GC_length_difference": statistics.mean(label_len),
        "paragraph_mean_absolute_IT_GC_length_difference": statistics.mean(p_len),
        "label_equal_IT_GC_length_fraction": sum(v == 0 for v in label_len) / len(label_len),
        "paragraph_equal_IT_GC_length_fraction": sum(v == 0 for v in p_len) / len(p_len),
    }
    sensitivity = [
        pair for pair in pairs
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

    complete = len(null) == PERMUTATIONS
    result["scientific_gates"] = {
        "Delta_positive": observed_delta > 0,
        "p_upper_at_most_0_05": p_upper <= 0.05,
        "permutations_complete": complete,
    }
    if not complete:
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
