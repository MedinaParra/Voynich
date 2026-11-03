#!/usr/bin/env python3
"""Independent exact audit of segmentation certificates and fragility radius.

No imports from the experiment, OCR, neural inference or paleographic approval.
The audit verifies a finite annotation family, not all possible word boundaries.
"""
import argparse
from fractions import Fraction
import gzip
import hashlib
import itertools
import json
from pathlib import Path


def raw(path):
    if path.exists():
        data = path.read_bytes()
        return gzip.decompress(data) if path.suffix == '.gz' else data
    return gzip.decompress(path.with_suffix(path.suffix + '.gz').read_bytes())


def read(path):
    return json.loads(raw(path))


def as_fraction(value):
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError('Expected [integer numerator, integer denominator]')
    a, b = value
    if type(a) is not int or type(b) is not int or b <= 0:
        raise ValueError('Invalid exact rational')
    return Fraction(a, b)


def pair(value):
    return [value.numerator, value.denominator]


def edit(a, b):
    matrix = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        matrix[i][0] = i
    for j in range(len(b) + 1):
        matrix[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            matrix[i][j] = min(matrix[i-1][j] + 1,
                               matrix[i][j-1] + 1,
                               matrix[i-1][j-1] + int(a[i-1] != b[j-1]))
    return matrix[-1][-1]


def near(a, b):
    return int(min(len(a), len(b)) >= 3 and edit(a, b) <= 1)


def tokens_at(chars, cuts):
    edges = [0] + sorted(cuts) + [len(chars)]
    return [chars[a:b] for a, b in zip(edges, edges[1:])]


def score(tokens):
    middle = tokens[1:-1]
    n = len(middle)
    if n < 2:
        return Fraction(0)
    adjacent = sum(near(a, b) for a, b in zip(middle, middle[1:]))
    ordered = sum(near(middle[i], middle[j])
                  for i in range(n) for j in range(n) if i != j)
    return Fraction(adjacent, n-1) - Fraction(ordered, n*(n-1))


def exact_cost_extremes(options):
    """Two independent cost-indexed Bellman tables, retaining exact fractions."""
    lower = {0: Fraction(0)}
    upper = {0: Fraction(0)}
    for locus_options in options:
        next_lower = {}
        next_upper = {}
        for total, previous in lower.items():
            for cost, value in locus_options:
                key = total + cost
                proposal = previous + value
                if key not in next_lower or proposal < next_lower[key]:
                    next_lower[key] = proposal
        for total, previous in upper.items():
            for cost, value in locus_options:
                key = total + cost
                proposal = previous + value
                if key not in next_upper or proposal > next_upper[key]:
                    next_upper[key] = proposal
        lower, upper = next_lower, next_upper
    return lower, upper


class Checks:
    def __init__(self):
        self.count = 0
        self.mismatches = []

    def check(self, name, actual, expected=True):
        self.count += 1
        if actual != expected:
            self.mismatches.append({'check': name, 'actual': repr(actual),
                                    'expected': repr(expected)})


def controls(checks):
    checks.check('control/edit_identity', edit('daiin', 'daiin'), 0)
    checks.check('control/edit_empty', edit('', 'abc'), 3)
    checks.check('control/edit_substitute', edit('cham', 'chag'), 1)
    checks.check('control/edit_two', edit('abc', 'axy'), 2)
    checks.check('control/short_exclusion', near('ab', 'abc'), 0)
    checks.check('control/eligible_near', near('abc', 'abd'), 1)
    checks.check('control/token_split', tokens_at('abcdef', [2, 4]), ['ab', 'cd', 'ef'])
    checks.check('control/fewer_than_two_middle', score(['edge', 'abc', 'edge']), Fraction(0))
    checks.check('control/two_middle_cancel', score(['edge', 'abc', 'abd', 'edge']), Fraction(0))
    checks.check('control/excess_positive', score(['edge', 'aaa', 'aab', 'abb', 'edge']), Fraction(1, 3))
    checks.check('control/excess_negative', score(['edge', 'aaa', 'abb', 'aab', 'edge']), Fraction(-1, 6))
    fixtures = [
        [[(0, Fraction(1, 3)), (1, Fraction(-1, 2))]],
        [[(0, Fraction(1, 7)), (1, Fraction(-2, 5))],
         [(0, Fraction(-1, 3)), (1, Fraction(2, 3)), (2, Fraction(-1, 7))]],
        [[(0, Fraction(1, 3)), (2, Fraction(1, 5))],
         [(0, Fraction(1, 4)), (1, Fraction(-1, 2))],
         [(0, Fraction(1, 2)), (1, Fraction(-2, 3))]],
    ]
    enumerated = 0
    for index, fixture in enumerate(fixtures):
        lower, upper = exact_cost_extremes(fixture)
        brute = {}
        for combination in itertools.product(*fixture):
            cost = sum(c for c, _ in combination)
            value = sum((v for _, v in combination), Fraction(0))
            brute.setdefault(cost, []).append(value)
            enumerated += 1
        checks.check(f'control/fixture{index}/costs', set(lower), set(brute))
        for cost in sorted(brute):
            checks.check(f'control/fixture{index}/min{cost}', lower[cost], min(brute[cost]))
            checks.check(f'control/fixture{index}/max{cost}', upper[cost], max(brute[cost]))
            checks.check(f'control/fixture{index}/budget_min{cost}',
                         min(v for c, v in lower.items() if c <= cost),
                         min(v for c, values in brute.items() if c <= cost for v in values))
    return {'tiny_fixture_global_combinations': enumerated, 'fixtures': len(fixtures),
            'scope': 'Exact scoring examples and independent DP versus exhaustive product enumeration.'}


def audit(repo):
    bundle = repo/'results/boundary_adversary'
    result_path = bundle/'result.json'
    result_bytes = raw(result_path)
    result = json.loads(result_bytes)
    checks = Checks()
    control_summary = controls(checks)
    control_checks = checks.count
    loci = result['loci']
    source_path = repo/'results/transcription_boundaries/comparison.json'
    source_bytes = raw(source_path)
    source = json.loads(source_bytes)
    expected_loci = {r['id']: r for r in source['loci']
                     if r.get('status') == 'compared' and r.get('letter_equal')}
    checks.check('exact_source_locus_ids', sorted(r['id'] for r in loci), sorted(expected_loci))
    checks.check('source_locus_count', len(loci), 98)
    options = []
    path_maps = []
    baseline = Fraction(0)
    local_paths = 0
    for locus in loci:
        name = locus['id']
        original = expected_loci.get(name)
        if original is None:
            continue
        a = {b['offset']: b['kind'] for b in original['vt']['boundaries']}
        b = {b['offset']: b['kind'] for b in original['zl']['boundaries']}
        mandatory = {i for i in set(a) & set(b) if a[i] != ',' and b[i] != ','}
        optional = (set(a) | set(b)) - mandatory
        checks.check(name+'/chars', locus['chars'], original['vt']['chars'])
        checks.check(name+'/mandatory', locus['mandatory'], sorted(mandatory))
        checks.check(name+'/optional', locus['optional'], sorted(optional))
        checks.check(name+'/VT_cuts', locus['vt_cuts'], sorted(a))
        checks.check(name+'/interior_offsets', all(0 < i < len(locus['chars']) for i in mandatory | optional))
        paths = locus['paths']
        checks.check(name+'/path_count', len(paths), 2**len(optional))
        checks.check(name+'/unique_path_ids', len({p['id'] for p in paths}), len(paths))
        expected_cuts = {tuple(sorted(mandatory | {offset for k, offset in enumerate(sorted(optional)) if mask & (1 << k)}))
                         for mask in range(2**len(optional))}
        actual_cuts = {tuple(p['cuts']) for p in paths}
        checks.check(name+'/all_boundary_worlds', actual_cuts, expected_cuts)
        values = []
        lookup = {}
        zero = []
        for p in paths:
            label = name+'/'+str(p['id'])
            cuts = p['cuts']
            checks.check(label+'/unique_ordered_cuts', cuts, sorted(set(cuts)))
            tokens = tokens_at(locus['chars'], cuts)
            exact = score(tokens)
            flips = len(set(cuts) ^ set(locus['vt_cuts']))
            checks.check(label+'/tokens', p['tokens'], tokens)
            checks.check(label+'/flips', p['flips'], flips)
            checks.check(label+'/score', as_fraction(p['score']), exact)
            values.append((flips, exact))
            lookup[p['id']] = (flips, exact)
            if flips == 0:
                zero.append(exact)
        checks.check(name+'/single_VT_path', len(zero), 1)
        if zero:
            baseline += zero[0]
        options.append(values)
        path_maps.append(lookup)
        local_paths += len(paths)
    checks.check('VT_score', as_fraction(result['vt_score']), baseline)
    lower, upper = exact_cost_extremes(options)
    certificates = result['certificates']
    checks.check('certificate_budgets_unique', len({c['budget'] for c in certificates}), len(certificates))
    for certificate in certificates:
        budget = certificate['budget']
        label = 'budget/'+str(budget)
        low = min(v for c, v in lower.items() if c <= budget)
        high = max(v for c, v in upper.items() if c <= budget)
        checks.check(label+'/minimum', as_fraction(certificate['min']), low)
        checks.check(label+'/maximum', as_fraction(certificate['max']), high)
        for mode, expected in [('min', low), ('max', high)]:
            witness = certificate[mode+'_witness']
            checks.check(label+'/'+mode+'/witness_length', len(witness), len(loci))
            valid = len(witness) == len(path_maps) and all(pid in mapping for pid, mapping in zip(witness, path_maps))
            checks.check(label+'/'+mode+'/valid_path_ids', valid)
            if valid:
                cost = sum(mapping[pid][0] for pid, mapping in zip(witness, path_maps))
                value = sum((mapping[pid][1] for pid, mapping in zip(witness, path_maps)), Fraction(0))
                checks.check(label+'/'+mode+'/budget_admissible', cost <= budget)
                checks.check(label+'/'+mode+'/witness_value', value, expected)
    fragile = min((c for c, v in lower.items() if v <= 0), default=None)
    checks.check('fragility_min_flips_to_nonpositive', result['fragility_min_flips_to_nonpositive'], fragile)
    return {'status': 'PASS' if not checks.mismatches else 'FAIL',
            'checks': checks.count, 'mismatches': checks.mismatches,
            'control_checks': control_checks, 'controls': control_summary,
            'loci': len(loci), 'local_paths_recomputed': local_paths,
            'certificates': len(certificates), 'VT_score_recomputed': pair(baseline),
            'fragility_min_flips_to_nonpositive': fragile,
            'exact_total_costs': len(lower),
            'result_sha256': hashlib.sha256(result_bytes).hexdigest(),
            'comparison_source_sha256': hashlib.sha256(source_bytes).hexdigest(),
            'scope': 'Independent full-matrix edit scores, exact rational cost DP, exhaustive local boundary sets, certificate witnesses and tiny global brute-force controls. Finite annotation family only; no language identification, OCR, neural inference, paleographic validation, or permutation-p-value audit.',
            'translation': 'NOT_RUN', 'training': 'NOT_RUN'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    if args.controls_only:
        checks = Checks()
        summary = controls(checks)
        output = {'status': 'PASS' if not checks.mismatches else 'FAIL',
                  'checks': checks.count, 'mismatches': checks.mismatches, 'controls': summary}
    else:
        if args.repo is None or args.out is None:
            parser.error('--repo and --out required unless --controls-only')
        output = audit(args.repo)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps({k: output[k] for k in ['status', 'checks', 'mismatches']}))
    raise SystemExit(0 if output['status'] == 'PASS' else 1)
