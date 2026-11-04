#!/usr/bin/env python3
"""Evaluate stage88 only after published prediction/config/packet hashes freeze.
No tuning, reweighting or searching occurs here. Oracle LM is a reference, not an
upper bound: a false or collapsed plaintext can score above the true plaintext.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import string
import struct

ALPHABET = string.ascii_lowercase
LM_SHA256 = "9206bde5bb6252ddb4de70dd2ea28aef6cc0ca5f59effbc2deac3e34546eae77"
N = 2000
ROLES = {"monoalphabetic_positive", "homophonic_positive", "frequency_matched_null"}

def check(ok, message):
    if not ok:
        raise ValueError(message)

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def read(path):
    return json.loads(path.read_bytes())

def sha256(raw):
    return hashlib.sha256(raw).hexdigest()

def unique_index(rows, label):
    check(isinstance(rows, list) and all(isinstance(row, dict) and isinstance(row.get("id"), str) for row in rows),
          label + " must be a list with string IDs")
    index = {row["id"]: row for row in rows}
    check(len(index) == len(rows), "Duplicate IDs: " + label)
    return index

def true_ceiling(cipher, key):
    count = Counter(cipher)
    groups = defaultdict(list)
    for cipher_symbol, plain_symbol in zip(ALPHABET, key):
        groups[plain_symbol].append(count[cipher_symbol])
    return sum(max(values) for values in groups.values())

def lm_score(plain, lm):
    a = [ord(c)-97 for c in plain]
    return sum(lm[((a[i]*26+a[i+1])*26+a[i+2])*26+a[i+3]] for i in range(len(a)-3))

def evaluate(public, private, predictions_path, freeze_path, lm_path):
    manifest_raw = (public/"manifest.json").read_bytes()
    manifest = json.loads(manifest_raw)
    predictions_raw = predictions_path.read_bytes()
    predictions = json.loads(predictions_raw)
    freeze = read(freeze_path)
    check(freeze.get("public_manifest_git_blob") == git_blob(manifest_raw), "Frozen public manifest mismatch")
    check(freeze.get("predictions_git_blob") == git_blob(predictions_raw), "Frozen prediction Git blob mismatch")
    check(freeze.get("config_git_blob") == predictions.get("config_git_blob"), "Frozen config Git blob mismatch")
    check(isinstance(freeze.get("config_git_blob"), str) and len(freeze["config_git_blob"]) == 40,
          "Missing config commitment")
    check(isinstance(freeze.get("publication_commit"), str) and len(freeze["publication_commit"]) == 40,
          "Missing prediction publication commit")
    if "prediction_sha256" in freeze:
        check(freeze["prediction_sha256"] == sha256(predictions_raw), "Prediction SHA256 mismatch")
    if "predictions_sha256" in freeze:
        check(freeze["predictions_sha256"] == sha256(predictions_raw), "Predictions SHA256 mismatch")
    cipher_raw = (public/"ciphertexts.json").read_bytes()
    check(git_blob(cipher_raw) == manifest["ciphertexts_git_blob_sha1"], "Public ciphertext commitment mismatch")
    truth_raw = (private/"truth.json").read_bytes()
    check(git_blob(truth_raw) == manifest["truth_git_blob_sha1"], "Truth commitment mismatch")
    seed_raw = (private/"seed.json").read_bytes()
    check(git_blob(seed_raw) == manifest["seed_git_blob_sha1"], "Seed commitment mismatch")
    lm_raw = lm_path.read_bytes()
    check(sha256(lm_raw) == LM_SHA256 == manifest["lm_sha256"], "Frozen stage86 LM mismatch")
    check(len(lm_raw) == 4 * 26**4, "Wrong LM length")
    lm = struct.unpack("<" + str(26**4) + "i", lm_raw)
    pub = unique_index(json.loads(cipher_raw)["cases"], "public cases")
    truth = unique_index(json.loads(truth_raw)["cases"], "truth cases")
    check(set(pub) == set(truth) == {f"U{i:02d}" for i in range(1, 10)}, "Expected exactly U01..U09")
    check(manifest["case_count"] == 9 and manifest["letters_per_case"] == N, "Wrong packet dimensions")
    check(Counter(c["role"] for c in truth.values()) == Counter({role: 3 for role in ROLES}),
          "Expected three mono, three homo and three null cases")
    for case_id, expected in truth.items():
        cipher = pub[case_id]["ciphertext"]
        check(cipher == expected["ciphertext"] and len(cipher) == N and set(cipher) <= set(ALPHABET),
              "Truth/public mismatch, length or alphabet violation")
        key = expected["decryption_key_cipher_to_plain"]
        check(isinstance(key, str) and len(key) == 26 and set(key) <= set(ALPHABET), "Invalid generating map")
        plain = cipher.translate(str.maketrans(ALPHABET, key))
        check(plain == expected["plaintext"] == expected["letters_plaintext"], "Truth decode mismatch")
        check(expected["bijective_ceiling_correct_letters"] == true_ceiling(cipher, key),
              "Incorrect committed bijective ceiling")
        check(expected["observed_cipher_symbols"] == "".join(sorted(set(cipher))), "Observed symbols mismatch")
        check(expected["letter_end_exclusive"] - expected["letter_start"] == N, "Invalid source interval")
        if expected["role"] == "monoalphabetic_positive":
            check(set(key) == set(ALPHABET), "Mono generating map must be bijective")
        else:
            aliases = expected["aliases_plain_to_cipher"]
            flat = [c for group in aliases.values() for c in group]
            check(sorted(flat) == list(ALPHABET), "Homophonic groups must partition all26symbols")
            check(all(key[ALPHABET.index(c)] == p for p, group in aliases.items() for c in group),
                  "Alias groups disagree with generating map")
        if expected["role"] == "frequency_matched_null":
            parent = truth[expected["parent_homophonic_id"]]
            check(parent["role"] == "homophonic_positive" and parent["pair_id"] == expected["pair_id"],
                  "Wrong null parent")
            check(Counter(cipher) == Counter(parent["ciphertext"]), "Null frequency mismatch")
            check(key == parent["decryption_key_cipher_to_plain"], "Null mapping mismatch")
            check(expected["bijective_ceiling_correct_letters"] == parent["bijective_ceiling_correct_letters"],
                  "Null and homophonic ceilings differ")
    for pair_id in ("P1", "P2", "P3"):
        group = [c for c in truth.values() if c["pair_id"] == pair_id]
        check(Counter(c["role"] for c in group) == Counter({role: 1 for role in ROLES}), "Invalid dependent triple")
        mono = next(c for c in group if c["role"] == "monoalphabetic_positive")
        homo = next(c for c in group if c["role"] == "homophonic_positive")
        check(mono["plaintext"] == homo["plaintext"], "Mono/homo plaintext pair mismatch")
        check(all((c["source_path"], c["letter_start"], c["letter_end_exclusive"]) ==
                  (mono["source_path"], mono["letter_start"], mono["letter_end_exclusive"]) for c in group),
              "Triple source-interval mismatch")
    check(predictions.get("schema_version") == 1, "Unknown prediction schema")
    models = predictions.get("models")
    check(isinstance(models, list) and len(models) == 2, "Expected two models")
    check({model.get("name") for model in models} == {"bijective", "many_to_one"}, "Wrong or duplicate model names")
    rows = []
    indexed_rows = {}
    for model in models:
        name = model["name"]
        pred = unique_index(model["cases"], name + " predictions")
        check(set(pred) == set(pub), "Missing or extra model case IDs")
        for case_id in sorted(pub):
            prediction, expected = pred[case_id], truth[case_id]
            cipher = pub[case_id]["ciphertext"]
            key = prediction.get("key")
            check(isinstance(key, str) and len(key) == 26 and set(key) <= set(ALPHABET),
                  case_id + ": invalid predicted mapping")
            if name == "bijective":
                check(set(key) == set(ALPHABET), case_id + ": bijective model returned repeated outputs")
            plain = cipher.translate(str.maketrans(ALPHABET, key))
            check(prediction.get("plaintext") == plain == prediction.get("letters_plaintext"),
                  case_id + ": prediction not consistent with mapping")
            check(len(plain) == N, "Wrong predicted plaintext length")
            score = prediction.get("score")
            check(isinstance(score, int) and not isinstance(score, bool), "Score must be an integer")
            check(score == lm_score(plain, lm), "Reported integer LM score mismatch")
            check(prediction.get("annealing_proposals") == 8*50000, "Annealing budget differs from preregistration")
            restart_scores = prediction.get("restart_scores")
            check(isinstance(restart_scores, list) and len(restart_scores) == 8 and
                  all(isinstance(s, int) and not isinstance(s, bool) for s in restart_scores), "Expected8restart scores")
            check(all(s <= score for s in restart_scores), "Final selection below a recorded restart score")
            for field in ("seed", "polish_pair_checks", "accepted"):
                check(isinstance(prediction.get(field), int) and not isinstance(prediction[field], bool) and prediction[field] >= 0,
                      "Invalid integer run diagnostic: " + field)
            check(prediction["accepted"] <= prediction["annealing_proposals"], "Accepted proposals exceed budget")
            observed = "".join(sorted(set(cipher)))
            unobserved = "".join(c for c in ALPHABET if c not in observed)
            true_key = expected["decryption_key_cipher_to_plain"]
            correct = sum(a == b for a, b in zip(plain, expected["letters_plaintext"]))
            key_correct = sum(key[ALPHABET.index(c)] == true_key[ALPHABET.index(c)] for c in observed)
            oracle = lm_score(expected["letters_plaintext"], lm)
            ceiling = expected["bijective_ceiling_correct_letters"]
            if name == "bijective":
                check(correct <= ceiling, "Bijective output exceeds exact combinatorial ceiling")
            row = {"model": name, "id": case_id, "role": expected["role"], "pair_id": expected["pair_id"],
                   "characters_correct": correct, "characters_total": N, "character_accuracy": correct/N,
                   "all_exact": correct == N, "observed_symbols_correct": key_correct,
                   "observed_symbols_total": len(observed), "observed_symbol_key_accuracy": key_correct/len(observed),
                   "unobserved_cipher_symbols": unobserved, "unobserved_mapping_evaluation": "unidentifiable; excluded",
                   "score": score, "true_plaintext_lm_score": oracle, "predicted_minus_true_lm_score": score-oracle,
                   "bijective_ceiling_correct_letters": ceiling, "bijective_character_accuracy_ceiling": ceiling/N,
                   "predicted_output_symbols_observed": len({key[ALPHABET.index(c)] for c in observed}),
                   "predicted_output_symbols_full_key": len(set(key)),
                   "predicted_plaintext_counts": dict(sorted(Counter(plain).items())),
                   "true_plaintext_counts": dict(sorted(Counter(expected["letters_plaintext"]).items())),
                   "annealing_proposals": prediction["annealing_proposals"],
                   "polish_pair_checks": prediction["polish_pair_checks"], "accepted": prediction["accepted"],
                   "restart_scores": restart_scores, "solver_seed": prediction["seed"]}
            if expected["role"] == "frequency_matched_null":
                row["accuracy_interpretation"] = expected["accuracy_interpretation"]
                row["parent_homophonic_id"] = expected["parent_homophonic_id"]
            indexed_rows[(name, case_id)] = row
            rows.append(row)
    summary = []
    for name in ("bijective", "many_to_one"):
        for role in sorted(ROLES):
            group = [row for row in rows if row["model"] == name and row["role"] == role]
            summary.append({"model": name, "role": role, "case_count": len(group),
                            "all_exact_count": sum(row["all_exact"] for row in group),
                            "mean_character_accuracy": statistics.mean(row["character_accuracy"] for row in group),
                            "mean_observed_symbol_key_accuracy": statistics.mean(row["observed_symbol_key_accuracy"] for row in group),
                            "mean_score": statistics.mean(row["score"] for row in group),
                            "mean_predicted_output_symbols_observed": statistics.mean(row["predicted_output_symbols_observed"] for row in group)})
    differences = []
    for case_id in sorted(pub):
        a, b = indexed_rows[("bijective", case_id)], indexed_rows[("many_to_one", case_id)]
        differences.append({"id": case_id, "role": a["role"], "pair_id": a["pair_id"],
                            "many_minus_bijective_accuracy": b["character_accuracy"]-a["character_accuracy"],
                            "many_minus_bijective_score": b["score"]-a["score"],
                            "many_minus_bijective_observed_key_accuracy": b["observed_symbol_key_accuracy"]-a["observed_symbol_key_accuracy"]})
    return {"schema": "mapping-freedom-evaluation-v1", "experiment": 88,
            "scope": "Controlled Latin benchmark; not Voynich decipherment",
            "independent_source_passages": 3, "dependent_mono_homo_pairs": 3, "homo_dependent_nulls": 3,
            "commitments": {"public_manifest_git_blob": git_blob(manifest_raw),
                            "predictions_git_blob": git_blob(predictions_raw),
                            "prediction_sha256": sha256(predictions_raw),
                            "config_git_blob": predictions["config_git_blob"],
                            "truth_git_blob_sha1": git_blob(truth_raw), "seed_git_blob_sha1": git_blob(seed_raw),
                            "lm_sha256": sha256(lm_raw), "freeze_git_blob": git_blob(freeze_path.read_bytes()),
                            "publication_commit": freeze["publication_commit"]},
            "interpretation": "Three independent passages only. Mono/homo are paired. Nulls recover an arbitrary generating map, not Latin. True-plaintext LM score is a reference, not an upper bound. Equal proposal counts do not equalize search-neighborhood difficulty.",
            "cases": rows, "summary": summary, "paired_model_differences": differences}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--lm", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = evaluate(args.public, args.private, args.predictions, args.freeze, args.lm)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode()
    args.out.write_bytes(raw)
    print(json.dumps({"evaluation_git_blob": git_blob(raw), "evaluation_sha256": sha256(raw),
                      "summary": report["summary"]}, sort_keys=True))

if __name__ == "__main__":
    main()
