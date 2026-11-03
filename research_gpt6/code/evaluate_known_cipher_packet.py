#!/usr/bin/env python3
"""Evaluate experiment-86 predictions only after solver/predictions are frozen.

Requires a separate freeze receipt with solver_sha256, predictions_sha256 and
manifest_sha256 (the public packet manifest committed before solving).
Predictions schema: {"solver_sha256": "...", "cases": [{"id": "C01",
"key": "26-char cipher-a..z-to-plain permutation", "plaintext": "...",
"letters_plaintext": "2000 letters", "score": number}, ...]}.

The optional frozen_predictions_sha256 field is informational; the authoritative
file hash is external in the freeze receipt, avoiding a self-referential hash.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import string


ALPHABET = string.ascii_lowercase


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text())


def hamming_accuracy(predicted, expected):
    require(len(predicted) == len(expected), "Mismatched accuracy lengths")
    return sum(a == b for a, b in zip(predicted, expected)) / len(expected)


def evaluate(public, private, predictions_path, solver_path, freeze_path):
    freeze = read_json(freeze_path)
    solver_hash, prediction_hash = digest(solver_path), digest(predictions_path)
    require(freeze.get("solver_sha256") == solver_hash, "Solver differs from frozen solver hash")
    require(freeze.get("predictions_sha256") == prediction_hash, "Predictions differ from frozen hash")
    require(freeze.get("manifest_sha256") == digest(public / "manifest.json"),
            "Public manifest differs from the pre-solve frozen packet hash")
    manifest = read_json(public / "manifest.json")
    for name, expected in manifest["public_files_sha256"].items():
        require(digest(public / name) == expected, f"Public packet integrity failure: {name}")
    truth_hash = digest(private / "truth.json")
    require(truth_hash == manifest["truth_commitment_sha256"], "Private truth violates public commitment")
    public_cases = read_json(public / "ciphertexts.json")["cases"]
    truth_cases = read_json(private / "truth.json")["cases"]
    predictions = read_json(predictions_path)
    require(predictions.get("solver_sha256") == solver_hash, "Predictions identify a different solver")
    require(isinstance(predictions.get("cases"), list), "Missing prediction cases list")

    def index_unique(rows, name):
        require(all(isinstance(row, dict) and isinstance(row.get("id"), str) for row in rows),
                f"Invalid {name} IDs")
        indexed = {row["id"]: row for row in rows}
        require(len(indexed) == len(rows), f"Duplicate {name} IDs")
        return indexed

    pub = index_unique(public_cases, "public")
    tru = index_unique(truth_cases, "truth")
    pred = index_unique(predictions["cases"], "prediction")
    require(set(pub) == set(tru) == set(pred), "Public, truth and prediction ID sets differ")
    require(len(pub) == manifest["case_count"] == 10, "Expected exactly ten frozen cases")
    results = []
    for case_id in sorted(pub):
        cipher, expected, prediction = pub[case_id]["ciphertext"], tru[case_id], pred[case_id]
        require(cipher == expected["ciphertext"], "Ciphertext does not match committed truth")
        key = prediction.get("key")
        require(isinstance(key, str) and len(key) == 26 and set(key) == set(ALPHABET),
                f"{case_id}: key must be a 26-letter permutation mapping cipher a..z to plain")
        decoded = cipher.translate(str.maketrans(ALPHABET, key))
        require(prediction.get("plaintext") == decoded,
                f"{case_id}: plaintext is inconsistent with key or input spacing")
        letters = decoded.replace(" ", "")
        require(prediction.get("letters_plaintext") == letters,
                f"{case_id}: letters_plaintext is inconsistent with plaintext")
        require(len(letters) == manifest["letters_per_case"], f"{case_id}: wrong number of letters")
        score = prediction.get("score")
        require(isinstance(score, (int, float)) and not isinstance(score, bool)
                and math.isfinite(score), f"{case_id}: score must be finite")
        observed = "".join(sorted(set(cipher) - {" "}))
        unobserved = "".join(c for c in ALPHABET if c not in observed)
        true_key = expected["decryption_key_cipher_to_plain"]
        key_correct = sum(key[ALPHABET.index(c)] == true_key[ALPHABET.index(c)] for c in observed)
        character_accuracy = hamming_accuracy(letters, expected["letters_plaintext"])
        result = {"id": case_id, "role": expected["role"], "variant": expected["variant"],
                  "pair_id": expected["pair_id"], "score": score,
                  "character_accuracy": character_accuracy,
                  "characters_correct": round(character_accuracy * len(letters)),
                  "characters_total": len(letters),
                  "all_exact": letters == expected["letters_plaintext"],
                  "observed_symbol_key_accuracy": key_correct / len(observed),
                  "observed_symbols_correct": key_correct,
                  "observed_symbols_total": len(observed),
                  "unobserved_cipher_symbols": unobserved,
                  "unobserved_mapping_evaluation": "not_identifiable_from_this_case; excluded from key accuracy"}
        if expected["role"] == "frequency_matched_null":
            result["accuracy_interpretation"] = expected["accuracy_interpretation"]
        if expected["role"] == "homophonic_wrong_model":
            counts = Counter(cipher.replace(" ", ""))
            ceiling_correct = sum(max(counts[c] for c in group)
                                  for group in expected["aliases_plain_to_cipher"].values())
            require(ceiling_correct == expected["best_bijective_correct_letters"],
                    "Homophonic ceiling integrity failure")
            result["best_bijective_correct_letters"] = ceiling_correct
            result["best_bijective_character_accuracy"] = ceiling_correct / len(letters)
            result["gap_below_bijective_ceiling"] = (ceiling_correct / len(letters)) - character_accuracy
            require(character_accuracy <= ceiling_correct / len(letters) + 1e-12,
                    "Prediction exceeds exact bijective ceiling")
        results.append(result)
    grouped = defaultdict(list)
    for result in results:
        grouped[(result["role"], result["variant"])].append(result)
    summary = []
    for (role, variant), rows in sorted(grouped.items()):
        summary.append({"role": role, "variant": variant, "case_count": len(rows),
                        "all_exact_count": sum(row["all_exact"] for row in rows),
                        "mean_character_accuracy": statistics.mean(row["character_accuracy"] for row in rows),
                        "mean_observed_symbol_key_accuracy": statistics.mean(
                            row["observed_symbol_key_accuracy"] for row in rows),
                        "mean_score": statistics.mean(row["score"] for row in rows)})
    pairs = []
    for pair_id in sorted({row["pair_id"] for row in results if row["pair_id"] is not None}):
        paired = [row for row in results if row["pair_id"] == pair_id
                  and row["role"] == "monoalphabetic_positive"]
        require(len(paired) == 2, "Missing correlated space/no-space positive pair")
        first, second = paired
        observed = set(pub[first["id"]]["ciphertext"]) - {" "}
        a, b = pred[first["id"]]["key"], pred[second["id"]]["key"]
        pairs.append({"pair_id": pair_id, "case_ids": [row["id"] for row in paired],
                      "full_predicted_keys_equal": a == b,
                      "predicted_keys_equal_on_observed_symbols": all(
                          a[ALPHABET.index(c)] == b[ALPHABET.index(c)] for c in observed),
                      "true_keys_equal": tru[first["id"]]["decryption_key_cipher_to_plain"]
                          == tru[second["id"]]["decryption_key_cipher_to_plain"],
                      "independent_replicates": 1})
    return {"schema": "known-cipher-evaluation-v1", "experiment": 86,
            "solver_sha256": solver_hash, "predictions_sha256": prediction_hash,
            "freeze_receipt_sha256": digest(freeze_path),
            "manifest_sha256": digest(public / "manifest.json"),
            "truth_commitment_sha256": truth_hash,
            "independent_positive_passages": 3, "correlated_positive_cases": 6,
            "classification": "CONTROL_CALIBRATION_NOT_VOYNICH_DECIPHERMENT",
            "interpretation": "Null accuracy measures the arbitrary generating key, not recovery of meaningful Latin. Unseen cipher-symbol mappings are unidentifiable. Space/no-space pairs share plaintext letters and true key.",
            "cases": results, "summary": summary, "space_pair_key_consistency": pairs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True,
                        help="Root-created freeze receipt; evaluation is forbidden before freezing")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(args.public, args.private, args.predictions, args.solver, args.freeze)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"evaluation_path": str(args.out.resolve()),
                      "evaluation_sha256": digest(args.out), "summary": report["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
