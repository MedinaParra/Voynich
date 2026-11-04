#!/usr/bin/env python3
"""Stage 88 blind mapping-freedom packet; no branch/ref writes.
Replays the JS mirror byte-for-byte with the same nonzero xorshift32 seed.
All new plaintext, offsets, keys and seed remain private until predictions freeze.
"""
import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import string

ALPHABET = string.ascii_lowercase
N = 2000
SOURCE_COMMIT = "960254605ab910ed90af8d3a8cc7278bbb202185"
SOURCE_BUNDLE_BLOB = "78cac8d327438695cd226a62529ad7ac078f59d1"
PRIOR_TRUTH_BLOB = "d19cc5cdcc5bba1976ba05e61bccfcddbea5739a"
LM_SHA256 = "9206bde5bb6252ddb4de70dd2ea28aef6cc0ca5f59effbc2deac3e34546eae77"
TEST_PATHS = ["caesar/gall1.txt", "caesar/gall2.txt", "caesar/gall3.txt"]
RNG_SPEC = "xorshift32 shifts13,17,5 unsigned32; rejection randbelow; Fisher-Yates descending"
NORMALIZATION = "drop first line; exclude str.isupper lines; lower; regex [a-z]+; join words with ASCII space; no i/j or u/v merging; windows count letters, remove spaces"
VERSION = "mapping-freedom-generator-v1"

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

class XorShift32:
    def __init__(self, seed):
        if isinstance(seed, bool) or not isinstance(seed, int) or not 0 < seed < 2**32:
            raise ValueError("Seed must be a nonzero uint32")
        self.state = seed
    def next(self):
        x = self.state
        x ^= (x << 13) & 0xffffffff
        x ^= x >> 17
        x ^= (x << 5) & 0xffffffff
        self.state = x & 0xffffffff
        return self.state
    def below(self, n):
        if not 0 < n <= 2**32:
            raise ValueError("Bad randbelow bound")
        limit = (2**32 // n) * n
        while True:
            x = self.next()
            if x < limit:
                return x % n
    def shuffle(self, values):
        for i in range(len(values)-1, 0, -1):
            j = self.below(i+1)
            values[i], values[j] = values[j], values[i]

def sources(bundle_raw):
    if git_blob(bundle_raw) != SOURCE_BUNDLE_BLOB:
        raise ValueError("Latin bundle differs from pinned base")
    bundle = json.loads(bundle_raw)
    texts = {}
    provenance = []
    for entry in bundle["files"]:
        raw = base64.b64decode(entry["base64"])
        if git_blob(raw) != entry["sha"] or len(raw) != entry["size"]:
            raise ValueError("Source blob or byte size mismatch")
        lines = [line for i, line in enumerate(raw.decode("utf-8").splitlines())
                 if i > 0 and not line.isupper()]
        text = " ".join(re.findall("[a-z]+", "\n".join(lines).lower()))
        texts[entry["path"]] = text
        provenance.append({"path": entry["path"], "git_blob_sha1": entry["sha"],
                           "normalized_letters": len(text.replace(" ", ""))})
    if any(path not in texts for path in TEST_PATHS):
        raise ValueError("Missing reserved book")
    return bundle["commit"], texts, provenance

def excluded_intervals(prior_raw):
    if git_blob(prior_raw) != PRIOR_TRUTH_BLOB:
        raise ValueError("Prior truth differs from committed stage86 reveal")
    excluded = {path: set() for path in TEST_PATHS}
    for case in json.loads(prior_raw)["cases"]:
        if case.get("source_path") in excluded:
            excluded[case["source_path"]].add((case["letter_start"], case["letter_end_exclusive"]))
    return {path: sorted(intervals) for path, intervals in excluded.items()}

def sample_window(text, excluded, rng):
    letters = text.replace(" ", "")
    candidates = [start for start in range(len(letters)-N+1)
                  if all(start+N <= lo or start >= hi for lo, hi in excluded)]
    if not candidates:
        raise ValueError("No stage86-disjoint sample window")
    start = candidates[rng.below(len(candidates))]
    return start, letters[start:start+N]

def mono(plain, rng):
    key = list(ALPHABET)
    rng.shuffle(key)
    encryption = "".join(key)
    decryption = "".join(ALPHABET[encryption.index(c)] for c in ALPHABET)
    cipher = plain.translate(str.maketrans(ALPHABET, encryption))
    return cipher, encryption, decryption

def homo(plain, rng):
    count = Counter(plain)
    chars = sorted(count)
    if len(chars) >= 26:
        raise ValueError("No spare homophonic symbols")
    available = list(ALPHABET)
    rng.shuffle(available)
    aliases = {char: [available.pop()] for char in chars}
    ranked = sorted(chars, key=lambda c: (-count[c], c))
    for i, symbol in enumerate(available):
        aliases[ranked[i % len(ranked)]].append(symbol)
    reverse = {symbol: char for char, group in aliases.items() for symbol in group}
    key = "".join(reverse[c] for c in ALPHABET)
    cipher = "".join(aliases[c][rng.below(len(aliases[c]))] for c in plain)
    return cipher, aliases, key

def ceiling(cipher, key):
    grouped = {}
    count = Counter(cipher)
    for symbol, char in zip(ALPHABET, key):
        grouped.setdefault(char, []).append(count[symbol])
    return sum(max(values) for values in grouped.values())

def prepare(bundle_raw, prior_raw, seed):
    latin_commit, texts, provenance = sources(bundle_raw)
    excluded = excluded_intervals(prior_raw)
    rng = XorShift32(seed)
    cases = []
    for i, path in enumerate(TEST_PATHS, 1):
        start, plain = sample_window(texts[path], excluded[path], rng)
        pair = "P" + str(i)
        common = {"pair_id": pair, "variant": "no_spaces", "source_path": path,
                  "letter_start": start, "letter_end_exclusive": start+N, "letters_total": N}
        mono_cipher, encryption, mono_key = mono(plain, rng)
        cases.append({**common, "role": "monoalphabetic_positive", "ciphertext": mono_cipher,
                      "plaintext": plain, "letters_plaintext": plain,
                      "encryption_key_plain_to_cipher": encryption,
                      "decryption_key_cipher_to_plain": mono_key})
        homo_cipher, aliases, homo_key = homo(plain, rng)
        cases.append({**common, "role": "homophonic_positive", "ciphertext": homo_cipher,
                      "plaintext": plain, "letters_plaintext": plain,
                      "aliases_plain_to_cipher": aliases,
                      "decryption_key_cipher_to_plain": homo_key})
        shuffled = list(homo_cipher)
        rng.shuffle(shuffled)
        null_cipher = "".join(shuffled)
        null_plain = null_cipher.translate(str.maketrans(ALPHABET, homo_key))
        cases.append({**common, "role": "frequency_matched_null", "ciphertext": null_cipher,
                      "plaintext": null_plain, "letters_plaintext": null_plain,
                      "aliases_plain_to_cipher": aliases,
                      "decryption_key_cipher_to_plain": homo_key,
                      "accuracy_interpretation": "Generating-map recovery only; shuffled plaintext is not coherent Latin"})
    rng.shuffle(cases)
    for i, case in enumerate(cases, 1):
        case["id"] = f"U{i:02d}"
        case["observed_cipher_symbols"] = "".join(sorted(set(case["ciphertext"])))
        case["bijective_ceiling_correct_letters"] = ceiling(case["ciphertext"], case["decryption_key_cipher_to_plain"])
    homo_by_pair = {case["pair_id"]: case["id"] for case in cases if case["role"] == "homophonic_positive"}
    for case in cases:
        if case["role"] == "frequency_matched_null":
            case["parent_homophonic_id"] = homo_by_pair[case["pair_id"]]
    seed_record = {"schema": "mapping-freedom-seed-v1", "seed_u32": seed, "rng_spec": RNG_SPEC,
                   "generator_version": VERSION}
    truth = {"schema": "mapping-freedom-truth-v1", "experiment": 88, "source_commit": SOURCE_COMMIT,
             "latin_source_commit": latin_commit, "prior_truth_git_blob_sha1": PRIOR_TRUTH_BLOB,
             "source_bundle_git_blob_sha1": SOURCE_BUNDLE_BLOB, "generator_version": VERSION,
             "normalization": NORMALIZATION, "cases": cases}
    cipher_public = {"schema": "mapping-freedom-cases-v1",
                     "cases": [{"id": case["id"], "ciphertext": case["ciphertext"]} for case in cases]}
    manifest = {"schema": "mapping-freedom-public-v1", "experiment": 88,
                "generator_version": VERSION, "alphabet": ALPHABET, "spacing": "none",
                "case_count": 9, "letters_per_case": N, "source_commit": SOURCE_COMMIT,
                "latin_source_commit": latin_commit, "source_bundle_git_blob_sha1": SOURCE_BUNDLE_BLOB,
                "prior_truth_git_blob_sha1": PRIOR_TRUTH_BLOB, "normalization": NORMALIZATION,
                "prior_exclusion_rule": "Exclude every stage86 revealed [letter_start,letter_end_exclusive) interval of the same source book",
                "lm_sha256": LM_SHA256,
                "lm_source_path": "research_gpt6/results/known_cipher_recovery/model/lm_int32.bin",
                "lm_policy": "Reuse stage86 Apicius LM bytes; no retraining or reweighting",
                "rng_spec": RNG_SPEC, "seed_bits": 32, "sources": provenance,
                "truth_git_blob_sha1": git_blob(canonical(truth)),
                "seed_git_blob_sha1": git_blob(canonical(seed_record)),
                "ciphertexts_git_blob_sha1": git_blob(canonical(cipher_public))}
    return {"public": {"ciphertexts.json": cipher_public, "manifest.json": manifest},
            "private": {"truth.json": truth, "seed.json": seed_record}}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latin", type=Path, required=True)
    parser.add_argument("--prior-truth", type=Path, required=True)
    parser.add_argument("--seed-file", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    seed = json.loads(args.seed_file.read_text())["seed_u32"]
    packet = prepare(args.latin.read_bytes(), args.prior_truth.read_bytes(), seed)
    if args.out.exists() and any(args.out.iterdir()):
        raise ValueError("Refuse to replace an existing packet")
    commitments = {}
    for group, files in packet.items():
        directory = args.out/group
        directory.mkdir(parents=True, exist_ok=True)
        if group == "private":
            directory.chmod(0o700)
        for name, value in files.items():
            raw = canonical(value)
            path = directory/name
            path.write_bytes(raw)
            if group == "private":
                path.chmod(0o600)
            commitments[group+"/"+name] = git_blob(raw)
    print(json.dumps({"file_git_blobs": commitments}, sort_keys=True))

if __name__ == "__main__":
    main()
