#!/usr/bin/env python3
"""Independent stage90 audit built by plaintext generation and alias expansion.

Does not import the inverse-likelihood enumerator. Integer likelihood numerators
are generated forward from every plaintext, then compared with its output.
This is a finite invented-language calibration, not Voynich decipherment.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path


METHODS = ('lm_only_key_map', 'channel_key_map', 'channel_plaintext_map',
           'channel_hamming_free', 'channel_hamming_key')
CLEAR, CIPHER, N = 'abc', 'wxyz', 6
PI, TRANS = (3, 2, 1), ((3, 2, 1), (1, 4, 1), (2, 1, 3))
DEN = 6


class Checks:
    def __init__(self):
        self.count = 0
        self.mismatches = []
        self.mismatch_count = 0

    def check(self, label, actual, expected=True):
        self.count += 1
        if actual != expected:
            self.mismatch_count += 1
            if len(self.mismatches) < 50:
                self.mismatches.append({'check': label, 'actual': actual, 'expected': expected})


def ratio(value):
    value = Fraction(value)
    return {'numerator': value.numerator, 'denominator': value.denominator}


def read_json(path):
    payload = path.read_bytes()
    if path.suffix == '.gz':
        payload = gzip.decompress(payload)
    return json.loads(payload)


def hash_file(path):
    payload = path.read_bytes()
    if path.suffix == '.gz':
        payload = gzip.decompress(payload)
    return hashlib.sha256(payload).hexdigest()


def keys():
    return [''.join(k) for k in product(CLEAR, repeat=len(CIPHER)) if set(k) == set(CLEAR)]


def lm_numerator(y):
    indices = [CLEAR.index(c) for c in y]
    value = PI[indices[0]]
    for a, b in zip(indices, indices[1:]):
        value *= TRANS[a][b]
    return value


def forward_table():
    """Expand all Y and its emissions; do not compute likelihood from f(C)."""
    keylist = keys()
    cleartexts = [''.join(y) for y in product(CLEAR, repeat=N)]
    ciphers = [''.join(c) for c in product(CIPHER, repeat=N)]
    cipher_index = {c: i for i, c in enumerate(ciphers)}
    weights = [[0] * len(keylist) for _ in ciphers]
    emitted_plaintexts = [[None] * len(keylist) for _ in ciphers]
    generated_counts = []
    for kindex, key in enumerate(keylist):
        aliases = {p: [c for c, output in zip(CIPHER, key) if output == p] for p in CLEAR}
        expanded = 0
        for y in cleartexts:
            multiplicity = 1
            choices = []
            for p in y:
                choices.append(aliases[p])
                multiplicity *= len(aliases[p])
            # P(Y) has denominator6^6; each alias row has size1 or2.
            numerator = lm_numerator(y) * (2 ** N // multiplicity)
            for emission in product(*choices):
                row = cipher_index[''.join(emission)]
                if emitted_plaintexts[row][kindex] is not None:
                    raise ValueError('A ciphertext has multiple plaintext preimages for a fixed key')
                weights[row][kindex] = numerator
                emitted_plaintexts[row][kindex] = y
                expanded += 1
        generated_counts.append(expanded)
    return keylist, cleartexts, ciphers, weights, emitted_plaintexts, generated_counts


def controls(checks):
    keylist = keys()
    checks.check('control/key_count', len(keylist), 36)
    checks.check('control/alias_cardinalities',
                 all(sorted(Counter(k).values()) == [1, 1, 2] for k in keylist))
    checks.check('control/initial_mass', sum(PI), DEN)
    for i, row in enumerate(TRANS):
        checks.check('control/transition_row_mass/' + str(i), sum(row), DEN)
    # Explicit forward enumeration for N=1 with Fraction arithmetic.
    one = {c: [] for c in CIPHER}
    for key in keylist:
        aliases = {p: [c for c, output in zip(CIPHER, key) if output == p] for p in CLEAR}
        for p in CLEAR:
            joint = Fraction(PI[CLEAR.index(p)], DEN * len(aliases[p]) * len(keylist))
            for c in aliases[p]:
                one[c].append((key, p, joint))
    key_success = Fraction(0)
    text_success = Fraction(0)
    for c, records in one.items():
        mass = sum((r[2] for r in records), Fraction(0))
        checks.check('control/n1_cipher_mass/' + c, ratio(mass), ratio(Fraction(1, 4)))
        plain_mass = {p: sum((w for _, y, w in records if y == p), Fraction(0)) for p in CLEAR}
        posterior = [plain_mass[p] / mass for p in CLEAR]
        checks.check('control/n1_plain_posterior/' + c,
                     [ratio(x) for x in posterior], [ratio(Fraction(x, DEN)) for x in PI])
        key_success += max(r[2] for r in records)
        text_success += max(plain_mass.values())
    checks.check('control/n1_key_MAP_success', ratio(key_success), ratio(Fraction(1, 18)))
    checks.check('control/n1_text_MAP_success', ratio(text_success), ratio(Fraction(1, 2)))
    checks.check('control/uniform_LM_only_unnormalized_mass',
                 ratio(Fraction(4 ** N, 3 ** N)), ratio(Fraction(4, 3) ** N))
    checks.check('control/all_four_symbols_inclusion_exclusion',
                 sum(len(set(c)) == 4 for c in product(CIPHER, repeat=N)),
                 4 ** N - 4 * 3 ** N + 6 * 2 ** N - 4)
    return {'construction': 'Forward enumeration of plaintexts and alias emissions; independent of inverse scorer',
            'n1_cipher_mass': ratio(Fraction(1, 4)),
            'n1_plain_posterior': [ratio(Fraction(x, DEN)) for x in PI],
            'n1_key_MAP_success': ratio(key_success), 'n1_text_MAP_success': ratio(text_success),
            'uniform_LM_only_mass': ratio(Fraction(4, 3) ** N)}


def expected_row(cipher, keylist, weights, plaintexts):
    evidence = sum(weights)
    by_text = defaultdict(int)
    marginals = [{p: 0 for p in CLEAR} for _ in range(N)]
    for y, weight in zip(plaintexts, weights):
        by_text[y] += weight
        for i, p in enumerate(y):
            marginals[i][p] += weight
    def char_correct(y):
        return sum(marginals[i][p] for i, p in enumerate(y))
    lm_scores = [lm_numerator(y) for y in plaintexts]
    max_lm = max(lm_scores)
    lm_key = next(i for i, x in enumerate(lm_scores) if x == max_lm)
    best_weight = max(weights)
    map_key = next(i for i, w in enumerate(weights) if w == best_weight)
    max_text = max(by_text.values())
    map_text = min(y for y, w in by_text.items() if w == max_text)
    free_text = ''.join(min(p for p, w in marginal.items() if w == max(marginal.values()))
                        for marginal in marginals)
    char_scores = [char_correct(y) for y in plaintexts]
    max_char = max(char_scores)
    hamming_key = next(i for i, w in enumerate(char_scores) if w == max_char)
    selected = {'lm_only_key_map': (lm_key, plaintexts[lm_key]),
                'channel_key_map': (map_key, plaintexts[map_key]),
                'channel_plaintext_map': (None, map_text),
                'channel_hamming_free': (None, free_text),
                'channel_hamming_key': (hamming_key, plaintexts[hamming_key])}
    methods = {}
    for name, (kindex, y) in selected.items():
        methods[name] = {'key': None if kindex is None else keylist[kindex], 'text': y,
                         'text_correct_weight': by_text.get(y, 0),
                         'character_correct_weight': char_correct(y),
                         'key_correct_weight': None if kindex is None else weights[kindex],
                         'representable': y in by_text}
    return {'cipher': cipher, 'evidence_numerator': evidence,
            'key_map_ties': sum(w == best_weight for w in weights),
            'text_map_ties': sum(w == max_text for w in by_text.values()), 'methods': methods}


def audit(repo, bundle):
    checks = Checks()
    control_summary = controls(checks)
    config_path = repo / 'data/tiny_channel_plan.json'
    config = read_json(config_path)
    checks.check('config/schema', config['schema'], 'tiny-channel-plan-v1')
    checks.check('config/clear', config['clear_alphabet'], CLEAR)
    checks.check('config/cipher', config['cipher_alphabet'], CIPHER)
    checks.check('config/length', config['length'], N)
    checks.check('config/initial', config['initial_units'], list(PI))
    checks.check('config/transitions', config['transition_units'], [list(r) for r in TRANS])
    checks.check('config/probability_denominator', config['probability_denominator'], DEN)
    checks.check('config/methods', config['methods'], list(METHODS))
    inputs = [config_path, bundle / 'likelihoods.json.gz', bundle / 'decisions.json.gz', bundle / 'result.json']
    likelihoods, decisions, result = [read_json(p) for p in inputs[1:]]
    keylist, cleartexts, ciphers, weights, plaintexts, generated = forward_table()
    common_denominator = 12 ** N
    joint_denominator = len(keylist) * common_denominator
    checks.check('schema/likelihoods', likelihoods['schema'], 'tiny-channel-likelihoods-v1')
    checks.check('schema/decisions', decisions['schema'], 'tiny-channel-decisions-v1')
    checks.check('schema/result', result['schema'], 'tiny-channel-result-v1')
    checks.check('result/config_sha256', result['config_sha256'], hash_file(config_path))
    checks.check('likelihoods/key_order', likelihoods['keys'], keylist)
    checks.check('likelihoods/cipher_order', likelihoods['ciphertexts'], ciphers)
    checks.check('likelihoods/denominator', likelihoods['likelihood_denominator'], common_denominator)
    checks.check('likelihoods/row_count', len(likelihoods['numerators']), len(ciphers))
    checks.check('generator/expansions_per_key', generated, [4 ** N] * len(keylist))
    checks.check('generator/all_preimages_present', all(all(y is not None for y in row) for row in plaintexts))
    masses = [sum(row[k] for row in weights) for k in range(len(keylist))]
    checks.check('normalization/each_conditional_mass', masses, [common_denominator] * len(keylist))
    checks.check('normalization/joint_mass', sum(masses), joint_denominator)
    checks.check('result/counts', result['counts'], {'keys': 36, 'ciphertexts': 4096,
                 'key_cipher_pairs': 147456, 'cleartexts': 729})
    checks.check('result/conditional_mass_numerators',
                 result['normalization']['conditional_mass_numerators'], masses)
    checks.check('result/conditional_denominator',
                 result['normalization']['conditional_denominator'], common_denominator)
    checks.check('result/joint_mass_numerator', result['normalization']['joint_mass_numerator'], sum(masses))
    checks.check('result/joint_denominator', result['normalization']['joint_denominator'], joint_denominator)
    canonical = keylist.index('aabc')
    for cipher, expected in [('wwwwww', 729), ('xxxxxx', 729), ('yyyyyy', 131072),
                             ('zzzzzz', 15552), ('wyzwyz', 384)]:
        checks.check('control/manual_weight/' + cipher, weights[ciphers.index(cipher)][canonical], expected)
    # Cipher renaming transports keys; likelihood is exactly equivariant.
    swap_index = [CIPHER.index(c) for c in 'xwyz']
    for ci, cipher in enumerate(ciphers):
        renamed = cipher.translate(str.maketrans(CIPHER, 'xwyz'))
        renamed_row = ciphers.index(renamed)
        for ki, key in enumerate(keylist):
            renamed_key = ''.join(key[i] for i in swap_index)
            checks.check('equivariance/' + cipher + '/' + key,
                         weights[renamed_row][keylist.index(renamed_key)], weights[ci][ki])
    actual_cases = decisions['cases']
    checks.check('decisions/row_count', len(actual_cases), len(ciphers))
    checks.check('decisions/unique_ciphertexts', len({r['cipher'] for r in actual_cases}), len(ciphers))
    actual_index = {r['cipher']: r for r in actual_cases}
    checks.check('decisions/cipher_set', sorted(actual_index), ciphers)
    totals = {name: {'text_correct_weight': 0, 'character_correct_weight': 0,
                     'key_correct_weight': 0 if name.endswith('key_map') or name == 'channel_hamming_key' else None}
              for name in METHODS}
    diagnostics = Counter()
    for ci, cipher in enumerate(ciphers):
        actual_weights = likelihoods['numerators'][ci]
        checks.check('likelihoods/row_width/' + cipher, len(actual_weights), len(keylist))
        for ki, key in enumerate(keylist):
            checks.check('likelihood/' + cipher + '/' + key, actual_weights[ki], weights[ci][ki])
        expected = expected_row(cipher, keylist, weights[ci], plaintexts[ci])
        actual = actual_index[cipher]
        for field in ('evidence_numerator', 'key_map_ties', 'text_map_ties'):
            checks.check('decision/' + cipher + '/' + field, actual[field], expected[field])
        checks.check('decision/' + cipher + '/method_names', sorted(actual['methods']), sorted(METHODS))
        for name in METHODS:
            checks.check('decision/' + cipher + '/' + name, actual['methods'][name], expected['methods'][name])
            for field, value in expected['methods'][name].items():
                if field in totals[name] and value is not None:
                    totals[name][field] += value
        m = expected['methods']
        checks.check('optimality/key_MAP/' + cipher, m['channel_key_map']['key_correct_weight'] >= m['lm_only_key_map']['key_correct_weight'])
        checks.check('optimality/plain_MAP/' + cipher,
                     all(m['channel_plaintext_map']['text_correct_weight'] >= r['text_correct_weight'] for r in m.values()))
        checks.check('optimality/free_Hamming/' + cipher,
                     all(m['channel_hamming_free']['character_correct_weight'] >= r['character_correct_weight'] for r in m.values()))
        checks.check('optimality/key_Hamming/' + cipher,
                     m['channel_hamming_key']['character_correct_weight'] >= m['channel_key_map']['character_correct_weight'])
        diagnostics['all_four_symbols_ciphertexts'] += len(set(cipher)) == 4
        diagnostics['key_MAP_tied_ciphertexts'] += expected['key_map_ties'] > 1
        diagnostics['text_MAP_tied_ciphertexts'] += expected['text_map_ties'] > 1
        diagnostics['free_Hamming_unrepresentable_ciphertexts'] += not m['channel_hamming_free']['representable']
    summaries = {}
    for name, values in totals.items():
        summaries[name] = {'text_success': ratio(Fraction(values['text_correct_weight'], joint_denominator)),
                           'character_accuracy': ratio(Fraction(values['character_correct_weight'], N * joint_denominator)),
                           'key_success': None if values['key_correct_weight'] is None else ratio(Fraction(values['key_correct_weight'], joint_denominator))}
        for metric, value in summaries[name].items():
            checks.check('result/method/' + name + '/' + metric, result['methods'][name][metric], value)
    checks.check('control/all_four_ciphertexts_exact', diagnostics['all_four_symbols_ciphertexts'], 1560)
    return {'schema': 'independent-tiny-channel-audit-v1',
            'status': 'PASS' if checks.mismatch_count == 0 else 'FAIL', 'checks': checks.count,
            'mismatch_count': checks.mismatch_count, 'mismatches': checks.mismatches,
            'counts': {'keys': len(keylist), 'ciphertexts': len(ciphers), 'plaintexts': len(cleartexts),
                       'forward_emission_contributions': sum(generated)},
            'control_summary': control_summary, 'method_summary': summaries, 'diagnostics': dict(diagnostics),
            'normalization': {'all_conditional_masses': '1', 'joint_mass': '1'},
            'input_sha256': {name: hash_file(path) for name, path in zip(
                ('config', 'likelihoods', 'decisions', 'result'), inputs)},
            'input_hash_scope': 'Uncompressed JSON bytes for gzip tables; raw bytes for plain JSON',
            'scope': 'Independent finite-model normalization, inference and expected-risk audit. Not a Latin recovery trial or Voynich translation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('research_gpt6'))
    parser.add_argument('--bundle', type=Path, default=Path('research_gpt6/results/exact_tiny_channel'))
    parser.add_argument('--out', type=Path)
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    if args.controls_only:
        checks = Checks()
        summary = controls(checks)
        result = {'status': 'PASS' if checks.mismatch_count == 0 else 'FAIL', 'checks': checks.count,
                  'mismatches': checks.mismatches, 'control_summary': summary}
    else:
        result = audit(args.repo, args.bundle)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'checks', 'mismatches')}, sort_keys=True))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
