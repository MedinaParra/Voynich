#!/usr/bin/env python3
"""Exhaustive inverse likelihood calculation for the preregistered tiny model.

This is a finite mathematical calibration, not a manuscript decipherer.
All comparisons use the same surjective-key family and exact integer weights.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path

METHODS = ['lm_only_key_map', 'channel_key_map', 'channel_plaintext_map',
           'channel_hamming_free', 'channel_hamming_key']


def ratio(n, d=1):
    f = Fraction(n, d)
    return {'numerator': f.numerator, 'denominator': f.denominator}


def write_json(path, value, compressed=False):
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode()
    path.write_bytes(gzip.compress(raw, mtime=0) if compressed else raw)


def lm_units(text, pi, transition):
    value = pi[text[0]]
    for a, b in zip(text, text[1:]):
        value *= transition[a][b]
    return value


def enumerate_model(n, pi, transition):
    """Inverse formula: decode C under each key, then apply alias penalties."""
    keys = [k for k in product(range(3), repeat=4) if set(k) == {0, 1, 2}]
    streams = list(product(range(4), repeat=n))
    denominator = 12**n
    weights = []
    lm_scores = []
    for stream in streams:
        row, unnormalized = [], []
        for key in keys:
            plain = tuple(key[c] for c in stream)
            language = lm_units(plain, pi, transition)
            duplicated = next(p for p in range(3) if key.count(p) == 2)
            count = plain.count(duplicated)
            row.append(language * 2**(n-count))
            unnormalized.append(language)
        weights.append(row)
        lm_scores.append(unnormalized)
    return keys, streams, weights, lm_scores, denominator


def decisions(keys, streams, weights, lm_scores):
    cases = []
    totals = {name: {'text': 0, 'characters': 0, 'key': 0 if name in
              ('lm_only_key_map', 'channel_key_map', 'channel_hamming_key') else None}
              for name in METHODS}
    diagnostics = Counter()
    for stream, row, language in zip(streams, weights, lm_scores):
        z = sum(row)
        decoded = [tuple(k[c] for c in stream) for k in keys]
        mass = defaultdict(int)
        marginals = [[0]*3 for _ in stream]
        for weight, plain in zip(row, decoded):
            mass[plain] += weight
            for i, p in enumerate(plain):
                marginals[i][p] += weight
        assert z > 0 and sum(mass.values()) == z
        assert all(sum(marginal) == z for marginal in marginals)
        key_index = max(range(len(keys)), key=lambda i: row[i])
        heuristic_index = max(range(len(keys)), key=lambda i: language[i])
        best_text_weight = max(mass.values())
        text_map = min(p for p, weight in mass.items() if weight == best_text_weight)
        free_text = tuple(max(range(3), key=lambda p: m[p]) for m in marginals)
        char_rewards = [sum(marginals[i][p] for i, p in enumerate(plain))
                        for plain in decoded]
        ham_index = max(range(len(keys)), key=lambda i: char_rewards[i])
        selected = {'lm_only_key_map': (heuristic_index, decoded[heuristic_index]),
                    'channel_key_map': (key_index, decoded[key_index]),
                    'channel_plaintext_map': (None, text_map),
                    'channel_hamming_free': (None, free_text),
                    'channel_hamming_key': (ham_index, decoded[ham_index])}
        methods = {}
        for name, (index, plain) in selected.items():
            text_weight = mass.get(plain, 0)
            char_weight = sum(marginals[i][p] for i, p in enumerate(plain))
            key_weight = None if index is None else row[index]
            methods[name] = {
                'key': None if index is None else ''.join('abc'[p] for p in keys[index]),
                'text': ''.join('abc'[p] for p in plain),
                'text_correct_weight': text_weight,
                'character_correct_weight': char_weight,
                'key_correct_weight': key_weight,
                'representable': plain in mass}
            totals[name]['text'] += text_weight
            totals[name]['characters'] += char_weight
            if index is not None:
                totals[name]['key'] += key_weight
        key_ties = sum(w == row[key_index] for w in row)
        text_ties = sum(w == best_text_weight for w in mass.values())
        diagnostics['ciphertexts_with_key_map_tie'] += key_ties > 1
        diagnostics['ciphertexts_with_text_map_tie'] += text_ties > 1
        diagnostics['key_map_decoding_differs_from_plaintext_map'] += decoded[key_index] != text_map
        diagnostics['key_map_decoding_not_in_plaintext_map_set'] += mass[decoded[key_index]] < best_text_weight
        diagnostics['lm_only_decoding_differs_from_channel_key_map'] += decoded[heuristic_index] != decoded[key_index]
        diagnostics['free_hamming_not_representable'] += free_text not in mass
        diagnostics['ciphertexts_observing_all_four_symbols'] += len(set(stream)) == 4
        # Mathematical decision inequalities, not claims about real plaintext.
        assert all(methods['channel_plaintext_map']['text_correct_weight'] >=
                   m['text_correct_weight'] for m in methods.values())
        assert all(methods['channel_hamming_free']['character_correct_weight'] >=
                   m['character_correct_weight'] for m in methods.values())
        assert all(methods['channel_hamming_key']['character_correct_weight'] >=
                   m['character_correct_weight'] for m in methods.values() if m['representable'])
        assert row[key_index] >= row[heuristic_index]
        if len(set(stream)) == 4:
            assert len(mass) == len(keys)
            # Sets correspond; lexicographic key/text tie-breaks need not.
            assert {decoded[i] for i, w in enumerate(row) if w == row[key_index]} == {
                text for text, w in mass.items() if w == best_text_weight}
        cases.append({'cipher': ''.join('wxyz'[c] for c in stream),
                      'evidence_numerator': z, 'key_map_ties': key_ties,
                      'text_map_ties': text_ties, 'methods': methods})
    return cases, totals, dict(diagnostics)


def controls(pi, transition):
    keys, streams, weights, language, d = enumerate_model(1, pi, transition)
    rows, totals, _ = decisions(keys, streams, weights, language)
    assert all(Fraction(sum(row), len(keys)*d) == Fraction(1, 4) for row in weights)
    posterior = []
    for c, row in zip(streams, weights):
        posterior.append([Fraction(sum(w for key, w in zip(keys, row) if key[c[0]] == p),
                                   sum(row)) for p in range(3)])
    assert all(row == [Fraction(p, 6) for p in pi] for row in posterior)
    assert Fraction(totals['channel_key_map']['key'], 36*d) == Fraction(1, 18)
    assert Fraction(totals['channel_plaintext_map']['text'], 36*d) == Fraction(1, 2)
    # Uniform LM: constant 3^-6; exactly 4^6 possible cipher strings.
    unnormalized = Fraction(4**6, 3**6)
    normalized_masses = []
    for key in keys:
        mass = Fraction()
        for stream in product(range(4), repeat=6):
            denominator = 3**6
            for c in stream:
                denominator *= key.count(key[c])
            mass += Fraction(1, denominator)
        assert mass == 1
        normalized_masses.append(ratio(mass))
    assert unnormalized != 1
    return {'length_one': {'cipher_marginal': ratio(1, 4),
                           'plaintext_posterior': [ratio(p, 6) for p in pi],
                           'key_map_success': ratio(totals['channel_key_map']['key'], 36*d),
                           'text_map_success': ratio(totals['channel_plaintext_map']['text'], 36*d)},
            'uniform_lm': {'uncorrected_mass_per_key': ratio(unnormalized),
                           'corrected_mass_per_key': normalized_masses},
            'scope': 'Closed-form mathematical references, not additional manuscript or Latin cases'}


def run(plan_path, out):
    raw = plan_path.read_bytes()
    p = json.loads(raw)
    assert p['clear_alphabet'] == 'abc' and p['cipher_alphabet'] == 'wxyz'
    assert p['length'] == 6 and p['probability_denominator'] == 6
    pi, transition, n = p['initial_units'], p['transition_units'], p['length']
    assert pi == [3, 2, 1] and transition == [[3, 2, 1], [1, 4, 1], [2, 1, 3]]
    assert sum(pi) == 6 and all(sum(row) == 6 and min(row) > 0 for row in transition)
    reference = controls(pi, transition)
    keys, streams, weights, language, d = enumerate_model(n, pi, transition)
    assert len(keys) == 36 and len(streams) == 4096
    columns = [sum(row[i] for row in weights) for i in range(len(keys))]
    assert columns == [d]*36 and sum(columns) == 36*d
    cases, totals, diagnostics = decisions(keys, streams, weights, language)
    assert diagnostics['ciphertexts_observing_all_four_symbols'] == 1560
    summaries = {name: {'text_success': ratio(t['text'], 36*d),
                        'character_accuracy': ratio(t['characters'], 36*d*n),
                        'key_success': None if t['key'] is None else ratio(t['key'], 36*d)}
                 for name, t in totals.items()}
    lm_mass = [ratio(sum(row[i] for row in language), 6**n) for i in range(36)]
    result = {'schema': 'tiny-channel-result-v1',
              'config_sha256': hashlib.sha256(raw).hexdigest(),
              'scope': p['scope'],
              'counts': {'keys': 36, 'ciphertexts': 4096, 'key_cipher_pairs': 147456, 'cleartexts': 729},
              'normalization': {'conditional_mass_numerators': columns, 'conditional_denominator': d,
                                'joint_mass_numerator': sum(columns), 'joint_denominator': 36*d,
                                'posterior_rows_normalized': len(cases)},
              'lm_only_mass_per_key': lm_mass,
              'methods': summaries, 'diagnostics': diagnostics,
              'truth_sampled': False, 'Voynich_translation': 'NOT_RUN',
              'meaning': 'Expected correctness probabilities under the fixed invented model, not observed historical recoveries.'}
    out.mkdir(parents=True, exist_ok=True)
    write_json(out/'likelihoods.json.gz', {'schema': 'tiny-channel-likelihoods-v1',
               'keys': [''.join('abc'[p] for p in key) for key in keys],
               'ciphertexts': [''.join('wxyz'[c] for c in stream) for stream in streams],
               'likelihood_denominator': d, 'numerators': weights}, compressed=True)
    write_json(out/'decisions.json.gz', {'schema': 'tiny-channel-decisions-v1', 'cases': cases}, compressed=True)
    write_json(out/'controls.json', reference)
    write_json(out/'result.json', result)
    print(json.dumps({'counts': result['counts'], 'methods': summaries, 'diagnostics': diagnostics}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.plan, args.out)
